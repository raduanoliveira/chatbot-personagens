from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import logging

from app.api.routes.characters import router as characters_router
from app.api.routes.chat import router as chat_router
from app.core.config import settings
from app.core.guardrails import initialize_guardrails, ModerationLevel

logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Captura erros de validação do Pydantic e loga detalhes."""
    body = await request.body()
    logger.error(f"❌ Erro de validação na rota {request.url.path}:")
    logger.error(f"   Método: {request.method}")
    logger.error(f"   Erros: {exc.errors()}")
    try:
        import json
        body_str = json.dumps(json.loads(body.decode('utf-8')), indent=2, ensure_ascii=False)
        logger.error(f"   Body recebido:\n{body_str}")
    except Exception:
        logger.error(f"   Body recebido (raw): {body.decode('utf-8', errors='ignore')[:500]}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )

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

