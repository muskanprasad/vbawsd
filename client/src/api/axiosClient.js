// src/api/axiosClient.js
import axios from "axios";

// baseURL used in your project
const axiosClient = axios.create({
  baseURL: "https://vbawsd-server.onrender.com",
  timeout: 20000, // 20s timeout
});

// attach token (if present)
axiosClient.interceptors.request.use(
  (config) => {
    try {
      const token = localStorage.getItem("token");
      if (token) {
        config.headers = config.headers || {};
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (e) {
      // ignore
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// response interceptor: handle 401 globally
axiosClient.interceptors.response.use(
  (res) => res,
  (error) => {
    const status = error?.response?.status;
    if (status === 401) {
      // clear auth and redirect to login
      try {
        localStorage.removeItem("token");
        localStorage.removeItem("role");
        localStorage.removeItem("username");
      } catch (_) {}
      // navigate to login (hard redirect is safest from non-react module)
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default axiosClient;
