"""
Token management service (Part 4 - Token Economics & Spam Prevention).

Implements token counting, spam detection, and overflow handling.
"""

from typing import Optional, Literal

from ..utils.token_utils import count_text_tokens, pick_encoding
from ..utils.router import pick_model
from ..utils.prompts import render
from ..utils.llm_client import LLMClient
from ..schemas.token_management import SpamFilterResult, ProviderConfig


class TokenManagementService:
    """Service for token management and spam prevention."""
    
    def __init__(self, provider: str = "groq"):
        """
        Initialize token management service.
        
        Args:
            provider: Default LLM provider to use
        """
        self.provider = provider
    
    def check_and_filter_spam(
        self,
        message: str,
        max_tokens: int = 150,
        strategy: Literal["truncate", "summarize"] = "truncate",
        provider_config: Optional[ProviderConfig] = None
    ) -> tuple[SpamFilterResult, int]:
        """
        Check message token count and filter spam.
        
        Args:
            message: Input message to check
            max_tokens: Maximum allowed tokens
            strategy: Strategy for handling overflow ("truncate" or "summarize")
            provider_config: Optional provider configuration override
        
        Returns:
            Tuple of (SpamFilterResult, latency_ms)
        """
        import time
        start_time = time.time()
        
        # Determine provider
        provider = provider_config.provider if provider_config else self.provider
        
        # Count tokens
        model = pick_model(provider, "general", tier="general")
        original_token_count = count_text_tokens(message, provider, model)
        
        # If within limit, accept as-is
        if original_token_count <= max_tokens:
            latency_ms = int((time.time() - start_time) * 1000)
            return SpamFilterResult(
                status="ACCEPTED",
                original_token_count=original_token_count,
                processed_token_count=original_token_count,
                processed_message=message,
                action="None",
                tokens_saved=0
            ), latency_ms
        
        # Message exceeds limit - apply strategy
        if strategy == "truncate":
            result = self._truncate_message(message, max_tokens, provider, model)
            latency_ms = int((time.time() - start_time) * 1000)
            return result, latency_ms
        
        elif strategy == "summarize":
            result = self._summarize_message(
                message, max_tokens, provider, model, provider_config
            )
            latency_ms = int((time.time() - start_time) * 1000)
            return result, latency_ms
        
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    
    def _truncate_message(
        self,
        message: str,
        max_tokens: int,
        provider: str,
        model: str
    ) -> SpamFilterResult:
        """Truncate message to max_tokens."""
        enc = pick_encoding(provider, model)
        tokens = enc.encode(message, disallowed_special=())
        truncated_tokens = tokens[:max_tokens]
        truncated_message = enc.decode(truncated_tokens) + "... [TRUNCATED]"
        
        processed_token_count = count_text_tokens(truncated_message, provider, model)
        original_token_count = len(tokens)
        
        return SpamFilterResult(
            status="BLOCKED/TRUNCATED",
            original_token_count=original_token_count,
            processed_token_count=processed_token_count,
            processed_message=truncated_message,
            action="Truncated",
            tokens_saved=original_token_count - processed_token_count
        )
    
    def _summarize_message(
        self,
        message: str,
        max_tokens: int,
        provider: str,
        model: str,
        provider_config: Optional[ProviderConfig]
    ) -> SpamFilterResult:
        """Summarize message using LLM."""
        original_token_count = count_text_tokens(message, provider, model)
        
        # Render overflow_summarize prompt
        prompt_text, spec = render(
            "overflow_summarize.v1",
            max_tokens_context=str(max_tokens - 50),  # Leave room for task
            context=message,
            task="Extract and preserve ONLY critical crisis information: location, district, emergency type, number of people, urgency level, and contact info.",
            format="Concise summary in 2-3 sentences maximum"
        )
        
        # Call LLM to summarize
        client = LLMClient(provider, model)
        response = client.chat(
            messages=[{"role": "user", "content": prompt_text}],
            temperature=provider_config.temperature if provider_config else spec.temperature or 0.0,
            max_tokens=max_tokens
        )
        
        summarized_message = response["text"].strip()
        processed_token_count = count_text_tokens(summarized_message, provider, model)
        
        return SpamFilterResult(
            status="SUMMARIZED",
            original_token_count=original_token_count,
            processed_token_count=processed_token_count,
            processed_message=summarized_message,
            action="Intelligently Summarized",
            tokens_saved=original_token_count - processed_token_count
        )

