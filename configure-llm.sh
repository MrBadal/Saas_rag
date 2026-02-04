#!/bin/bash

# LLM Configuration Helper Script
# This script helps you configure the DataQuery AI system for optimal performance

echo "=========================================="
echo "DataQuery AI - LLM Configuration Helper"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
fi

echo "How would you like to configure your LLM?"
echo ""
echo "1) Cloud LLMs (Recommended - Fast, No memory issues)"
echo "2) Local Models (Ollama - Privacy-focused, requires RAM)"
echo "3) Show current configuration"
echo ""
read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "Configuring for Cloud LLMs..."
        echo ""
        
        # Update .env to disable local models
        if grep -q "USE_LOCAL_MODELS=" .env; then
            sed -i 's/USE_LOCAL_MODELS=.*/USE_LOCAL_MODELS=false/' .env
        else
            echo "USE_LOCAL_MODELS=false" >> .env
        fi
        
        echo "✓ Cloud LLM mode enabled"
        echo ""
        echo "Next steps:"
        echo "1. Start the application: ./start.sh"
        echo "2. Open http://localhost:3000"
        echo "3. Click 'LLM Settings' in the UI"
        echo "4. Select your provider (OpenAI/Google/OpenRouter)"
        echo "5. Enter your API key"
        echo "6. Select a model and save"
        echo ""
        echo "Get API keys from:"
        echo "- OpenAI: https://platform.openai.com/api-keys"
        echo "- Google Gemini: https://makersuite.google.com/app/apikey"
        echo "- OpenRouter: https://openrouter.ai/keys"
        ;;
        
    2)
        echo ""
        echo "Configuring for Local Models (Ollama)..."
        echo ""
        
        # Check available memory
        if command -v free &> /dev/null; then
            available_mem=$(free -g | awk '/^Mem:/{print $7}')
            echo "Available memory: ${available_mem}GB"
            echo ""
            
            if [ "$available_mem" -lt 2 ]; then
                echo "⚠️  WARNING: Low memory detected!"
                echo "Recommended: Use smallest model (llama3.2:1b)"
                model="llama3.2:1b"
            elif [ "$available_mem" -lt 4 ]; then
                echo "Memory sufficient for small-medium models"
                model="llama3.2"
            else
                echo "Memory sufficient for larger models"
                model="llama3.2:3b"
            fi
        else
            model="llama3.2:1b"
        fi
        
        echo "Recommended model: $model"
        echo ""
        read -p "Use recommended model? (y/n): " use_recommended
        
        if [ "$use_recommended" != "y" ]; then
            echo ""
            echo "Available models:"
            echo "1) llama3.2:1b (1.3GB RAM) - Fastest"
            echo "2) llama3.2 (2.0GB RAM) - Balanced"
            echo "3) llama3.2:3b (2.3GB RAM) - Better quality"
            echo "4) mistral (4.1GB RAM) - High quality"
            echo ""
            read -p "Enter choice (1-4): " model_choice
            
            case $model_choice in
                1) model="llama3.2:1b" ;;
                2) model="llama3.2" ;;
                3) model="llama3.2:3b" ;;
                4) model="mistral" ;;
                *) model="llama3.2:1b" ;;
            esac
        fi
        
        echo ""
        echo "Pulling Ollama model: $model"
        ollama pull $model
        
        if [ $? -eq 0 ]; then
            echo "✓ Model downloaded successfully"
            
            # Update .env
            if grep -q "USE_LOCAL_MODELS=" .env; then
                sed -i 's/USE_LOCAL_MODELS=.*/USE_LOCAL_MODELS=true/' .env
            else
                echo "USE_LOCAL_MODELS=true" >> .env
            fi
            
            if grep -q "OLLAMA_MODEL=" .env; then
                sed -i "s/OLLAMA_MODEL=.*/OLLAMA_MODEL=$model/" .env
            else
                echo "OLLAMA_MODEL=$model" >> .env
            fi
            
            echo "✓ Configuration updated"
            echo ""
            echo "Next steps:"
            echo "1. Start the application: ./start.sh"
            echo "2. Open http://localhost:3000"
            echo "3. Start chatting!"
        else
            echo "✗ Failed to download model"
            echo "Please ensure Ollama is installed and running"
            echo "Install: https://ollama.ai"
        fi
        ;;
        
    3)
        echo ""
        echo "Current Configuration:"
        echo "====================="
        if [ -f ".env" ]; then
            echo ""
            grep "USE_LOCAL_MODELS" .env || echo "USE_LOCAL_MODELS not set"
            grep "OLLAMA_MODEL" .env || echo "OLLAMA_MODEL not set"
            echo ""
            
            if grep -q "USE_LOCAL_MODELS=true" .env; then
                echo "Mode: Local Models (Ollama)"
                model=$(grep "OLLAMA_MODEL" .env | cut -d'=' -f2)
                echo "Model: $model"
                echo ""
                echo "Check Ollama status:"
                ollama list
            else
                echo "Mode: Cloud LLMs"
                echo "Configure API keys in the UI (LLM Settings)"
            fi
        else
            echo ".env file not found"
        fi
        ;;
        
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "Configuration complete!"
echo "=========================================="