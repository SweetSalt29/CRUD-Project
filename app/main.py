from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from . import models, schemas, auth, dependencies, CRUD, database

app = FastAPI(title="CRUD API Project (Notes App)")

# Define the Auth Router
auth_router = APIRouter(prefix="/auth", tags=["Register/Login"])

# --- CORS Setup ---
origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "https://www.example.com",
    "https://example.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

# Attach endpoints to the auth_router instead of @app
@auth_router.post("/register", response_model=schemas.UserOut)
async def register(user: schemas.UserCreate, db: AsyncSession = Depends(dependencies.get_db)):
    result = await db.execute(select(models.User).where(models.User.email == user.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = models.User(
        email=user.email, 
        hashed_password=auth.hash_password(user.password),
        role=user.role
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@auth_router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(dependencies.get_db)):
    result = await db.execute(select(models.User).where(models.User.email == form_data.username))
    user = result.scalars().first()
    
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer", "role": user.role}

# 3. Include both Routers in the main app
app.include_router(auth_router)  # Handles /auth/register and /auth/login
app.include_router(CRUD.router)  # Handles your notes routes