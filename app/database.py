from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

## For PostgreSQL, we remove 'check_same_thread' (which was only for SQLite)
engine = create_async_engine(
    DATABASE_URL, 
    echo=True,
    pool_size=10,         # Keeps 10 connections open for faster response
    max_overflow=20       # Allows 20 extra connections during heavy traffic
)

SessionLocal = async_sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine, 
    class_=AsyncSession
)

class Base(DeclarativeBase):
    """Base class for all database models."""
    pass