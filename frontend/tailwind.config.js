/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        navy: {
          950: '#060B18',
          900: '#0B132B',
          800: '#152238',
          700: '#1C2D4A',
          600: '#283E63',
        },
        accent: {
          blue: '#2563EB',
          cyan: '#06B6D4',
          emerald: '#10B981',
          rose: '#EF4444',
          amber: '#F59E0B',
        }
      }
    },
  },
  plugins: [],
}
