import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
  LabelList,
} from 'recharts';
import { Box, Typography, alpha } from '@mui/material';

interface HiringFunnelProps {
  data?: { stage: string; count: number; conversion: number }[];
}

const defaultData = [
  { stage: 'Applied', count: 450, conversion: 100 },
  { stage: 'AI Screening', count: 320, conversion: 71 },
  { stage: 'Shortlisted', count: 180, conversion: 56 },
  { stage: 'Interview', count: 95, conversion: 53 },
  { stage: 'Offered', count: 32, conversion: 34 },
  { stage: 'Hired', count: 24, conversion: 75 },
];

const COLORS = ['#8B5CF6', '#7C3AED', '#6D28D9', '#5B21B6', '#4C1D95', '#3B0764'];

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{ payload: { stage: string; count: number; conversion: number } }>;
}

const CustomTooltip: React.FC<CustomTooltipProps> = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
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
          {data.stage}
        </Typography>
        <Typography variant="body2" sx={{ color: '#F8FAFC', fontWeight: 700 }}>
          {data.count} candidates
        </Typography>
        <Typography variant="caption" sx={{ color: '#8B5CF6', fontWeight: 600 }}>
          {data.conversion}% conversion
        </Typography>
      </Box>
    );
  }
  return null;
};

export const HiringFunnel: React.FC<HiringFunnelProps> = ({
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
        Hiring Funnel
      </Typography>
      <Typography
        variant="caption"
        sx={{ color: '#94A3B8', display: 'block', mb: 2 }}
      >
        Candidate progression through stages
      </Typography>

      <Box sx={{ width: '100%', height: 300 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            layout="vertical"
            margin={{ top: 5, right: 60, left: 10, bottom: 5 }}
          >
            <XAxis
              type="number"
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#64748B', fontSize: 12 }}
            />
            <YAxis
              type="category"
              dataKey="stage"
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#94A3B8', fontSize: 12, fontWeight: 500 }}
              width={100}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: alpha('#8B5CF6', 0.04) }} />
            <Bar
              dataKey="count"
              radius={[0, 8, 8, 0]}
              barSize={28}
              animationDuration={1500}
              animationEasing="ease-out"
            >
              {data.map((_, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={COLORS[index % COLORS.length]}
                  style={{
                    filter: `drop-shadow(0 2px 8px ${COLORS[index % COLORS.length]}30)`,
                  }}
                />
              ))}
              <LabelList
                dataKey="conversion"
                position="right"
                formatter={(val: number) => `${val}%`}
                style={{
                  fill: '#94A3B8',
                  fontSize: 11,
                  fontWeight: 600,
                }}
              />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </Box>
    </Box>
  );
};

export default HiringFunnel;
