import type { Config } from 'tailwindcss';

export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        dark: {
          bg: '#0F172A',
          card: '#1E293B',
          border: '#334155',
          hover: '#475569',
        },
        brand: {
          primary: '#8B5CF6',
          secondary: '#6366F1',
          accent: '#A78BFA',
        },
        score: {
          high: '#22C55E',
          medium: '#EAB308',
          low: '#EF4444',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-in-right': 'slideInRight 0.3s ease-out',
        'pulse-glow': 'pulseGlow 2s infinite',
      },
      keyframes: {
        fadeIn: { '0%': { opacity: '0' }, '100%': { opacity: '1' } },
        slideUp: { '0%': { transform: 'translateY(10px)', opacity: '0' }, '100%': { transform: 'translateY(0)', opacity: '1' } },
        slideInRight: { '0%': { transform: 'translateX(100%)' }, '100%': { transform: 'translateX(0)' } },
        pulseGlow: { '0%, 100%': { boxShadow: '0 0 5px rgba(139,92,246,0.5)' }, '50%': { boxShadow: '0 0 20px rgba(139,92,246,0.8)' } },
      },
    },
  },
  plugins: [],
} satisfies Config;
