from pydantic import BaseModel
from typing import Literal


UserRole = Literal["соискатель", "работодатель"]

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: UserRole

class User(UserCreate):
    id: int

    class Config:
        orm_mode = True
