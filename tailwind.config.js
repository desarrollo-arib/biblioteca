/** @type {import('tailwindcss').Config} */
// tailwind.config.js

module.exports = {
  content: [
    './templates/**/*.html',
    // Otras rutas si es necesario
  ],
  theme: {
    extend: {
      backgroundImage: theme => ({
        'login-bg': "url('https://df5kbf1hky40.cloudfront.net/media/library_center/login/2019/03/20190326170836.jpg)",
      }),
      colors: {
        primary: '#1E3A8A',
        secondary: '#2563EB',
        accent: '#F59E0B',
        emphasis: '#10B981',
        warning: '#EF4444',
        'bg-light': '#F9FAFB',
        'bg-dark': '#111827',
      },
    },
  },
  plugins: [],
}
