// src/api/authApi.js
import axiosClient from "./axiosClient";

/**
 * NOTE:
 * - loginApi returns response.data
 * - signup returns response.data
 */

export const signup = (data) => axiosClient.post("/api/auth/signup", data).then(r => r.data);

export const loginApi = (data) =>
  axiosClient.post("/auth/login", data).then((r) => r.data);

// optionally export a /me or verify token endpoint if backend provides
export const me = () => axiosClient.get("/auth/me").then(r => r.data);


// import axiosClient from "./axiosClient";

// export const loginUser = (data) =>
//   axiosClient.post("/auth/login", data);

// export const registerUser = (data) =>
//   axiosClient.post("/auth/register", data);
