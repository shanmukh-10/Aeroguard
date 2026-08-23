import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        aqi: {
          good: "#10B981",
          satisfactory: "#84CC16",
          moderate: "#EAB308",
          poor: "#F97316",
          verypoor: "#EF4444",
          severe: "#881337",
          emergency: "#4C0519",
        },
        brand: {
          50: "#f0fdf4",
          100: "#dcfce7",
          500: "#10b981",
          600: "#059669",
          700: "#047857",
          900: "#064e3b",
        }
      },
    },
  },
  plugins: [],
};
export default config;
