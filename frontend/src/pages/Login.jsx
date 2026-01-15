import React, { useState } from "react";
import api from "../services/api";
import { useAuth } from "../context/AuthProvider";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const [username, setUser] = useState("admin");
  const [password, setPass] = useState("password");
  const [msg, setMsg] = useState("");
  const { login } = useAuth();
  const navigate = useNavigate();

  const doLogin = async (e) => {
    if (e && e.preventDefault) e.preventDefault();
    setMsg("");
    try {
      const res = await api.post("/auth/login", { username, password });
      // validate server response shape before using it
      const body = res && res.data ? res.data : {};
      const access_token = body.access_token || body.accessToken || body.token;
      const refresh_token = body.refresh_token || body.refreshToken || body.refresh;
      if (!access_token || !refresh_token) {
        console.error('Invalid login response', res);
        setMsg('Invalid server response during login');
        return;
      }
      login({ access_token, refresh_token, username });
      navigate("/");
    } catch (err) {
      console.error('Login error', err);
      const serverMsg = err?.response?.data?.msg || err?.message;
      setMsg(serverMsg || "Login failed. Check credentials.");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="card w-full max-w-md">
        <h2 className="section-title mb-4 text-center">Welcome back</h2>
        <p className="text-muted mb-4 text-center">Sign in to explore bottled water profiles and community ratings.</p>

        {msg && <div className="text-red-600 mb-3 text-center" role="alert">{msg}</div>}

        <form onSubmit={doLogin} aria-label="Login form">
          <div className="mb-3">
            <label className="block text-sm mb-1">Username</label>
            <input
              name="username"
              aria-label="username"
              value={username}
              onChange={(e) => setUser(e.target.value)}
              required
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm mb-1">Password</label>
            <input
              name="password"
              type="password"
              aria-label="password"
              value={password}
              onChange={(e) => setPass(e.target.value)}
              required
            />
          </div>

          <div className="flex gap-3 justify-center">
            <button type="submit" className="btn-primary">Login</button>
            <button type="button" className="btn" onClick={() => navigate('/register')}>Register</button>
          </div>
        </form>

        <div className="mt-4 text-sm text-muted text-center">
          <div>Demo: <strong>admin</strong> / <strong>password</strong></div>
        </div>
      </div>
    </div>
  );
}
