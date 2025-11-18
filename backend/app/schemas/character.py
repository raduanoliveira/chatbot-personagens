from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class CharacterBase(BaseModel):
    name: str
    description: Optional[str] = None
    catchphrase: Optional[str] = None
    personality_traits: List[str] = Field(default_factory=list)
    image_url: Optional[HttpUrl] = None
    system_prompt: str = Field(..., min_length=1, description="Contexto do prompt é obrigatório")


class CharacterCreate(CharacterBase):
    pass


class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    catchphrase: Optional[str] = None
    personality_traits: Optional[List[str]] = None
    image_url: Optional[HttpUrl] = None
    system_prompt: Optional[str] = Field(None, min_length=1, description="Se fornecido, deve ter pelo menos 1 caractere")


class CharacterOut(CharacterBase):
    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True

