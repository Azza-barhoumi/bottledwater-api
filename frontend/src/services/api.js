import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:5000";

const api = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
  headers: {
    "Content-Type": "application/json"
  }
});

// Attach access token to all requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("bw_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// response interceptor to handle 401 -> try refresh once
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) prom.reject(error);
    else prom.resolve(token);
  });
  failedQueue = [];
};

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const originalRequest = err.config;
    if (!originalRequest) return Promise.reject(err);

    if (err.response && err.response.status === 401 && !originalRequest._retry) {
      // attempt to refresh
      if (isRefreshing) {
        return new Promise(function (resolve, reject) {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = "Bearer " + token;
            return axios(originalRequest);
          })
          .catch((e) => Promise.reject(e));
      }

      originalRequest._retry = true;
      isRefreshing = true;
      const refreshToken = localStorage.getItem("bw_refresh");
      if (!refreshToken) {
        // no refresh token, redirect to login or reject
        isRefreshing = false;
        return Promise.reject(err);
      }

      return new Promise((resolve, reject) => {
        axios
          .post(API_BASE + "/auth/refresh", null, {
            headers: { Authorization: "Bearer " + refreshToken }
          })
          .then((response) => {
            const newAccess = response.data.access_token;
            localStorage.setItem("bw_token", newAccess);
            api.defaults.headers.common["Authorization"] = "Bearer " + newAccess;
            originalRequest.headers["Authorization"] = "Bearer " + newAccess;
            processQueue(null, newAccess);
            resolve(api(originalRequest));
          })
          .catch((e) => {
            processQueue(e, null);
            // clear tokens
            localStorage.removeItem("bw_token");
            localStorage.removeItem("bw_refresh");
            reject(e);
          })
          .finally(() => {
            isRefreshing = false;
          });
      });
    }
    return Promise.reject(err);
  }
);

export default api;
