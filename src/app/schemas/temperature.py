"""
Schemas for temperature analysis API (Part 2).
"""

from typing import Optional
from pydantic import BaseModel, Field

from .common import ProviderConfig


class TemperatureTestResult(BaseModel):
    """Result from a single temperature test iteration."""
    
    temperature: float = Field(description="Temperature value used")
    iteration: int = Field(description="Iteration number")
    response: str = Field(description="LLM response text")
    latency_ms: int = Field(description="Response latency in milliseconds")
    tokens_used: dict = Field(description="Token usage for this iteration")


class TemperatureAnalysisRequest(BaseModel):
    """Request to analyze temperature stability."""
    
    scenario: str = Field(
        description="Crisis scenario to analyze",
        min_length=10,
        max_length=10000
    )
    temperatures: list[float] = Field(
        default=[0.0, 1.0],
        description="List of temperature values to test",
        min_length=1,
        max_length=10
    )
    iterations_per_temperature: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of iterations per temperature value"
    )
    provider_config: Optional[ProviderConfig] = Field(
        default=None,
        description="Optional provider configuration override"
    )


class TemperatureAnalysisResponse(BaseModel):
    """Response from temperature analysis."""

    results: list[TemperatureTestResult] = Field(
        description="Test results for all temperature/iteration combinations"
    )
    analysis: dict = Field(
        description="Statistical analysis of consistency across temperatures"
    )
    recommendation: str = Field(
        description="Recommended temperature setting for crisis systems"
    )
    total_latency_ms: int = Field(description="Total analysis time")
    total_tokens_used: dict = Field(description="Aggregate token usage")


class BatchTemperatureAnalysisRequest(BaseModel):
    """
    Request to analyze temperature stability for scenarios from file.

    Automatically reads scenarios from data/Scenarios.txt and tests:
    - 3 runs at temperature=1.0 (high variability)
    - 1 run at temperature=0.0 (deterministic)
    """

    provider_config: Optional[ProviderConfig] = Field(
        default=None,
        description="Optional provider configuration override"
    )


class BatchTemperatureAnalysisResponse(BaseModel):
    """Response from batch temperature analysis."""

    scenarios_analyzed: int = Field(description="Number of scenarios analyzed")
    results_per_scenario: list[TemperatureAnalysisResponse] = Field(
        description="Analysis results for each scenario"
    )
    overall_recommendation: str = Field(
        description="Overall recommendation based on all scenarios"
    )
    total_latency_ms: int = Field(description="Total processing time")
    total_tokens_used: dict = Field(description="Aggregate token usage")

