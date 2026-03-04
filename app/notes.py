from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
import schemas, models, dependencies

router = APIRouter(prefix="/notes", tags=["Notes"])

@router.post("/", response_model=schemas.NoteOut, status_code=status.HTTP_201_CREATED)
async def create_note(
    note: schemas.NoteCreate, 
    db: AsyncSession = Depends(dependencies.get_db), 
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """Creates a note linked to the authenticated user."""
    new_note = models.Note(**note.model_dump(), user_id=current_user.id)
    db.add(new_note)
    await db.commit()
    await db.refresh(new_note)
    return new_note

@router.get("/", response_model=List[schemas.NoteOut])
async def read_notes(
    db: AsyncSession = Depends(dependencies.get_db), 
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """Retrieves only the notes belonging to the authenticated user."""
    result = await db.execute(
        select(models.Note).where(models.Note.user_id == current_user.id)
    )
    return result.scalars().all()

@router.put("/{note_id}", response_model=schemas.NoteOut)
async def update_note(
    note_id: int, 
    note_update: schemas.NoteCreate, 
    db: AsyncSession = Depends(dependencies.get_db), 
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """Updates a specific note after verifying ownership."""
    result = await db.execute(select(models.Note).where(models.Note.id == note_id))
    db_note = result.scalars().first()

    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Ownership Check: Crucial for security
    if db_note.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this note")

    db_note.title = note_update.title
    db_note.content = note_update.content
    
    await db.commit()
    await db.refresh(db_note)
    return db_note

@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int, 
    db: AsyncSession = Depends(dependencies.get_db), 
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """Deletes a specific note after verifying ownership."""
    result = await db.execute(select(models.Note).where(models.Note.id == note_id))
    db_note = result.scalars().first()

    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")

    # Ownership Check
    if db_note.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this note")

    await db.delete(db_note)
    await db.commit()
    return None