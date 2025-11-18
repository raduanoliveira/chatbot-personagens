from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.characters import router as characters_router
from app.api.routes.chat import router as chat_router
from app.core.config import settings
from app.core.guardrails import initialize_guardrails, ModerationLevel

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}


app.include_router(characters_router, prefix=settings.api_prefix)
app.include_router(chat_router, prefix=settings.api_prefix)


@app.on_event("startup")
async def startup_event():
    """Inicializa os guardrails na inicialização da aplicação."""
    if settings.moderation_enabled:
        try:
            # Converte string para ModerationLevel
            level_map = {
                "strict": ModerationLevel.STRICT,
                "moderate": ModerationLevel.MODERATE,
                "permissive": ModerationLevel.PERMISSIVE
            }
            moderation_level = level_map.get(
                settings.moderation_level.lower(),
                ModerationLevel.MODERATE
            )
            initialize_guardrails(moderation_level=moderation_level)
        except Exception as e:
            # Log do erro mas não impede a inicialização da aplicação
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Erro ao inicializar guardrails: {e}. Moderação desabilitada.")

