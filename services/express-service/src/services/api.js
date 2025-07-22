import axios from "axios";
const api = axios.create({
  baseURL: process.env.TRUVERA_API || "https://api-testnet.truvera.io",
  headers: {
    Authorization: `Bearer ${process.env.TRUVERA_JWT}`,
    "Content-Type": "application/json",
    Accept: "*/*",
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      // window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default api;
