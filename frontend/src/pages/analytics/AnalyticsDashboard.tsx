import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  TextField,
  MenuItem,
  CircularProgress,
  alpha,
} from '@mui/material';
import {
  TrendingUp as TrendIcon,
  People as HeadcountIcon,
  Work as JobsIcon,
  MonetizationOn as PayoutIcon,
} from '@mui/icons-material';
import PageHeader from '@/components/ui/PageHeader';
import HeadcountTrend from '@/components/charts/HeadcountTrend';
import DeptPieChart from '@/components/charts/DeptPieChart';
import HiringFunnel from '@/components/charts/HiringFunnel';
import AttritionHeatmap from '@/components/charts/AttritionHeatmap';
import PerformanceBell from '@/components/charts/PerformanceBell';
import { analyticsApi } from '@/api/analytics.api';

// Pre-seeded fallback mock stats in case API returns empty
const defaultStats = {
  headcount: 148,
  activeOpenings: 12,
  payout: '₹12,45,000',
  attritionRate: '4.2%',
};

export default function AnalyticsDashboard() {
  const [timeRange, setTimeRange] = useState('12m');

  // Query general analytics overview stats
  const { data: analyticsOverview, isLoading } = useQuery({
    queryKey: ['analytics-overview', timeRange],
    queryFn: () => analyticsApi.getOverviewMetrics(),
  });

  return (
    <Box>
      <PageHeader
        title="Analytics Dashboard"
        subtitle="Gain data-backed organizational insights using interactive charts and key predictive metrics."
      />

      {/* Select Timeframe Filter */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'flex-end' }}>
        <TextField
          select
          size="small"
          label="Timeframe"
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value)}
          sx={{ minWidth: 160, background: alpha('#1E293B', 0.6), borderRadius: '8px' }}
        >
          <MenuItem value="3m">Last 3 Months</MenuItem>
          <MenuItem value="6m">Last 6 Months</MenuItem>
          <MenuItem value="12m">Last 12 Months</MenuItem>
          <MenuItem value="ytd">Year to Date (YTD)</MenuItem>
        </TextField>
      </Box>

      {/* KPI Cards Row */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {[
          { label: 'Total Headcount', value: analyticsOverview?.headcount || defaultStats.headcount, icon: <HeadcountIcon sx={{ color: '#8B5CF6' }} /> },
          { label: 'Active Job Openings', value: defaultStats.activeOpenings, icon: <JobsIcon sx={{ color: '#3B82F6' }} /> },
          { label: 'Monthly Payroll Payout', value: defaultStats.payout, icon: <PayoutIcon sx={{ color: '#10B981' }} /> },
          { label: 'Annual Attrition Risk', value: defaultStats.attritionRate, icon: <TrendIcon sx={{ color: '#EF4444' }} /> },
        ].map((stat, idx) => (
          <Grid item xs={12} sm={6} md={3} key={idx}>
            <Card
              sx={{
                background: 'linear-gradient(135deg, #1E293B, #0F172A)',
                border: '1px solid #334155',
                borderRadius: '16px',
                position: 'relative',
              }}
            >
              <CardContent sx={{ p: 3, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="caption" color="text.secondary" fontWeight={600}>
                    {stat.label}
                  </Typography>
                  <Typography variant="h4" fontWeight={800} sx={{ color: '#F8FAFC', mt: 0.5 }}>
                    {stat.value}
                  </Typography>
                </Box>
                <Box
                  sx={{
                    p: 1.5,
                    borderRadius: '12px',
                    bgcolor: alpha('#1E293B', 0.8),
                    border: '1px solid #334155',
                    display: 'flex',
                  }}
                >
                  {stat.icon}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Interactive Charts Grid */}
      <Grid container spacing={3}>
        {/* Headcount Trend */}
        <Grid item xs={12} md={8}>
          <Card sx={{ background: '#1E293B', border: '1px solid #334155', borderRadius: '16px', p: 2 }}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={700} sx={{ color: '#F8FAFC', mb: 2 }}>
                Organizational Growth & Headcount Trend
              </Typography>
              <HeadcountTrend />
            </CardContent>
          </Card>
        </Grid>

        {/* Department Distribution */}
        <Grid item xs={12} md={4}>
          <Card sx={{ background: '#1E293B', border: '1px solid #334155', borderRadius: '16px', p: 2 }}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={700} sx={{ color: '#F8FAFC', mb: 2 }}>
                Department Distribution
              </Typography>
              <DeptPieChart />
            </CardContent>
          </Card>
        </Grid>

        {/* Hiring Funnel */}
        <Grid item xs={12} md={6}>
          <Card sx={{ background: '#1E293B', border: '1px solid #334155', borderRadius: '16px', p: 2 }}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={700} sx={{ color: '#F8FAFC', mb: 2 }}>
                Recruitment Funnel & Candidate Conversion
              </Typography>
              <HiringFunnel />
            </CardContent>
          </Card>
        </Grid>

        {/* Performance Curve */}
        <Grid item xs={12} md={6}>
          <Card sx={{ background: '#1E293B', border: '1px solid #334155', borderRadius: '16px', p: 2 }}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={700} sx={{ color: '#F8FAFC', mb: 2 }}>
                Performance Review Bell Curve distribution
              </Typography>
              <PerformanceBell />
            </CardContent>
          </Card>
        </Grid>

        {/* Attrition Risk Heatmap */}
        <Grid item xs={12}>
          <Card sx={{ background: '#1E293B', border: '1px solid #334155', borderRadius: '16px', p: 2 }}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={700} sx={{ color: '#F8FAFC', mb: 2 }}>
                Employee Retention Heatmap & Attrition Warning Indicators
              </Typography>
              <AttritionHeatmap />
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
