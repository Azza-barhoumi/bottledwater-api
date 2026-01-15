import React from 'react';

function Star({ filled, size = 20, label }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill={filled ? 'currentColor' : 'none'}
      stroke="currentColor"
      strokeWidth="1.2"
      aria-hidden={label ? 'false' : 'true'}
      role={label ? 'img' : undefined}
    >
      <title>{label}</title>
      <path d="M12 .587l3.668 7.431L23.6 9.75l-5.8 5.657L19.6 24 12 19.897 4.4 24l1.8-8.593L.4 9.75l7.932-1.732z" />
    </svg>
  );
}

export default function StarRating({ value = 0, onChange = () => {}, size = 24, name }) {
  const stars = [1, 2, 3, 4, 5];

  const handleKey = (e, v) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onChange(v);
    }
    if (e.key === 'ArrowRight' || e.key === 'ArrowUp') {
      e.preventDefault();
      onChange(Math.min(5, value + 1));
    }
    if (e.key === 'ArrowLeft' || e.key === 'ArrowDown') {
      e.preventDefault();
      onChange(Math.max(1, value - 1));
    }
  };

  return (
    <div role="radiogroup" aria-label={name} className="inline-flex items-center gap-1">
      {stars.map((s) => (
        <button
          key={s}
          type="button"
          role="radio"
          aria-checked={value === s}
          aria-label={`${s} star${s > 1 ? 's' : ''}`}
          onClick={() => onChange(s)}
          onKeyDown={(e) => handleKey(e, s)}
          className={`text-xl leading-none ${value >= s ? 'text-yellow-500' : 'text-gray-300'}`}
          style={{ background: 'transparent', border: 'none', padding: 2, cursor: 'pointer' }}
        >
          <Star filled={value >= s} size={size} label={`${s} star`} />
        </button>
      ))}
    </div>
  );
}
