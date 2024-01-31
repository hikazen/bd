from datetime import datetime
from typing import List

from pydantic import BaseModel, validator


class PostCreate(BaseModel):
    title: str
    text: str

    user_id: int


class PostBase(BaseModel):
    id: int
    title: str
    text: str
    

    created_at: datetime
    updated_at: datetime

    user_id: int


class Config:
    arbitrary_types_allowed = True


class SignUpModel(BaseModel):
    email: str
    password: str
    password_confirm: str


class SignInModel(BaseModel):
    email: str
    password: str


class UserModel(BaseModel):
    id: int
    email: str
    first_name: str = ''
    last_name: str = ''
    posts: List[PostBase]