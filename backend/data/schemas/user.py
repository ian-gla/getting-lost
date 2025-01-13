from pydantic import ConfigDict, BaseModel

from .utils import to_camel


class UserResponse(BaseModel):
    id: int


class UserBase(BaseModel):
    age: str
    gender: str
    nav_skill: int
    position: int


class UserUpdate(UserBase):
    pass


class UserCreate(UserBase):
    age: str
    gender: str
    nav_skill: int
    position: int


class User(UserCreate):
    id: int
    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)
