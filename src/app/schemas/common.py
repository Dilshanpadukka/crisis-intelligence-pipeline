"""
Common schemas used across the API.
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field


class ProviderConfig(BaseModel):
    """LLM provider configuration."""
    
    provider: Literal["openai", "google", "groq"] = Field(
        default="groq",
        description="LLM provider to use"
    )
    temperature: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=2.0,
        description="Sampling temperature (0.0-2.0). None uses prompt default."
    )
    max_tokens: Optional[int] = Field(
        default=None,
        gt=0,
        description="Maximum tokens to generate. None uses prompt default."
    )


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str = Field(default="healthy", description="Service status")
    version: str = Field(description="API version")
    providers_available: list[str] = Field(description="Available LLM providers")


class ErrorResponse(BaseModel):
    """Standard error response."""
    
    error: str = Field(description="Error type")
    message: str = Field(description="Human-readable error message")
    detail: Optional[dict] = Field(default=None, description="Additional error details")

