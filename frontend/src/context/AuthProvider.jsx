import React, { createContext, useContext, useEffect, useState } from "react";
import api from "../services/api.js";

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const u = localStorage.getItem("bw_user");
    return u ? JSON.parse(u) : null;
  });

  // try to keep access token in memory; it is stored in localStorage too
  useEffect(() => {
    const token = localStorage.getItem("bw_token");
    if (token && !user) {
      // optionally fetch profile
      (async () => {
        try {
          // call refresh or user endpoint if you had one; we'll just keep stored username
          const uname = localStorage.getItem("bw_username");
          if (uname) setUser({ username: uname });
        } catch (e) {
          console.error(e);
        }
      })();
    }
  }, []);

  const login = ({ access_token, refresh_token, username }) => {
    // Accept a few possible token field names for robustness
    const access = access_token || (refresh_token && null) || null;
    const refresh = refresh_token || null;
    if (!access || !refresh) {
      throw new Error("Invalid token response");
    }
    localStorage.setItem("bw_token", access);
    localStorage.setItem("bw_refresh", refresh);
    localStorage.setItem("bw_username", username);
    localStorage.setItem("bw_user", JSON.stringify({ username }));
    setUser({ username });
  };

  const logout = async () => {
    // call revoke endpoints if desired
    const access = localStorage.getItem("bw_token");
    const refresh = localStorage.getItem("bw_refresh");
    try {
      if (access) await api.post("/auth/logout_access");
    } catch {}
    try {
      if (refresh) await api.post("/auth/logout_refresh");
    } catch {}
    localStorage.removeItem("bw_token");
    localStorage.removeItem("bw_refresh");
    localStorage.removeItem("bw_username");
    localStorage.removeItem("bw_user");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, setUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
