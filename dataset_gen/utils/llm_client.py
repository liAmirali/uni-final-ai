"""
LLM client wrapper for OpenAI-compatible APIs.
"""
from typing import List, Dict, Any, Optional
from openai import OpenAI
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)

from config import (
    METIS_API_KEY,
    METIS_BASE_URL,
    DEFAULT_MODEL,
    TEMPERATURE,
    TOP_P,
    PRESENCE_PENALTY,
    FREQUENCY_PENALTY
)


def create_openai_client(api_key: Optional[str] = None, base_url: Optional[str] = None) -> OpenAI:
    """
    Create an OpenAI client instance.
    
    Args:
        api_key: API key (defaults to config)
        base_url: Base URL (defaults to config)
    
    Returns:
        OpenAI client instance
    """
    return OpenAI(
        api_key=api_key or METIS_API_KEY,
        base_url=base_url or METIS_BASE_URL,
        http_client=None
    )


class LLMClient:
    """Wrapper for LLM API calls with support for langchain messages."""
    
    def __init__(
        self,
        client: Optional[OpenAI] = None,
        temperature: float = TEMPERATURE,
        top_p: float = TOP_P,
        presence_penalty: float = PRESENCE_PENALTY,
        frequency_penalty: float = FREQUENCY_PENALTY
    ):
        """
        Initialize LLM client.
        
        Args:
            client: OpenAI client (creates default if not provided)
            temperature: Temperature for generation
            top_p: Top-p for generation
            presence_penalty: Presence penalty
            frequency_penalty: Frequency penalty
        """
        self.client = client or create_openai_client()
        self.temperature = temperature
        self.top_p = top_p
        self.presence_penalty = presence_penalty
        self.frequency_penalty = frequency_penalty
    
    def _role(self, m: BaseMessage) -> str:
        """Extract role from message."""
        return "assistant" if m.type == "ai" else "user" if m.type == "human" else "system"
    
    def _text(self, content: Any) -> str:
        """Extract text content from message."""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for p in content:
                if isinstance(p, dict):
                    parts.append(p.get("text") or p.get("content") or "")
                else:
                    parts.append(str(p))
            return "\n".join(x for x in parts if x)
        return str(content)
    
    def _build_payload(self, messages: List[BaseMessage]) -> List[ChatCompletionMessageParam]:
        """Build API payload from langchain messages."""
        payload = []
        for m in messages:
            if isinstance(m, SystemMessage):
                payload.append(ChatCompletionSystemMessageParam(
                    role="system",
                    content=self._text(m.content),
                ))
            elif isinstance(m, HumanMessage):
                payload.append(ChatCompletionUserMessageParam(
                    role="user",
                    content=self._text(m.content),
                ))
            elif isinstance(m, AIMessage):
                payload.append(ChatCompletionAssistantMessageParam(
                    role="assistant",
                    content=self._text(m.content),
                ))
        return payload
    
    def generate(
        self,
        messages: List[BaseMessage],
        model: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        Generate completion from messages.
        
        Args:
            messages: List of langchain messages
            model: Model to use (defaults to config)
            **kwargs: Additional generation parameters
        
        Returns:
            OpenAI completion response
        """
        payload = self._build_payload(messages)
        
        generation_params = {
            "model": model or DEFAULT_MODEL,
            "messages": payload,
            "temperature": kwargs.get("temperature", self.temperature),
            "top_p": kwargs.get("top_p", self.top_p),
        }
        
        # Only add penalties if they're non-zero
        if self.presence_penalty:
            generation_params["presence_penalty"] = kwargs.get("presence_penalty", self.presence_penalty)
        if self.frequency_penalty:
            generation_params["frequency_penalty"] = kwargs.get("frequency_penalty", self.frequency_penalty)
        
        return self.client.chat.completions.create(**generation_params)
    
    def generate_simple(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        Generate completion from simple dict messages.
        
        Args:
            messages: List of dicts with 'role' and 'content' keys
            model: Model to use
            **kwargs: Additional generation parameters
        
        Returns:
            OpenAI completion response
        """
        generation_params = {
            "model": model or DEFAULT_MODEL,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.temperature),
            "top_p": kwargs.get("top_p", self.top_p),
        }
        
        if self.presence_penalty:
            generation_params["presence_penalty"] = kwargs.get("presence_penalty", self.presence_penalty)
        if self.frequency_penalty:
            generation_params["frequency_penalty"] = kwargs.get("frequency_penalty", self.frequency_penalty)
        
        return self.client.chat.completions.create(**generation_params)

