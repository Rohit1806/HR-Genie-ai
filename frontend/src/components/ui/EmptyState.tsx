import React from 'react';
import { Box, Typography, alpha } from '@mui/material';

interface EmptyStateProps {
  icon: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  action,
}) => {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        py: 8,
        px: 4,
        animation: 'emptyFadeIn 0.6s ease-out',
        '@keyframes emptyFadeIn': {
          from: { opacity: 0, transform: 'scale(0.95)' },
          to: { opacity: 1, transform: 'scale(1)' },
        },
      }}
    >
      <Box
        sx={{
          width: 96,
          height: 96,
          borderRadius: '24px',
          background: alpha('#334155', 0.3),
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          mb: 3,
          color: '#475569',
          '& .MuiSvgIcon-root': {
            fontSize: 48,
          },
        }}
      >
        {icon}
      </Box>

      <Typography
        variant="h6"
        sx={{
          color: '#94A3B8',
          fontWeight: 600,
          mb: 1,
          textAlign: 'center',
        }}
      >
        {title}
      </Typography>

      {description && (
        <Typography
          variant="body2"
          sx={{
            color: '#64748B',
            textAlign: 'center',
            maxWidth: 360,
            lineHeight: 1.6,
            mb: action ? 3 : 0,
          }}
        >
          {description}
        </Typography>
      )}

      {action && <Box>{action}</Box>}
    </Box>
  );
};

export default EmptyState;
