import { useState, useEffect, useRef } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { query, connections } from '../api/client';
import LLMSettings from './LLMSettings';

function ChatInterface() {
  const [searchParams] = useSearchParams();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [connectionList, setConnectionList] = useState([]);
  const [selectedConnection, setSelectedConnection] = useState(null);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [llmConfig, setLlmConfig] = useState(null);
  const messagesEndRef = useRef(null);

  const loadingSteps = [
    { message: '🤔 Understanding your question...', duration: 5000 },
    { message: '🔍 Analyzing database schema...', duration: 5000 },
    { message: '⚡ Generating optimized query...', duration: 8000 },
    { message: '🚀 Executing query on database...', duration: 10000 },
    { message: '📊 Processing results...', duration: 5000 },
    { message: '✨ Finalizing response...', duration: 3000 }
  ];

  useEffect(() => {
    loadConnections();
    loadHistory();
    const storedConfig = localStorage.getItem('llm_config');
    if (storedConfig) {
      setLlmConfig(JSON.parse(storedConfig));
    }
  }, []);

  useEffect(() => {
    const connId = searchParams.get('connection');
    if (connId && connectionList.length > 0) {
      setSelectedConnection(parseInt(connId));
    }
  }, [searchParams, connectionList]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadConnections = async () => {
    try {
      const response = await connections.list();
      setConnectionList(response.data);
      if (response.data.length > 0 && !selectedConnection) {
        setSelectedConnection(response.data[0].id);
      }
    } catch (err) {
      console.error('Failed to load connections:', err);
    }
  };

  const loadHistory = async () => {
    try {
      const response = await query.getHistory();
      const historyMessages = response.data.flatMap(item => [
        { role: 'user', content: item.query },
        { role: 'assistant', content: item.response }
      ]);
      setMessages(historyMessages.slice(-10));
    } catch (err) {
      console.error('Failed to load history:', err);
    }
  };

  // Progress animation effect
  useEffect(() => {
    let interval;
    if (loading) {
      let currentStep = 0;
      setLoadingStep(0);
      setLoadingMessage(loadingSteps[0].message);
      
      interval = setInterval(() => {
        currentStep++;
        if (currentStep < loadingSteps.length) {
          setLoadingStep(currentStep);
          setLoadingMessage(loadingSteps[currentStep].message);
        }
      }, 4000); // Change step every 4 seconds
    }
    return () => clearInterval(interval);
  }, [loading]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || !selectedConnection) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setLoadingStep(0);
    setLoadingMessage(loadingSteps[0].message);

    const startTime = Date.now();

    try {
      // Force query execution for better UX
      const response = await query.execute(selectedConnection, input, llmConfig, true);

      let assistantContent = response.data.answer;
      const executionTime = response.data.execution_time || (Date.now() - startTime) / 1000;
      
      // Add execution metadata
      assistantContent += `\n\n---\n📊 **Query Summary:**`;
      assistantContent += `\n⏱️ Response time: ${executionTime.toFixed(2)}s`;
      
      if (response.data.auto_executed) {
        assistantContent += `\n✅ Query was auto-executed`;
      }

      if (response.data.generated_query) {
        assistantContent += `\n\n**Generated Query:**\n\`\`\`${connectionList.find(c => c.id === selectedConnection)?.db_type || 'sql'}\n${response.data.generated_query}\n\`\`\``;
      }

      if (response.data.query_results && response.data.query_results.length > 0) {
        assistantContent += `\n\n📈 **Results:** ${response.data.query_results.length} rows returned`;
      }

      setMessages(prev => [...prev, { role: 'assistant', content: assistantContent }]);
    } catch (err) {
      const errorTime = (Date.now() - startTime) / 1000;
      let errorMessage = `❌ Sorry, I encountered an error processing your query (${errorTime.toFixed(2)}s).`;
      
      // Check for specific error types
      if (err.response?.status === 503) {
        const detail = err.response?.data?.detail || '';
        if (detail.includes('memory') || detail.includes('Ollama')) {
          errorMessage = `❌ **Local Model Memory Issue**\n\n` +
            `The local Ollama model requires more memory than available.\n\n` +
            `**Quick Fix:**\n` +
            `1. Click "LLM Settings" above\n` +
            `2. Uncheck "Use Local Models"\n` +
            `3. Select a cloud provider (OpenAI/Google/OpenRouter)\n` +
            `4. Enter your API key\n` +
            `5. Save and try again\n\n` +
            `This will use cloud LLMs which are faster and don't require local memory.\n\n` +
            `Error details: ${detail}`;
        } else {
          errorMessage += `\n\n${detail}`;
        }
      } else if (err.response?.status === 400) {
        errorMessage = `❌ **Configuration Required**\n\n` +
          `Please configure your LLM settings:\n` +
          `1. Click "LLM Settings" above\n` +
          `2. Choose local or cloud provider\n` +
          `3. Enter required credentials\n` +
          `4. Save and try again`;
      } else {
        errorMessage += `\n\nPlease check your connection settings and try again.`;
      }
      
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: errorMessage
      }]);
    } finally {
      setLoading(false);
    }
  };

  const formatMessage = (content) => {
    // Simple markdown-like formatting
    return content.split('\n').map((line, i) => {
      if (line.startsWith('**') && line.endsWith('**')) {
        return <p key={i} className="font-bold text-blue-300 mt-3 mb-2">{line.replace(/\*\*/g, '')}</p>;
      }
      if (line.startsWith('```')) {
        return null; // Handled separately
      }
      return <p key={i} className="mb-1">{line}</p>;
    });
  };

  const selectedConnData = connectionList.find(c => c.id === selectedConnection);

  return (
    <div className="min-h-screen animated-bg flex flex-col">
      {/* Navigation */}
      <nav className="nav-blur">
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
              <button
                onClick={() => setIsSettingsOpen(true)}
                className="text-gray-300 hover:text-white transition-colors flex items-center gap-2 px-4 py-2 rounded-lg hover:bg-white/5"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                LLM Settings
              </button>
            </div>
          </div>
        </div>
      </nav>

      <LLMSettings
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        savedConfig={llmConfig}
        onSave={(config) => {
          setLlmConfig(config);
          localStorage.setItem('llm_config', JSON.stringify(config));
        }}
      />

      {/* Main Chat Area */}
      <div className="flex-1 max-w-6xl w-full mx-auto p-4 flex flex-col">
        {/* Connection Selector */}
        <div className="glass-card p-4 rounded-xl mb-4">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-gray-300">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
              </svg>
              <span className="font-medium">Database:</span>
            </div>
            <select
              value={selectedConnection || ''}
              onChange={(e) => setSelectedConnection(parseInt(e.target.value))}
              className="input-modern px-4 py-2 rounded-lg text-white min-w-[200px]"
            >
              <option value="" className="bg-gray-800">Choose a connection...</option>
              {connectionList.map(conn => (
                <option key={conn.id} value={conn.id} className="bg-gray-800">
                  {conn.name} ({conn.db_type})
                </option>
              ))}
            </select>
            {selectedConnData && (
              <span className={`badge ${selectedConnData.db_type === 'postgresql' ? 'badge-postgresql' : 'badge-mongodb'}`}>
                {selectedConnData.db_type}
              </span>
            )}
          </div>
        </div>

        {/* Active Configuration Display */}
        {llmConfig && llmConfig.api_key && (
          <div className="flex justify-end mb-2 px-2">
            <div className="text-xs font-mono text-gray-400 bg-white/5 px-3 py-1 rounded-full border border-white/10 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
              Using {llmConfig.provider === 'google' ? 'Gemini' : llmConfig.provider === 'openrouter' ? 'OpenRouter' : 'OpenAI'}
              {llmConfig.model && <span className="text-gray-500"> / {llmConfig.model}</span>}
            </div>
          </div>
        )}

        {/* Messages Area */}
        <div className="flex-1 glass-card rounded-2xl p-6 mb-4 overflow-y-auto min-h-[400px]">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center">
              <div className="w-24 h-24 rounded-full bg-gradient-to-br from-blue-500/20 to-purple-600/20 flex items-center justify-center mb-6">
                <svg className="w-12 h-12 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold text-white mb-4">Start a Conversation</h3>
              <p className="text-gray-400 mb-8 max-w-md">
                Ask questions about your database in plain English. No SQL knowledge required!
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-lg">
                {[
                  'Show me all users from the database',
                  'Get the latest 10 orders',
                  'How many records are in each table?',
                  'Find all active customers'
                ].map((suggestion, idx) => (
                  <button
                    key={idx}
                    onClick={() => setInput(suggestion)}
                    className="text-left px-4 py-3 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 hover:border-blue-500/50 transition-all text-gray-300 text-sm"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`flex gap-3 max-w-[80%] ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${msg.role === 'user'
                      ? 'bg-gradient-to-br from-blue-500 to-purple-600'
                      : 'bg-gradient-to-br from-green-500 to-emerald-600'
                      }`}>
                      {msg.role === 'user' ? (
                        <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                        </svg>
                      ) : (
                        <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                      )}
                    </div>
                    <div
                      className={`px-5 py-3 ${msg.role === 'user'
                        ? 'message-user text-white'
                        : 'message-assistant text-gray-200'
                        }`}
                    >
                      <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed">
                        {msg.content}
                      </pre>
                    </div>
                  </div>
                </div>
              ))}
              {loading && (
                <div className="flex justify-start">
                  <div className="flex gap-3 max-w-[85%]">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center flex-shrink-0">
                      <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                    </div>
                    <div className="message-assistant px-5 py-4 w-full">
                      {/* Progress Steps */}
                      <div className="mb-3">
                        <div className="flex items-center gap-2 mb-2">
                          <div className="flex space-x-1">
                            {[...Array(3)].map((_, i) => (
                              <div 
                                key={i} 
                                className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"
                                style={{ animationDelay: `${i * 0.15}s` }}
                              />
                            ))}
                          </div>
                          <span className="text-blue-300 text-sm font-medium">{loadingMessage}</span>
                        </div>
                        
                        {/* Progress Bar */}
                        <div className="w-full bg-gray-700 rounded-full h-2 mb-3">
                          <div 
                            className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full transition-all duration-1000 ease-out"
                            style={{ width: `${((loadingStep + 1) / loadingSteps.length) * 100}%` }}
                          />
                        </div>
                        
                        {/* Step Indicators */}
                        <div className="flex justify-between text-xs text-gray-400">
                          {loadingSteps.map((step, idx) => (
                            <div 
                              key={idx}
                              className={`flex flex-col items-center ${idx <= loadingStep ? 'text-blue-400' : ''}`}
                            >
                              <div 
                                className={`w-2 h-2 rounded-full mb-1 ${
                                  idx < loadingStep ? 'bg-blue-500' : 
                                  idx === loadingStep ? 'bg-blue-400 animate-pulse' : 
                                  'bg-gray-600'
                                }`}
                              />
                            </div>
                          ))}
                        </div>
                      </div>
                      
                      <p className="text-xs text-gray-500 italic">
                        ⏱️ This may take 30-60 seconds with local LLM. Consider switching to cloud LLM for faster responses.
                      </p>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <form onSubmit={handleSubmit} className="flex gap-3">
          <div className="flex-1 relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={selectedConnection ? "Ask a question about your database..." : "Select a database connection first..."}
              className="input-modern w-full px-5 py-4 rounded-xl text-white placeholder-gray-500 pr-12"
              disabled={!selectedConnection || loading}
            />
            <svg className="absolute right-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
          </div>
          <button
            type="submit"
            disabled={!selectedConnection || loading || !input.trim()}
            className="btn-primary text-white px-6 py-4 rounded-xl font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {loading ? (
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
            ) : (
              <>
                <span>Send</span>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}

export default ChatInterface;
