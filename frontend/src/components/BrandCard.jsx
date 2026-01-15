import React, { useEffect, useState } from "react";
import api from "../services/api";
import CompositionRadar from "./CompositionRadar";
import StarRating from "./StarRating";

export default function BrandCard({ brandId }) {
  const [info, setInfo] = useState(null);
  const [ratings, setRatings] = useState([]);
  const [form, setForm] = useState({
    taste: 4,
    freshness: 4,
    smoothness: 4,
    overall: 4,
    comment: ""
  });

  useEffect(() => {
    if (!brandId) return;
    (async () => {
      const res = await api.get(`/brand/${brandId}`);
      setInfo(res.data);
      const r = await api.get(`/ratings/${brandId}`);
      setRatings(r.data);
    })();
  }, [brandId]);

  const submit = async () => {
    try {
      await api.post("/ratings", { brand_id: brandId, ...form });
      const r = await api.get(`/ratings/${brandId}`);
      setRatings(r.data);
      const refreshed = await api.get(`/brand/${brandId}`);
      setInfo(refreshed.data);
      // friendly inline confirmation instead of alert
      const el = document.createElement('div');
      el.textContent = 'Rating submitted';
      el.className = 'text-sm text-green-600 mt-2';
      // append to card briefly
      const parent = document.querySelector('.card');
      if (parent) parent.appendChild(el);
      setTimeout(() => el.remove(), 1800);
    } catch (e) {
      alert("Login required or error");
    }
  };

  if (!info) return <div className="card">Loading...</div>;

  return (
    <div className="card mt-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-xl font-semibold">{info.name}</h3>
          <div className="mb-2 text-sm text-muted">{info.type} — {info.company} ({info.region})</div>
          <div className="mb-2"><strong>Personality:</strong> {info.personality}</div>
        </div>
        <div className="w-48">
          <div className="text-sm text-muted mb-2">Rating summary</div>
          <div className="text-lg font-semibold">{info.rating_summary.count > 0 ? `${info.rating_summary.overall.toFixed(2)} / 5` : '—'}</div>
          <div className="text-sm text-muted">{info.rating_summary.count} reviews</div>
        </div>
      </div>

      <div className="mt-4">
        <CompositionRadar info={info} />
      </div>

      <div className="mt-4 grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div>
          <strong>Recommendations</strong>
          <ul className="list-disc pl-6 mt-2">
            {info.recommendations.map((r,i)=> <li key={i}>{r}</li>)}
          </ul>
        </div>

        <div>
          <strong>Submit rating</strong>
          <div className="mt-2 grid grid-cols-2 gap-3">
            {['taste','freshness','smoothness','overall'].map((k)=> (
              <div key={k}>
                <label className="block text-sm capitalize mb-1">{k}</label>
                <StarRating name={k} value={form[k]} onChange={(v)=>setForm({...form,[k]:v})} />
              </div>
            ))}
          </div>
          <textarea className="w-full border rounded p-2 mt-3" placeholder="notes" value={form.comment} onChange={(e)=>setForm({...form, comment: e.target.value})} />
          <div className="flex gap-2 mt-3">
            <button className="btn-primary" onClick={submit}>Submit</button>
          </div>
        </div>
      </div>

      <div className="mt-6">
        <strong>Community ratings</strong>
        <ul className="mt-2">
          {ratings.map(r => (
            <li key={r.id} className="border-b py-3">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm"><strong>Overall {r.overall}</strong></div>
                  <div className="text-xs text-muted">Taste {r.taste} · Freshness {r.freshness} · Smoothness {r.smoothness}</div>
                </div>
                <div className="text-xs text-gray-400">{new Date(r.created_at).toLocaleString()}</div>
              </div>
              {r.comment && <div className="text-sm text-muted mt-2">{r.comment}</div>}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}


