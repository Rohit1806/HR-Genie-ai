import React, { useMemo } from 'react';
import { Box, Typography, alpha } from '@mui/material';
import { TrendingUp, TrendingDown } from '@mui/icons-material';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
} from 'recharts';

interface KPICardProps {
  label: string;
  value: string | number;
  trend_percent?: number;
  trend_direction?: 'up' | 'down';
  icon: React.ReactNode;
  color: string;
  sparklineData?: number[];
}

export const KPICard: React.FC<KPICardProps> = ({
  label,
  value,
  trend_percent,
  trend_direction = 'up',
  icon,
  color,
  sparklineData,
}) => {
  const trendColor = trend_direction === 'up' ? '#22C55E' : '#EF4444';

  const chartData = useMemo(
    () =>
      sparklineData?.map((val, i) => ({ index: i, value: val })) || [],
    [sparklineData]
  );

  return (
    <Box
      sx={{
        position: 'relative',
        background: alpha('#1E293B', 0.7),
        backdropFilter: 'blur(20px)',
        borderRadius: '16px',
        border: '1px solid',
        borderColor: alpha('#334155', 0.5),
        borderLeft: `4px solid ${color}`,
        p: 3,
        overflow: 'hidden',
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        cursor: 'pointer',
        '&:hover': {
          transform: 'translateY(-4px) scale(1.01)',
          boxShadow: `0 20px 40px ${alpha(color, 0.15)}, 0 0 0 1px ${alpha(color, 0.2)}`,
          borderColor: alpha(color, 0.3),
        },
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          right: 0,
          width: '50%',
          height: '100%',
          background: `radial-gradient(circle at top right, ${alpha(color, 0.05)}, transparent 70%)`,
          pointerEvents: 'none',
        },
      }}
    >
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
        <Box
          sx={{
            width: 44,
            height: 44,
            borderRadius: '12px',
            background: alpha(color, 0.12),
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: color,
          }}
        >
          {icon}
        </Box>

        {trend_percent !== undefined && (
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 0.3,
              background: alpha(trendColor, 0.1),
              borderRadius: '8px',
              px: 1,
              py: 0.3,
            }}
          >
            {trend_direction === 'up' ? (
              <TrendingUp sx={{ fontSize: 16, color: trendColor }} />
            ) : (
              <TrendingDown sx={{ fontSize: 16, color: trendColor }} />
            )}
            <Typography
              variant="caption"
              sx={{ color: trendColor, fontWeight: 700, fontSize: '0.75rem' }}
            >
              {trend_percent}%
            </Typography>
          </Box>
        )}
      </Box>

      <Typography
        variant="h4"
        sx={{
          color: '#F8FAFC',
          fontWeight: 800,
          lineHeight: 1.1,
          mb: 0.5,
          fontSize: { xs: '1.5rem', md: '1.75rem' },
        }}
      >
        {value}
      </Typography>

      <Typography
        variant="body2"
        sx={{ color: '#94A3B8', fontWeight: 500, fontSize: '0.8rem' }}
      >
        {label}
      </Typography>

      {/* Sparkline */}
      {sparklineData && sparklineData.length > 0 && (
        <Box
          sx={{
            position: 'absolute',
            bottom: 0,
            right: 0,
            width: '45%',
            height: 40,
            opacity: 0.4,
          }}
        >
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id={`sparkGrad-${label.replace(/\s/g, '')}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={color} stopOpacity={0.6} />
                  <stop offset="100%" stopColor={color} stopOpacity={0} />
                </linearGradient>
              </defs>
              <Area
                type="monotone"
                dataKey="value"
                stroke={color}
                strokeWidth={1.5}
                fill={`url(#sparkGrad-${label.replace(/\s/g, '')})`}
                dot={false}
                isAnimationActive={true}
                animationDuration={1500}
              />
            </AreaChart>
          </ResponsiveContainer>
        </Box>
      )}
    </Box>
  );
};

export default KPICard;
