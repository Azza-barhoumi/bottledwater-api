import React, { useState } from "react";
import api from "../services/api";
import { useNavigate } from "react-router-dom";

export default function Register() {
  const [username, setUser] = useState("");
  const [password, setPass] = useState("");
  const [msg, setMsg] = useState("");
  const navigate = useNavigate();

  const doRegister = async () => {
    try {
      await api.post("/auth/register", { username, password });
      setMsg("Account created. Please login.");
      setTimeout(()=> navigate("/login"), 1200);
    } catch (e) {
      setMsg("Registration failed");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="card w-full max-w-md">
        <h2 className="section-title mb-4 text-center">Create account</h2>
        <p className="text-muted mb-4 text-center">Join to rate and explore bottled water brands.</p>
        {msg && <div className="text-green-600 mb-2 text-center">{msg}</div>}
        
        <form onSubmit={(e) => { e.preventDefault(); doRegister(); }}>
          <div className="mb-3">
            <label className="block text-sm mb-1">Username</label>
            <input value={username} onChange={(e)=>setUser(e.target.value)} required />
          </div>
          <div className="mb-4">
            <label className="block text-sm mb-1">Password</label>
            <input type="password" value={password} onChange={(e)=>setPass(e.target.value)} required />
          </div>
          <div className="flex gap-3 justify-center">
            <button type="submit" className="btn-primary">Create account</button>
            <button type="button" className="btn" onClick={()=>navigate("/login")}>Back</button>
          </div>
        </form>
      </div>
    </div>
  );
}
