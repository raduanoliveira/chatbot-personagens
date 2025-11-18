from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.character import Character
from app.schemas.character import CharacterCreate, CharacterOut, CharacterUpdate

router = APIRouter(prefix="/characters", tags=["characters"])


@router.get("/", response_model=List[CharacterOut])
def list_characters(db: Session = Depends(get_db)):
    stmt = select(Character).order_by(Character.name.asc())
    result = db.execute(stmt).scalars().all()
    return result


@router.get("/{character_id}", response_model=CharacterOut)
def get_character(character_id: int, db: Session = Depends(get_db)):
    character = db.get(Character, character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Personagem não encontrado.")
    return character


@router.post("/", response_model=CharacterOut, status_code=status.HTTP_201_CREATED)
def create_character(payload: CharacterCreate, db: Session = Depends(get_db)):
    existing = db.execute(
        select(Character).where(Character.name == payload.name)
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Nome já está em uso.")

    character = Character(**payload.model_dump())
    db.add(character)
    db.commit()
    db.refresh(character)
    return character


@router.put("/{character_id}", response_model=CharacterOut)
def update_character(
    character_id: int, payload: CharacterUpdate, db: Session = Depends(get_db)
):
    character = db.get(Character, character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Personagem não encontrado.")

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(character, key, value)

    db.add(character)
    db.commit()
    db.refresh(character)
    return character


@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_character(character_id: int, db: Session = Depends(get_db)):
    character = db.get(Character, character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Personagem não encontrado.")

    total = db.scalar(select(func.count()).select_from(Character))
    if total is not None and total <= 1:
        raise HTTPException(
            status_code=400,
            detail="Não é possível remover todos os personagens. Pelo menos um deve permanecer.",
        )

    db.delete(character)
    db.commit()
    return None

