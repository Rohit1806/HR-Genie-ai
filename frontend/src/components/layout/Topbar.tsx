import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Box,
  AppBar,
  Toolbar,
  IconButton,
  InputBase,
  Badge,
  Avatar,
  Typography,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Tooltip,
  alpha,
  Breadcrumbs,
  Link,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Search as SearchIcon,
  Notifications as NotificationsIcon,
  Psychology as PsychologyIcon,
  Person as PersonIcon,
  Settings as SettingsIcon,
  Logout as LogoutIcon,
  NavigateNext as NavigateNextIcon,
} from '@mui/icons-material';

interface TopbarProps {
  sidebarWidth: number;
  onMenuClick: () => void;
  onNotificationsClick: () => void;
}

const breadcrumbMap: Record<string, string> = {
  dashboard: 'Dashboard',
  employees: 'Employees',
  recruitment: 'Recruitment',
  attendance: 'Attendance',
  leaves: 'Leaves',
  payroll: 'Payroll',
  performance: 'Performance',
  analytics: 'Analytics',
  settings: 'Settings',
  profile: 'Profile',
  apply: 'Apply Leave',
  approvals: 'Approvals',
  goals: 'Goals',
  reviews: 'Reviews',
  insights: 'AI Insights',
  onboarding: 'Onboarding',
  pipeline: 'Pipeline',
  postings: 'Job Postings',
  payslips: 'Payslips',
};

export const Topbar: React.FC<TopbarProps> = ({
  sidebarWidth,
  onMenuClick,
  onNotificationsClick,
}) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [searchFocused, setSearchFocused] = useState(false);

  const pathSegments = location.pathname.split('/').filter(Boolean);

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  return (
    <>
      <AppBar
        position="fixed"
        elevation={0}
        sx={{
          left: sidebarWidth,
          width: `calc(100% - ${sidebarWidth}px)`,
          height: 64,
          transition: 'left 0.3s cubic-bezier(0.4, 0, 0.2, 1), width 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          background: alpha('#1E293B', 0.8),
          backdropFilter: 'blur(20px)',
          borderBottom: '1px solid',
          borderColor: alpha('#334155', 0.5),
          '@media (max-width: 900px)': {
            left: 0,
            width: '100%',
          },
        }}
      >
        <Toolbar
          sx={{
            height: 64,
            minHeight: '64px !important',
            px: { xs: 1.5, md: 3 },
            gap: 2,
          }}
        >
          {/* Menu Button (Mobile) */}
          <IconButton
            onClick={onMenuClick}
            sx={{
              display: { md: 'none' },
              color: '#94A3B8',
              '&:hover': { color: '#F8FAFC' },
            }}
          >
            <MenuIcon />
          </IconButton>

          {/* Breadcrumb */}
          <Breadcrumbs
            separator={<NavigateNextIcon sx={{ fontSize: 16, color: '#475569' }} />}
            sx={{
              flex: '0 0 auto',
              '& .MuiBreadcrumbs-li': { lineHeight: 1 },
            }}
          >
            {pathSegments.map((segment, index) => {
              const path = '/' + pathSegments.slice(0, index + 1).join('/');
              const label = breadcrumbMap[segment] || segment.charAt(0).toUpperCase() + segment.slice(1);
              const isLast = index === pathSegments.length - 1;

              return isLast ? (
                <Typography
                  key={path}
                  variant="body2"
                  sx={{ color: '#F8FAFC', fontWeight: 600, fontSize: '0.875rem' }}
                >
                  {label}
                </Typography>
              ) : (
                <Link
                  key={path}
                  onClick={() => navigate(path)}
                  underline="hover"
                  sx={{
                    color: '#94A3B8',
                    fontSize: '0.875rem',
                    cursor: 'pointer',
                    '&:hover': { color: '#8B5CF6' },
                  }}
                >
                  {label}
                </Link>
              );
            })}
          </Breadcrumbs>

          {/* Spacer */}
          <Box sx={{ flex: 1 }} />

          {/* Search */}
          <Box
            sx={{
              alignItems: 'center',
              background: searchFocused ? alpha('#334155', 0.8) : alpha('#334155', 0.4),
              borderRadius: '12px',
              px: 2,
              py: 0.5,
              width: searchFocused ? 360 : 280,
              transition: 'all 0.3s ease',
              border: '1px solid',
              borderColor: searchFocused ? alpha('#8B5CF6', 0.4) : 'transparent',
              '&:hover': {
                background: alpha('#334155', 0.6),
              },
              display: { xs: 'none', sm: 'flex' },
            }}
          >
            <SearchIcon sx={{ color: '#94A3B8', fontSize: 20, mr: 1 }} />
            <InputBase
              placeholder="Search employees, jobs, actions..."
              onFocus={() => setSearchFocused(true)}
              onBlur={() => setSearchFocused(false)}
              sx={{
                flex: 1,
                color: '#F8FAFC',
                fontSize: '0.875rem',
                '& ::placeholder': {
                  color: '#64748B',
                  opacity: 1,
                },
              }}
            />
            <Typography
              variant="caption"
              sx={{
                color: '#64748B',
                border: '1px solid #475569',
                borderRadius: '6px',
                px: 0.8,
                py: 0.1,
                fontSize: '0.65rem',
                fontWeight: 500,
              }}
            >
              ⌘K
            </Typography>
          </Box>

          {/* Spacer */}
          <Box sx={{ flex: 1 }} />

          {/* Actions */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            {/* Notifications */}
            <Tooltip title="Notifications">
              <IconButton
                onClick={onNotificationsClick}
                sx={{
                  color: '#94A3B8',
                  '&:hover': { color: '#F8FAFC', background: alpha('#334155', 0.5) },
                }}
              >
                <Badge
                  badgeContent={3}
                  sx={{
                    '& .MuiBadge-badge': {
                      background: 'linear-gradient(135deg, #8B5CF6, #6D28D9)',
                      color: '#fff',
                      fontSize: '0.65rem',
                      fontWeight: 700,
                      minWidth: 18,
                      height: 18,
                    },
                  }}
                >
                  <NotificationsIcon fontSize="small" />
                </Badge>
              </IconButton>
            </Tooltip>

            {/* AI Copilot Button */}
            <Tooltip title="AI Copilot">
              <IconButton
                sx={{
                  color: '#8B5CF6',
                  position: 'relative',
                  '&:hover': { background: alpha('#8B5CF6', 0.1) },
                  '&::after': {
                    content: '""',
                    position: 'absolute',
                    inset: -2,
                    borderRadius: '50%',
                    border: '2px solid',
                    borderColor: alpha('#8B5CF6', 0.3),
                    animation: 'topbarPulse 2s infinite',
                  },
                  '@keyframes topbarPulse': {
                    '0%': { transform: 'scale(1)', opacity: 1 },
                    '50%': { transform: 'scale(1.15)', opacity: 0 },
                    '100%': { transform: 'scale(1)', opacity: 0 },
                  },
                }}
              >
                <PsychologyIcon fontSize="small" />
              </IconButton>
            </Tooltip>

            {/* User Avatar */}
            <IconButton onClick={handleProfileMenuOpen} sx={{ ml: 0.5, p: 0.5 }}>
              <Avatar
                sx={{
                  width: 34,
                  height: 34,
                  background: 'linear-gradient(135deg, #8B5CF6, #6D28D9)',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  border: '2px solid',
                  borderColor: alpha('#8B5CF6', 0.3),
                }}
              >
                AU
              </Avatar>
            </IconButton>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Profile Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleProfileMenuClose}
        transformOrigin={{ horizontal: 'right', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
        PaperProps={{
          sx: {
            mt: 1,
            background: '#1E293B',
            border: '1px solid #334155',
            borderRadius: '12px',
            minWidth: 200,
            boxShadow: '0 20px 60px rgba(0,0,0,0.5)',
            '& .MuiMenuItem-root': {
              color: '#94A3B8',
              fontSize: '0.875rem',
              py: 1.2,
              px: 2,
              borderRadius: '8px',
              mx: 0.5,
              '&:hover': {
                background: alpha('#8B5CF6', 0.08),
                color: '#F8FAFC',
              },
            },
          },
        }}
      >
        <Box sx={{ px: 2, py: 1.5, borderBottom: '1px solid #334155' }}>
          <Typography variant="body2" sx={{ color: '#F8FAFC', fontWeight: 600 }}>
            Admin User
          </Typography>
          <Typography variant="caption" sx={{ color: '#64748B' }}>
            admin@hrgenie.ai
          </Typography>
        </Box>
        <MenuItem onClick={() => { handleProfileMenuClose(); navigate('/settings'); }}>
          <ListItemIcon><PersonIcon sx={{ color: '#94A3B8' }} fontSize="small" /></ListItemIcon>
          <ListItemText>Profile</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => { handleProfileMenuClose(); navigate('/settings'); }}>
          <ListItemIcon><SettingsIcon sx={{ color: '#94A3B8' }} fontSize="small" /></ListItemIcon>
          <ListItemText>Settings</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => { handleProfileMenuClose(); navigate('/login'); }}>
          <ListItemIcon><LogoutIcon sx={{ color: '#EF4444' }} fontSize="small" /></ListItemIcon>
          <ListItemText sx={{ '& .MuiTypography-root': { color: '#EF4444' } }}>Logout</ListItemText>
        </MenuItem>
      </Menu>
    </>
  );
};

export default Topbar;
