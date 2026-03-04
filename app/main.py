from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import models, schemas, auth, dependencies, notes, database

app = FastAPI(title="Notes CRUD API")

# Define the origins of your local frontend apps
origins = [
    "http://localhost:5500",   # VS Code Live Server
    "http://127.0.0.1:5500",   # VS Code Live Server (IP version)
    "https://www.example.com",
    "https://example.com",
]

# Testing script: Goto  inspect -> Console
# Paste: fetch("http://127.0.0.1:8000/notes/")
#   .then(res => console.log("Success! Status:", res.status))
#   .catch(err => console.error("Blocked by CORS:", err));

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the notes router
app.include_router(notes.router)

@app.on_event("startup")
async def startup():
    """Initializes the database tables on application start."""
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

@app.post("/register", response_model=schemas.UserOut)
async def register(user: schemas.UserCreate, db: AsyncSession = Depends(dependencies.get_db)):
    """Registers a new user with a specific role (Teacher/Student)."""
    # Check if user already exists
    result = await db.execute(select(models.User).where(models.User.email == user.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user with the role provided in the request
    new_user = models.User(
        email=user.email, 
        hashed_password=auth.hash_password(user.password),
        role=user.role  # Captured from schemas.UserCreate
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(dependencies.get_db)):
    """Authenticates user and returns a JWT token along with their role."""
    result = await db.execute(select(models.User).where(models.User.email == form_data.username))
    user = result.scalars().first()
    
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect email or password"
        )
    
    # Create token using the email as the subject
    access_token = auth.create_access_token(data={"sub": user.email})
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": user.role # Helpful for the frontend to know the role immediately
    }