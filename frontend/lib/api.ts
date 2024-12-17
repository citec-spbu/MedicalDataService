"use client";

import axios from "axios";
import { jwtDecode } from "jwt-decode";
import { redirect } from "next/navigation";

const api = axios.create({
  baseURL: process.env.API,
  withCredentials: true
});

export const refreshAccessToken = async () => {
  try {
    const response = await axios(`${process.env.API}/user/refresh`, {
      method: "post",
      withCredentials: true
    });
    const { access_token: accessToken } = response.data;
    localStorage.setItem("accessToken", accessToken);
    return accessToken;
  } catch (error) {
    console.log("Can't update access token. Navigating to /login");
    throw error;
  }
};

api.interceptors.request.use(async (config) => {
  try {
    let accessToken = localStorage.getItem("accessToken");
    if (!accessToken) {
      accessToken = await refreshAccessToken();
    } else {
      const decodedToken = jwtDecode(accessToken);
      const currentTime = Date.now() / 1000;

      if (decodedToken.exp! < currentTime) {
        accessToken = await refreshAccessToken();
      }
    }

    config.headers["Authorization"] = `Bearer ${accessToken}`;
    return config;
  } catch {
    localStorage.removeItem("accessToken");
    redirect("/auth/login");
  }
});

export default api;
