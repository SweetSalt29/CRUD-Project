from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# echo=True allows you to see the generated SQL in your terminal (great for debugging)
engine = create_async_engine(DATABASE_URL, echo=True)

SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

class Base(DeclarativeBase):
    """Base class for all database models."""
    pass