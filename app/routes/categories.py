from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.dependencies import get_current_user

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[schemas.CategoryResponse])
def list_categories(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return (
        db.query(models.Category)
        .filter(models.Category.user_id == current_user.id)
        .order_by(models.Category.type.asc(), models.Category.name.asc())
        .all()
    )


@router.post("/", response_model=schemas.CategoryResponse)
def create_category(
    payload: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    existing = (
        db.query(models.Category)
        .filter(
            models.Category.name == payload.name,
            models.Category.type == payload.type,
            models.Category.user_id == current_user.id,
        )
        .first()
    )

    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")

    category = models.Category(
        **payload.model_dump(),
        user_id=current_user.id,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.put("/{category_id}", response_model=schemas.CategoryResponse)
def update_category(
    category_id: int,
    payload: schemas.CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    category = (
        db.query(models.Category)
        .filter(
            models.Category.id == category_id,
            models.Category.user_id == current_user.id,
        )
        .first()
    )

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    category.name = payload.name
    category.type = payload.type

    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    category = (
        db.query(models.Category)
        .filter(
            models.Category.id == category_id,
            models.Category.user_id == current_user.id,
        )
        .first()
    )

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    db.delete(category)
    db.commit()
    return {"message": "Category deleted"}