from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, EmailStr


class ModelName(Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


class Image(BaseModel):
    url: str
    name: str


class Item(BaseModel):
    name: str
    description: Optional[str] = Field(
        None, title="The description of the item", max_length=300
    )
    price: float = Field(..., gt=0, description="The price must be greater than zero")
    tax: Optional[float] = None
    tags: set[str] = set()
    image: Optional[Image] = None


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserIn(UserBase):
    password: str


class UserInDb(UserBase):
    hashed_password: str


class UserOut(UserBase):
    pass
