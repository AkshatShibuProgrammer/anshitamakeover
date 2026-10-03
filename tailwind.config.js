/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    "./components/**/*.{ts,tsx}",
    "./app/**/*.{ts,tsx}",
    "./src/**/*.{ts,tsx}",
    "./django/**/*.{html,js}"
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border, 38 35% 20%))",
        input: "hsl(var(--input, 38 35% 20%))",
        ring: "hsl(var(--ring, 43 74% 49%))",
        background: "hsl(var(--background, 310 40% 3%))",
        foreground: "hsl(var(--foreground, 43 65% 90%))",
        primary: {
          DEFAULT: "hsl(var(--primary, 43 74% 49%))",
          foreground: "hsl(var(--primary-foreground, 310 40% 3%))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted, 310 25% 12%))",
          foreground: "hsl(var(--muted-foreground, 43 25% 65%))",
        },
      },
    },
  },
  plugins: [],
};
