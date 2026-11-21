from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class LLMMessage(BaseModel):
    role: str  # "system", "user", "assistant"
    content: str

class LLMResponse(BaseModel):
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    usage: Optional[Dict[str, int]] = None

class BaseLLMProvider(ABC):
    @abstractmethod
    async def chat_complete(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.2,
        format_json: bool = False,
        system_prompt: Optional[str] = None
    ) -> str:
        """Execute a completion request and return the text or JSON response."""
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if provider endpoint is reachable."""
        pass
