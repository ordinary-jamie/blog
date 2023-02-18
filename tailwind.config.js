/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx,html}'],
  theme: {
    extend: {},
    fontFamily: {
      'sans': ['Helvetica', 'Arial', 'sans-serif'],
      'serif': ['Roboto Serif', 'Georgia', 'Times New Roman'],
      'mono': ['Courier', 'Courier New']
    }
  },
  plugins: [],
}
