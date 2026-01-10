# Operation Ditwah - Crisis Intelligence Pipeline

**Scenario:** Post-Cyclone Ditwah Relief (Sri Lanka)  

## 🎯 Mission Overview

Crisis Intelligence Pipeline that demonstrates production-ready prompt engineering techniques for disaster response.

## 📋 Project Structure

```
crisis_intelligence_pipeline/
├── data/
│   ├── Sample Messages.txt    # 99 crisis messages for classification
│   ├── Scenarios.txt          # Complex crisis scenarios for CoT analysis
│   ├── Incidents.txt          # Resource allocation incidents
│   └── News Feed.txt          # 30 news items for structured extraction
├── notebooks/
│   └── operation_ditwah_crisis_pipeline.ipynb  # Main implementation
├── output/
│   ├── classified_messages.xlsx  # Part 1 output
│   └── flood_report.xlsx         # Part 5 output
├── utils/
│   ├── prompts.py            # Centralized prompt templates
│   ├── llm_client.py         # Multi-provider LLM client
│   ├── router.py             # Automatic model routing
│   ├── token_utils.py        # Token counting and management
│   └── logging_utils.py      # CSV logging with metrics
└── logs/
    └── runs.csv              # Comprehensive API call logs
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.11+** with dependencies installed
2. **API Keys** configured in `.env`:
   ```
   OPENAI_API_KEY=your_key_here
   GEMINI_API_KEY=your_key_here
   GROQ_API_KEY=your_key_here
   ```

### Installation

```bash
# Install dependencies (using uv or pip)
uv sync
# or
pip install -r requirements.txt
```

### Running the Pipeline

1. Open `notebooks/operation_ditwah_crisis_pipeline.ipynb`
2. Select your provider (OpenAI, Google, or Groq) in the configuration cell
3. Run all cells sequentially
4. Review outputs in `output/` directory

## 📊 Implementation Details

### Part 1: Message Classification

**Objective:** Distinguish real SOS calls from news noise using few-shot learning.

**Implementation:**
- Uses `few_shot.v1` prompt template from `utils/prompts.py`
- Provides exactly 4 labeled examples covering:
  - **Rescue:** Life-threatening emergencies
  - **Supply:** Resource requests
  - **Info:** News reports and updates
  - **Other:** Spam and irrelevant content

**Output Format:**
```
District: [Colombo/Gampaha/Kandy/etc.] | Intent: [Rescue/Supply/Info/Other] | Priority: [High/Low]
```

**Success Criteria:**
- Input: "Breaking News: Kelani River level at 9m." → `District: Colombo | Intent: Info | Priority: Low`
- Input: "We are trapped on the roof with 3 kids!" → `District: None | Intent: Rescue | Priority: High`

### Part 2: Temperature Stability Experiment

**Objective:** Prove deterministic behavior is critical for crisis systems.

**Implementation:**
- Uses `cot_reasoning.v1` prompt template
- Runs same scenario at:
  - `temperature=1.0` (3 iterations) - demonstrates variability
  - `temperature=0.0` (1 iteration) - demonstrates determinism

**Key Findings:**
- High temperature produces inconsistent recommendations (dangerous in crisis)
- Low temperature ensures repeatable, auditable decisions
- Crisis systems MUST use temperature=0.0 for reliability

### Part 3: Resource Allocation with CoT & ToT

**Objective:** Optimize limited rescue resources using advanced reasoning.

**Setup:**
- ONE rescue boat at Ragama
- Travel times: Ragama → Ja-Ela (10 min), Ja-Ela → Gampaha (40 min)

**Step A - Priority Scoring (CoT):**
```
Base Score: 5
+2 if Age > 60 or < 5 (vulnerable populations)
+3 if Need == "Rescue" (life-threatening)
+1 if Need == "Medicine/Insulin" (medical emergency)
Result: Score X/10
```

**Step B - Route Optimization (ToT):**
Explores 3 strategies:
1. Highest priority first (greedy)
2. Closest location first (minimize travel)
3. Furthest location first (logistics efficiency)

**Goal:** Maximize total priority score within shortest time frame.

### Part 4: Token Economics & Spam Prevention

**Objective:** Control API costs through intelligent token management.

**Implementation:**
- Uses `count_messages_tokens()` from `utils/token_utils.py`
- Logic: If message > 150 tokens → BLOCK/TRUNCATE
- Alternative: Apply `overflow_summarize.v1` for long valid messages

**Metrics:**
- Demonstrates >30% token reduction through spam filtering
- Logs all BLOCKED/TRUNCATED messages
- Tracks cost savings in `logs/runs.csv`

### Part 5: News Feed Processing Pipeline

**Objective:** Transform raw text into structured Excel database.

**Pydantic Schema:**
```python
class CrisisEvent(BaseModel):
    district: Literal["Colombo", "Gampaha", "Kandy", "Kalutara", "Galle", "Matara", "Other"]
    flood_level_meters: Optional[float] = None
    victim_count: int = 0
    main_need: str
    status: Literal["Critical", "Warning", "Stable"]
```

**Pipeline Steps:**
1. Load `data/News Feed.txt` (30 items)
2. Use `json_extract.v1` prompt for structured extraction
3. Validate with `CrisisEvent.model_validate_json()`
4. Skip invalid entries with warning logs
5. Convert to pandas DataFrame
6. Export as `output/flood_report.xlsx`

**Success Metrics:**
- <5% invalid entries
- Complete structured data for valid entries
- Summary statistics (by district, status, needs)

## 🛠️ Technical Excellence

### Leveraging Existing Codebase

- **Prompt Templates:** All prompts use `utils/prompts.py` catalog
- **LLM Client:** Unified `LLMClient` with retry logic and token guards
- **Model Routing:** Automatic selection via `pick_model()` based on technique
- **Token Management:** Pre-call estimation and overflow handling
- **Logging:** Comprehensive CSV logging with cost estimates

### Error Handling

- Robust validation with Pydantic schemas
- Graceful degradation for failed extractions
- Retry logic with exponential backoff
- Context overflow detection and handling

### Documentation

- Clear comments explaining crisis-specific adaptations
- Inline documentation for all functions
- Comprehensive README (this file)
- Jupyter notebook with markdown explanations

## 📈 Success Metrics

- ✅ Classification accuracy > 90% on test messages
- ✅ Consistent outputs at temperature=0.0
- ✅ Optimal resource allocation strategy identified
- ✅ Token usage reduced by >30% through spam filtering
- ✅ Complete news feed processing with <5% invalid entries

## 📁 Deliverables

1. ✅ Modified codebase with crisis intelligence functionality
2. ✅ All required data files (provided in `data/`)
3. ✅ Output files (`classified_messages.xlsx`, `flood_report.xlsx`)
4. ✅ Jupyter notebook demonstrating complete pipeline
5. ✅ Analysis report (embedded in notebook)

## 🔍 Next Steps

1. **Review Logs:** Check `logs/runs.csv` for detailed API usage metrics
2. **Analyze Outputs:** Review Excel files for classification patterns and insights
3. **Optimize Costs:** Experiment with different providers and models
4. **Scale Up:** Process full datasets (currently limited for demo)
5. **Real-time Integration:** Consider streaming data processing
6. **Dashboard:** Build visualization layer for DMC operators

## 📚 References

- **OpenAI API:** https://platform.openai.com/docs
- **Google Gemini:** https://ai.google.dev/docs
- **Groq:** https://console.groq.com/docs
- **Pydantic:** https://docs.pydantic.dev/

## 🎓 Learning Outcomes

By completing this project, you have demonstrated:

1. **Few-Shot Learning:** Effective use of examples to guide model behavior
2. **Temperature Control:** Understanding of determinism in production systems
3. **Advanced Reasoning:** Application of CoT and ToT for complex decisions
4. **Token Economics:** Cost-aware prompt engineering
5. **Structured Outputs:** Schema-driven extraction with validation
6. **Production Practices:** Logging, error handling, and code organization

---

**Operation Ditwah - Mission Accomplished** 🎯

