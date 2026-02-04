# Step-by-Step Fix Guide

## 🎯 Goal
Fix the memory error and get your system working with cloud LLMs in under 5 minutes.

---

## 📋 Step 1: Update Configuration File

### Open `.env` file in your project root

**Find this line:**
```env
USE_LOCAL_MODELS=true
```

**Change it to:**
```env
USE_LOCAL_MODELS=false
```

**Save the file.**

---

## 🔄 Step 2: Restart Backend

### Stop the current backend process:
- Press `Ctrl+C` in the terminal running the backend

### Start it again:
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Wait for:** `Application startup complete`

---

## 🌐 Step 3: Open the Application

### In your browser, go to:
```
http://localhost:3000
```

---

## ⚙️ Step 4: Configure Cloud LLM

### Click the "LLM Settings" button
- Located in the top-right corner of the navigation bar
- Has a gear/settings icon

### In the settings dialog:

1. **Uncheck** the box that says:
   ```
   ☐ Use Local Models (Ollama)
   ```

2. **Select a provider** from the dropdown:
   - Choose `OpenAI` (recommended for beginners)
   - Or `Google Gemini` (cheapest option)
   - Or `OpenRouter` (most model options)

3. **Get an API key:**

   **For OpenAI:**
   - Go to: https://platform.openai.com/api-keys
   - Sign up (you get $5 free credit)
   - Click "Create new secret key"
   - Copy the key

   **For Google Gemini:**
   - Go to: https://makersuite.google.com/app/apikey
   - Sign in with Google
   - Click "Create API key"
   - Copy the key

   **For OpenRouter:**
   - Go to: https://openrouter.ai/keys
   - Sign up
   - Add credits ($5 minimum)
   - Create API key
   - Copy the key

4. **Paste your API key** in the "API Key" field

5. **Wait a moment** - The system will automatically fetch available models

6. **Select a model** from the dropdown:
   - For OpenAI: Choose `gpt-3.5-turbo` (fast and cheap)
   - For Google: Choose `gemini-1.5-flash` (fastest)
   - For OpenRouter: Choose `anthropic/claude-3-sonnet` (best quality)

7. **Click "Save Configuration"**

---

## ✅ Step 5: Test It

### In the chat interface:

1. **Select a database connection** from the dropdown

2. **Type a test question:**
   ```
   Show me all users
   ```

3. **Click "Send"**

### Expected Result:
- Response in 3-5 seconds
- You'll see a green indicator showing which provider is being used
- Query results will be displayed
- Execution time will be shown

---

## 🎉 Success!

You should now see:
- ✅ Fast responses (3-5 seconds)
- ✅ No memory errors
- ✅ Automatic query execution
- ✅ Results displayed inline

---

## 🔍 Troubleshooting

### If you see "Failed to fetch models":
- Check your API key is correct
- Make sure you have internet connection
- Try clicking "Refresh models"

### If you see "API key required":
- Make sure you entered the API key
- Click "Save Configuration" after entering it

### If queries are still slow:
- Check you're using cloud LLMs (indicator should show)
- Verify `USE_LOCAL_MODELS=false` in `.env`
- Restart the backend

### If you see "Connection refused":
- Make sure backend is running
- Check it's on port 8000
- Verify no firewall blocking

---

## 💡 Tips

### Save Money:
- Use Google Gemini (cheapest)
- Use `gpt-3.5-turbo` instead of GPT-4
- Monitor your usage in provider dashboard

### Best Performance:
- Use `gemini-1.5-flash` (fastest)
- Or `gpt-3.5-turbo` (very fast)
- Keep queries specific

### For Privacy:
- Use local models with sufficient RAM
- Or use OpenRouter with privacy-focused models
- Check provider's data retention policies

---

## 📊 What You Get

### With Cloud LLMs:
- ⚡ **Speed**: 3-5 second responses
- 🎯 **Accuracy**: Better query generation
- 💪 **Reliability**: No memory issues
- 📈 **Scalability**: Works under load

### Cost Estimate:
- **OpenAI GPT-3.5**: ~$0.002 per query
- **Google Gemini**: ~$0.0001 per query
- **100 queries/day**: ~$0.20-$6/month

---

## 🔄 Switching Back to Local

If you want to try local models later:

1. Install Ollama: https://ollama.ai
2. Pull a small model: `ollama pull llama3.2:1b`
3. Edit `.env`: `USE_LOCAL_MODELS=true`
4. Set model: `OLLAMA_MODEL=llama3.2:1b`
5. Restart backend
6. In UI, check "Use Local Models"

---

## 📚 More Help

- **Quick reference**: `QUICK_FIX_GUIDE.md`
- **Detailed troubleshooting**: `TROUBLESHOOTING_MEMORY_ISSUE.md`
- **All features**: `ENHANCED_FEATURES_GUIDE.md`

---

## ✨ That's It!

Your system is now configured to use cloud LLMs and should work perfectly without any memory issues. Enjoy fast, reliable database querying!