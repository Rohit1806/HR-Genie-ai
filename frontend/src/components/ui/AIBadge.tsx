import React from 'react';
import { Chip, Tooltip, alpha, keyframes } from '@mui/material';
import { AutoAwesome as AutoAwesomeIcon } from '@mui/icons-material';

interface AIBadgeProps {
  label: string;
  tooltip?: string;
}

const pulseGlow = keyframes`
  0% {
    box-shadow: 0 0 0 0 rgba(139, 92, 246, 0.4);
  }
  50% {
    box-shadow: 0 0 12px 4px rgba(139, 92, 246, 0.15);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(139, 92, 246, 0);
  }
`;

export const AIBadge: React.FC<AIBadgeProps> = ({
  label,
  tooltip = 'AI-powered insight',
}) => {
  return (
    <Tooltip
      title={tooltip}
      arrow
      placement="top"
      componentsProps={{
        tooltip: {
          sx: {
            background: '#1E293B',
            color: '#F8FAFC',
            border: '1px solid #334155',
            borderRadius: '8px',
            fontSize: '0.75rem',
            px: 1.5,
            py: 1,
            maxWidth: 280,
            boxShadow: '0 10px 30px rgba(0,0,0,0.3)',
          },
        },
        arrow: {
          sx: {
            color: '#1E293B',
            '&::before': {
              border: '1px solid #334155',
            },
          },
        },
      }}
    >
      <Chip
        icon={<AutoAwesomeIcon sx={{ fontSize: '14px !important', color: '#A78BFA !important' }} />}
        label={label}
        size="small"
        sx={{
          height: 26,
          fontSize: '0.72rem',
          fontWeight: 600,
          background: `linear-gradient(135deg, ${alpha('#8B5CF6', 0.15)}, ${alpha('#6D28D9', 0.15)})`,
          color: '#A78BFA',
          border: `1px solid ${alpha('#8B5CF6', 0.3)}`,
          borderRadius: '20px',
          animation: `${pulseGlow} 3s ease-in-out infinite`,
          cursor: 'pointer',
          transition: 'all 0.2s ease',
          '&:hover': {
            background: `linear-gradient(135deg, ${alpha('#8B5CF6', 0.25)}, ${alpha('#6D28D9', 0.25)})`,
            borderColor: alpha('#8B5CF6', 0.5),
            transform: 'scale(1.05)',
          },
          '& .MuiChip-label': {
            px: 1,
          },
        }}
      />
    </Tooltip>
  );
};

export default AIBadge;
