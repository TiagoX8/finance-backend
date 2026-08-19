from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr


TransactionType = Literal["income", "expense"]
CategoryType = Literal["income", "expense"]


class TransactionBase(BaseModel):
    title: str
    category: str
    amount: float
    type: TransactionType
    date: date


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(TransactionBase):
    pass


class TransactionResponse(TransactionBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class CategoryBase(BaseModel):
    name: str
    type: CategoryType


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    email: EmailStr
    name: str | None = None


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse