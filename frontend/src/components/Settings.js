import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { settings } from '../api/client';

function Settings() {
    const [providers, setProviders] = useState([]);
    const [userSettings, setUserSettings] = useState({
        llm_provider: 'openai',
        llm_model: 'gpt-3.5-turbo',
        llm_api_key: ''
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [showApiKey, setShowApiKey] = useState(false);

    useEffect(() => {
        loadProviders();
        loadSettings();
    }, []);

    const loadProviders = async () => {
        try {
            const response = await settings.getProviders();
            setProviders(response.data.providers);
        } catch (err) {
            console.error('Failed to load providers:', err);
        }
    };

    const loadSettings = async () => {
        try {
            const response = await settings.get();
            setUserSettings(prev => ({
                ...prev,
                llm_provider: response.data.llm_provider,
                llm_model: response.data.llm_model
            }));
        } catch (err) {
            console.error('Failed to load settings:', err);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setSuccess('');

        try {
            await settings.update(userSettings);
            setSuccess('Settings saved successfully!');
            setUserSettings(prev => ({ ...prev, llm_api_key: '' }));
            setTimeout(() => setSuccess(''), 3000);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to save settings');
        } finally {
            setLoading(false);
        }
    };

    const currentProvider = providers.find(p => p.id === userSettings.llm_provider);
    const currentModels = currentProvider?.models || [];

    return (
        <div className="min-h-screen animated-bg">
            {/* Navigation */}
            <nav className="nav-blur fixed w-full z-50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between h-16 items-center">
                        <div className="flex items-center gap-3">
                            <Link to="/dashboard" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
                                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                                    </svg>
                                </div>
                                <span className="text-xl font-bold gradient-text">DataQuery AI</span>
                            </Link>
                        </div>
                        <div className="flex items-center gap-4">
                            <Link to="/dashboard" className="text-gray-300 hover:text-white transition-colors flex items-center gap-2 px-4 py-2 rounded-lg hover:bg-white/5">
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                                </svg>
                                Dashboard
                            </Link>
                            <Link to="/connections" className="text-gray-300 hover:text-white transition-colors flex items-center gap-2 px-4 py-2 rounded-lg hover:bg-white/5">
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                                </svg>
                                Connections
                            </Link>
                            <Link to="/chat" className="text-gray-300 hover:text-white transition-colors flex items-center gap-2 px-4 py-2 rounded-lg hover:bg-white/5">
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                                </svg>
                                Chat
                            </Link>
                        </div>
                    </div>
                </div>
            </nav>

            {/* Main Content */}
            <div className="pt-24 pb-12 px-4 sm:px-6 lg:px-8">
                <div className="max-w-3xl mx-auto">
                    {/* Header */}
                    <div className="mb-8">
                        <h1 className="text-4xl font-bold gradient-text mb-2">Settings</h1>
                        <p className="text-gray-400">Configure your AI model preferences and API keys</p>
                    </div>

                    {/* Alerts */}
                    {error && (
                        <div className="bg-red-500/20 border border-red-500/50 text-red-300 px-6 py-4 rounded-xl mb-6 flex items-center gap-3">
                            <svg className="w-6 h-6 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            {error}
                        </div>
                    )}

                    {success && (
                        <div className="bg-green-500/20 border border-green-500/50 text-green-300 px-6 py-4 rounded-xl mb-6 flex items-center gap-3">
                            <svg className="w-6 h-6 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            {success}
                        </div>
                    )}

                    {/* Settings Form */}
                    <div className="glass-card p-8 rounded-2xl">
                        <form onSubmit={handleSubmit} className="space-y-8">
                            {/* LLM Provider Selection */}
                            <div>
                                <label className="block text-gray-300 text-sm font-medium mb-4">
                                    AI Provider
                                </label>
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    {providers.map((provider) => (
                                        <button
                                            key={provider.id}
                                            type="button"
                                            onClick={() => setUserSettings({
                                                ...userSettings,
                                                llm_provider: provider.id,
                                                llm_model: provider.models[0]?.id || ''
                                            })}
                                            className={`p-4 rounded-xl border transition-all text-left ${userSettings.llm_provider === provider.id
                                                    ? 'bg-blue-500/20 border-blue-500/50'
                                                    : 'bg-white/5 border-white/10 hover:bg-white/10'
                                                }`}
                                        >
                                            <div className="font-semibold text-white mb-1">{provider.name}</div>
                                            <div className="text-sm text-gray-400">{provider.models.length} models</div>
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Model Selection */}
                            {currentModels.length > 0 && (
                                <div>
                                    <label className="block text-gray-300 text-sm font-medium mb-4">
                                        Model
                                    </label>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                                        {currentModels.map((model) => (
                                            <button
                                                key={model.id}
                                                type="button"
                                                onClick={() => setUserSettings({ ...userSettings, llm_model: model.id })}
                                                className={`p-4 rounded-xl border transition-all text-left ${userSettings.llm_model === model.id
                                                        ? 'bg-purple-500/20 border-purple-500/50'
                                                        : 'bg-white/5 border-white/10 hover:bg-white/10'
                                                    }`}
                                            >
                                                <div className="font-medium text-white">{model.name}</div>
                                                <div className="text-sm text-gray-400 font-mono mt-1">{model.id}</div>
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* API Key Input */}
                            <div>
                                <div className="flex items-center justify-between mb-2">
                                    <label className="block text-gray-300 text-sm font-medium">
                                        API Key
                                    </label>
                                    {currentProvider && (
                                        <a
                                            href={currentProvider.key_url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="text-sm text-blue-400 hover:text-blue-300 flex items-center gap-1"
                                        >
                                            Get API Key
                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                            </svg>
                                        </a>
                                    )}
                                </div>
                                <div className="relative">
                                    <input
                                        type={showApiKey ? 'text' : 'password'}
                                        value={userSettings.llm_api_key}
                                        onChange={(e) => setUserSettings({ ...userSettings, llm_api_key: e.target.value })}
                                        className="input-modern w-full px-4 py-3 rounded-xl text-white placeholder-gray-500 pr-12"
                                        placeholder={`Enter your ${currentProvider?.name || 'API'} key`}
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowApiKey(!showApiKey)}
                                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white"
                                    >
                                        {showApiKey ? (
                                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                                            </svg>
                                        ) : (
                                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                            </svg>
                                        )}
                                    </button>
                                </div>
                                <p className="text-gray-500 text-sm mt-2">
                                    Your API key is securely stored and used only for generating AI responses.
                                </p>
                            </div>

                            {/* Submit Button */}
                            <div className="pt-4">
                                <button
                                    type="submit"
                                    disabled={loading || !userSettings.llm_api_key}
                                    className="btn-primary w-full text-white font-semibold py-3 px-8 rounded-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                                >
                                    {loading ? (
                                        <>
                                            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                                            </svg>
                                            Saving...
                                        </>
                                    ) : (
                                        <>
                                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                            </svg>
                                            Save Settings
                                        </>
                                    )}
                                </button>
                            </div>
                        </form>
                    </div>

                    {/* Info Card */}
                    <div className="glass-card p-6 rounded-2xl mt-6">
                        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                            <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            About AI Providers
                        </h3>
                        <div className="space-y-3 text-gray-400 text-sm">
                            <p>
                                <strong className="text-white">OpenAI:</strong> GPT models known for strong reasoning and code generation capabilities.
                            </p>
                            <p>
                                <strong className="text-white">Google Gemini:</strong> Multimodal models with large context windows and competitive pricing.
                            </p>
                            <p>
                                <strong className="text-white">Anthropic Claude:</strong> Models focused on safety and helpfulness with excellent reasoning.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Settings;
