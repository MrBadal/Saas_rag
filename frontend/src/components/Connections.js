import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { connections } from '../api/client';

function Connections() {
  const [connectionList, setConnectionList] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    db_type: 'postgresql',
    connection_string: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  useEffect(() => {
    loadConnections();
  }, []);

  const loadConnections = async () => {
    try {
      const response = await connections.list();
      setConnectionList(response.data);
    } catch (err) {
      console.error('Failed to load connections:', err);
    }
  };

  const handleDeleteConnection = async (id, name) => {
    if (deleteConfirm === id) {
      try {
        await connections.delete(id);
        setSuccess(`Connection "${name}" deleted successfully!`);
        loadConnections();
        setDeleteConfirm(null);
        setTimeout(() => setSuccess(''), 3000);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to delete connection');
      }
    } else {
      setDeleteConfirm(id);
      setTimeout(() => setDeleteConfirm(null), 3000);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await connections.create(formData);
      setSuccess('Connection created successfully!');
      setShowForm(false);
      setFormData({ name: '', db_type: 'postgresql', connection_string: '' });
      loadConnections();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      const errorDetail = err.response?.data?.detail || 'Failed to create connection';

      // Check if it's an OpenAI API key error
      if (typeof errorDetail === 'string' && errorDetail.includes('Incorrect API key provided')) {
        setError(
          <div>
            <p className="font-semibold mb-2">OpenAI API Key Required</p>
            <p className="text-sm mb-2">
              The application needs a valid OpenAI API key to process your database connection.
            </p>
            <ol className="text-sm list-decimal list-inside space-y-1 ml-2">
              <li>Get your API key from{' '}
                <a
                  href="https://platform.openai.com/account/api-keys"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-400 hover:text-blue-300 underline"
                >
                  OpenAI Platform
                </a>
              </li>
              <li>Open the <code className="bg-white/10 px-1 rounded">.env</code> file in the project root</li>
              <li>Replace <code className="bg-white/10 px-1 rounded">your_openai_api_key_here</code> with your actual API key</li>
              <li>Restart the application with: <code className="bg-white/10 px-1 rounded">docker-compose down && docker-compose up -d</code></li>
            </ol>
          </div>
        );
      } else {
        setError(errorDetail);
      }
    } finally {
      setLoading(false);
    }
  };

  const getDbIcon = (type) => {
    if (type === 'postgresql') {
      return (
        <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm0 22c-5.523 0-10-4.477-10-10S6.477 2 12 2s10 4.477 10 10-4.477 10-10 10z" />
        </svg>
      );
    }
    return (
      <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
      </svg>
    );
  };

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
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
            <div>
              <h1 className="text-4xl font-bold gradient-text mb-2">Database Connections</h1>
              <p className="text-gray-400">Manage your PostgreSQL and MongoDB connections</p>
            </div>
            <button
              onClick={() => setShowForm(!showForm)}
              className="btn-primary text-white px-6 py-3 rounded-xl font-semibold flex items-center gap-2"
            >
              {showForm ? (
                <>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                  Cancel
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  Add Connection
                </>
              )}
            </button>
          </div>

          {/* Alerts */}
          {error && (
            <div className={`border px-6 py-4 rounded-xl mb-6 flex items-start gap-3 ${typeof error === 'object'
              ? 'bg-yellow-500/20 border-yellow-500/50 text-yellow-200'
              : 'bg-red-500/20 border-red-500/50 text-red-300'
              }`}>
              <svg className="w-6 h-6 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div className="flex-1">{error}</div>
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

          {/* Add Connection Form */}
          {showForm && (
            <div className="glass-card p-8 rounded-2xl mb-8">
              <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                </div>
                New Database Connection
              </h2>
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-gray-300 text-sm font-medium mb-2">Connection Name</label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="input-modern w-full px-4 py-3 rounded-xl text-white placeholder-gray-500"
                      placeholder="My Production Database"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-gray-300 text-sm font-medium mb-2">Database Type</label>
                    <div className="grid grid-cols-2 gap-3">
                      <button
                        type="button"
                        onClick={() => setFormData({ ...formData, db_type: 'postgresql' })}
                        className={`flex items-center justify-center gap-2 px-4 py-3 rounded-xl border transition-all ${formData.db_type === 'postgresql'
                          ? 'bg-blue-500/20 border-blue-500/50 text-blue-300'
                          : 'bg-white/5 border-white/10 text-gray-400 hover:bg-white/10'
                          }`}
                      >
                        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
                        </svg>
                        PostgreSQL
                      </button>
                      <button
                        type="button"
                        onClick={() => setFormData({ ...formData, db_type: 'mongodb' })}
                        className={`flex items-center justify-center gap-2 px-4 py-3 rounded-xl border transition-all ${formData.db_type === 'mongodb'
                          ? 'bg-green-500/20 border-green-500/50 text-green-300'
                          : 'bg-white/5 border-white/10 text-gray-400 hover:bg-white/10'
                          }`}
                      >
                        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
                        </svg>
                        MongoDB
                      </button>
                    </div>
                  </div>
                </div>

                <div>
                  <label className="block text-gray-300 text-sm font-medium mb-2">Connection String</label>
                  <input
                    type="text"
                    value={formData.connection_string}
                    onChange={(e) => setFormData({ ...formData, connection_string: e.target.value })}
                    className="input-modern w-full px-4 py-3 rounded-xl text-white placeholder-gray-500 font-mono text-sm"
                    placeholder={formData.db_type === 'postgresql'
                      ? 'postgresql://user:password@host:5432/database'
                      : 'mongodb://user:password@host:27017/database'}
                    required
                  />
                  <p className="text-gray-500 text-sm mt-2">
                    {formData.db_type === 'postgresql'
                      ? 'Format: postgresql://username:password@hostname:port/database'
                      : 'Format: mongodb://username:password@hostname:port/database'}
                  </p>
                </div>

                <div className="flex gap-4">
                  <button
                    type="submit"
                    disabled={loading}
                    className="btn-primary text-white font-semibold py-3 px-8 rounded-xl disabled:opacity-50 flex items-center gap-2"
                  >
                    {loading ? (
                      <>
                        <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                        </svg>
                        Connecting...
                      </>
                    ) : (
                      <>
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                        Create Connection
                      </>
                    )}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowForm(false)}
                    className="glass text-white font-semibold py-3 px-8 rounded-xl hover:bg-white/10 transition-all"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* Connection Grid */}
          {connectionList.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {connectionList.map((conn) => (
                <div key={conn.id} className="connection-card p-6 rounded-2xl">
                  <div className="flex items-start justify-between mb-4">
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${conn.db_type === 'postgresql'
                      ? 'bg-blue-500/20 text-blue-400'
                      : 'bg-green-500/20 text-green-400'
                      }`}>
                      {getDbIcon(conn.db_type)}
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`badge ${conn.db_type === 'postgresql' ? 'badge-postgresql' : 'badge-mongodb'}`}>
                        {conn.db_type}
                      </span>
                      <button
                        onClick={() => handleDeleteConnection(conn.id, conn.name)}
                        className={`p-2 rounded-lg transition-all ${deleteConfirm === conn.id
                            ? 'text-red-400 bg-red-500/20 animate-pulse'
                            : 'text-gray-400 hover:text-red-400 hover:bg-red-500/10'
                          }`}
                        title={deleteConfirm === conn.id ? 'Click again to confirm delete' : 'Delete connection'}
                      >
                        {deleteConfirm === conn.id ? (
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                          </svg>
                        ) : (
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        )}
                      </button>
                    </div>
                  </div>

                  <h3 className="text-xl font-bold text-white mb-2">{conn.name}</h3>

                  <div className="space-y-2 mb-6">
                    <div className="flex items-center gap-2 text-gray-400 text-sm">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
                      </svg>
                      {Object.keys(conn.metadata?.schema || {}).length} tables/collections
                    </div>
                    <div className="flex items-center gap-2 text-gray-400 text-sm">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      Connected
                    </div>
                  </div>

                  <Link
                    to={`/chat?connection=${conn.id}`}
                    className="btn-primary w-full text-white py-3 rounded-xl font-semibold flex items-center justify-center gap-2"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                    </svg>
                    Query Database
                  </Link>
                </div>
              ))}
            </div>
          ) : (
            !showForm && (
              <div className="glass-card p-12 rounded-2xl text-center">
                <div className="w-20 h-20 rounded-full bg-gradient-to-br from-blue-500/20 to-purple-600/20 flex items-center justify-center mx-auto mb-6">
                  <svg className="w-10 h-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
                  </svg>
                </div>
                <h3 className="text-2xl font-bold text-white mb-4">No Connections Yet</h3>
                <p className="text-gray-400 mb-8 max-w-md mx-auto">
                  Get started by adding your first database connection. We support PostgreSQL and MongoDB.
                </p>
                <button
                  onClick={() => setShowForm(true)}
                  className="btn-primary text-white px-8 py-3 rounded-xl font-semibold inline-flex items-center gap-2"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  Add Your First Connection
                </button>
              </div>
            )
          )}
        </div>
      </div>
    </div>
  );
}

export default Connections;
