import React, { useState } from "react";
import api from "../services/api";

export default function PasswordReset() {
  const [username, setUser] = useState("");
  const [token, setToken] = useState("");
  const [newPass, setNewPass] = useState("");
  const [msg, setMsg] = useState("");

  const requestReset = async () => {
    setMsg("");
    try {
      const res = await api.post("/auth/request_password_reset", { username });
      // backend returns token for local testing; display it so dev can copy-paste
      setToken(res.data.reset_token || "");
      setMsg("Reset token generated and displayed (for local testing). In production you'd email it.");
    } catch (err) {
      setMsg(err?.response?.data?.msg || "Request failed");
    }
  };

  const applyReset = async () => {
    setMsg("");
    try {
      await api.post("/auth/reset_password", { token, new_password: newPass });
      setMsg("Password reset. You can now login.");
      setToken("");
      setNewPass("");
    } catch (err) {
      setMsg(err?.response?.data?.msg || "Reset failed");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="card w-full max-w-md">
        <h3 className="section-title mb-4 text-center">Password Reset</h3>
        <p className="text-muted mb-4 text-center">Enter your username to generate a password reset token. For local testing the token is shown below.</p>

        <div className="mb-3">
          <label className="block text-sm mb-1">Username</label>
          <input value={username} onChange={e=>setUser(e.target.value)} />
        </div>
        <div className="flex gap-3 justify-center mb-3">
          <button className="btn" onClick={requestReset}>Request Reset Token</button>
        </div>

        <div className="mb-3">
          <label className="block text-sm mb-1">Token (for testing)</label>
          <textarea value={token} onChange={e=>setToken(e.target.value)} />
        </div>

        <div className="mb-3">
          <label className="block text-sm mb-1">New password</label>
          <input type="password" value={newPass} onChange={e=>setNewPass(e.target.value)} />
        </div>

        <div className="flex gap-3 justify-center">
          <button className="btn-primary" onClick={applyReset}>Reset Password</button>
        </div>

        {msg && <div className="mt-3 text-sm text-muted text-center">{msg}</div>}
      </div>
    </div>
  );
}
