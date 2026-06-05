import React from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';
import { Box, Typography, alpha } from '@mui/material';

interface HeadcountTrendProps {
  data?: { month: string; count: number }[];
}

const defaultData = [
  { month: 'Jan', count: 342 },
  { month: 'Feb', count: 348 },
  { month: 'Mar', count: 355 },
  { month: 'Apr', count: 361 },
  { month: 'May', count: 358 },
  { month: 'Jun', count: 367 },
  { month: 'Jul', count: 372 },
  { month: 'Aug', count: 380 },
  { month: 'Sep', count: 385 },
  { month: 'Oct', count: 392 },
  { month: 'Nov', count: 398 },
  { month: 'Dec', count: 405 },
];

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{ value: number }>;
  label?: string;
}

const CustomTooltip: React.FC<CustomTooltipProps> = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
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
        <Typography variant="caption" sx={{ color: '#94A3B8', fontWeight: 500 }}>
          {label}
        </Typography>
        <Typography variant="body2" sx={{ color: '#F8FAFC', fontWeight: 700 }}>
          {payload[0].value.toLocaleString()} employees
        </Typography>
      </Box>
    );
  }
  return null;
};

export const HeadcountTrend: React.FC<HeadcountTrendProps> = ({
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
        Headcount Trend
      </Typography>
      <Typography
        variant="caption"
        sx={{ color: '#94A3B8', display: 'block', mb: 2 }}
      >
        12-month employee count
      </Typography>

      <Box sx={{ width: '100%', height: 280 }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 5, right: 10, left: -10, bottom: 0 }}>
            <defs>
              <linearGradient id="headcountGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#8B5CF6" stopOpacity={0.4} />
                <stop offset="50%" stopColor="#8B5CF6" stopOpacity={0.1} />
                <stop offset="100%" stopColor="#8B5CF6" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#334155"
              strokeOpacity={0.3}
              vertical={false}
            />
            <XAxis
              dataKey="month"
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#64748B', fontSize: 12 }}
            />
            <YAxis
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#64748B', fontSize: 12 }}
              domain={['dataMin - 20', 'dataMax + 20']}
            />
            <Tooltip content={<CustomTooltip />} />
            <Area
              type="monotone"
              dataKey="count"
              stroke="#8B5CF6"
              strokeWidth={2.5}
              fill="url(#headcountGradient)"
              dot={false}
              activeDot={{
                r: 6,
                fill: '#8B5CF6',
                stroke: '#1E293B',
                strokeWidth: 3,
              }}
              animationDuration={2000}
              animationEasing="ease-out"
            />
          </AreaChart>
        </ResponsiveContainer>
      </Box>
    </Box>
  );
};

export default HeadcountTrend;
