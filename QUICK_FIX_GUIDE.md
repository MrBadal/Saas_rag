# Quick Fix Guide - Memory Error

## 🔴 Error You're Seeing
```
Ollama call failed with status code 500
model requires more system memory (2.3 GiB) than is available (1.4 GiB)
```

## ✅ 2-Minute Fix

### Step 1: Edit `.env` file
Open `.env` and change this line:
```env
USE_LOCAL_MODELS=false
```

### Step 2: Restart Backend
```bash
cd backend
# Press Ctrl+C to stop current process
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Configure Cloud LLM in UI
1. Open http://localhost:3000
2. Click **"LLM Settings"** button (top right)
3. **Uncheck** "Use Local Models (Ollama)"
4. Select a provider:
   - **OpenAI** (recommended)
   - **Google Gemini** (cheapest)
   - **OpenRouter** (most options)
5. Enter your API key
6. Select a model from dropdown
7. Click **"Save Configuration"**

### Step 4: Test
Ask a question like "Show me all users" - should work in 3-5 seconds!

## 🔑 Get API Keys (Free Tier Available)

### OpenAI (Recommended)
- Go to: https://platform.openai.com/api-keys
- Sign up (free $5 credit)
- Create API key
- Use model: `gpt-3.5-turbo`

### Google Gemini (Cheapest)
- Go to: https://makersuite.google.com/app/apikey
- Sign up (free tier: 60 req/min)
- Create API key
- Use model: `gemini-1.5-flash`

### OpenRouter (Most Options)
- Go to: https://openrouter.ai/keys
- Sign up
- Add credits ($5 minimum)
- Create API key
- Use model: `anthropic/claude-3-sonnet`

## 🎯 Why This Works

- **Before**: Trying to run large AI model locally → Not enough RAM
- **After**: Using cloud AI service → No local memory needed
- **Bonus**: Faster responses (3-5s vs 15-30s)

## 🔄 Alternative: Use Smaller Local Model

If you prefer local models:

```bash
# Pull smallest model (1.3GB)
ollama pull llama3.2:1b

# Edit .env
USE_LOCAL_MODELS=true
OLLAMA_MODEL=llama3.2:1b

# Restart backend
```

## 📊 Quick Comparison

| Option | Speed | Cost | Memory | Setup |
|--------|-------|------|--------|-------|
| **Cloud (OpenAI)** | ⚡ 3-5s | 💰 ~$0.002/query | ✅ None | ⭐ Easy |
| **Cloud (Gemini)** | ⚡ 2-4s | 💰 ~$0.0001/query | ✅ None | ⭐ Easy |
| **Local (small)** | 🐌 10-20s | 💰 Free | ⚠️ 1.3GB | 🔧 Medium |

## ✨ That's It!

Your system will now use cloud LLMs and work perfectly without memory issues.

**Need help?** Check `TROUBLESHOOTING_MEMORY_ISSUE.md` for detailed guide.