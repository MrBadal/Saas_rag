import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

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
  execute: (connection_id, query, llm_config) =>
    client.post('/api/query/', { connection_id, query, llm_config }),
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
