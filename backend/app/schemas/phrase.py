from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class PhraseBase(BaseModel):
    phrase: str = Field(..., min_length=1, max_length=255, description="Texto da fala")
    purpose: str = Field(..., description="Finalidade da fala")


class PhraseCreate(PhraseBase):
    pass


class PhraseUpdate(BaseModel):
    phrase: Optional[str] = Field(None, min_length=1, max_length=255)
    purpose: Optional[str] = None


class PhraseOut(PhraseBase):
    id: int
    character_id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True

