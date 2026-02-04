# Memory Issue Fix - Complete Guide

## 🔴 Problem
You encountered this error:
```
{"detail": "Ollama call failed with status code 500. Details: {\"error\":\"model requires more system memory (2.3 GiB) than is available (1.4 GiB)\"}"}
```

## ✅ Solution Implemented

I've implemented a comprehensive fix that:

1. **Prioritizes Cloud LLMs** - System now properly detects and uses cloud LLMs when configured
2. **Better Error Handling** - Clear error messages guide users to fix configuration
3. **Flexible Configuration** - Easy switching between local and cloud providers
4. **Memory-Aware Defaults** - Recommends appropriate models based on available memory

## 🚀 Quick Fix (Recommended)

### Option A: Use Cloud LLMs (Fastest & Easiest)

**Windows:**
```cmd
configure-llm.bat
# Select option 1 (Cloud LLMs)
```

**Linux/Mac:**
```bash
chmod +x configure-llm.sh
./configure-llm.sh
# Select option 1 (Cloud LLMs)
```

**Or manually:**
1. Edit `.env` file:
   ```env
   USE_LOCAL_MODELS=false
   ```

2. Restart backend:
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. Configure in UI:
   - Open http://localhost:3000
   - Click "LLM Settings"
   - Uncheck "Use Local Models"
   - Select provider (OpenAI/Google/OpenRouter)
   - Enter API key
   - Select model
   - Save

### Option B: Use Smaller Local Model

**Windows:**
```cmd
ollama pull llama3.2:1b
configure-llm.bat
# Select option 2 (Local Models)
```

**Linux/Mac:**
```bash
ollama pull llama3.2:1b
./configure-llm.sh
# Select option 2 (Local Models)
```

## 📋 What Changed

### Backend Changes

1. **Enhanced Query API** (`backend/app/api/query.py`)
   - Now prioritizes user-provided LLM config over environment settings
   - Better error handling with specific messages for memory issues
   - Graceful fallback when local models fail

2. **Updated Configuration** (`.env.example`)
   - Changed default to `USE_LOCAL_MODELS=false`
   - Added memory-appropriate model recommendations
   - Better documentation of options

3. **Improved Error Messages**
   - Specific guidance for memory issues
   - Clear instructions for switching to cloud LLMs
   - Links to get API keys

### Frontend Changes

1. **Enhanced Error Handling** (`frontend/src/components/ChatInterface.js`)
   - Detects memory-related errors
   - Provides step-by-step fix instructions
   - Guides users to LLM Settings

2. **Better User Guidance**
   - Clear indicators of which LLM is being used
   - Helpful error messages with solutions
   - Quick access to configuration

### New Tools

1. **Configuration Scripts**
   - `configure-llm.sh` (Linux/Mac)
   - `configure-llm.bat` (Windows)
   - Interactive setup with memory detection

2. **Documentation**
   - `TROUBLESHOOTING_MEMORY_ISSUE.md` - Detailed troubleshooting
   - `MEMORY_ISSUE_FIX.md` - This file
   - Updated guides with cloud LLM instructions

## 🎯 How It Works Now

### Priority System
```
1. User provides API key in UI → Use Cloud LLM
2. USE_LOCAL_MODELS=false in .env → Require Cloud LLM
3. USE_LOCAL_MODELS=true in .env → Try Local, fail gracefully
```

### Error Flow
```
Local Model Fails (Memory)
    ↓
Clear Error Message
    ↓
Guide to LLM Settings
    ↓
Configure Cloud LLM
    ↓
Success!
```

## 📊 Configuration Matrix

| Scenario | .env Setting | UI Config | Result |
|----------|-------------|-----------|--------|
| Cloud Only | `USE_LOCAL_MODELS=false` | API key provided | ✅ Uses cloud |
| Cloud Override | `USE_LOCAL_MODELS=true` | API key provided | ✅ Uses cloud |
| Local Only | `USE_LOCAL_MODELS=true` | No API key | ✅ Uses local |
| Not Configured | `USE_LOCAL_MODELS=false` | No API key | ❌ Clear error |

## 🔧 Testing the Fix

### Test Cloud LLM:
```bash
# 1. Configure for cloud
echo "USE_LOCAL_MODELS=false" > .env

# 2. Start backend
cd backend
uvicorn app.main:app --reload

# 3. Open UI and configure API key

# 4. Test query
# Should work without memory issues
```

### Test Local Model:
```bash
# 1. Pull small model
ollama pull llama3.2:1b

# 2. Configure
echo "USE_LOCAL_MODELS=true" > .env
echo "OLLAMA_MODEL=llama3.2:1b" >> .env

# 3. Start backend
cd backend
uvicorn app.main:app --reload

# 4. Test query
# Should work with low memory
```

## 🎓 Best Practices

### For Development:
- Use cloud LLMs for faster iteration
- Keep local models as backup
- Test with both configurations

### For Production:
- **Recommended**: Cloud LLMs (OpenAI/Google)
  - Faster responses (3-5s vs 15-30s)
  - No memory management
  - Better quality
  - Scalable

- **Alternative**: Local models
  - For sensitive data
  - For offline scenarios
  - Requires proper resource allocation

### For Low-Resource Systems:
- Always use cloud LLMs
- Or use `llama3.2:1b` if local required
- Monitor memory usage
- Consider upgrading RAM

## 📈 Performance Comparison

| Configuration | Response Time | Memory | Cost | Quality |
|--------------|---------------|--------|------|---------|
| OpenAI GPT-3.5 | 3-5s | Minimal | $0.002 | Excellent |
| Google Gemini Flash | 2-4s | Minimal | $0.0001 | Excellent |
| OpenRouter Claude | 4-6s | Minimal | $0.015 | Excellent |
| Local llama3.2:1b | 10-20s | 1.3GB | Free | Good |
| Local llama3.2:3b | 15-30s | 2.3GB | Free | Great |

## 🆘 Still Having Issues?

### Check System Status:
```bash
# Check Ollama
ollama list
curl http://localhost:11434/api/tags

# Check memory
free -h  # Linux
wmic OS get FreePhysicalMemory  # Windows

# Check backend logs
# Look for detailed error messages
```

### Common Issues:

1. **"Local model service unavailable"**
   - Solution: Switch to cloud LLMs or start Ollama

2. **"Cloud LLM requires API key"**
   - Solution: Configure API key in UI

3. **"Failed to fetch models"**
   - Solution: Verify API key is valid

4. **Still getting memory errors**
   - Solution: Use cloud LLMs or smaller model

## 📞 Get API Keys

- **OpenAI**: https://platform.openai.com/api-keys
  - Free tier: $5 credit
  - Pay-as-you-go after

- **Google Gemini**: https://makersuite.google.com/app/apikey
  - Free tier: 60 requests/minute
  - Very affordable

- **OpenRouter**: https://openrouter.ai/keys
  - Access to multiple models
  - Pay only for what you use

## ✨ Summary

The system now:
- ✅ Properly uses cloud LLMs when configured
- ✅ Provides clear error messages for memory issues
- ✅ Guides users to fix configuration
- ✅ Supports easy switching between local and cloud
- ✅ Includes helper scripts for setup
- ✅ Works on low-memory systems with cloud LLMs

**Recommended Action**: Use cloud LLMs for the best experience. They're faster, more reliable, and don't have memory constraints.