import React from 'react';
import { useAuthStore } from '@/store/authStore';
import { Box, CircularProgress, Typography } from '@mui/material';

import AdminDashboard from './AdminDashboard';
import ManagerDashboard from './ManagerDashboard';
import HRDashboard from './HRDashboard';
import EmployeeDashboard from './EmployeeDashboard';

export default function DashboardRouter() {
  const user = useAuthStore((s) => s.user);
  const role = user?.role;

  if (!user) {
    return (
      <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" height="60vh" gap={2}>
        <CircularProgress />
        <Typography variant="body1" color="text.secondary">
          Loading your personalized dashboard...
        </Typography>
      </Box>
    );
  }

  switch (role) {
    case 'admin':
      return <AdminDashboard />;
    case 'senior_manager':
      return <ManagerDashboard />;
    case 'hr_recruiter':
      return <HRDashboard />;
    case 'employee':
      return <EmployeeDashboard />;
    default:
      // Fallback to employee dashboard
      return <EmployeeDashboard />;
  }
}
