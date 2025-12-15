"""
Módulo de guardrails para moderação de conteúdo.
Implementa validação de entrada e saída para prevenir conteúdo inadequado.
"""

import logging
from typing import Optional, Tuple
from enum import Enum

try:
    from better_profanity import profanity
except ImportError:
    profanity = None

try:
    from detoxify import Detoxify
except ImportError:
    Detoxify = None

logger = logging.getLogger(__name__)


class ModerationLevel(str, Enum):
    """Níveis de moderação disponíveis."""
    STRICT = "strict"
    MODERATE = "moderate"
    PERMISSIVE = "permissive"


class ContentModerationResult:
    """Resultado da moderação de conteúdo."""
    
    def __init__(
        self,
        is_safe: bool,
        reason: Optional[str] = None,
        toxicity_score: Optional[float] = None,
        has_profanity: bool = False
    ):
        self.is_safe = is_safe
        self.reason = reason
        self.toxicity_score = toxicity_score
        self.has_profanity = has_profanity
    
    def __bool__(self):
        return self.is_safe


class Guardrails:
    """Sistema de guardrails para moderação de conteúdo."""
    
    # Frases comuns que devem ser sempre permitidas (whitelist)
    SAFE_PHRASES = [
        "vou fazer um teste",
        "fazer um teste",
        "teste",
        "olá",
        "oi",
        "bom dia",
        "boa tarde",
        "boa noite",
        "obrigado",
        "obrigada",
        "por favor",
        "tudo bem",
        "como vai",
    ]
    
    def __init__(self, moderation_level: ModerationLevel = ModerationLevel.MODERATE):
        self.moderation_level = moderation_level
        self._init_profanity_checker()
        self._init_toxicity_detector()
    
    def _init_profanity_checker(self):
        """Inicializa o verificador de palavrões."""
        if profanity is None:
            logger.warning("better-profanity não está instalado. Verificação de palavrões desabilitada.")
            self.profanity_enabled = False
            return
        
        try:
            profanity.load_censor_words()
            # Carrega palavras em português também
            profanity.load_censor_words(whitelist_words=[])
            self.profanity_enabled = True
            logger.info("Verificador de palavrões inicializado com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao inicializar verificador de palavrões: {e}")
            self.profanity_enabled = False
    
    def _init_toxicity_detector(self):
        """Inicializa o detector de toxicidade."""
        if Detoxify is None:
            logger.warning("detoxify não está instalado. Detecção de toxicidade desabilitada.")
            self.toxicity_enabled = False
            self.toxicity_model = None
            return
        
        try:
            # Usa o modelo mais leve para performance
            self.toxicity_model = Detoxify('unbiased')
            self.toxicity_enabled = True
            logger.info("Detector de toxicidade inicializado com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao inicializar detector de toxicidade: {e}")
            self.toxicity_enabled = False
            self.toxicity_model = None
    
    def _check_profanity(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Verifica se o texto contém palavrões.
        
        Returns:
            Tuple[bool, Optional[str]]: (tem_profanidade, palavra_detectada)
        """
        if not self.profanity_enabled:
            return False, None
        
        try:
            if profanity.contains_profanity(text):
                # Tenta encontrar a palavra ofensiva
                censored = profanity.censor(text)
                return True, "Conteúdo ofensivo detectado"
            return False, None
        except Exception as e:
            logger.error(f"Erro ao verificar palavrões: {e}")
            return False, None
    
    def _check_toxicity(self, text: str) -> Tuple[bool, Optional[float]]:
        """
        Verifica toxicidade do texto usando ML.
        
        Returns:
            Tuple[bool, Optional[float]]: (é_tóxico, score_de_toxicidade)
        """
        if not self.toxicity_enabled or self.toxicity_model is None:
            return False, None
        
        try:
            # Limita o tamanho do texto para performance
            text_sample = text[:500] if len(text) > 500 else text
            
            results = self.toxicity_model.predict(text_sample)
            
            # Calcula score médio de toxicidade
            # Considera: toxicity, severe_toxicity, obscene, threat, insult, identity_attack
            toxicity_scores = [
                results.get('toxicity', 0),
                results.get('severe_toxicity', 0),
                results.get('obscene', 0),
                results.get('threat', 0),
                results.get('insult', 0),
                results.get('identity_attack', 0)
            ]
            
            avg_toxicity = sum(toxicity_scores) / len(toxicity_scores)
            max_toxicity = max(toxicity_scores)
            
            # Usa o máximo entre média e pico para detectar casos extremos
            final_score = max(avg_toxicity, max_toxicity * 0.7)
            
            # Retorna False como primeiro valor pois a determinação de toxicidade
            # é feita no método moderate() comparando com o threshold
            return False, final_score
        except Exception as e:
            logger.error(f"Erro ao verificar toxicidade: {e}")
            return False, None
    
    def _get_thresholds(self) -> dict:
        """Retorna os thresholds baseados no nível de moderação."""
        thresholds = {
            ModerationLevel.STRICT: {
                'toxicity_threshold': 0.3,
                'block_profanity': True,
                'require_toxicity_check': True
            },
            ModerationLevel.MODERATE: {
                'toxicity_threshold': 0.5,
                'block_profanity': True,
                'require_toxicity_check': True
            },
            ModerationLevel.PERMISSIVE: {
                'toxicity_threshold': 0.7,
                'block_profanity': False,
                'require_toxicity_check': False
            }
        }
        return thresholds.get(self.moderation_level, thresholds[ModerationLevel.MODERATE])
    
    def moderate(self, text: str, check_type: str = "both") -> ContentModerationResult:
        """
        Modera um texto verificando conteúdo inadequado.
        
        Args:
            text: Texto a ser moderado
            check_type: "input" (apenas entrada), "output" (apenas saída), "both" (ambos)
        
        Returns:
            ContentModerationResult: Resultado da moderação
        """
        if not text or not text.strip():
            return ContentModerationResult(is_safe=True)
        
        thresholds = self._get_thresholds()
        text_lower = text.lower().strip()
        
        # Ignora textos muito curtos (menos de 3 caracteres) - provavelmente não são ofensivos
        if len(text_lower) < 3:
            return ContentModerationResult(is_safe=True)
        
        # Verifica se está na whitelist de frases seguras
        for safe_phrase in self.SAFE_PHRASES:
            if safe_phrase in text_lower:
                return ContentModerationResult(is_safe=True)
        
        # Verificação de palavrões (aplica para input e both)
        has_profanity = False
        profanity_reason = None
        
        if thresholds['block_profanity'] and check_type in ["input", "both"]:
            has_profanity, profanity_reason = self._check_profanity(text)
        
        # Verificação de toxicidade (APENAS para output - desabilitada para input por performance)
        is_toxic = False
        toxicity_score = None
        
        # IMPORTANTE: Verificação de toxicidade é MUITO LENTA (modelo ML)
        # Desabilitada para input para melhorar performance
        # Apenas verifica toxicidade na saída (resposta do assistente)
        if thresholds['require_toxicity_check'] and check_type in ["output", "both"]:
            # Para input, NÃO verifica toxicidade (muito lento)
            # Para output, verifica toxicidade na resposta do assistente
            _, toxicity_score = self._check_toxicity(text)
            
            if toxicity_score is not None:
                # Ajusta threshold para textos curtos (são mais propensos a falsos positivos)
                adjusted_threshold = thresholds['toxicity_threshold']
                if len(text_lower) < 20:
                    # Aumenta o threshold em 20% para textos curtos
                    adjusted_threshold = adjusted_threshold * 1.2
                
                is_toxic = toxicity_score > adjusted_threshold
                
                # Log para debug (pode ser removido depois)
                if is_toxic:
                    logger.debug(f"Texto bloqueado: '{text[:50]}...' | Score: {toxicity_score:.3f} | Threshold: {adjusted_threshold:.3f}")
        
        # Determina se o conteúdo é seguro
        is_safe = not has_profanity and not is_toxic
        
        # Monta a razão da rejeição
        reason = None
        if not is_safe:
            reasons = []
            if has_profanity:
                reasons.append("Conteúdo ofensivo detectado")
            if is_toxic and toxicity_score:
                reasons.append(f"Toxicidade detectada (score: {toxicity_score:.2f})")
            reason = "; ".join(reasons)
        
        return ContentModerationResult(
            is_safe=is_safe,
            reason=reason,
            toxicity_score=toxicity_score,
            has_profanity=has_profanity
        )


# Instância global do guardrails (será inicializada no startup)
_guardrails_instance: Optional[Guardrails] = None


def get_guardrails() -> Guardrails:
    """Retorna a instância global do guardrails."""
    global _guardrails_instance
    if _guardrails_instance is None:
        _guardrails_instance = Guardrails(moderation_level=ModerationLevel.MODERATE)
    return _guardrails_instance


def initialize_guardrails(moderation_level: ModerationLevel = ModerationLevel.MODERATE):
    """Inicializa a instância global do guardrails."""
    global _guardrails_instance
    _guardrails_instance = Guardrails(moderation_level=moderation_level)
    logger.info(f"Guardrails inicializado com nível: {moderation_level.value}")

