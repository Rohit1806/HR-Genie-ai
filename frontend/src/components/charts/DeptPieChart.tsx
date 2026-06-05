import React from 'react';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
} from 'recharts';
import { Box, Typography, alpha } from '@mui/material';

interface DeptPieChartProps {
  data?: { name: string; value: number }[];
}

const COLORS = ['#8B5CF6', '#6366F1', '#3B82F6', '#06B6D4', '#14B8A6', '#10B981'];

const defaultData = [
  { name: 'Engineering', value: 120 },
  { name: 'Sales', value: 85 },
  { name: 'Marketing', value: 45 },
  { name: 'HR', value: 30 },
  { name: 'Finance', value: 40 },
  { name: 'Operations', value: 60 },
];

interface CustomLabelProps {
  cx: number;
  cy: number;
  midAngle: number;
  innerRadius: number;
  outerRadius: number;
  name: string;
  value: number;
  percent: number;
}

const renderCustomLabel = ({
  cx,
  cy,
  midAngle,
  innerRadius,
  outerRadius,
  name,
  value,
}: CustomLabelProps) => {
  const RADIAN = Math.PI / 180;
  const radius = outerRadius + 25;
  const x = cx + radius * Math.cos(-midAngle * RADIAN);
  const y = cy + radius * Math.sin(-midAngle * RADIAN);

  return (
    <text
      x={x}
      y={y}
      fill="#94A3B8"
      textAnchor={x > cx ? 'start' : 'end'}
      dominantBaseline="central"
      fontSize={11}
      fontWeight={500}
    >
      {`${name} (${value})`}
    </text>
  );
};

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{ name: string; value: number; payload: { name: string; value: number } }>;
}

const CustomTooltip: React.FC<CustomTooltipProps> = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const data = payload[0];
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
          {data.payload.name}
        </Typography>
        <Typography variant="body2" sx={{ color: '#F8FAFC', fontWeight: 700 }}>
          {data.value} employees
        </Typography>
      </Box>
    );
  }
  return null;
};

export const DeptPieChart: React.FC<DeptPieChartProps> = ({
  data = defaultData,
}) => {
  const total = data.reduce((sum, item) => sum + item.value, 0);

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
        animation: 'fadeIn 0.6s ease-out 0.1s both',
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
        Department Distribution
      </Typography>
      <Typography
        variant="caption"
        sx={{ color: '#94A3B8', display: 'block', mb: 1 }}
      >
        Workforce by department
      </Typography>

      <Box sx={{ width: '100%', height: 280, position: 'relative' }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={55}
              outerRadius={85}
              paddingAngle={3}
              dataKey="value"
              stroke="none"
              animationDuration={1500}
              animationEasing="ease-out"
              label={renderCustomLabel}
              labelLine={{
                stroke: '#475569',
                strokeWidth: 1,
                strokeDasharray: '3 3',
              }}
            >
              {data.map((_, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={COLORS[index % COLORS.length]}
                  style={{
                    filter: `drop-shadow(0 0 8px ${COLORS[index % COLORS.length]}40)`,
                  }}
                />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        </ResponsiveContainer>

        {/* Center Total */}
        <Box
          sx={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            textAlign: 'center',
          }}
        >
          <Typography
            variant="h5"
            sx={{ color: '#F8FAFC', fontWeight: 800, lineHeight: 1 }}
          >
            {total}
          </Typography>
          <Typography variant="caption" sx={{ color: '#64748B', fontSize: '0.65rem' }}>
            Total
          </Typography>
        </Box>
      </Box>

      {/* Legend */}
      <Box
        sx={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: 1.5,
          justifyContent: 'center',
          mt: 1,
        }}
      >
        {data.map((item, index) => (
          <Box key={item.name} sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <Box
              sx={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                background: COLORS[index % COLORS.length],
              }}
            />
            <Typography variant="caption" sx={{ color: '#94A3B8', fontSize: '0.7rem' }}>
              {item.name}
            </Typography>
          </Box>
        ))}
      </Box>
    </Box>
  );
};

export default DeptPieChart;
