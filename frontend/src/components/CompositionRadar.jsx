import React from "react";
import { Radar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
} from "chart.js";

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

export default function CompositionRadar({ info }) {
  // Show all minerals
  const labels = ["Calcium","Magnesium","Sodium","Bicarbonates","Sulfates","Nitrates"];
  const values = [
    info.calcium || 0,
    info.magnesium || 0,
    info.sodium || 0,
    info.bicarbonates || 0,
    info.sulfates || 0,
    info.nitrates || 0
  ];
  const data = {
    labels,
    datasets: [{
      label: "mg/L",
      data: values,
      backgroundColor: "rgba(14,165,164,0.2)",
      borderColor: "rgba(14,165,164,1)",
      pointBackgroundColor: "rgba(14,165,164,1)"
    }]
  };
  const maxVal = Math.max(...values, 50);
  const suggestedMax = Math.ceil(maxVal / 10) * 10 + 10;
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false }
    },
    scales: {
      r: {
        beginAtZero: true,
        suggestedMax,
        ticks: { backdropColor: 'transparent', color: '#475569' },
        pointLabels: { color: '#0f172a', font: { weight: 600 } }
      }
    }
  };

  return (
    <div style={{ height: 260 }} className="card">
      <Radar data={data} options={options} />
    </div>
  );
}
