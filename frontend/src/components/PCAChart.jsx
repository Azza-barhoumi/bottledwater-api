import React, { useEffect, useState } from "react";
import { Scatter } from "react-chartjs-2";
import api from "../services/api";
import {
  Chart as ChartJS, PointElement, LinearScale, Tooltip, Legend
} from "chart.js";
ChartJS.register(PointElement, LinearScale, Tooltip, Legend);

export default function PCAChart() {
  const [pts, setPts] = useState(null);
  useEffect(() => {
    (async () => {
      try {
        const res = await api.post("/analysis/cluster", { n_clusters: 6 });
        setPts(res.data.assignments);
      } catch (e) {
        console.error("PCA failed", e);
      }
    })();
  }, []);

  if (!pts) return <div>Loading PCA...</div>;

  // Find best (closest to center) and worst (farthest from center) brands
  let bestBrand = null, worstBrand = null;
  if (pts && pts.length) {
    // Center is (0,0) in PCA
    let minDist = Infinity, maxDist = -Infinity;
    pts.forEach(p => {
      const dist = Math.sqrt((p.pc1 || 0) ** 2 + (p.pc2 || 0) ** 2);
      if (dist < minDist) {
        minDist = dist;
        bestBrand = p.brand;
      }
      if (dist > maxDist) {
        maxDist = dist;
        worstBrand = p.brand;
      }
    });
  }

  const groups = {};
  pts.forEach(p => {
    groups[p.cluster] = groups[p.cluster] || [];
    groups[p.cluster].push({ x: p.pc1, y: p.pc2, label: p.brand });
  });

  const colors = ["#1f77b4","#ff7f0e","#2ca02c","#d62728","#9467bd","#17becf","#7f7f7f"];

  const datasets = Object.keys(groups).map((k,i)=>({
    label: "Cluster " + k,
    data: groups[k],
    backgroundColor: colors[i % colors.length],
    pointRadius: 6
  }));

  return (
    <div className="pca-chart">
      <Scatter
        data={{ datasets }}
        options={{
          plugins: {
            tooltip: {
              callbacks: {
                label: ctx => ctx.raw.label
              }
            }
          },
          scales: {
            x: { title: { display: true, text: "PC1" } },
            y: { title: { display: true, text: "PC2" } }
          }
        }}
      />

      <div className="mt-4 text-sm text-gray-700">
        {bestBrand && worstBrand && (
          <div className="mb-3 p-2 rounded bg-slate-50 border border-slate-200">
            <strong>PCA-based Brand Assessment:</strong>
            <p className="mt-2">
              <span className="font-semibold text-emerald-700">Best (most balanced):</span> <span className="font-bold">{bestBrand}</span><br/>
              <span className="font-semibold text-rose-700">Worst (most extreme):</span> <span className="font-bold">{worstBrand}</span>
            </p>
            <p className="mt-2 text-xs text-slate-600">
              <em>Best brand is closest to the PCA center (most balanced mineral profile). Worst brand is farthest from center (most extreme mineral composition). This is a statistical assessment, not a health or taste recommendation.</em>
            </p>
          </div>
        )}
        <strong>Interpreting the PCA plot:</strong>
        <p className="mt-2">
          Each point represents a brand projected onto the first two principal components (PC1 and PC2).
          PC1 and PC2 are the directions that capture the most variation in the original feature space —
          points that are close together have similar chemical/compositional profiles, while points far apart
          are more different.
        </p>
        <p className="mt-2">
          Colors correspond to clustering assignments (clusters were computed with k-means). Hover over a point
          to see the brand name. Use this plot to identify groups of similar brands and potential outliers.
        </p>
        <hr className="my-3" />
        <strong>Best and Worst Water Brands:</strong>
        <p className="mt-2">
          The PCA chart does not directly rank brands as "best" or "worst"—instead, it shows how brands differ in mineral composition. Brands near the center or grouped together typically have balanced mineral profiles, which may be preferred for general health. Brands far from the center or isolated may have extreme mineral content (very high or low), which could be less suitable for everyday consumption or only recommended for specific health needs.
        </p>
        <p className="mt-2">
          <strong>Best brands:</strong> Usually those with moderate, balanced mineral content, not too high in sodium, calcium, or other minerals. These are often found in clusters near the center of the PCA plot.
        </p>
        <p className="mt-2">
          <strong>Worst brands:</strong> Brands that are outliers—far from other clusters—may have excessive or deficient mineral levels. For example, very high sodium or very low calcium. These may be less suitable for regular drinking, but could be chosen for specific dietary needs.
        </p>
        <p className="mt-2">
          <em>Note:</em> The "best" water depends on individual health, taste, and dietary requirements. Always check the detailed mineral composition and consult health guidelines if you have specific needs.
        </p>
      </div>
    </div>
  );
}
