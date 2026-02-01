# Enhanced Features Setup Guide

## 🚀 New Features Overview

Your DataQuery AI system now includes several powerful enhancements:

1. **Automatic Query Execution** - Queries are automatically executed when you ask for data
2. **Enhanced LLM Support** - Switch between local and cloud LLM providers
3. **Performance Optimizations** - Faster response times (5-15s vs 60-120s)
4. **Model Auto-Discovery** - Automatically fetch available models from your API keys

## 🔧 Setup Instructions

### 1. Backend Dependencies
Install the new required packages:

```bash
cd backend
pip install -r requirements.txt
```

New dependencies added:
- `httpx==0.27.0` - For async HTTP requests
- `openai==1.51.0` - Updated OpenAI client
- `google-generativeai==0.8.3` - Google Gemini support

### 2. Environment Configuration
Update your `.env` file with optional cloud provider settings:

```env
# Existing settings
USE_LOCAL_MODELS=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Optional: Default API keys (users can override in UI)
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_google_key_here
```

### 3. Start the Enhanced System
```bash
# Start backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend (in another terminal)
cd frontend
npm start
```

## 🎯 Using the New Features

### Automatic Query Execution
Simply ask natural questions that indicate you want to see data:

**✅ These will auto-execute:**
- "Show me all users"
- "Get the latest 10 orders"
- "How many customers do we have?"
- "Find all active products"
- "List recent transactions"

**ℹ️ These will provide guidance only:**
- "How do I query users?"
- "What's the database structure?"
- "Explain the schema"

### LLM Provider Configuration

#### Option 1: Use Local Models (Default)
1. Make sure Ollama is running: `ollama serve`
2. Pull a model: `ollama pull llama3.2`
3. In the UI, click "LLM Settings"
4. Check "Use Local Models (Ollama)"
5. Click "Save Configuration"

#### Option 2: Use Cloud Providers
1. Click "LLM Settings" in the chat interface
2. Uncheck "Use Local Models"
3. Select your provider (OpenAI, Google Gemini, or OpenRouter)
4. Enter your API key
5. Wait for models to load automatically
6. Select your preferred model
7. Click "Save Configuration"

### Model Auto-Discovery
When you enter an API key for cloud providers:
- **OpenAI**: Automatically fetches GPT models (3.5-turbo, GPT-4, etc.)
- **Google Gemini**: Fetches available Gemini models (1.5-flash, 1.5-pro, etc.)
- **OpenRouter**: Fetches the full catalog of available models

## 📊 Performance Monitoring

### Response Time Indicators
- All responses now show execution time
- Auto-executed queries are marked with ✅
- Failed operations show ❌ with timing

### Example Response:
```
Here are your users:
1. John Doe (john@example.com)
2. Jane Smith (jane@example.com)
...

✅ Auto-executed query (3.2s)

Generated Query:
SELECT * FROM users LIMIT 100;
```

## 🔒 Security Features

### Read-Only Safety
- Only SELECT, SHOW, DESCRIBE queries are auto-executed
- INSERT, UPDATE, DELETE operations are blocked
- Automatic LIMIT 100 added to prevent large result sets

### API Key Security
- Keys are stored only in browser session
- Not persisted to backend database
- Can be cleared by refreshing the page

## 🛠️ Troubleshooting

### Common Issues

#### 1. "Failed to fetch models"
- **Cause**: Invalid API key or network issue
- **Solution**: Verify API key, check internet connection

#### 2. Slow responses with local models
- **Cause**: Ollama not optimized or insufficient resources
- **Solution**: 
  - Ensure Ollama has adequate RAM (8GB+ recommended)
  - Try smaller models like `llama3.2:1b`
  - Check Ollama logs: `ollama logs`

#### 3. Auto-execution not working
- **Cause**: Query doesn't contain trigger keywords
- **Solution**: Use phrases like "show me", "get", "find", "list"

#### 4. Model list empty
- **Cause**: API key validation failed
- **Solution**: 
  - Verify API key is correct
  - Check provider-specific requirements
  - Try clicking "Refresh models"

### Performance Tips

1. **For Speed**: Use local models with sufficient hardware
2. **For Accuracy**: Use cloud models like GPT-4 or Claude
3. **For Cost**: Use smaller models or local alternatives
4. **For Privacy**: Always use local models

## 🔮 Advanced Usage

### Custom Model Selection
For OpenRouter, you can use any available model:
- `anthropic/claude-3-opus` - Most capable
- `mistralai/mixtral-8x7b-instruct` - Good balance
- `meta-llama/llama-3.1-8b-instruct` - Fast and efficient

### Query Optimization
The system automatically:
- Adds LIMIT clauses to prevent large results
- Validates query safety before execution
- Formats results for better readability
- Provides execution timing for performance monitoring

## 📞 Support

If you encounter issues:
1. Check the browser console for error details
2. Review backend logs for performance issues
3. Verify all dependencies are installed correctly
4. Ensure API keys have proper permissions

The enhanced system provides significant performance improvements and new capabilities while maintaining the same easy-to-use interface!