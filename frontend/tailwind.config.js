/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#090d16",
        surface: "#111827",
        "surface-card": "#1f2937",
        pms: {
          green: "#10b981",
          yellow: "#f59e0b",
          red: "#f43f5e",
        }
      },
      boxShadow: {
        'glow-green': '0 0 20px -3px rgba(16, 185, 129, 0.4)',
        'glow-yellow': '0 0 20px -3px rgba(245, 158, 11, 0.5)',
        'glow-red': '0 0 20px -3px rgba(244, 63, 94, 0.5)',
      }
    },
  },
  plugins: [],
};
