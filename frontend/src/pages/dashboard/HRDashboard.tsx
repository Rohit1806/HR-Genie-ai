import React from 'react';
import { Box, Grid } from '@mui/material';
import PageHeader from '@/components/ui/PageHeader';
import KPICard from '@/components/ui/KPICard';
import HiringFunnel from '@/components/charts/HiringFunnel';
import HeadcountTrend from '@/components/charts/HeadcountTrend';
import { Work, Badge, AssignmentInd, Speed } from '@mui/icons-material';

export default function HRDashboard() {
  return (
    <Box>
      <PageHeader
        title="HR Operations Dashboard"
        subtitle="Track hiring, onboarding, pipeline activity, and workforce composition."
      />
      
      <Grid container spacing={3} sx={{ mt: 1 }}>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            label="Open Jobs"
            value="14"
            icon={<Work />}
            trend_percent={27}
            trend_direction="up"
            color="#8B5CF6"
            sparklineData={[10, 11, 12, 12, 13, 14, 14]}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            label="Candidates Screened"
            value="892"
            icon={<AssignmentInd />}
            trend_percent={14.5}
            trend_direction="up"
            color="#3B82F6"
            sparklineData={[700, 720, 750, 780, 820, 850, 892]}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            label="Onboarding Pending"
            value="8"
            icon={<Badge />}
            color="#10B981"
            sparklineData={[5, 6, 4, 7, 9, 8, 8]}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            label="Avg Time to Hire"
            value="24 Days"
            icon={<Speed />}
            trend_percent={12}
            trend_direction="down"
            color="#EF4444"
            sparklineData={[28, 27, 26, 25, 25, 24, 24]}
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <Box sx={{ bgcolor: 'background.paper', p: 3, borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
            <HiringFunnel />
          </Box>
        </Grid>
        <Grid item xs={12} md={6}>
          <Box sx={{ bgcolor: 'background.paper', p: 3, borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
            <HeadcountTrend />
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
}
