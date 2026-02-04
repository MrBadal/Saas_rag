import axios from 'axios';

// Get API URL from environment or use default
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

console.log('API URL:', API_URL); // Debug log

const client = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
});

// Add token to requests
client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    console.log(`Making ${config.method?.toUpperCase()} request to: ${config.url}`); // Debug log
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
client.interceptors.response.use(
  (response) => {
    console.log(`Response from ${response.config.url}:`, response.status); // Debug log
    return response;
  },
  (error) => {
    if (error.code === 'ECONNABORTED') {
      console.error('Request timeout - backend may be down or unreachable');
    } else if (error.response) {
      // Server responded with error status
      console.error('Server error:', error.response.status, error.response.data);
    } else if (error.request) {
      // Request made but no response received
      console.error('No response from server - check if backend is running at:', API_URL);
    } else {
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export const auth = {
  register: (email, password) =>
    client.post('/api/auth/register', { email, password }),
  login: (email, password) =>
    client.post('/api/auth/login', { email, password }),
};

export const connections = {
  create: (data) =>
    client.post('/api/connections/', data),
  list: () =>
    client.get('/api/connections/'),
  getSchema: (id) =>
    client.get(`/api/connections/${id}/schema`),
  delete: (id) =>
    client.delete(`/api/connections/${id}`),
};

export const query = {
  execute: (connection_id, query_text, llm_config, force_execute = true) =>
    client.post('/api/query/', { 
      connection_id, 
      query: query_text, 
      llm_config,
      execute_query: force_execute
    }),
  getHistory: () =>
    client.get('/api/query/history'),
  getModels: (llm_config) =>
    client.post('/api/query/models', llm_config),
};

export const settings = {
  get: () =>
    client.get('/api/settings/'),
  update: (data) =>
    client.post('/api/settings/', data),
  getProviders: () =>
    client.get('/api/settings/providers'),
};

export default client;
