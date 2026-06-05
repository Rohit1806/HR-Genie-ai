import React from 'react';
import { Box, Grid } from '@mui/material';
import PageHeader from '@/components/ui/PageHeader';
import KPICard from '@/components/ui/KPICard';
import HeadcountTrend from '@/components/charts/HeadcountTrend';
import DeptPieChart from '@/components/charts/DeptPieChart';
import AttritionHeatmap from '@/components/charts/AttritionHeatmap';
import { People, Apartment, TrendingUp, Engineering } from '@mui/icons-material';

export default function AdminDashboard() {
  return (
    <Box>
      <PageHeader
        title="Admin Control Center"
        subtitle="Full organizational overview, system status, and cross-department metrics."
      />
      
      <Grid container spacing={3} sx={{ mt: 1 }}>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            label="Total Employees"
            value="142"
            icon={<People />}
            trend_percent={12}
            trend_direction="up"
            color="#8B5CF6"
            sparklineData={[120, 122, 125, 130, 135, 140, 142]}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            label="Active Departments"
            value="8"
            icon={<Apartment />}
            trend_percent={0}
            trend_direction="up"
            color="#3B82F6"
            sparklineData={[8, 8, 8, 8, 8, 8, 8]}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            label="Avg Performance"
            value="84.2%"
            icon={<TrendingUp />}
            trend_percent={2.4}
            trend_direction="up"
            color="#10B981"
            sparklineData={[81, 82, 82.5, 83, 83.8, 84, 84.2]}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            label="System Load"
            value="Minimal"
            icon={<Engineering />}
            color="#EF4444"
            sparklineData={[2, 5, 4, 10, 8, 3, 2]}
          />
        </Grid>

        <Grid item xs={12} md={8}>
          <Box sx={{ bgcolor: 'background.paper', p: 3, borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
            <HeadcountTrend />
          </Box>
        </Grid>
        <Grid item xs={12} md={4}>
          <Box sx={{ bgcolor: 'background.paper', p: 3, borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
            <DeptPieChart />
          </Box>
        </Grid>

        <Grid item xs={12}>
          <Box sx={{ bgcolor: 'background.paper', p: 3, borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
            <AttritionHeatmap />
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
}
