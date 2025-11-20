import axios from 'axios';

// ✅ Use localhost since React and backend are on same machine
const BASE_URL = 'http://127.0.0.1:8100';

// Alternative: Use your Mac IP if accessing from another device
// const BASE_URL = 'http://192.168.0.5:8100';

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 seconds
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log('🚀 API Request:', config.method.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log('✅ API Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    if (error.response) {
      // Server responded with error status
      console.error('❌ Server Error:', error.response.status, error.response.data);
    } else if (error.request) {
      // Request made but no response
      console.error('❌ No Response from server:', error.message);
    } else {
      // Something else went wrong
      console.error('❌ Request Setup Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// =====================================================
// API Functions
// =====================================================

// Stats
export const getStats = () => {
  console.log('📊 Fetching stats...');
  return api.get('/stats/');
};

// Organizations
export const getOrganizations = (skip = 0, limit = 100) => 
  api.get('/organizations/', { params: { skip, limit } });

export const getOrganization = (id) => 
  api.get(`/organizations/${id}`);

export const createOrganization = (data) => 
  api.post('/organizations/', data);

export const updateOrganization = (id, data) => 
  api.patch(`/organizations/${id}`, data);

// Users
export const getUsers = (params = {}) => 
  api.get('/users/', { params });

export const getUser = (id) => 
  api.get(`/users/${id}`);

export const createUser = (data) => 
  api.post('/users/', data);

export const updateUser = (id, data) => 
  api.patch(`/users/${id}`, data);

// Schemes
export const getSchemes = (params = {}) => 
  api.get('/schemes/', { params });

export const getScheme = (id) => 
  api.get(`/schemes/${id}`);

export const createScheme = (data) => 
  api.post('/schemes/', data);

// Test connection
export const testConnection = () => {
  console.log('🔌 Testing backend connection...');
  return api.get('/');
};

export default api;
