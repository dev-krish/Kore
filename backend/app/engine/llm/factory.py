import logging
from app.core.config import settings
from app.engine.llm.base import BaseLLMProvider
from app.engine.llm.ollama import OllamaProvider
from app.engine.llm.mock import MockLLMProvider

logger = logging.getLogger(__name__)

_provider_instance: BaseLLMProvider = None

def get_llm_provider() -> BaseLLMProvider:
    global _provider_instance
    if _provider_instance is not None:
        return _provider_instance

    provider_type = settings.LLM_PROVIDER.lower()
    logger.info(f"Initializing LLM Provider: {provider_type}")
    
    if provider_type == "ollama":
        _provider_instance = OllamaProvider(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL
        )
    elif provider_type == "mock" or provider_type == "demo":
        _provider_instance = MockLLMProvider()
    else:
        logger.warning(f"Unknown LLM_PROVIDER '{provider_type}'. Falling back to Ollama.")
        _provider_instance = OllamaProvider()

    return _provider_instance
