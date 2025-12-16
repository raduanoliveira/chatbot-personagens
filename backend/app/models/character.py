from sqlalchemy import Column, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import relationship

from app.models.base import Base


class Character(Base):
    """Represents a playable chatbot persona."""

    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    catchphrase = Column(String(255), nullable=True)
    personality_traits = Column(JSON, nullable=True)
    image_url = Column(Text, nullable=True)
    who_is_character = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    
    # Relacionamento
    phrases = relationship("Phrase", back_populates="character", cascade="all, delete-orphan")


