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
        graphite: {
          950: '#0a0c10',
          900: '#11141a',
          850: '#161a22',
          800: '#1e232d',
          750: '#252b37',
          700: '#2e3543',
          600: '#40495c',
          500: '#5a657d',
        },
        crimson: {
          950: '#2b040d',
          900: '#4c0519',
          800: '#881337',
          700: '#be123c',
          600: '#e11d48',
          500: '#f43f5e',
          400: '#fb7185',
        },
        status: {
          allowed: '#10b981',
          rejected: '#e11d48',
          warning: '#f59e0b',
        }
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
      }
    },
  },
  plugins: [],
}
