import { createTheme } from '@mui/material/styles';

export const muiTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#8B5CF6', light: '#A78BFA', dark: '#7C3AED' },
    secondary: { main: '#6366F1' },
    background: { default: '#0F172A', paper: '#1E293B' },
    text: { primary: '#F8FAFC', secondary: '#94A3B8' },
    divider: '#334155',
    success: { main: '#22C55E' },
    warning: { main: '#EAB308' },
    error: { main: '#EF4444' },
    info: { main: '#3B82F6' },
  },
  typography: {
    fontFamily: '"Inter", system-ui, -apple-system, sans-serif',
    h1: { fontWeight: 800, fontSize: '2.5rem', letterSpacing: '-0.02em' },
    h2: { fontWeight: 700, fontSize: '2rem', letterSpacing: '-0.01em' },
    h3: { fontWeight: 700, fontSize: '1.5rem' },
    h4: { fontWeight: 600, fontSize: '1.25rem' },
    h5: { fontWeight: 600, fontSize: '1.1rem' },
    h6: { fontWeight: 600, fontSize: '1rem' },
    body1: { fontSize: '0.9375rem', lineHeight: 1.6 },
    body2: { fontSize: '0.875rem', lineHeight: 1.5 },
    button: { textTransform: 'none', fontWeight: 600 },
  },
  shape: { borderRadius: 12 },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          padding: '8px 20px',
          fontSize: '0.875rem',
          transition: 'all 0.2s ease',
        },
        contained: {
          boxShadow: '0 4px 14px rgba(139, 92, 246, 0.3)',
          '&:hover': {
            boxShadow: '0 6px 20px rgba(139, 92, 246, 0.4)',
            transform: 'translateY(-1px)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          background: '#1E293B',
          border: '1px solid #334155',
          borderRadius: 16,
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
          transition: 'all 0.2s ease',
          '&:hover': {
            borderColor: '#475569',
            boxShadow: '0 8px 25px rgba(0, 0, 0, 0.2)',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 10,
            '& fieldset': { borderColor: '#334155' },
            '&:hover fieldset': { borderColor: '#475569' },
            '&.Mui-focused fieldset': { borderColor: '#8B5CF6' },
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          fontWeight: 500,
        },
      },
    },
    // @ts-ignore
    MuiDataGrid: {
      styleOverrides: {
        root: {
          border: '1px solid #334155',
          borderRadius: 12,
          '& .MuiDataGrid-cell': { borderBottom: '1px solid #1E293B' },
          '& .MuiDataGrid-columnHeaders': {
            backgroundColor: '#0F172A',
            borderBottom: '1px solid #334155',
          },
          '& .MuiDataGrid-row:hover': {
            backgroundColor: 'rgba(139, 92, 246, 0.05)',
          },
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          background: '#1E293B',
          borderRight: '1px solid #334155',
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          background: '#1E293B',
          border: '1px solid #334155',
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          borderBottom: '1px solid #334155',
        },
      },
    },
    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          backgroundColor: '#334155',
          fontSize: '0.8125rem',
          borderRadius: 8,
        },
      },
    },
  },
});
