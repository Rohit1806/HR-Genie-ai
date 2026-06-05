import React from 'react';
import { Box, Typography, Tooltip, alpha, Grid } from '@mui/material';

interface DepartmentRisk {
  department: string;
  risk_score: number;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  headcount: number;
  attrition_rate: number;
}

interface AttritionHeatmapProps {
  data?: DepartmentRisk[];
}

const defaultData: DepartmentRisk[] = [
  { department: 'Engineering', risk_score: 72, risk_level: 'medium', headcount: 120, attrition_rate: 8.5 },
  { department: 'Sales', risk_score: 85, risk_level: 'high', headcount: 85, attrition_rate: 12.3 },
  { department: 'Marketing', risk_score: 45, risk_level: 'low', headcount: 45, attrition_rate: 4.2 },
  { department: 'HR', risk_score: 30, risk_level: 'low', headcount: 30, attrition_rate: 2.1 },
  { department: 'Finance', risk_score: 55, risk_level: 'medium', headcount: 40, attrition_rate: 5.8 },
  { department: 'Operations', risk_score: 68, risk_level: 'medium', headcount: 60, attrition_rate: 7.1 },
  { department: 'Product', risk_score: 42, risk_level: 'low', headcount: 35, attrition_rate: 3.5 },
  { department: 'Support', risk_score: 91, risk_level: 'critical', headcount: 55, attrition_rate: 15.2 },
];

function getRiskColor(riskScore: number): string {
  if (riskScore >= 80) return '#EF4444';
  if (riskScore >= 60) return '#EAB308';
  if (riskScore >= 40) return '#F59E0B';
  return '#22C55E';
}

function getRiskGradient(riskScore: number): string {
  const color = getRiskColor(riskScore);
  return `linear-gradient(135deg, ${alpha(color, 0.15)}, ${alpha(color, 0.05)})`;
}

export const AttritionHeatmap: React.FC<AttritionHeatmapProps> = ({
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
        animation: 'fadeIn 0.6s ease-out 0.2s both',
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
        Attrition Risk Heatmap
      </Typography>
      <Typography
        variant="caption"
        sx={{ color: '#94A3B8', display: 'block', mb: 2 }}
      >
        Department-wise attrition risk assessment
      </Typography>

      <Grid container spacing={1.5}>
        {data.map((dept) => {
          const color = getRiskColor(dept.risk_score);
          return (
            <Grid item xs={6} sm={4} md={3} key={dept.department}>
              <Tooltip
                title={
                  <Box>
                    <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                      {dept.department}
                    </Typography>
                    <Typography variant="caption" sx={{ display: 'block' }}>
                      Risk Score: {dept.risk_score}/100
                    </Typography>
                    <Typography variant="caption" sx={{ display: 'block' }}>
                      Headcount: {dept.headcount}
                    </Typography>
                    <Typography variant="caption" sx={{ display: 'block' }}>
                      Attrition Rate: {dept.attrition_rate}%
                    </Typography>
                  </Box>
                }
                arrow
                componentsProps={{
                  tooltip: {
                    sx: {
                      background: '#1E293B',
                      color: '#F8FAFC',
                      border: '1px solid #334155',
                      borderRadius: '8px',
                      px: 1.5,
                      py: 1,
                      boxShadow: '0 10px 30px rgba(0,0,0,0.3)',
                    },
                  },
                  arrow: { sx: { color: '#1E293B' } },
                }}
              >
                <Box
                  sx={{
                    p: 2,
                    borderRadius: '12px',
                    background: getRiskGradient(dept.risk_score),
                    border: '1px solid',
                    borderColor: alpha(color, 0.2),
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    textAlign: 'center',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      borderColor: alpha(color, 0.4),
                      boxShadow: `0 8px 24px ${alpha(color, 0.15)}`,
                    },
                  }}
                >
                  <Typography
                    variant="caption"
                    sx={{
                      color: '#94A3B8',
                      fontWeight: 500,
                      display: 'block',
                      mb: 0.5,
                      fontSize: '0.7rem',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    {dept.department}
                  </Typography>
                  <Typography
                    variant="h6"
                    sx={{
                      color: color,
                      fontWeight: 800,
                      lineHeight: 1,
                      mb: 0.3,
                    }}
                  >
                    {dept.risk_score}
                  </Typography>
                  <Typography
                    variant="caption"
                    sx={{
                      color: alpha(color, 0.8),
                      fontSize: '0.6rem',
                      fontWeight: 600,
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em',
                    }}
                  >
                    {dept.risk_level}
                  </Typography>
                </Box>
              </Tooltip>
            </Grid>
          );
        })}
      </Grid>

      {/* Legend */}
      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', mt: 2 }}>
        {[
          { label: 'Low', color: '#22C55E' },
          { label: 'Medium', color: '#EAB308' },
          { label: 'High', color: '#F59E0B' },
          { label: 'Critical', color: '#EF4444' },
        ].map((item) => (
          <Box key={item.label} sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <Box
              sx={{
                width: 10,
                height: 10,
                borderRadius: '3px',
                background: item.color,
              }}
            />
            <Typography variant="caption" sx={{ color: '#64748B', fontSize: '0.7rem' }}>
              {item.label}
            </Typography>
          </Box>
        ))}
      </Box>
    </Box>
  );
};

export default AttritionHeatmap;
