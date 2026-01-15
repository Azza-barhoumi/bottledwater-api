/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        primary: "#0ea5a4",
        accent: 'var(--accent)',
      },
    },
  },
  plugins: [],
};
