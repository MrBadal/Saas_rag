import React, { useState, useEffect } from 'react';
import client from '../api/client';

function ConnectionStatus() {
  const [status, setStatus] = useState('checking');
  const [error, setError] = useState(null);
  const [apiUrl, setApiUrl] = useState('');

  useEffect(() => {
    checkConnection();
  }, []);

  const checkConnection = async () => {
    try {
      // Show which API URL is being used
      setApiUrl(process.env.REACT_APP_API_URL || 'http://localhost:8000');
      
      // Try to connect to backend health endpoint
      const response = await client.get('/health');
      
      if (response.status === 200) {
        setStatus('connected');
        setError(null);
      } else {
        setStatus('error');
        setError(`Unexpected response: ${response.status}`);
      }
    } catch (err) {
      setStatus('error');
      setError(err.message);
      console.error('Connection check failed:', err);
    }
  };

  if (status === 'checking') {
    return (
      <div className="p-4 bg-yellow-100 border border-yellow-400 rounded">
        <p className="text-yellow-800">Checking backend connection...</p>
        <p className="text-sm text-yellow-600">API URL: {apiUrl}</p>
      </div>
    );
  }

  if (status === 'error') {
    return (
      <div className="p-4 bg-red-100 border border-red-400 rounded">
        <h3 className="font-bold text-red-800">Backend Connection Error</h3>
        <p className="text-red-700">{error}</p>
        <p className="text-sm text-red-600 mt-2">API URL: {apiUrl}</p>
        <div className="mt-4 text-sm text-red-800">
          <p className="font-semibold">Troubleshooting steps:</p>
          <ol className="list-decimal list-inside mt-2 space-y-1">
            <li>Ensure backend is running on port 8000</li>
            <li>Check that the API URL is correct: {apiUrl}</li>
            <li>Verify AWS security group allows port 8000</li>
            <li>Check browser console for CORS errors</li>
            <li>Try accessing backend directly: {apiUrl}/health</li>
          </ol>
        </div>
        <button 
          onClick={checkConnection}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Retry Connection
        </button>
      </div>
    );
  }

  return (
    <div className="p-4 bg-green-100 border border-green-400 rounded">
      <p className="text-green-800">✅ Backend connected successfully</p>
      <p className="text-sm text-green-600">API URL: {apiUrl}</p>
    </div>
  );
}

export default ConnectionStatus;
