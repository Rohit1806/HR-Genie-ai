import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts';
import { Box, Typography, alpha } from '@mui/material';

interface PerformanceBellProps {
  data?: { range: string; count: number; curve: number }[];
}

const defaultData = [
  { range: '0-20', count: 8, curve: 10 },
  { range: '20-40', count: 32, curve: 35 },
  { range: '40-60', count: 85, curve: 80 },
  { range: '60-80', count: 120, curve: 115 },
  { range: '80-100', count: 55, curve: 60 },
];

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{ dataKey: string; value: number; payload: { range: string } }>;
}

const CustomTooltip: React.FC<CustomTooltipProps> = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const barData = payload.find((p) => p.dataKey === 'count');
    const range = payload[0]?.payload?.range;
    return (
      <Box
        sx={{
          background: '#1E293B',
          border: '1px solid #334155',
          borderRadius: '10px',
          px: 2,
          py: 1.5,
          boxShadow: '0 10px 30px rgba(0,0,0,0.4)',
        }}
      >
        <Typography variant="caption" sx={{ color: '#94A3B8', fontWeight: 500, display: 'block' }}>
          Score Range: {range}
        </Typography>
        <Typography variant="body2" sx={{ color: '#F8FAFC', fontWeight: 700 }}>
          {barData?.value || 0} employees
        </Typography>
      </Box>
    );
  }
  return null;
};

export const PerformanceBell: React.FC<PerformanceBellProps> = ({
  data = defaultData,
}) => {
  return (
    <Box
      sx={{
        p: 3,
        background: alpha('#1E293B', 0.7),
        backdropFilter: 'blur(20px)',
        borderRadius: '16px',
        border: '1px solid',
        borderColor: alpha('#334155', 0.5),
        height: '100%',
        animation: 'fadeIn 0.6s ease-out',
        '@keyframes fadeIn': {
          from: { opacity: 0, transform: 'translateY(8px)' },
          to: { opacity: 1, transform: 'translateY(0)' },
        },
      }}
    >
      <Typography
        variant="subtitle1"
        sx={{ color: '#F8FAFC', fontWeight: 700, mb: 0.5 }}
      >
        Performance Distribution
      </Typography>
      <Typography
        variant="caption"
        sx={{ color: '#94A3B8', display: 'block', mb: 2 }}
      >
        Score distribution with bell curve overlay
      </Typography>

      <Box sx={{ width: '100%', height: 280 }}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
            <defs>
              <linearGradient id="performBarGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#8B5CF6" stopOpacity={0.8} />
                <stop offset="100%" stopColor="#8B5CF6" stopOpacity={0.3} />
              </linearGradient>
            </defs>
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#334155"
              strokeOpacity={0.3}
              vertical={false}
            />
            <XAxis
              dataKey="range"
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#64748B', fontSize: 12 }}
            />
            <YAxis
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#64748B', fontSize: 12 }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar
              dataKey="count"
              fill="url(#performBarGrad)"
              radius={[6, 6, 0, 0]}
              barSize={50}
              animationDuration={1500}
            />
            <Line
              type="monotone"
              dataKey="curve"
              stroke="#A78BFA"
              strokeWidth={2.5}
              dot={false}
              strokeDasharray="6 3"
              animationDuration={2000}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </Box>
    </Box>
  );
};

export default PerformanceBell;
