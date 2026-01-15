"""
Resource allocation service (Part 3 - CoT & ToT Reasoning).

Implements priority scoring with CoT and route optimization with ToT.
"""

from typing import Optional

from ..utils.prompts import render
from ..utils.llm_client import LLMClient
from ..utils.logging_utils import log_llm_call
from ..utils.router import pick_model
from ..schemas.resource_allocation import (
    IncidentData,
    ScoredIncident,
    ProviderConfig,
)


class ResourceAllocationService:
    """Service for resource allocation using CoT and ToT reasoning."""
    
    def __init__(self, provider: str = "groq"):
        """
        Initialize resource allocation service.
        
        Args:
            provider: Default LLM provider to use
        """
        self.provider = provider
    
    def score_incident_with_cot(
        self,
        incident: IncidentData,
        provider_config: Optional[ProviderConfig] = None
    ) -> tuple[ScoredIncident, int, dict]:
        """
        Score an incident using CoT reasoning.
        
        Scoring logic:
        - Base Score: 5
        - +2 if Age > 60 or < 5 (vulnerable populations)
        - +3 if Need == "Rescue" (life-threatening)
        - +1 if Need == "Medicine" or "Insulin" (medical emergency)
        - Result: Score X/10
        
        Args:
            incident: Incident data to score
            provider_config: Optional provider configuration override
        
        Returns:
            Tuple of (ScoredIncident, latency_ms, token_usage)
        """
        # Determine provider
        provider = provider_config.provider if provider_config else self.provider
        
        # Select model for CoT reasoning
        model = pick_model(provider, "cot_reasoning", tier="reason")
        
        # Format incident data
        incident_text = f"""Location: {incident.location}
Description: {incident.description}"""
        
        if incident.people_affected:
            incident_text += f"\nPeople Affected: {incident.people_affected}"
        if incident.need_type:
            incident_text += f"\nNeed Type: {incident.need_type}"
        if incident.age_info:
            incident_text += f"\nAge Information: {incident.age_info}"
        
        # Render CoT prompt
        prompt_text, spec = render(
            "cot_reasoning.v1",
            role="Crisis Priority Analyst",
            problem=f"""Score this incident using the following logic:

Base Score: 5
+2 if Age > 60 or < 5 (vulnerable populations)
+3 if Need == "Rescue" (life-threatening)
+1 if Need == "Medicine" or "Insulin" (medical emergency)
Result: Score X/10

Incident:
{incident_text}

Show your reasoning step-by-step, then provide the final score.
Answer format: Score: X/10"""
        )
        
        # Create client and call
        client = LLMClient(provider, model)
        response = client.chat(
            messages=[{"role": "user", "content": prompt_text}],
            temperature=0.0,  # Deterministic for crisis
            max_tokens=spec.max_tokens
        )
        
        # Log the call
        log_llm_call(
            provider=provider,
            model=model,
            technique="cot_priority_scoring",
            latency_ms=response["latency_ms"],
            usage=response["usage"],
            retry_count=response["meta"]["retry_count"],
            backoff_ms_total=response["meta"]["backoff_ms_total"],
            overflow_handled=response["meta"]["overflow_handled"]
        )
        
        # Extract score from response
        text = response["text"]
        score = 5  # default
        
        # Try to extract score
        if "Score:" in text:
            try:
                score_str = text.split("Score:")[1].split("/")[0].strip()
                score = int(score_str)
                # Clamp to valid range
                score = max(0, min(10, score))
            except:
                pass
        
        scored_incident = ScoredIncident(
            incident=incident,
            score=score,
            reasoning=text
        )
        
        return scored_incident, response["latency_ms"], response["usage"]
    
    def score_incidents_batch(
        self,
        incidents: list[IncidentData],
        provider_config: Optional[ProviderConfig] = None
    ) -> tuple[list[ScoredIncident], int, dict]:
        """
        Score multiple incidents.
        
        Args:
            incidents: List of incidents to score
            provider_config: Optional provider configuration override
        
        Returns:
            Tuple of (scored_incidents, total_latency, total_tokens)
        """
        scored_incidents = []
        total_latency = 0
        total_tokens = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        
        for incident in incidents:
            scored, latency, usage = self.score_incident_with_cot(incident, provider_config)
            scored_incidents.append(scored)
            total_latency += latency
            
            # Aggregate tokens
            for key in total_tokens:
                if key in usage:
                    total_tokens[key] += usage.get(key, 0) or 0
        
        return scored_incidents, total_latency, total_tokens

    def optimize_route_with_tot(
        self,
        scored_incidents: list[ScoredIncident],
        starting_location: str,
        travel_times: Optional[dict[str, dict[str, int]]],
        provider_config: Optional[ProviderConfig] = None
    ) -> tuple[list[str], str, str, Optional[int], int, int, dict]:
        """
        Optimize rescue route using Tree-of-Thought reasoning.

        Explores 3 distinct strategies:
        1. Highest priority first (greedy approach)
        2. Closest location first (minimize travel time)
        3. Furthest location first (logistics efficiency)

        Args:
            scored_incidents: Pre-scored incidents
            starting_location: Starting location for rescue team
            travel_times: Optional travel time matrix
            provider_config: Optional provider configuration override

        Returns:
            Tuple of (optimal_route, strategy_used, reasoning, estimated_time,
                     total_priority_score, latency_ms, token_usage)
        """
        # Determine provider
        provider = provider_config.provider if provider_config else self.provider

        # Select model for ToT reasoning
        model = pick_model(provider, "tot_reasoning", tier="reason")

        # Create incidents summary
        incidents_summary = "\n".join([
            f"Incident {i+1}: {inc.incident.location} - {inc.incident.description[:80]}... | Score: {inc.score}/10"
            for i, inc in enumerate(scored_incidents)
        ])

        # Format travel times if provided
        travel_info = ""
        if travel_times:
            travel_info = "\nTravel times:\n"
            for from_loc, to_locs in travel_times.items():
                for to_loc, time in to_locs.items():
                    travel_info += f"  {from_loc} → {to_loc}: {time} min\n"
        else:
            travel_info = "\nTravel times: Ragama → Ja-Ela (10 min), Ja-Ela → Gampaha (40 min), Ragama → Gampaha (30 min)"

        # Render ToT prompt
        prompt_text, spec = render(
            "tot_reasoning.v1",
            role="Crisis Logistics Optimizer",
            branches="3",
            problem=f"""Optimize the rescue boat route to maximize total priority score within shortest time.

Setup:
- ONE rescue boat stationed at {starting_location}
{travel_info}

Incidents with scores:
{incidents_summary}

Explore these 3 strategies:
Branch 1: Highest priority first (greedy approach)
Branch 2: Closest location first (minimize travel time)
Branch 3: Furthest location first (logistics efficiency)

For each branch:
- Calculate total priority score achieved
- Calculate total time taken
- Evaluate trade-offs

Then select the best strategy and explain why."""
        )

        # Create client and call
        client = LLMClient(provider, model)
        response = client.chat(
            messages=[{"role": "user", "content": prompt_text}],
            temperature=0.0,
            max_tokens=spec.max_tokens
        )

        # Log the call
        log_llm_call(
            provider=provider,
            model=model,
            technique="tot_route_optimization",
            latency_ms=response["latency_ms"],
            usage=response["usage"],
            retry_count=response["meta"]["retry_count"],
            backoff_ms_total=response["meta"]["backoff_ms_total"],
            overflow_handled=response["meta"]["overflow_handled"]
        )

        # Parse response to extract route
        reasoning = response["text"]

        # Extract optimal route (simple heuristic - look for location names)
        locations = [inc.incident.location for inc in scored_incidents]
        optimal_route = [starting_location]

        # Try to extract strategy
        strategy_used = "Highest priority first"  # default
        if "Branch 2" in reasoning or "closest" in reasoning.lower():
            strategy_used = "Closest location first"
        elif "Branch 3" in reasoning or "furthest" in reasoning.lower():
            strategy_used = "Furthest location first"

        # Sort by priority for default strategy
        sorted_incidents = sorted(scored_incidents, key=lambda x: x.score, reverse=True)
        optimal_route.extend([inc.incident.location for inc in sorted_incidents])

        # Calculate total priority score
        total_priority_score = sum(inc.score for inc in scored_incidents)

        return (
            optimal_route,
            strategy_used,
            reasoning,
            None,  # estimated_time (would need actual calculation)
            total_priority_score,
            response["latency_ms"],
            response["usage"]
        )

