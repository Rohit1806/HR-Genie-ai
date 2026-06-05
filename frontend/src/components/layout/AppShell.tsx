import { Outlet } from 'react-router-dom';
import { Box, Drawer, AppBar, Toolbar, IconButton, Typography, Badge, Avatar, Tooltip, useMediaQuery, useTheme } from '@mui/material';
import {
  Menu as MenuIcon,
  Notifications as NotificationsIcon,
  AutoAwesome as CopilotIcon,
  ChevronLeft as ChevronLeftIcon,
  Search as SearchIcon,
} from '@mui/icons-material';
import { useAuthStore } from '@/store/authStore';
import { useUIStore } from '@/store/uiStore';
import { useWebSocket } from '@/hooks/useWebSocket';
import { useUnreadCount } from '@/hooks/useNotifications';
import Sidebar from './Sidebar';
import NotificationDrawer from './NotificationDrawer';
import AICopilotDrawer from '@/components/ai/AICopilotDrawer';

const SIDEBAR_WIDTH = 260;
const SIDEBAR_COLLAPSED_WIDTH = 72;

export default function AppShell() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const user = useAuthStore((s) => s.user);
  const {
    sidebarOpen,
    sidebarCollapsed,
    toggleSidebar,
    toggleSidebarCollapse,
    notificationDrawerOpen,
    setNotificationDrawer,
    copilotOpen,
    setCopilotOpen,
    unreadCount,
  } = useUIStore();

  // Connect WebSocket for real-time notifications
  useWebSocket();
  // Poll unread count as backup
  useUnreadCount();

  const currentSidebarWidth = sidebarCollapsed ? SIDEBAR_COLLAPSED_WIDTH : SIDEBAR_WIDTH;

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default' }}>
      {/* Sidebar */}
      <Drawer
        variant={isMobile ? 'temporary' : 'permanent'}
        open={isMobile ? sidebarOpen : true}
        onClose={toggleSidebar}
        sx={{
          width: currentSidebarWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: currentSidebarWidth,
            transition: 'width 0.2s ease',
            overflowX: 'hidden',
          },
        }}
      >
        <Sidebar collapsed={sidebarCollapsed} onToggleCollapse={toggleSidebarCollapse} />
      </Drawer>

      {/* Main content area */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          ml: isMobile ? 0 : `${currentSidebarWidth}px`,
          transition: 'margin-left 0.2s ease',
          minHeight: '100vh',
        }}
      >
        {/* Top AppBar */}
        <AppBar
          position="sticky"
          elevation={0}
          sx={{
            bgcolor: 'background.default',
            borderBottom: '1px solid',
            borderColor: 'divider',
            backdropFilter: 'blur(12px)',
          }}
        >
          <Toolbar sx={{ justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {isMobile && (
                <IconButton onClick={toggleSidebar} sx={{ color: 'text.primary' }}>
                  <MenuIcon />
                </IconButton>
              )}
              {!isMobile && (
                <IconButton onClick={toggleSidebarCollapse} sx={{ color: 'text.secondary' }}>
                  <ChevronLeftIcon sx={{ transform: sidebarCollapsed ? 'rotate(180deg)' : 'none', transition: '0.2s' }} />
                </IconButton>
              )}
              {/* Global Search */}
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  bgcolor: 'background.paper',
                  border: '1px solid',
                  borderColor: 'divider',
                  borderRadius: 2,
                  px: 2,
                  py: 0.5,
                  minWidth: 280,
                  cursor: 'pointer',
                  '&:hover': { borderColor: 'primary.main' },
                }}
              >
                <SearchIcon sx={{ color: 'text.secondary', mr: 1, fontSize: 20 }} />
                <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                  Search employees, jobs, reports…
                </Typography>
                <Typography
                  variant="caption"
                  sx={{
                    ml: 'auto',
                    color: 'text.secondary',
                    bgcolor: 'background.default',
                    px: 1,
                    py: 0.25,
                    borderRadius: 1,
                    fontSize: '0.7rem',
                  }}
                >
                  ⌘K
                </Typography>
              </Box>
            </Box>

            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {/* AI Copilot Toggle */}
              <Tooltip title="AI Copilot">
                <IconButton
                  onClick={() => setCopilotOpen(!copilotOpen)}
                  sx={{
                    color: copilotOpen ? 'primary.main' : 'text.secondary',
                    bgcolor: copilotOpen ? 'rgba(139, 92, 246, 0.1)' : 'transparent',
                    '&:hover': { bgcolor: 'rgba(139, 92, 246, 0.15)' },
                  }}
                >
                  <CopilotIcon />
                </IconButton>
              </Tooltip>

              {/* Notifications */}
              <Tooltip title="Notifications">
                <IconButton
                  onClick={() => setNotificationDrawer(!notificationDrawerOpen)}
                  sx={{ color: 'text.secondary' }}
                >
                  <Badge badgeContent={unreadCount} color="error" max={99}>
                    <NotificationsIcon />
                  </Badge>
                </IconButton>
              </Tooltip>

              {/* User Avatar */}
              <Tooltip title={user?.full_name || 'Account'}>
                <Avatar
                  sx={{
                    width: 36,
                    height: 36,
                    bgcolor: 'primary.main',
                    fontSize: '0.875rem',
                    fontWeight: 600,
                    cursor: 'pointer',
                  }}
                >
                  {user?.full_name
                    ?.split(' ')
                    .map((n) => n[0])
                    .join('')
                    .slice(0, 2)
                    .toUpperCase() || 'U'}
                </Avatar>
              </Tooltip>
            </Box>
          </Toolbar>
        </AppBar>

        {/* Page content */}
        <Box sx={{ flexGrow: 1, p: 3 }}>
          <Outlet />
        </Box>
      </Box>

      {/* Notification Drawer */}
      <NotificationDrawer
        open={notificationDrawerOpen}
        onClose={() => setNotificationDrawer(false)}
      />

      {/* AI Copilot Drawer */}
      <AICopilotDrawer
        open={copilotOpen}
        onClose={() => setCopilotOpen(false)}
      />
    </Box>
  );
}
