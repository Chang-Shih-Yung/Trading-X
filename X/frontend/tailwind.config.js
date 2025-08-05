/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'trading': {
          'primary': '#1a1a2e',
          'secondary': '#16213e',
          'accent': '#0f4c75',
          'success': '#10b981',
          'warning': '#f59e0b',
          'danger': '#ef4444',
          'critical': '#dc2626',
          'high': '#f97316',
          'medium': '#3b82f6',
          'low': '#6b7280'
        }
      },
      animation: {
        'pulse-slow': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-slow': 'bounce 1s infinite',
        'flash': 'flash 1s infinite'
      },
      keyframes: {
        flash: {
          '0%, 100%': { backgroundColor: 'rgba(239, 68, 68, 0.1)' },
          '50%': { backgroundColor: 'rgba(239, 68, 68, 0.3)' }
        }
      }
    },
  },
  plugins: [],
}
