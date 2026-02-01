import React, { useState, useEffect } from 'react';
import { query } from '../api/client';

function LLMSettings({ isOpen, onClose, onSave, savedConfig }) {
    const [provider, setProvider] = useState('openai');
    const [apiKey, setApiKey] = useState('');
    const [model, setModel] = useState('');
    const [availableModels, setAvailableModels] = useState([]);
    const [loadingModels, setLoadingModels] = useState(false);
    const [error, setError] = useState('');
    const [useLocal, setUseLocal] = useState(false);

    // Load saved config when opening
    useEffect(() => {
        if (savedConfig) {
            setProvider(savedConfig.provider || 'openai');
            setApiKey(savedConfig.api_key || '');
            setModel(savedConfig.model || '');
            setUseLocal(savedConfig.use_local || false);
        }
    }, [savedConfig, isOpen]);

    // Fetch models when provider or API key changes
    useEffect(() => {
        if (apiKey && provider !== 'local' && !useLocal) {
            fetchAvailableModels();
        } else {
            setAvailableModels([]);
        }
    }, [provider, apiKey, useLocal]);

    const fetchAvailableModels = async () => {
        if (!apiKey.trim()) return;
        
        setLoadingModels(true);
        setError('');
        
        try {
            const response = await query.getModels({
                provider,
                api_key: apiKey,
                model: null
            });
            
            setAvailableModels(response.data.models);
            
            // Auto-select first model if none selected
            if (!model && response.data.models.length > 0) {
                setModel(response.data.models[0].id);
            }
        } catch (err) {
            console.error('Failed to fetch models:', err);
            setError('Failed to fetch models. Please check your API key.');
            setAvailableModels([]);
        } finally {
            setLoadingModels(false);
        }
    };

    const handleSave = () => {
        setError('');

        if (useLocal) {
            // For local models, no API key needed
            onSave({ 
                provider: 'local', 
                api_key: null, 
                model: 'llama3.2',
                use_local: true 
            });
            onClose();
            return;
        }

        if (!apiKey.trim()) {
            setError('API Key is required for cloud providers');
            return;
        }

        if (provider === 'openrouter' && !model.trim()) {
            setError('Model name is required for OpenRouter');
            return;
        }

        onSave({ 
            provider, 
            api_key: apiKey, 
            model: model || null,
            use_local: false 
        });
        onClose();
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
            <div className="glass-card w-full max-w-md rounded-2xl p-6 relative max-h-[90vh] overflow-y-auto">
                <h2 className="text-2xl font-bold text-white mb-6">LLM Settings</h2>

                {error && (
                    <div className="mb-4 p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-red-200 text-sm">
                        {error}
                    </div>
                )}

                <div className="space-y-4">
                    {/* Local vs Cloud Toggle */}
                    <div className="flex items-center gap-3 p-3 bg-white/5 rounded-lg">
                        <input
                            type="checkbox"
                            id="useLocal"
                            checked={useLocal}
                            onChange={(e) => {
                                setUseLocal(e.target.checked);
                                if (e.target.checked) {
                                    setProvider('local');
                                    setApiKey('');
                                    setModel('llama3.2');
                                    setAvailableModels([]);
                                } else {
                                    setProvider('openai');
                                    setModel('');
                                }
                                setError('');
                            }}
                            className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500"
                        />
                        <label htmlFor="useLocal" className="text-gray-300 text-sm">
                            Use Local Models (Ollama)
                        </label>
                    </div>

                    {!useLocal && (
                        <>
                            <div>
                                <label className="block text-gray-400 text-sm mb-2">Provider</label>
                                <select
                                    value={provider}
                                    onChange={(e) => {
                                        setProvider(e.target.value);
                                        setModel('');
                                        setAvailableModels([]);
                                        setError('');
                                    }}
                                    className="input-modern w-full px-4 py-3 rounded-xl text-white outline-none"
                                >
                                    <option value="openai" className="bg-gray-800">OpenAI</option>
                                    <option value="google" className="bg-gray-800">Google Gemini</option>
                                    <option value="openrouter" className="bg-gray-800">OpenRouter</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-gray-400 text-sm mb-2">API Key</label>
                                <input
                                    type="password"
                                    value={apiKey}
                                    onChange={(e) => setApiKey(e.target.value)}
                                    placeholder="Enter your API Key"
                                    className="input-modern w-full px-4 py-3 rounded-xl text-white outline-none"
                                />
                                <p className="text-xs text-gray-500 mt-1">
                                    Your key is only used for this session and is not stored permanently.
                                </p>
                            </div>

                            {/* Model Selection */}
                            <div>
                                <label className="block text-gray-400 text-sm mb-2">
                                    Model
                                    {provider === 'openrouter' && <span className="text-red-400 ml-1">*</span>}
                                </label>
                                
                                {loadingModels ? (
                                    <div className="input-modern w-full px-4 py-3 rounded-xl text-gray-400 flex items-center gap-2">
                                        <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                                        </svg>
                                        Loading models...
                                    </div>
                                ) : availableModels.length > 0 ? (
                                    <select
                                        value={model}
                                        onChange={(e) => setModel(e.target.value)}
                                        className="input-modern w-full px-4 py-3 rounded-xl text-white outline-none"
                                    >
                                        <option value="" className="bg-gray-800">Select a model...</option>
                                        {availableModels.map((modelOption) => (
                                            <option key={modelOption.id} value={modelOption.id} className="bg-gray-800">
                                                {modelOption.name}
                                                {modelOption.description && ` - ${modelOption.description}`}
                                            </option>
                                        ))}
                                    </select>
                                ) : provider === 'openrouter' ? (
                                    <input
                                        type="text"
                                        value={model}
                                        onChange={(e) => setModel(e.target.value)}
                                        placeholder="e.g., anthropic/claude-3-opus"
                                        className="input-modern w-full px-4 py-3 rounded-xl text-white outline-none"
                                    />
                                ) : (
                                    <input
                                        type="text"
                                        value={model}
                                        onChange={(e) => setModel(e.target.value)}
                                        placeholder="Enter model name (optional)"
                                        className="input-modern w-full px-4 py-3 rounded-xl text-white outline-none"
                                    />
                                )}
                                
                                {provider === 'openrouter' && (
                                    <p className="text-xs text-blue-300 mt-1">
                                        Check OpenRouter docs for model IDs (e.g., mistralai/mixtral-8x7b-instruct)
                                    </p>
                                )}
                                
                                {apiKey && availableModels.length === 0 && !loadingModels && (
                                    <button
                                        onClick={fetchAvailableModels}
                                        className="text-xs text-blue-400 hover:text-blue-300 mt-1"
                                    >
                                        Refresh models
                                    </button>
                                )}
                            </div>
                        </>
                    )}

                    {useLocal && (
                        <div className="p-4 bg-green-500/10 border border-green-500/30 rounded-lg">
                            <div className="flex items-center gap-2 text-green-400 mb-2">
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                <span className="font-medium">Local Mode Enabled</span>
                            </div>
                            <p className="text-sm text-gray-300">
                                Using Ollama with llama3.2 model. Make sure Ollama is running locally.
                            </p>
                        </div>
                    )}
                </div>

                <div className="flex gap-3 justify-end mt-8">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 rounded-lg text-gray-300 hover:text-white transition-colors"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={handleSave}
                        className="btn-primary px-6 py-2 rounded-lg text-white font-medium"
                    >
                        Save Configuration
                    </button>
                </div>
            </div>
        </div>
    );
}

export default LLMSettings;
