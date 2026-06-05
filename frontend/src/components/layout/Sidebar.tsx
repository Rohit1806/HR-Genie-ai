import { useLocation, useNavigate } from 'react-router-dom';
import {
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  Divider,
  Tooltip,
  IconButton,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  Work as RecruitmentIcon,
  AccessTime as AttendanceIcon,
  EventNote as LeavesIcon,
  AccountBalance as PayrollIcon,
  TrendingUp as PerformanceIcon,
  Analytics as AnalyticsIcon,
  Settings as SettingsIcon,
  AutoAwesome as AIIcon,
  Logout as LogoutIcon,
} from '@mui/icons-material';
import { useLogout } from '@/hooks/useAuth';

interface SidebarProps {
  collapsed: boolean;
  onToggleCollapse: () => void;
}

interface NavItem {
  label: string;
  icon: React.ReactNode;
  path: string;
  children?: { label: string; path: string }[];
}

const navItems: NavItem[] = [
  { label: 'Dashboard', icon: <DashboardIcon />, path: '/dashboard' },
  {
    label: 'Employees',
    icon: <PeopleIcon />,
    path: '/employees',
    children: [
      { label: 'Directory', path: '/employees' },
      { label: 'Onboarding', path: '/employees/new' },
    ],
  },
  {
    label: 'Recruitment',
    icon: <RecruitmentIcon />,
    path: '/recruitment',
    children: [
      { label: 'Job Postings', path: '/recruitment' },
    ],
  },
  {
    label: 'Attendance',
    icon: <AttendanceIcon />,
    path: '/attendance',
    children: [
      { label: 'My Attendance', path: '/attendance' },
      { label: 'Team View', path: '/attendance/team' },
    ],
  },
  {
    label: 'Leaves',
    icon: <LeavesIcon />,
    path: '/leaves',
    children: [
      { label: 'My Leaves', path: '/leaves' },
      { label: 'Apply Leave', path: '/leaves/apply' },
      { label: 'Approvals', path: '/leaves/approvals' },
    ],
  },
  {
    label: 'Payroll',
    icon: <PayrollIcon />,
    path: '/payroll',
    children: [
      { label: 'Dashboard', path: '/payroll' },
      { label: 'Payslips', path: '/payroll/payslips' },
    ],
  },
  {
    label: 'Performance',
    icon: <PerformanceIcon />,
    path: '/performance/goals',
    children: [
      { label: 'Goals', path: '/performance/goals' },
      { label: 'Reviews', path: '/performance/reviews' },
      { label: 'AI Insights', path: '/performance/ai-insights' },
    ],
  },
  { label: 'Analytics', icon: <AnalyticsIcon />, path: '/analytics' },
  { label: 'Settings', icon: <SettingsIcon />, path: '/settings' },
];

export default function Sidebar({ collapsed }: SidebarProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const { mutate: logout } = useLogout();

  const isActive = (path: string) => {
    if (path === '/dashboard') return location.pathname === '/dashboard';
    return location.pathname.startsWith(path);
  };

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        bgcolor: 'background.paper',
      }}
    >
      {/* Logo */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1.5,
          px: collapsed ? 1.5 : 2.5,
          py: 2,
          borderBottom: '1px solid',
          borderColor: 'divider',
          justifyContent: collapsed ? 'center' : 'flex-start',
        }}
      >
        <Box
          sx={{
            width: 36,
            height: 36,
            borderRadius: 2,
            background: 'linear-gradient(135deg, #8B5CF6, #6366F1)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
          }}
        >
          <AIIcon sx={{ color: '#fff', fontSize: 22 }} />
        </Box>
        {!collapsed && (
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 800, fontSize: '1.1rem', lineHeight: 1.2 }}>
              HRGenie
            </Typography>
            <Typography variant="caption" sx={{ color: 'text.secondary', fontSize: '0.65rem' }}>
              AI-Powered HR
            </Typography>
          </Box>
        )}
      </Box>

      {/* Navigation */}
      <Box sx={{ flexGrow: 1, overflow: 'auto', py: 1 }}>
        <List disablePadding>
          {navItems.map((item) => {
            const active = isActive(item.path);
            const button = (
              <ListItem key={item.label} disablePadding sx={{ px: 1, mb: 0.25 }}>
                <ListItemButton
                  onClick={() => navigate(item.path)}
                  sx={{
                    borderRadius: 2,
                    minHeight: 44,
                    justifyContent: collapsed ? 'center' : 'initial',
                    px: collapsed ? 1.5 : 2,
                    bgcolor: active ? 'rgba(139, 92, 246, 0.12)' : 'transparent',
                    color: active ? 'primary.main' : 'text.secondary',
                    '&:hover': {
                      bgcolor: active ? 'rgba(139, 92, 246, 0.18)' : 'action.hover',
                    },
                    transition: 'all 0.15s ease',
                  }}
                >
                  <ListItemIcon
                    sx={{
                      minWidth: 0,
                      mr: collapsed ? 0 : 2,
                      justifyContent: 'center',
                      color: active ? 'primary.main' : 'text.secondary',
                    }}
                  >
                    {item.icon}
                  </ListItemIcon>
                  {!collapsed && (
                    <ListItemText
                      primary={item.label}
                      primaryTypographyProps={{
                        fontSize: '0.875rem',
                        fontWeight: active ? 600 : 400,
                      }}
                    />
                  )}
                </ListItemButton>
              </ListItem>
            );

            return collapsed ? (
              <Tooltip key={item.label} title={item.label} placement="right">
                {button}
              </Tooltip>
            ) : (
              button
            );
          })}
        </List>
      </Box>

      {/* Logout */}
      <Divider />
      <Box sx={{ p: 1 }}>
        {collapsed ? (
          <Tooltip title="Logout" placement="right">
            <IconButton onClick={() => logout()} sx={{ color: 'text.secondary', mx: 'auto', display: 'flex' }}>
              <LogoutIcon />
            </IconButton>
          </Tooltip>
        ) : (
          <ListItemButton
            onClick={() => logout()}
            sx={{
              borderRadius: 2,
              color: 'text.secondary',
              '&:hover': { bgcolor: 'rgba(239, 68, 68, 0.1)', color: 'error.main' },
            }}
          >
            <ListItemIcon sx={{ minWidth: 0, mr: 2, color: 'inherit' }}>
              <LogoutIcon />
            </ListItemIcon>
            <ListItemText primary="Logout" primaryTypographyProps={{ fontSize: '0.875rem' }} />
          </ListItemButton>
        )}
      </Box>
    </Box>
  );
}
