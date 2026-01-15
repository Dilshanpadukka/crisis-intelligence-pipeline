"""
Schemas for token management API (Part 4).
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field

from .common import ProviderConfig


class SpamFilterResult(BaseModel):
    """Result of spam filtering."""
    
    status: Literal["ACCEPTED", "BLOCKED/TRUNCATED", "SUMMARIZED"] = Field(
        description="Filter decision"
    )
    original_token_count: int = Field(description="Original message token count")
    processed_token_count: int = Field(description="Processed message token count")
    processed_message: str = Field(description="Processed message text")
    action: str = Field(description="Action taken (None/Truncated/Summarized)")
    tokens_saved: int = Field(description="Number of tokens saved")


class TokenCheckRequest(BaseModel):
    """Request to check and filter message tokens."""
    
    message: str = Field(
        description="Message to check",
        min_length=1,
        max_length=100000
    )
    max_tokens: int = Field(
        default=150,
        ge=10,
        le=10000,
        description="Maximum allowed tokens"
    )
    strategy: Literal["truncate", "summarize"] = Field(
        default="truncate",
        description="Strategy for handling overflow"
    )
    provider_config: Optional[ProviderConfig] = Field(
        default=None,
        description="Optional provider configuration override"
    )


class TokenCheckResponse(BaseModel):
    """Response from token check."""
    
    result: SpamFilterResult = Field(description="Spam filter result")
    latency_ms: int = Field(description="Processing time in milliseconds")

