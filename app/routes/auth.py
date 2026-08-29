from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.rate_limit import client_ip, enforce, login_limiter, register_limiter
from app.schemas import UserCreate, UserLogin, UserResponse, LoginResponse
from app.security import (
    create_access_token,
    hash_password,
    verify_password,
    waste_password_comparison,
)
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


def find_user_by_email(db: Session, email: str) -> User | None:
    """E-mails novos já chegam normalizados; a comparação em lower cobre os
    cadastros antigos, gravados com a caixa original."""
    return db.query(User).filter(func.lower(User.email) == email).first()


@router.post("/register", response_model=UserResponse)
def register(payload: UserCreate, request: Request, db: Session = Depends(get_db)):
    enforce(register_limiter, client_ip(request))

    existing_user = find_user_by_email(db, payload.email)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="E-mail já cadastrado",
        )

    user = User(
        email=payload.email,
        name=payload.name,
        password_hash=hash_password(payload.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post("/login", response_model=LoginResponse)
def login(payload: UserLogin, request: Request, db: Session = Depends(get_db)):
    ip = client_ip(request)

    enforce(login_limiter, f"ip:{ip}")
    enforce(login_limiter, f"email:{payload.email}")

    user = find_user_by_email(db, payload.email)

    if not user:
        waste_password_comparison()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
        )

    login_limiter.reset(f"ip:{ip}")
    login_limiter.reset(f"email:{payload.email}")

    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
        },
    }


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user