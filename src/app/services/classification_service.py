"""
Message classification service (Part 1 - Few-Shot Learning).

Converts the notebook's classify_message() function into a service class.
"""

import time
from typing import Optional

from ..utils.prompts import render
from ..utils.llm_client import LLMClient
from ..utils.logging_utils import log_llm_call
from ..utils.router import pick_model
from ..schemas.classification import ClassificationResult, ProviderConfig


# Few-shot examples (exactly 4 examples covering all categories)
FEW_SHOT_EXAMPLES = """Input: "SOS: 5 people trapped on a roof in Ja-Ela. Water rising fast. Need boat immediately."
Output: District: Gampaha | Intent: Rescue | Priority: High

Input: "Gampaha hospital is requesting drinking water for patients."
Output: District: Gampaha | Intent: Supply | Priority: High

Input: "BREAKING: Water levels in Kelani River have reached 9.5 meters. Critical flood warning issued."
Output: District: Colombo | Intent: Info | Priority: Low

Input: "Please share this post to help the victims."
Output: District: None | Intent: Other | Priority: Low"""


class ClassificationService:
    """Service for classifying crisis messages using few-shot learning."""
    
    def __init__(self, provider: str = "groq"):
        """
        Initialize classification service.
        
        Args:
            provider: Default LLM provider to use
        """
        self.provider = provider
    
    def classify_message(
        self,
        message: str,
        provider_config: Optional[ProviderConfig] = None
    ) -> tuple[ClassificationResult, int, dict]:
        """
        Classify a crisis message using few-shot learning.
        
        Args:
            message: Crisis message to classify
            provider_config: Optional provider configuration override
        
        Returns:
            Tuple of (ClassificationResult, latency_ms, token_usage)
        """
        # Determine provider and settings
        provider = provider_config.provider if provider_config else self.provider
        temperature = provider_config.temperature if provider_config else None
        max_tokens = provider_config.max_tokens if provider_config else None
        
        # Select model for general task
        model = pick_model(provider, "few_shot", tier="general")
        
        # Render few-shot prompt
        prompt_text, spec = render(
            "few_shot.v1",
            role="Crisis Message Classifier for Sri Lanka Disaster Management Center",
            examples=FEW_SHOT_EXAMPLES,
            query=message,
            constraints="Classify based on location (district), intent (Rescue/Supply/Info/Other), and priority (High/Low)",
            format="District: [Name or None] | Intent: [Category] | Priority: [High/Low]"
        )
        
        # Create client and call
        start_time = time.time()
        client = LLMClient(provider, model)
        response = client.chat(
            messages=[{"role": "user", "content": prompt_text}],
            temperature=temperature if temperature is not None else spec.temperature,
            max_tokens=max_tokens if max_tokens is not None else spec.max_tokens
        )
        
        # Log the call
        log_llm_call(
            provider=provider,
            model=model,
            technique="few_shot_classification",
            latency_ms=response["latency_ms"],
            usage=response["usage"],
            retry_count=response["meta"]["retry_count"],
            backoff_ms_total=response["meta"]["backoff_ms_total"],
            overflow_handled=response["meta"]["overflow_handled"]
        )
        
        # Parse output
        output = response["text"].strip()

        # Extract fields using simple parsing
        district = "None"
        intent = "Other"
        priority = "Low"

        if "District:" in output:
            district_raw = output.split("District:")[1].split("|")[0].strip()
            # Clean district (take first word/line)
            district = district_raw.split("\n")[0].strip()

        if "Intent:" in output:
            intent_raw = output.split("Intent:")[1].split("|")[0].strip()
            # Clean intent (take first word/line and normalize)
            intent_clean = intent_raw.split()[0].split("\n")[0].strip()
            # Map to valid intent values
            intent_lower = intent_clean.lower()
            if intent_lower in ["rescue", "救援"]:
                intent = "Rescue"
            elif intent_lower in ["supply", "supplies", "物资"]:
                intent = "Supply"
            elif intent_lower in ["info", "information", "信息"]:
                intent = "Info"
            else:
                intent = "Other"

        if "Priority:" in output:
            # Extract priority and clean it (remove any text after the value)
            priority_raw = output.split("Priority:")[1].strip()
            # Take only the first word/line and normalize
            priority_clean = priority_raw.split()[0].split("\n")[0].strip()
            # Ensure it's exactly "High" or "Low"
            if priority_clean.lower() == "high":
                priority = "High"
            elif priority_clean.lower() == "low":
                priority = "Low"
            else:
                priority = "Low"  # Default to Low if unclear

        # Create result
        result = ClassificationResult(
            message=message,
            district=district,
            intent=intent,  # type: ignore
            priority=priority,  # type: ignore
            raw_output=output
        )
        
        return result, response["latency_ms"], response["usage"]
    
    def classify_batch(
        self,
        messages: list[str],
        provider_config: Optional[ProviderConfig] = None
    ) -> tuple[list[ClassificationResult], int, dict]:
        """
        Classify multiple messages.
        
        Args:
            messages: List of crisis messages to classify
            provider_config: Optional provider configuration override
        
        Returns:
            Tuple of (results, total_latency_ms, total_token_usage)
        """
        results = []
        total_latency = 0
        total_tokens = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        
        for message in messages:
            result, latency, usage = self.classify_message(message, provider_config)
            results.append(result)
            total_latency += latency
            
            # Aggregate token usage
            for key in total_tokens:
                if key in usage:
                    total_tokens[key] += usage.get(key, 0) or 0
        
        return results, total_latency, total_tokens

