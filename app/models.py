from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
from typing import List

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))

    # Relationship to Notes
    notes: Mapped[List["Note"]] = relationship(back_populates="owner", cascade="all, delete-orphan")

class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), index=True)
    content: Mapped[str] = mapped_column(Text)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    owner: Mapped["User"] = relationship(back_populates="notes")