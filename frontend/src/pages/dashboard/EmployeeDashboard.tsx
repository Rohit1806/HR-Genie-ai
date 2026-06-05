import React from 'react';
import { Box, Grid, Typography, Card, CardContent } from '@mui/material';
import PageHeader from '@/components/ui/PageHeader';
import KPICard from '@/components/ui/KPICard';
import ScoreGauge from '@/components/ui/ScoreGauge';
import { WorkOutline, EventNote, BeachAccess, TrackChanges } from '@mui/icons-material';

export default function EmployeeDashboard() {
  return (
    <Box>
      <PageHeader
        title="My Dashboard"
        subtitle="Access your personal employment overview, leave balances, and objectives."
      />
      
      <Grid container spacing={3} sx={{ mt: 1 }}>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            label="Leave Balance"
            value="14 Days"
            icon={<BeachAccess />}
            color="#8B5CF6"
            sparklineData={[14, 14, 14, 14, 14, 14, 14]}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            label="Work Hours (This Month)"
            value="164 hrs"
            icon={<WorkOutline />}
            trend_percent={2.1}
            trend_direction="up"
            color="#3B82F6"
            sparklineData={[20, 40, 60, 80, 100, 120, 164]}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            label="Goals in Progress"
            value="4"
            icon={<TrackChanges />}
            color="#10B981"
            sparklineData={[4, 4, 4, 4, 4, 4, 4]}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            label="Regularization Pending"
            value="0"
            icon={<EventNote />}
            color="#EF4444"
            sparklineData={[1, 0, 0, 0, 0, 0, 0]}
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <Card sx={{ bgcolor: 'background.paper', borderRadius: 3, border: '1px solid', borderColor: 'divider', height: '100%' }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight={700} gutterBottom>My Performance Summary</Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
                Your current cycle objectives and manager rating summaries.
              </Typography>
              <Box display="flex" justifyContent="space-around" alignItems="center">
                <Box textAlign="center">
                  <ScoreGauge score={88} size="md" label="Goals Score" />
                </Box>
                <Box textAlign="center">
                  <ScoreGauge score={82} size="md" label="Review Score" />
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card sx={{ bgcolor: 'background.paper', borderRadius: 3, border: '1px solid', borderColor: 'divider', height: '100%' }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight={700} gutterBottom>Upcoming Holidays</Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Plan your leave around the upcoming company-wide holidays.
              </Typography>
              <Box display="flex" flexDirection="column" gap={2}>
                {[
                  { name: 'Independence Day', date: 'August 15, 2026', type: 'Compulsory' },
                  { name: 'Ganesh Chaturthi', date: 'September 15, 2026', type: 'Optional' },
                  { name: 'Gandhi Jayanti', date: 'October 2, 2026', type: 'Compulsory' },
                ].map((holiday) => (
                  <Box key={holiday.name} display="flex" justifyContent="space-between" alignItems="center" p={1.5} sx={{ bgcolor: 'action.hover', borderRadius: 2 }}>
                    <Box>
                      <Typography variant="subtitle2" fontWeight={600}>{holiday.name}</Typography>
                      <Typography variant="caption" color="text.secondary">{holiday.date}</Typography>
                    </Box>
                    <Typography variant="caption" fontWeight={700} color={holiday.type === 'Compulsory' ? 'primary' : 'secondary'}>
                      {holiday.type}
                    </Typography>
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
