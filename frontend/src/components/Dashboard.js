import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import ConnectionStatus from './ConnectionStatus';

function Dashboard({ onLogout }) {
  const navigate = useNavigate();

  const features = [
    {
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      ),
      title: 'Connect Database',
      description: 'Add PostgreSQL or MongoDB connections in seconds',
      link: '/connections',
      color: 'from-blue-500 to-cyan-500',
      bgColor: 'bg-blue-500/10',
      borderColor: 'border-blue-500/30'
    },
    {
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
        </svg>
      ),
      title: 'Query with AI',
      description: 'Ask questions in natural language and get instant answers',
      link: '/chat',
      color: 'from-purple-500 to-pink-500',
      bgColor: 'bg-purple-500/10',
      borderColor: 'border-purple-500/30'
    },
    {
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
      title: 'View Analytics',
      description: 'Get AI-powered insights and visualizations from your data',
      link: '/chat',
      color: 'from-green-500 to-emerald-500',
      bgColor: 'bg-green-500/10',
      borderColor: 'border-green-500/30'
    }
  ];

  const stats = [
    { label: 'Active Connections', value: '0', icon: '🔌' },
    { label: 'Queries Today', value: '0', icon: '💬' },
    { label: 'Data Sources', value: '2', icon: '📊' }
  ];

  return (
    <div className="min-h-screen animated-bg">
      {/* Navigation */}
      <nav className="nav-blur fixed w-full z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <span className="text-xl font-bold gradient-text">DataQuery AI</span>
            </div>
            <div className="flex items-center gap-4">
              <Link to="/connections" className="text-gray-300 hover:text-white transition-colors flex items-center gap-2 px-4 py-2 rounded-lg hover:bg-white/5">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
                Connections
              </Link>
              <Link to="/chat" className="text-gray-300 hover:text-white transition-colors flex items-center gap-2 px-4 py-2 rounded-lg hover:bg-white/5">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                Chat
              </Link>

              <button
                onClick={onLogout}
                className="bg-red-500/20 hover:bg-red-500/30 text-red-400 hover:text-red-300 px-4 py-2 rounded-lg transition-all flex items-center gap-2 border border-red-500/30"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="pt-24 pb-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          {/* Hero Section */}
          <div className="text-center mb-16">
            <h1 className="text-5xl md:text-6xl font-bold mb-6">
              <span className="gradient-text">Welcome to the Future</span>
              <br />
              <span className="text-white">of Database Queries</span>
            </h1>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-8">
              Connect your databases and query them using natural language powered by advanced AI
            </p>
            <div className="flex justify-center gap-4">
              <Link
                to="/connections"
                className="btn-primary text-white font-semibold py-3 px-8 rounded-xl inline-flex items-center gap-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                Add Connection
              </Link>
              <Link
                to="/chat"
                className="glass text-white font-semibold py-3 px-8 rounded-xl inline-flex items-center gap-2 hover:bg-white/10 transition-all"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                Start Chatting
              </Link>
            </div>
          </div>

          {/* Connection Status */}
          <div className="max-w-2xl mx-auto mb-8">
            <ConnectionStatus />
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
            {stats.map((stat, index) => (
              <div key={index} className="glass-card p-6 rounded-2xl text-center card-hover">
                <div className="text-4xl mb-2">{stat.icon}</div>
                <div className="text-3xl font-bold text-white mb-1">{stat.value}</div>
                <div className="text-gray-400">{stat.label}</div>
              </div>
            ))}
          </div>

          {/* Feature Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
            {features.map((feature, index) => (
              <Link
                key={index}
                to={feature.link}
                className={`glass-card p-8 rounded-2xl card-hover group border ${feature.borderColor}`}
              >
                <div className={`w-16 h-16 rounded-2xl ${feature.bgColor} flex items-center justify-center mb-6 group-hover:scale-110 transition-transform`}>
                  <div className={`bg-gradient-to-r ${feature.color} text-white rounded-xl p-3`}>
                    {feature.icon}
                  </div>
                </div>
                <h3 className="text-xl font-bold text-white mb-3">{feature.title}</h3>
                <p className="text-gray-400">{feature.description}</p>
                <div className="mt-6 flex items-center text-blue-400 group-hover:text-blue-300 transition-colors">
                  <span className="font-medium">Get Started</span>
                  <svg className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </div>
              </Link>
            ))}
          </div>

          {/* How it works */}
          <div className="glass-card p-8 rounded-2xl">
            <h3 className="text-2xl font-bold text-white mb-8 text-center">How It Works</h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
              {[
                { step: '1', title: 'Connect', desc: 'Add your PostgreSQL or MongoDB database' },
                { step: '2', title: 'Index', desc: 'We automatically analyze your schema & data' },
                { step: '3', title: 'Ask', desc: 'Query in plain English, no SQL needed' },
                { step: '4', title: 'Discover', desc: 'Get AI-powered insights instantly' }
              ].map((item, index) => (
                <div key={index} className="text-center">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-lg mx-auto mb-4">
                    {item.step}
                  </div>
                  <h4 className="text-white font-semibold mb-2">{item.title}</h4>
                  <p className="text-gray-400 text-sm">{item.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
