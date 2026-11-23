import axios from 'axios';

// Dedicated port 8088 for Smart Society Security backend
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8088/api';

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
  start: () => api.post('/gate/start'),
  stop: () => api.post('/gate/stop'),
  getStatus: () => api.get('/gate/status'),
  getStreamUrl: () => `${API_BASE_URL}/gate/stream`,
  updateThreshold: (threshold) => api.post('/gate/threshold', { threshold }),
  reloadDatabase: () => api.post('/gate/reload'),
};

export const logsApi = {
  getLogs: (params) => api.get('/logs', { params }),
  getLogById: (id) => api.get(`/logs/${id}`),
};

export const evaluationApi = {
  getSummary: () => api.get('/evaluation/summary'),
  getPlotUrl: (name) => `${API_BASE_URL}/evaluation/plot/${name}`,
};

export default api;
