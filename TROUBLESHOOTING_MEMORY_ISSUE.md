# Troubleshooting: Ollama Memory Issues

## Problem
You're seeing this error:
```
{"detail": "Ollama call failed with status code 500. Details: {\"error\":\"model requires more system memory (2.3 GiB) than is available (1.4 GiB)\"}"}
```

## Root Cause
The Ollama model you're trying to use requires more RAM than your system has available.

## Solutions (Choose One)

### ✅ Solution 1: Use Cloud LLMs (RECOMMENDED)
This is the easiest and fastest solution. Configure cloud LLMs instead of local models.

#### Steps:
1. **Update your `.env` file:**
   ```env
   USE_LOCAL_MODELS=false
   ```

2. **Restart the backend:**
   ```bash
   cd backend
   # Stop the current process (Ctrl+C)
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Configure LLM in the UI:**
   - Open the application in your browser
   - Click "LLM Settings" button
   - Uncheck "Use Local Models (Ollama)"
   - Select a provider (OpenAI, Google Gemini, or OpenRouter)
   - Enter your API key
   - Select a model from the dropdown
   - Click "Save Configuration"

4. **Get API Keys:**
   - **OpenAI**: https://platform.openai.com/api-keys
   - **Google Gemini**: https://makersuite.google.com/app/apikey
   - **OpenRouter**: https://openrouter.ai/keys

### ✅ Solution 2: Use Smaller Ollama Model
If you want to keep using local models, switch to a smaller model.

#### Steps:
1. **Pull a smaller model:**
   ```bash
   # Smallest model (1.3GB RAM required)
   ollama pull llama3.2:1b
   
   # Or use the default 2GB model
   ollama pull llama3.2
   ```

2. **Update your `.env` file:**
   ```env
   USE_LOCAL_MODELS=true
   OLLAMA_MODEL=llama3.2:1b
   ```

3. **Restart the backend:**
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

#### Available Ollama Models by Memory:
| Model | RAM Required | Quality | Speed |
|-------|-------------|---------|-------|
| `llama3.2:1b` | 1.3 GB | Good | Very Fast |
| `llama3.2` | 2.0 GB | Better | Fast |
| `llama3.2:3b` | 2.3 GB | Great | Medium |
| `phi3:mini` | 2.3 GB | Great | Fast |
| `mistral` | 4.1 GB | Excellent | Medium |
| `llama3.1:8b` | 4.7 GB | Excellent | Slower |

### ✅ Solution 3: Increase System Memory
If you're running in Docker or a VM, allocate more memory.

#### For Docker:
```bash
# Edit docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 4G  # Increase this
```

#### For WSL2 (Windows):
Create/edit `%USERPROFILE%\.wslconfig`:
```ini
[wsl2]
memory=4GB
```

Then restart WSL:
```powershell
wsl --shutdown
```

## Verification

### Test Cloud LLM Configuration:
1. Open the application
2. Go to chat interface
3. Ask a simple question: "What tables are in my database?"
4. You should see a response within 5-15 seconds
5. Check for the indicator showing which provider is being used

### Test Local Model:
```bash
# Test Ollama directly
ollama run llama3.2:1b "Hello, how are you?"

# If this works, your model is properly configured
```

## Quick Configuration Reference

### For Low Memory Systems (< 2GB available):
```env
USE_LOCAL_MODELS=false
# Configure cloud LLM via UI
```

### For Medium Memory Systems (2-4GB available):
```env
USE_LOCAL_MODELS=true
OLLAMA_MODEL=llama3.2:1b
```

### For High Memory Systems (4GB+ available):
```env
USE_LOCAL_MODELS=true
OLLAMA_MODEL=llama3.2:3b
# or
OLLAMA_MODEL=mistral
```

## Hybrid Approach (Best of Both Worlds)

You can use cloud LLMs for most queries and keep local models as backup:

1. Set `USE_LOCAL_MODELS=false` in `.env`
2. Configure cloud LLM in UI for daily use
3. Keep Ollama running with a small model for offline scenarios
4. Toggle between them in the UI as needed

## Performance Comparison

| Configuration | Response Time | Cost | Privacy | Memory |
|--------------|---------------|------|---------|--------|
| Cloud (OpenAI GPT-3.5) | 3-5s | ~$0.002/query | Low | Minimal |
| Cloud (Gemini Flash) | 2-4s | ~$0.0001/query | Low | Minimal |
| Local (llama3.2:1b) | 10-20s | Free | High | 1.3GB |
| Local (llama3.2:3b) | 15-30s | Free | High | 2.3GB |

## Still Having Issues?

### Check Ollama Status:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Check available models
ollama list

# Check system resources
ollama ps
```

### Check Backend Logs:
Look for detailed error messages in the backend console output.

### Common Error Messages:

1. **"Local model service unavailable"**
   - Ollama is not running
   - Solution: Start Ollama or switch to cloud LLMs

2. **"Cloud LLM requires API key"**
   - No API key configured
   - Solution: Configure API key in LLM Settings

3. **"Failed to initialize cloud RAG service"**
   - Invalid API key or network issue
   - Solution: Verify API key and internet connection

## Recommended Setup for Production

For production deployments, we recommend:

1. **Primary**: Cloud LLMs (OpenAI or Google Gemini)
   - Faster responses
   - Better quality
   - No memory constraints
   - Scalable

2. **Backup**: Local models (optional)
   - For offline scenarios
   - For sensitive data
   - Use smallest model that meets needs

## Need Help?

If you're still experiencing issues:
1. Check the backend logs for detailed error messages
2. Verify your system has sufficient available memory
3. Try the cloud LLM option first (easiest solution)
4. Ensure all dependencies are installed correctly