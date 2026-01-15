"""
Schemas for message classification API (Part 1).
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field

from .common import ProviderConfig


class ClassificationResult(BaseModel):
    """Result of classifying a single message."""
    
    message: str = Field(description="Original message text")
    district: str = Field(description="Identified district or 'None'")
    intent: Literal["Rescue", "Supply", "Info", "Other"] = Field(
        description="Message intent category"
    )
    priority: Literal["High", "Low"] = Field(description="Priority level")
    raw_output: str = Field(description="Raw LLM classification output")
    confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Classification confidence (if available)"
    )


class MessageClassificationRequest(BaseModel):
    """Request to classify a single crisis message."""
    
    message: str = Field(
        description="Crisis message to classify",
        min_length=1,
        max_length=5000
    )
    provider_config: Optional[ProviderConfig] = Field(
        default=None,
        description="Optional provider configuration override"
    )


class MessageClassificationResponse(BaseModel):
    """Response from message classification."""
    
    result: ClassificationResult = Field(description="Classification result")
    latency_ms: int = Field(description="Processing latency in milliseconds")
    tokens_used: dict = Field(description="Token usage statistics")


class BatchClassificationRequest(BaseModel):
    """
    Request to classify multiple messages in batch.

    Messages are automatically read from data/Sample Messages.txt file by default.
    You can optionally specify a custom file path.
    """

    file_path: Optional[str] = Field(
        default=None,
        description="Optional custom file path (absolute or relative to project root). "
                    "If not provided, defaults to 'data/Sample Messages.txt'"
    )
    provider_config: Optional[ProviderConfig] = Field(
        default=None,
        description="Optional provider configuration override"
    )


class BatchClassificationResponse(BaseModel):
    """Response from batch classification with file outputs."""

    excel_file_path: str = Field(description="Path to generated Excel file")
    preview_results: list[ClassificationResult] = Field(
        description="First 5 classification results for preview"
    )
    total_processed: int = Field(description="Total messages processed")
    total_latency_ms: int = Field(description="Total processing time in milliseconds")
    total_tokens_used: dict = Field(description="Aggregate token usage")

