/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './frontend/index.html',
    './frontend/src/**/*.{vue,js}',
  ],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Space Grotesk"', '"Noto Sans SC"', 'sans-serif'],
        body: ['"Noto Sans SC"', '"Space Grotesk"', 'sans-serif'],
      },
      colors: {
        ink: '#15233b',
        mist: '#f4f7fb',
        chat: {
          50: '#ecfeff',
          100: '#cffafe',
          500: '#0891b2',
          700: '#155e75',
        },
        checkin: {
          50: '#fff7ed',
          100: '#ffedd5',
          500: '#f97316',
          700: '#9a3412',
        },
        archive: {
          50: '#eef2ff',
          100: '#e0e7ff',
          500: '#6366f1',
          700: '#4338ca',
        },
        operator: {
          50: '#f5f3ff',
          100: '#ede9fe',
          500: '#7c3aed',
          700: '#5b21b6',
        },
      },
      boxShadow: {
        panel: '0 24px 64px rgba(15, 23, 42, 0.12)',
      },
      backgroundImage: {
        'student-grid': 'radial-gradient(circle at top left, rgba(14,165,233,0.18), transparent 28%), radial-gradient(circle at top right, rgba(99,102,241,0.16), transparent 24%)',
        'teacher-grid': 'radial-gradient(circle at top left, rgba(124,58,237,0.14), transparent 26%), radial-gradient(circle at top right, rgba(249,115,22,0.12), transparent 22%)',
      },
    },
  },
  plugins: [],
};
