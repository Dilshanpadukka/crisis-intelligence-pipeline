"""
Pydantic schemas for Operation Ditwah Crisis Intelligence API.

This module exports all request/response models for the FastAPI application.
"""

from .classification import (
    MessageClassificationRequest,
    MessageClassificationResponse,
    BatchClassificationRequest,
    BatchClassificationResponse,
    ClassificationResult,
)

from .temperature import (
    TemperatureAnalysisRequest,
    TemperatureAnalysisResponse,
    TemperatureTestResult,
)

from .resource_allocation import (
    IncidentData,
    PriorityScoreRequest,
    PriorityScoreResponse,
    RouteOptimizationRequest,
    RouteOptimizationResponse,
    ScoredIncident,
)

from .token_management import (
    TokenCheckRequest,
    TokenCheckResponse,
    SpamFilterResult,
)

from .news_processing import (
    CrisisEvent,
    NewsItem,
    NewsProcessingRequest,
    NewsProcessingResponse,
    BatchNewsProcessingRequest,
    BatchNewsProcessingResponse,
)

from .common import (
    HealthResponse,
    ErrorResponse,
    ProviderConfig,
)

__all__ = [
    # Classification
    "MessageClassificationRequest",
    "MessageClassificationResponse",
    "BatchClassificationRequest",
    "BatchClassificationResponse",
    "ClassificationResult",
    # Temperature
    "TemperatureAnalysisRequest",
    "TemperatureAnalysisResponse",
    "TemperatureTestResult",
    # Resource Allocation
    "IncidentData",
    "PriorityScoreRequest",
    "PriorityScoreResponse",
    "RouteOptimizationRequest",
    "RouteOptimizationResponse",
    "ScoredIncident",
    # Token Management
    "TokenCheckRequest",
    "TokenCheckResponse",
    "SpamFilterResult",
    # News Processing
    "CrisisEvent",
    "NewsItem",
    "NewsProcessingRequest",
    "NewsProcessingResponse",
    "BatchNewsProcessingRequest",
    "BatchNewsProcessingResponse",
    # Common
    "HealthResponse",
    "ErrorResponse",
    "ProviderConfig",
]

