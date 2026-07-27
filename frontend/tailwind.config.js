/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: { 50: '#eff6ff', 500: '#3b82f6', 700: '#1d4ed8' },
        critical: { bg: '#fee2e2', text: '#991b1b' },
        high: { bg: '#fed7aa', text: '#9a3412' },
        medium: { bg: '#fef3c7', text: '#92400e' },
        low: { bg: '#d1fae5', text: '#065f46' },
      },
    },
  },
  plugins: [],
};
