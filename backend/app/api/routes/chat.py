from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from openai import OpenAI

from app.database import get_db
from app.models.character import Character
from app.core.config import settings
from app.core.guardrails import get_guardrails, ModerationLevel

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessage(BaseModel):
    message: str
    character_id: int
    conversation_history: List[dict] = []


class ChatResponse(BaseModel):
    response: str


def get_openai_client():
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key não configurada. Configure OPENAI_API_KEY no ambiente."
        )
    return OpenAI(api_key=settings.openai_api_key)


@router.post("/", response_model=ChatResponse)
def chat(payload: ChatMessage, db: Session = Depends(get_db)):
    """Envia uma mensagem para o personagem e retorna a resposta."""
    character = db.get(Character, payload.character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Personagem não encontrado.")
    
    # Validação de entrada com guardrails (apenas palavrões para performance)
    if settings.moderation_enabled:
        guardrails = get_guardrails()
        # Verifica apenas palavrões na entrada (toxicidade é lenta, verifica apenas na saída)
        input_moderation = guardrails.moderate(payload.message, check_type="input")
        
        if not input_moderation:
            # Mensagem genérica para não expor detalhes da moderação
            safe_response = (
                "Desculpe, mas não posso responder a essa mensagem. "
                "Vamos manter nossa conversa respeitosa e apropriada!"
            )
            
            # Personaliza a resposta baseado no personagem se possível
            if character.name.lower() == "mario":
                safe_response = (
                    "Mamma mia! Desculpe, mas não posso responder isso. "
                    "Vamos manter nossa aventura divertida e respeitosa! It's-a me, Mario! 🍄"
                )
            
            return ChatResponse(response=safe_response)
    
    client = get_openai_client()
    
    # Monta o histórico de mensagens
    messages = [
        {"role": "system", "content": character.system_prompt}
    ]
    
    # Adiciona histórico da conversa
    messages.extend(payload.conversation_history)
    
    # Adiciona a mensagem atual do usuário
    messages.append({"role": "user", "content": payload.message})
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.8,
            max_tokens=2000  # Aumentado para permitir respostas mais completas
        )
        
        assistant_message = response.choices[0].message.content
        
        # Validação de saída com guardrails (apenas palavrões para performance)
        # Nota: Verificação de toxicidade na saída foi desabilitada para melhorar performance
        # A OpenAI já faz moderação de conteúdo, então isso é redundante
        if settings.moderation_enabled:
            guardrails = get_guardrails()
            # Verifica apenas palavrões na saída (rápido)
            output_moderation = guardrails.moderate(assistant_message, check_type="input")
            
            if not output_moderation:
                # Se a resposta do assistente for inadequada, retorna mensagem segura
                safe_response = (
                    "Desculpe, mas não consigo formular uma resposta apropriada no momento. "
                    "Vamos mudar de assunto?"
                )
                
                # Personaliza baseado no personagem
                if character.name.lower() == "mario":
                    safe_response = (
                        "Mamma mia! Deixa eu pensar melhor sobre isso... "
                        "Vamos falar de algo mais divertido! It's-a me, Mario! 🍄"
                    )
                
                return ChatResponse(response=safe_response)
        
        return ChatResponse(response=assistant_message)
    
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erro ao comunicar com a API da OpenAI: {str(e)}", exc_info=True)
        
        # Mensagem de erro mais amigável
        error_detail = str(e)
        if "api_key" in error_detail.lower() or "authentication" in error_detail.lower():
            error_detail = "Chave da API da OpenAI inválida ou não configurada"
        elif "rate limit" in error_detail.lower():
            error_detail = "Limite de requisições excedido. Tente novamente em alguns instantes."
        elif "timeout" in error_detail.lower():
            error_detail = "Tempo de resposta excedido. Tente novamente."
        
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar mensagem: {error_detail}"
        )

