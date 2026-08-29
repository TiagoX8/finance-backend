from datetime import date
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, BeforeValidator, ConfigDict, EmailStr, Field


TransactionType = Literal["income", "expense"]
CategoryType = Literal["income", "expense"]

# bcrypt rejeita entradas com mais de 72 bytes, e o limite é em bytes, não em
# caracteres: uma senha de 40 caracteres acentuados já pode estourar.
PASSWORD_MAX_BYTES = 72
PASSWORD_MIN_LENGTH = 8


def _check_password_bytes(value: str) -> str:
    if len(value.encode("utf-8")) > PASSWORD_MAX_BYTES:
        raise ValueError(f"A senha não pode ter mais de {PASSWORD_MAX_BYTES} bytes")

    return value


Email = Annotated[
    EmailStr,
    BeforeValidator(lambda v: v.strip().lower() if isinstance(v, str) else v),
]

Password = Annotated[
    str,
    Field(min_length=PASSWORD_MIN_LENGTH),
    AfterValidator(_check_password_bytes),
]


class TransactionBase(BaseModel):
    title: str
    category: str
    amount: float
    type: TransactionType
    date: date


class TransactionCreate(TransactionBase):
    title: str = Field(min_length=1, max_length=120)
    category: str = Field(min_length=1, max_length=80)


class TransactionUpdate(TransactionCreate):
    pass


class TransactionResponse(TransactionBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class CategoryBase(BaseModel):
    name: str
    type: CategoryType


class CategoryCreate(CategoryBase):
    name: str = Field(min_length=1, max_length=80)


class CategoryUpdate(CategoryCreate):
    pass


class CategoryResponse(CategoryBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    email: EmailStr
    name: str | None = None


class UserCreate(UserBase):
    email: Email
    name: str | None = Field(default=None, max_length=120)
    password: Password


class UserLogin(BaseModel):
    email: Email
    password: Annotated[str, AfterValidator(_check_password_bytes)]


class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse