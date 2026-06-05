import React from 'react';
import { Chip, alpha } from '@mui/material';

interface StatusPillProps {
  status: string;
  size?: 'small' | 'medium';
}

const statusColorMap: Record<string, { bg: string; text: string }> = {
  active: { bg: '#22C55E', text: '#22C55E' },
  present: { bg: '#22C55E', text: '#22C55E' },
  approved: { bg: '#22C55E', text: '#22C55E' },
  on_leave: { bg: '#3B82F6', text: '#3B82F6' },
  notice_period: { bg: '#EAB308', text: '#EAB308' },
  late: { bg: '#EAB308', text: '#EAB308' },
  terminated: { bg: '#EF4444', text: '#EF4444' },
  absent: { bg: '#EF4444', text: '#EF4444' },
  rejected: { bg: '#EF4444', text: '#EF4444' },
  pending: { bg: '#F59E0B', text: '#F59E0B' },
  draft: { bg: '#6B7280', text: '#6B7280' },
  open: { bg: '#3B82F6', text: '#3B82F6' },
  closed: { bg: '#6B7280', text: '#6B7280' },
  hired: { bg: '#22C55E', text: '#22C55E' },
  offered: { bg: '#8B5CF6', text: '#8B5CF6' },
  processing: { bg: '#F59E0B', text: '#F59E0B' },
  completed: { bg: '#22C55E', text: '#22C55E' },
  failed: { bg: '#EF4444', text: '#EF4444' },
  on_track: { bg: '#22C55E', text: '#22C55E' },
  at_risk: { bg: '#EAB308', text: '#EAB308' },
  behind: { bg: '#EF4444', text: '#EF4444' },
};

function getStatusColors(status: string): { bg: string; text: string } {
  const normalizedStatus = status.toLowerCase().replace(/[\s-]/g, '_');
  return statusColorMap[normalizedStatus] || { bg: '#6B7280', text: '#6B7280' };
}

function formatStatusLabel(status: string): string {
  return status
    .replace(/_/g, ' ')
    .replace(/-/g, ' ')
    .split(' ')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

export const StatusPill: React.FC<StatusPillProps> = ({ status, size = 'small' }) => {
  const colors = getStatusColors(status);

  return (
    <Chip
      label={formatStatusLabel(status)}
      size={size}
      sx={{
        height: size === 'small' ? 24 : 28,
        fontSize: size === 'small' ? '0.7rem' : '0.8rem',
        fontWeight: 600,
        letterSpacing: '0.02em',
        background: alpha(colors.bg, 0.12),
        color: colors.text,
        border: `1px solid ${alpha(colors.bg, 0.25)}`,
        borderRadius: '20px',
        '& .MuiChip-label': {
          px: size === 'small' ? 1.2 : 1.5,
        },
      }}
    />
  );
};

export default StatusPill;
