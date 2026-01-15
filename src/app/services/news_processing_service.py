"""
News processing service (Part 5 - Structured Extraction).

Extracts structured crisis events from news feed using JSON extraction.
"""

import json
from typing import Optional

from ..utils.prompts import render
from ..utils.llm_client import LLMClient
from ..utils.logging_utils import log_llm_call
from ..utils.router import pick_model
from ..utils.json_utils import pydantic_to_json_schema
from ..schemas.news_processing import CrisisEvent, NewsItem, ProviderConfig


class NewsProcessingService:
    """Service for processing news items into structured crisis events."""
    
    def __init__(self, provider: str = "groq"):
        """
        Initialize news processing service.
        
        Args:
            provider: Default LLM provider to use
        """
        self.provider = provider
        # Generate schema once
        self.schema_json = json.dumps(pydantic_to_json_schema(CrisisEvent), indent=2)
    
    def extract_crisis_event(
        self,
        news_item: NewsItem,
        provider_config: Optional[ProviderConfig] = None
    ) -> tuple[Optional[CrisisEvent], bool, Optional[str], int, dict]:
        """
        Extract structured crisis event from news text.
        
        Args:
            news_item: News item to process
            provider_config: Optional provider configuration override
        
        Returns:
            Tuple of (event, success, error, latency_ms, token_usage)
        """
        # Determine provider
        provider = provider_config.provider if provider_config else self.provider
        
        # Select model for JSON extraction
        model = pick_model(provider, "json_extract", tier="general")
        
        # Render json_extract prompt
        prompt_text, spec = render(
            "json_extract.v1",
            schema=self.schema_json,
            text=news_item.text
        )
        
        try:
            # Create client and call
            client = LLMClient(provider, model)
            response = client.json_chat(
                messages=[{"role": "user", "content": prompt_text}],
                temperature=spec.temperature,
                max_tokens=spec.max_tokens
            )
            
            # Log the call
            log_llm_call(
                provider=provider,
                model=model,
                technique="json_extraction",
                latency_ms=response["latency_ms"],
                usage=response["usage"],
                retry_count=response["meta"]["retry_count"],
                backoff_ms_total=response["meta"]["backoff_ms_total"],
                overflow_handled=response["meta"]["overflow_handled"]
            )
            
            # Parse and validate JSON
            json_text = response["text"].strip()
            
            # Clean up potential markdown code blocks
            if json_text.startswith("```"):
                json_text = json_text.split("```")[1]
                if json_text.startswith("json"):
                    json_text = json_text[4:]
                # Remove trailing ```
                if json_text.endswith("```"):
                    json_text = json_text[:-3]
                json_text = json_text.strip()
            
            # Validate with Pydantic
            event = CrisisEvent.model_validate_json(json_text)
            return event, True, None, response["latency_ms"], response["usage"]
        
        except Exception as e:
            error_msg = f"Failed to extract event: {str(e)}"
            # Return error but still log the attempt
            return None, False, error_msg, 0, {}
    
    def process_news_batch(
        self,
        news_items: list[NewsItem],
        provider_config: Optional[ProviderConfig] = None
    ) -> tuple[list[CrisisEvent], int, int, int, float, int, dict]:
        """
        Process multiple news items.
        
        Args:
            news_items: List of news items to process
            provider_config: Optional provider configuration override
        
        Returns:
            Tuple of (events, total_processed, successful, failed, 
                     success_rate, total_latency, total_tokens)
        """
        events = []
        successful = 0
        failed = 0
        total_latency = 0
        total_tokens = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        
        for news_item in news_items:
            event, success, error, latency, usage = self.extract_crisis_event(
                news_item, provider_config
            )
            
            if success and event:
                events.append(event)
                successful += 1
            else:
                failed += 1
            
            total_latency += latency
            
            # Aggregate tokens
            for key in total_tokens:
                if key in usage:
                    total_tokens[key] += usage.get(key, 0) or 0
        
        total_processed = len(news_items)
        success_rate = successful / total_processed if total_processed > 0 else 0.0
        
        return (
            events,
            total_processed,
            successful,
            failed,
            success_rate,
            total_latency,
            total_tokens
        )

