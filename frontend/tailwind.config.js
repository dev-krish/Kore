/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#080c14",
        surface: "#0f172a",
        "surface-card": "#131d35",
        "surface-hover": "#1e293b",
        border: "#1e293b",
        "border-glow": "#3b82f6",
        primary: {
          DEFAULT: "#3b82f6",
          hover: "#2563eb",
          foreground: "#ffffff",
        },
        accent: {
          DEFAULT: "#8b5cf6",
          hover: "#7c3aed",
          foreground: "#ffffff",
        },
        muted: "#94a3b8",
        success: "#10b981",
        warning: "#f59e0b",
        destructive: "#ef4444",
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      boxShadow: {
        card: "0 4px 20px -2px rgba(0, 0, 0, 0.5)",
        glow: "0 0 25px -5px rgba(59, 130, 246, 0.25)",
      },
    },
  },
  plugins: [],
};
