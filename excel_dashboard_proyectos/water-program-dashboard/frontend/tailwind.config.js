/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#EEF4FB',
          100: '#D9E6F2',
          200: '#B3CEE5',
          300: '#8DB6D8',
          400: '#679ECB',
          500: '#4472C4',
          600: '#365B9D',
          700: '#284476',
          800: '#1B2D4F',
          900: '#0D1627',
        },
        galapagos: {
          blue: '#1F3864',
          light: '#2E75B6',
          accent: '#F79646',
          green: '#5287936',
          red: '#C0504D',
        }
      },
    },
  },
  plugins: [],
}
