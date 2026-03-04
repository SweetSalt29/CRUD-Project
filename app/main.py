from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import models, schemas, auth, dependencies, notes, database

app = FastAPI(title="Notes CRUD API")

# Include the notes router
app.include_router(notes.router)

@app.on_event("startup")
async def startup():
    # Create tables on startup (For mini-projects; use Alembic for production)
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

@app.post("/register", response_model=schemas.UserOut)
async def register(user: schemas.UserCreate, db: AsyncSession = Depends(dependencies.get_db)):
    # Check if user exists
    result = await db.execute(select(models.User).where(models.User.email == user.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = models.User(email=user.email, hashed_password=auth.hash_password(user.password))
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(dependencies.get_db)):
    result = await db.execute(select(models.User).where(models.User.email == form_data.username))
    user = result.scalars().first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}