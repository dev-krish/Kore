import json
import logging
from typing import Any, Dict, List, Optional
import httpx
from app.core.config import settings
from app.engine.llm.base import BaseLLMProvider, LLMMessage

logger = logging.getLogger(__name__)

class OllamaProvider(BaseLLMProvider):
    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL

    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    async def chat_complete(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.2,
        format_json: bool = False,
        system_prompt: Optional[str] = None
    ) -> str:
        url = f"{self.base_url}/api/chat"
        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        
        for msg in messages:
            formatted_messages.append({"role": msg.role, "content": msg.content})

        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": 0.9,
                "num_predict": 400,  # Ensure snappy local responses on CPU/16GB RAM
            }
        }
        if format_json:
            payload["format"] = "json"

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                res = await client.post(url, json=payload)
                res.raise_for_status()
                data = res.json()
                content = data.get("message", {}).get("content", "")
                return content
        except Exception as e:
            logger.warning(f"Ollama request error for model {self.model}: {e}. Returning safe fallback.")
            if format_json:
                return json.dumps({
                    "status": "fallback",
                    "reasoning": f"Local inference timed out or model busy: {str(e)}"
                })
            return f"Ollama execution completed with fallback."
