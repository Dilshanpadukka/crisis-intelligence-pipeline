# Quick Start Guide

## 🚀 5-Minute Setup

### Step 1: Verify Environment

```bash
# Check Python version (need 3.11+)
python --version

# Verify you're in the project directory
pwd
# Should show: .../Mini Project 0 v1
```

### Step 2: Configure API Keys

Create or edit `.env` file in project root:

```bash
# Choose ONE provider (or configure all for flexibility)

# Option 1: Groq (Recommended - Fast & Free Tier)
GROQ_API_KEY=your_groq_api_key_here

# Option 2: OpenAI (Most Capable)
OPENAI_API_KEY=your_openai_api_key_here

# Option 3: Google Gemini (Large Context Window)
GEMINI_API_KEY=your_gemini_api_key_here
```

**Getting API Keys:**
- **Groq:** https://console.groq.com/keys (Free tier available)
- **OpenAI:** https://platform.openai.com/api-keys (Paid)
- **Google:** https://aistudio.google.com/apikey (Free tier available)

### Step 3: Install Dependencies

```bash
# If using uv (recommended)
uv sync

# If using pip
pip install -r requirements.txt

# If requirements.txt doesn't exist, install manually:
pip install openai google-genai groq python-dotenv tiktoken pydantic pandas openpyxl jupyter ipython pyyaml
```

### Step 4: Launch Jupyter

```bash
# Start Jupyter
jupyter notebook

# Or if using VS Code, just open the .ipynb file
```

### Step 5: Run the Pipeline

1. Open `notebooks/operation_ditwah_crisis_pipeline.ipynb`
2. In the configuration cell, set your provider:
   ```python
   PROVIDER = "groq"  # or "openai" or "google"
   ```
3. Run all cells (Cell → Run All)
4. Wait for processing to complete (~5-10 minutes depending on provider)

## 📊 Expected Outputs

After running the notebook, you should see:

### Files Created:
- `output/classified_messages.xlsx` - Part 1 results
- `output/flood_report.xlsx` - Part 5 results
- `logs/runs.csv` - API usage logs

### Console Output:
- Classification results for sample messages
- Temperature stability comparison
- Priority scores for incidents
- Route optimization analysis
- Token economics statistics
- News feed processing summary

## 🔧 Troubleshooting

### Issue: "API Key not found"
**Solution:** 
- Verify `.env` file exists in project root
- Check API key is correctly formatted (no quotes, no spaces)
- Restart Jupyter kernel after adding `.env`

### Issue: "Module not found"
**Solution:**
```bash
# Reinstall dependencies
pip install --upgrade openai google-genai groq python-dotenv tiktoken pydantic pandas openpyxl
```

### Issue: "Rate limit exceeded"
**Solution:**
- Switch to Groq (higher free tier limits)
- Reduce number of messages processed (edit notebook cells)
- Wait a few minutes and retry

### Issue: "Context window exceeded"
**Solution:**
- The code handles this automatically with truncation
- If issues persist, reduce message lengths in data files

### Issue: "JSON validation failed"
**Solution:**
- This is expected for some news items (logged as warnings)
- Success rate should be >95%
- Check logs for specific failures

## 📈 Cost Estimates

**Groq (Recommended for Demo):**
- Free tier: 30 requests/minute
- Cost: $0 for this project
- Speed: Very fast

**OpenAI:**
- Using gpt-4o-mini: ~$0.10-0.20 for full pipeline
- Using o3-mini for reasoning: ~$0.50-1.00 for full pipeline
- Speed: Moderate

**Google Gemini:**
- Free tier: 15 requests/minute
- Cost: $0 for this project (within free tier)
- Speed: Fast

## 🎯 Quick Validation

After running, verify success:

```python
# In a new notebook cell or Python console
import pandas as pd

# Check Part 1 output
df1 = pd.read_excel("output/classified_messages.xlsx")
print(f"Classified messages: {len(df1)}")
print(df1.head())

# Check Part 5 output
df5 = pd.read_excel("output/flood_report.xlsx")
print(f"Crisis events: {len(df5)}")
print(df5.head())

# Check logs
logs = pd.read_csv("logs/runs.csv")
print(f"Total API calls: {len(logs)}")
print(f"Total cost: {logs['cost_estimate_usd'].sum()}")
```

## 📚 Next Steps

1. **Review Results:** Open Excel files to see structured outputs
2. **Analyze Logs:** Check `logs/runs.csv` for performance metrics
3. **Experiment:** Try different providers and compare results
4. **Customize:** Modify few-shot examples for better accuracy
5. **Scale:** Process full datasets (remove limits in notebook)

## 💡 Tips for Best Results

1. **Use Groq for Development:** Fast and free, great for testing
2. **Use OpenAI o3-mini for Production:** Best reasoning quality
3. **Start Small:** Process 10-20 items first, then scale up
4. **Monitor Costs:** Check logs regularly if using paid APIs
5. **Temperature=0.0:** Always use for crisis systems (deterministic)

## 🆘 Getting Help

1. **Check Logs:** `logs/runs.csv` shows all API calls and errors
2. **Read Error Messages:** Most errors are self-explanatory
3. **Review Documentation:** See `OPERATION_DITWAH_README.md`
4. **Test Components:** Run individual cells to isolate issues

## ✅ Success Checklist

- [ ] API keys configured in `.env`
- [ ] Dependencies installed
- [ ] Jupyter notebook opens successfully
- [ ] Configuration cell runs without errors
- [ ] Part 1 completes and creates Excel file
- [ ] Part 2 shows temperature comparison
- [ ] Part 3 shows priority scores and route optimization
- [ ] Part 4 demonstrates token savings
- [ ] Part 5 creates flood report Excel file
- [ ] All outputs in `output/` directory
- [ ] Logs in `logs/runs.csv`

---

**Ready to save lives with AI! 🚁**

