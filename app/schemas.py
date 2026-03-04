from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

class UserOut(BaseModel):
    id: int
    email: EmailStr
    class Config:
        from_attributes = True

class NoteBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    content: str

class NoteCreate(NoteBase):
    pass

class NoteOut(NoteBase):
    id: int
    user_id: int
    class Config:
        from_attributes = True