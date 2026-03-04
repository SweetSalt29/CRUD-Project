from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from models import UserRole # Import the Enum for validation

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    # Allows users to choose a role, defaults to student
    role: UserRole = UserRole.STUDENT 

class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: UserRole

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