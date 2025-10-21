/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // InspireNest Brand Colors - Beige & Vibrant
        beige: {
          50: '#fdfaf6',
          100: '#f9f4ed',
          200: '#f3e8d9',
          300: '#ecdcc5',
          400: '#e0c9a6',
          500: '#d4b687',
          600: '#c8a368',
          700: '#a5864e',
          800: '#826a3e',
          900: '#5f4d2d',
        },
      },
    },
  },
  plugins: [],
}

