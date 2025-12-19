// src/api/axios.js
import axios from "axios";

const API_BASE_URL = "/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error = null) => {
  failedQueue.forEach((promise) => {
    error ? promise.reject(error) : promise.resolve();
  });
  failedQueue = [];
};

const normalizeUrl = (url) => url.replace(/^https?:\/\/[^/]+/, "");

// Request interceptor - ensure correct baseURL and remove auth headers
api.interceptors.request.use((config) => {
  config.baseURL = API_BASE_URL;
  delete config.headers?.Authorization;
  delete config.headers?.authorization;
  
  console.log(`→ ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`);
  return config;
});

// Response interceptor - handle 401 with token refresh
api.interceptors.response.use(
  (response) => {
    console.log(`← ${response.status} from ${response.config.url}`);
    return response;
  },
  async (error) => {
    const { config: original, response } = error;
    
    if (!original || response?.status !== 401 || original._retry) {
      return Promise.reject(error);
    }

    original._retry = true;

    // Queue subsequent requests while refreshing
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject });
      }).then(() => api({
        ...original,
        baseURL: API_BASE_URL,
        url: normalizeUrl(original.url),
      }));
    }

    isRefreshing = true;

    try {
      console.log("🔄 Refreshing token...");
      await api.post("/refresh");
      console.log("✅ Token refreshed");
      
      processQueue();
      
      return api({
        ...original,
        baseURL: API_BASE_URL,
        url: normalizeUrl(original.url),
      });
    } catch (refreshError) {
      console.error("❌ Refresh failed");
      processQueue(refreshError);
      window.location.href = "/login";
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  }
);

export default api;