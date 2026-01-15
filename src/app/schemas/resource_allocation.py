"""
Schemas for resource allocation API (Part 3).
"""

from typing import Optional
from pydantic import BaseModel, Field

from .common import ProviderConfig


class IncidentData(BaseModel):
    """Crisis incident data."""
    
    location: str = Field(description="Incident location")
    description: str = Field(description="Incident description")
    people_affected: Optional[int] = Field(default=None, description="Number of people affected")
    need_type: Optional[str] = Field(default=None, description="Type of need (Rescue/Medicine/Supply)")
    age_info: Optional[str] = Field(default=None, description="Age information of victims")


class ScoredIncident(BaseModel):
    """Incident with priority score."""
    
    incident: IncidentData = Field(description="Original incident data")
    score: int = Field(ge=0, le=10, description="Priority score (0-10)")
    reasoning: str = Field(description="CoT reasoning for the score")


class PriorityScoreRequest(BaseModel):
    """Request to score incident priority using CoT."""
    
    incidents: list[IncidentData] = Field(
        description="List of incidents to score",
        min_length=1,
        max_length=20
    )
    provider_config: Optional[ProviderConfig] = Field(
        default=None,
        description="Optional provider configuration override"
    )


class PriorityScoreResponse(BaseModel):
    """Response from priority scoring."""
    
    scored_incidents: list[ScoredIncident] = Field(description="Incidents with priority scores")
    total_latency_ms: int = Field(description="Total processing time")
    total_tokens_used: dict = Field(description="Aggregate token usage")


class RouteOptimizationRequest(BaseModel):
    """Request to optimize rescue route using ToT."""
    
    scored_incidents: list[ScoredIncident] = Field(
        description="Pre-scored incidents to optimize route for",
        min_length=2,
        max_length=10
    )
    starting_location: str = Field(
        default="Ragama",
        description="Starting location for rescue team"
    )
    travel_times: Optional[dict[str, dict[str, int]]] = Field(
        default=None,
        description="Travel time matrix (location -> location -> minutes)"
    )
    provider_config: Optional[ProviderConfig] = Field(
        default=None,
        description="Optional provider configuration override"
    )


class RouteOptimizationResponse(BaseModel):
    """Response from route optimization."""

    optimal_route: list[str] = Field(description="Optimized sequence of locations")
    strategy_used: str = Field(description="Strategy selected (e.g., 'Highest priority first')")
    reasoning: str = Field(description="ToT reasoning for route selection")
    estimated_total_time: Optional[int] = Field(
        default=None,
        description="Estimated total time in minutes"
    )
    total_priority_score: int = Field(description="Sum of priority scores addressed")
    latency_ms: int = Field(description="Processing time")
    tokens_used: dict = Field(description="Token usage")


class BatchResourceAllocationRequest(BaseModel):
    """
    Request to process incidents from file.

    Automatically reads incidents from data/Incidents.txt and:
    - Scores each incident using CoT reasoning
    - Optimizes rescue route using ToT reasoning
    """

    starting_location: str = Field(
        default="Ragama",
        description="Starting location for rescue team"
    )
    provider_config: Optional[ProviderConfig] = Field(
        default=None,
        description="Optional provider configuration override"
    )


class BatchResourceAllocationResponse(BaseModel):
    """Response from batch resource allocation."""

    scored_incidents: list[ScoredIncident] = Field(
        description="All incidents with priority scores"
    )
    optimal_route: list[str] = Field(description="Optimized rescue route")
    strategy_used: str = Field(description="ToT strategy selected")
    reasoning: str = Field(description="ToT reasoning for route")
    total_priority_score: int = Field(description="Sum of all priority scores")
    total_latency_ms: int = Field(description="Total processing time")
    total_tokens_used: dict = Field(description="Aggregate token usage")

