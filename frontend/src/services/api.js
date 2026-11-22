import axios from 'axios';

// Default to FastAPI backend port 8000
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    'Accept': 'application/json',
  },
});

export const healthApi = {
  getHealth: () => api.get('/health'),
};

export const dashboardApi = {
  getStats: () => api.get('/dashboard/stats'),
};

export const residentsApi = {
  getAll: () => api.get('/residents'),
  getPhotoUrl: (residentId) => `${API_BASE_URL}/residents/${residentId}/photo`,
  register: (formData) => api.post('/residents', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  delete: (residentId) => api.delete(`/residents/${residentId}`),
};

export const gateApi = {
  getStatus: () => api.get('/gate/status'),
  updateThreshold: (threshold) => api.post('/gate/threshold', { threshold }),
  reloadDatabase: () => api.post('/gate/reload'),
};

export const evaluationApi = {
  getSummary: () => api.get('/evaluation/summary'),
  getPlotUrl: (name) => `${API_BASE_URL}/evaluation/plot/${name}`,
};

export const logsApi = {
  getLogs: () => api.get('/logs'),
};

export default api;
