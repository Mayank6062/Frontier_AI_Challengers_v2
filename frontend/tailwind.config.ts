import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#F8FAFC",
        primary: {
          DEFAULT: "#2563EB",
          foreground: "#FFFFFF",
        },
        success: {
          DEFAULT: "#22C55E",
        },
        warning: {
          DEFAULT: "#F59E0B",
        },
        danger: {
          DEFAULT: "#EF4444",
        },
        card: "#FFFFFF",
      },
      boxShadow: {
        enterprise: "0 18px 40px rgba(15, 23, 42, 0.08)",
      },
    },
  },
  plugins: [],
};

export default config;
