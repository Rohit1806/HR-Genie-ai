import React from 'react';
import { Box, Grid } from '@mui/material';
import PageHeader from '@/components/ui/PageHeader';
import KPICard from '@/components/ui/KPICard';
import PerformanceBell from '@/components/charts/PerformanceBell';
import AttritionHeatmap from '@/components/charts/AttritionHeatmap';
import { Group, AssignmentTurnedIn, TrendingDown, HourglassEmpty } from '@mui/icons-material';

export default function ManagerDashboard() {
  return (
    <Box>
      <PageHeader
        title="Manager Overview"
        subtitle="Track team performance, task completions, and risk metrics."
      />
      
      <Grid container spacing={3} sx={{ mt: 1 }}>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            label="Team Members"
            value="12"
            icon={<Group />}
            trend_percent={9}
            trend_direction="up"
            color="#8B5CF6"
            sparklineData={[11, 11, 11, 11, 11, 12, 12]}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            label="Goals Achieved"
            value="92%"
            icon={<AssignmentTurnedIn />}
            trend_percent={5.5}
            trend_direction="up"
            color="#3B82F6"
            sparklineData={[85, 87, 88, 90, 91, 91.5, 92]}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            label="Team Attrition Risk"
            value="Low"
            icon={<TrendingDown />}
            color="#10B981"
            sparklineData={[15, 12, 10, 8, 5, 4, 3]}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            label="Pending Actions"
            value="3"
            icon={<HourglassEmpty />}
            color="#EF4444"
            sparklineData={[5, 4, 6, 3, 2, 4, 3]}
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <Box sx={{ bgcolor: 'background.paper', p: 3, borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
            <PerformanceBell />
          </Box>
        </Grid>
        <Grid item xs={12} md={6}>
          <Box sx={{ bgcolor: 'background.paper', p: 3, borderRadius: 3, border: '1px solid', borderColor: 'divider' }}>
            <AttritionHeatmap />
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
}
