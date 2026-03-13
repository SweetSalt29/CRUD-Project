from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt  #responsible for encoding (creating) and decoding (verifying) JSON Web Tokens
from passlib.context import CryptContext    #for password hashing
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Security config - pulling from environment with safe fallbacks
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
# Convert to int because env variables are always strings
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hashes a plain-text password using bcrypt."""
    return pwd_context.hash(password)
    
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against the stored hash."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a encoded JWT access token.
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Use the ALGORITHM variable from .env
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt