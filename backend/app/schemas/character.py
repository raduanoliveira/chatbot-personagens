from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator

from app.schemas.phrase import PhraseOut


# Finalidades disponíveis
AVAILABLE_PURPOSES = [
    "para se apresentar",
    "para surpresa",
    "para animar",
    "para comemorações",
    "para começar algo"
]


class PhraseInput(BaseModel):
    """Schema para entrada de frase no formulário."""
    phrase: str = Field(..., min_length=1, max_length=255, description="Texto da fala")
    purpose: str = Field(..., description="Finalidade da fala")


class CharacterBase(BaseModel):
    name: str
    description: Optional[str] = None
    catchphrase: Optional[str] = None
    personality_traits: List[str] = Field(default_factory=list)
    image_url: Optional[str] = Field(None, description="URL da imagem do personagem (pode ser URL ou data URI)")
    who_is_character: str = Field(..., min_length=1, max_length=255, description="Descrição de quem é o personagem")
    phrases: List[PhraseInput] = Field(..., min_items=5, max_items=5, description="Lista de falas (uma para cada finalidade)")
    
    @model_validator(mode='before')
    @classmethod
    def validate_image_url(cls, data):
        # Converte string vazia em None para image_url
        if isinstance(data, dict) and 'image_url' in data:
            if data['image_url'] == '' or (isinstance(data['image_url'], str) and not data['image_url'].strip()):
                data['image_url'] = None
        return data


class CharacterCreate(CharacterBase):
    pass


class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    catchphrase: Optional[str] = None
    personality_traits: Optional[List[str]] = None
    image_url: Optional[str] = Field(None, description="URL da imagem do personagem (pode ser URL ou data URI)")
    who_is_character: Optional[str] = Field(None, min_length=1, max_length=255)
    phrases: Optional[List[PhraseInput]] = Field(None, min_items=5, max_items=5)


class CharacterOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    catchphrase: Optional[str] = None
    personality_traits: List[str] = Field(default_factory=list)
    image_url: Optional[str] = None
    who_is_character: str
    phrases: List[PhraseOut]  # Retorna as frases completas com IDs
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
