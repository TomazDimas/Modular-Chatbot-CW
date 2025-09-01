import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#0b0f14",
        card: "#111827",
        ink: "#e5e7eb",
        accent: "#10b981",
        subtle: "#6b7280",
      },
      boxShadow: {
        soft: "0 8px 30px rgba(0,0,0,0.12)",
      },
      borderRadius: {
        xl2: "1rem",
      },
    },
  },
  plugins: [],
} satisfies Config;
