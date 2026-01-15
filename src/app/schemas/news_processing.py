"""
Schemas for news processing API (Part 5).
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field

from .common import ProviderConfig


class CrisisEvent(BaseModel):
    """Structured crisis event data model."""

    district: Literal["Colombo", "Gampaha", "Kandy", "Kalutara", "Galle", "Matara", "Ratnapura", "Other"] = Field(
        description="District where event occurred"
    )
    flood_level_meters: Optional[float] = Field(
        default=None,
        description="Flood level in meters"
    )
    victim_count: int = Field(
        default=0,
        ge=0,
        description="Number of victims/people affected"
    )
    main_need: str = Field(description="Primary need or emergency type")
    status: Literal["Critical", "Warning", "Stable"] = Field(
        description="Event status/severity"
    )


class NewsItem(BaseModel):
    """Single news item to process."""
    
    text: str = Field(
        description="News item text",
        min_length=1,
        max_length=10000
    )
    source: Optional[str] = Field(default=None, description="News source")
    timestamp: Optional[str] = Field(default=None, description="News timestamp")


class NewsProcessingRequest(BaseModel):
    """Request to process a single news item."""
    
    news_item: NewsItem = Field(description="News item to process")
    provider_config: Optional[ProviderConfig] = Field(
        default=None,
        description="Optional provider configuration override"
    )


class NewsProcessingResponse(BaseModel):
    """Response from processing a single news item."""
    
    event: Optional[CrisisEvent] = Field(
        default=None,
        description="Extracted crisis event (None if extraction failed)"
    )
    success: bool = Field(description="Whether extraction was successful")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    latency_ms: int = Field(description="Processing time")
    tokens_used: dict = Field(description="Token usage")


class BatchNewsProcessingRequest(BaseModel):
    """
    Request to process multiple news items in batch.

    News items are automatically read from data/News Feed.txt file by default.
    You can optionally specify a custom file path.
    """

    file_path: Optional[str] = Field(
        default=None,
        description="Optional custom file path (absolute or relative to project root). "
                    "If not provided, defaults to 'data/News Feed.txt'"
    )
    provider_config: Optional[ProviderConfig] = Field(
        default=None,
        description="Optional provider configuration override"
    )


class BatchNewsProcessingResponse(BaseModel):
    """Response from batch news processing with file output."""

    excel_file_path: str = Field(description="Path to generated Excel file")
    preview_events: list[CrisisEvent] = Field(
        description="First 5 successfully extracted events for preview"
    )
    total_processed: int = Field(description="Total news items processed")
    successful_extractions: int = Field(description="Number of successful extractions")
    failed_extractions: int = Field(description="Number of failed extractions")
    success_rate: float = Field(
        ge=0.0,
        le=1.0,
        description="Success rate (0.0-1.0)"
    )
    total_latency_ms: int = Field(description="Total processing time")
    total_tokens_used: dict = Field(description="Aggregate token usage")

