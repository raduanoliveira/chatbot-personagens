from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.character import Character
from app.models.phrase import Phrase
from app.schemas.character import CharacterCreate, CharacterOut, CharacterUpdate, AVAILABLE_PURPOSES

router = APIRouter(prefix="/characters", tags=["characters"])


@router.get("/", response_model=List[CharacterOut])
def list_characters(db: Session = Depends(get_db)):
    try:
        stmt = select(Character).options(joinedload(Character.phrases)).order_by(Character.name.asc())
        result = db.execute(stmt).unique().scalars().all()
        # Garante que todos os personagens têm phrases (mesmo que vazia)
        for character in result:
            if not hasattr(character, 'phrases') or character.phrases is None:
                character.phrases = []
        return result
    except Exception as e:
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        error_trace = traceback.format_exc()
        logger.error(f"Erro ao listar personagens: {e}\n{error_trace}")
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao listar personagens. Verifique se as migrations foram executadas. Erro: {str(e)}"
        )


@router.get("/{character_id}", response_model=CharacterOut)
def get_character(character_id: int, db: Session = Depends(get_db)):
    character = db.execute(
        select(Character).options(joinedload(Character.phrases)).where(Character.id == character_id)
    ).unique().scalar_one_or_none()
    if not character:
        raise HTTPException(status_code=404, detail="Personagem não encontrado.")
    return character


@router.post("/", response_model=CharacterOut, status_code=status.HTTP_201_CREATED)
def create_character(payload: CharacterCreate, db: Session = Depends(get_db)):
    import logging
    logger = logging.getLogger(__name__)
    
    # Log do payload recebido para debug
    try:
        logger.info(f"📥 Payload recebido: name={payload.name}, phrases_count={len(payload.phrases) if payload.phrases else 0}")
    except Exception as e:
        logger.error(f"❌ Erro ao processar payload: {e}")
        raise
    
    # Valida se nome já existe
    existing = db.execute(
        select(Character).where(Character.name == payload.name)
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Nome já está em uso.")
    
    # Valida que todas as finalidades estão presentes
    if len(payload.phrases) != len(AVAILABLE_PURPOSES):
        raise HTTPException(
            status_code=400,
            detail=f"É necessário fornecer exatamente {len(AVAILABLE_PURPOSES)} falas, uma para cada finalidade."
        )
    
    # Valida que não há finalidades duplicadas
    purposes = [p.purpose for p in payload.phrases]
    if len(purposes) != len(set(purposes)):
        raise HTTPException(
            status_code=400,
            detail="Não pode haver duas falas com a mesma finalidade."
        )
    
    # Valida que todas as finalidades obrigatórias estão presentes
    required_purposes = set(AVAILABLE_PURPOSES)
    provided_purposes = set(purposes)
    if required_purposes != provided_purposes:
        missing = required_purposes - provided_purposes
        raise HTTPException(
            status_code=400,
            detail=f"Faltam as seguintes finalidades: {', '.join(missing)}"
        )
    
    # Valida que todas as finalidades são válidas
    invalid_purposes = provided_purposes - required_purposes
    if invalid_purposes:
        raise HTTPException(
            status_code=400,
            detail=f"Finalidades inválidas: {', '.join(invalid_purposes)}. Finalidades válidas: {', '.join(AVAILABLE_PURPOSES)}"
        )

    # Cria o personagem
    character_data = payload.model_dump(exclude={"phrases"})
    character = Character(**character_data)
    db.add(character)
    db.flush()  # Para obter o ID do personagem
    
    # Cria as falas
    for phrase_data in payload.phrases:
        phrase = Phrase(
            character_id=character.id,
            phrase=phrase_data.phrase,
            purpose=phrase_data.purpose
        )
        db.add(phrase)
    
    db.commit()
    db.refresh(character)
    # Carrega as phrases para retornar
    db.refresh(character, ["phrases"])
    return character


@router.put("/{character_id}", response_model=CharacterOut)
def update_character(
    character_id: int, payload: CharacterUpdate, db: Session = Depends(get_db)
):
    character = db.execute(
        select(Character).options(joinedload(Character.phrases)).where(Character.id == character_id)
    ).unique().scalar_one_or_none()
    if not character:
        raise HTTPException(status_code=404, detail="Personagem não encontrado.")

    # Atualiza dados do personagem (exceto phrases)
    data = payload.model_dump(exclude_unset=True, exclude={"phrases"})
    for key, value in data.items():
        setattr(character, key, value)
    
    # Se phrases foram fornecidas, atualiza
    if payload.phrases is not None:
        # Valida que todas as finalidades estão presentes
        if len(payload.phrases) != len(AVAILABLE_PURPOSES):
            raise HTTPException(
                status_code=400,
                detail=f"É necessário fornecer exatamente {len(AVAILABLE_PURPOSES)} falas, uma para cada finalidade."
            )
        
        # Valida que não há finalidades duplicadas
        purposes = [p.purpose for p in payload.phrases]
        if len(purposes) != len(set(purposes)):
            raise HTTPException(
                status_code=400,
                detail="Não pode haver duas falas com a mesma finalidade."
            )
        
        # Valida que todas as finalidades obrigatórias estão presentes
        required_purposes = set(AVAILABLE_PURPOSES)
        provided_purposes = set(purposes)
        if required_purposes != provided_purposes:
            missing = required_purposes - provided_purposes
            raise HTTPException(
                status_code=400,
                detail=f"Faltam as seguintes finalidades: {', '.join(missing)}"
            )
        
        # Remove todas as phrases antigas
        # Cria uma cópia da lista para evitar problemas durante a iteração
        old_phrases = list(character.phrases)
        for old_phrase in old_phrases:
            db.delete(old_phrase)
        db.flush()  # Garante que as deletes foram processadas
        
        # Cria novas phrases
        for phrase_data in payload.phrases:
            phrase = Phrase(
                character_id=character.id,
                phrase=phrase_data.phrase,
                purpose=phrase_data.purpose
            )
            db.add(phrase)

    # Não precisa fazer db.add(character) novamente, pois já está na sessão
    db.commit()
    # Recarrega o character com as novas phrases
    db.refresh(character)
    # Força o reload das phrases
    character = db.execute(
        select(Character).options(joinedload(Character.phrases)).where(Character.id == character_id)
    ).unique().scalar_one()
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

