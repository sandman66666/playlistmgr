// frontend/tailwind.config.js
const path = require('path');

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: {
    relative: true,
    files: [
      './src/**/*.{js,jsx,ts,tsx}',
      './public/index.html'
    ]
  },
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
  corePlugins: {
    preflight: true,
  }
}