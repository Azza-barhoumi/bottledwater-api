import React, { useEffect, useState } from "react";
import api from "../services/api";
import { useAuth } from "../context/AuthProvider";
import BrandCard from "../components/BrandCard";
import PCAChart from "../components/PCAChart";

export default function Dashboard() {
  const [brands, setBrands] = useState([]);
  const [selected, setSelected] = useState(null);
  const { logout, user } = useAuth();

  useEffect(() => {
    (async () => {
      const res = await api.get("/brands");
      setBrands(res.data);
      if (res.data.length) setSelected(res.data[0].id);
    })();
  }, []);

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-semibold">BottledWater Explorer</h1>
        <div className="flex gap-2">
          <div className="text-sm text-muted">User: {localStorage.getItem("bw_username") || "—"}</div>
          <button className="btn" onClick={logout}>Logout</button>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-1">
          <div className="card">
            <label className="block mb-1">Choose Brand</label>
            <select className="w-full border rounded p-2" value={selected || ""} onChange={(e)=>setSelected(Number(e.target.value))}>
              {brands.map(b => <option key={b.id} value={b.id}>{b.name}</option>)}
            </select>
          </div>

          {selected && <BrandCard brandId={selected} />}
        </div>

        <div className="col-span-2">
          <div className="card mb-6">
            <PCAChart />
          </div>
        </div>
      </div>
    </div>
  );
}
