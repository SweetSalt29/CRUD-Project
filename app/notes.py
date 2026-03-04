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
    """Creates a note. Both teachers and students create notes for themselves."""
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
    """
    Teachers can see all notes in the system. 
    Students can only see their own.
    """
    if current_user.role == models.UserRole.TEACHER:
        # Teachers fetch everything
        query = select(models.Note)
    else:
        # Students fetch only their own
        query = select(models.Note).where(models.Note.user_id == current_user.id)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.put("/{note_id}", response_model=schemas.NoteOut)
async def update_note(
    note_id: int, 
    note_update: schemas.NoteCreate, 
    db: AsyncSession = Depends(dependencies.get_db), 
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """Updates a note if the user is a teacher OR the owner."""
    result = await db.execute(select(models.Note).where(models.Note.id == note_id))
    db_note = result.scalars().first()

    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Permission Logic: Allow if user is a teacher OR the original owner
    is_teacher = current_user.role == models.UserRole.TEACHER
    is_owner = db_note.user_id == current_user.id

    if not (is_teacher or is_owner):
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
    """Deletes a note if the user is a teacher OR the owner."""
    result = await db.execute(select(models.Note).where(models.Note.id == note_id))
    db_note = result.scalars().first()

    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")

    # Permission Logic: Allow if user is a teacher OR the original owner
    is_teacher = current_user.role == models.UserRole.TEACHER
    is_owner = db_note.user_id == current_user.id

    if not (is_teacher or is_owner):
        raise HTTPException(status_code=403, detail="Not authorized to delete this note")

    await db.delete(db_note)
    await db.commit()
    return None