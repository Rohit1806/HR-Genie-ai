import {
  Drawer,
  Box,
  Typography,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemButton,
  Button,
  Chip,
  Divider,
} from '@mui/material';
import { Close as CloseIcon, DoneAll as DoneAllIcon } from '@mui/icons-material';
import { useUIStore } from '@/store/uiStore';
import { useMarkRead, useMarkAllRead, useNotifications } from '@/hooks/useNotifications';

interface NotificationDrawerProps {
  open: boolean;
  onClose: () => void;
}

export default function NotificationDrawer({ open, onClose }: NotificationDrawerProps) {
  // Fetch notifications list
  useNotifications();

  const notifications = useUIStore((s) => s.notifications);
  const { mutate: markRead } = useMarkRead();
  const { mutate: markAllRead } = useMarkAllRead();

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
  };

  const getCategoryColor = (category: string) => {
    const map: Record<string, 'primary' | 'success' | 'warning' | 'error' | 'info'> = {
      leave: 'info',
      attendance: 'warning',
      payroll: 'success',
      performance: 'primary',
      recruitment: 'secondary' as any,
      system: 'error',
    };
    return map[category] || 'primary';
  };

  return (
    <Drawer
      anchor="right"
      open={open}
      onClose={onClose}
      sx={{
        '& .MuiDrawer-paper': {
          width: 380,
          bgcolor: 'background.paper',
          borderLeft: '1px solid',
          borderColor: 'divider',
        },
      }}
    >
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid', borderColor: 'divider' }}>
        <Typography variant="h6" fontWeight={700}>
          Notifications
        </Typography>
        <Box sx={{ display: 'flex', gap: 0.5 }}>
          <IconButton size="small" onClick={() => markAllRead()} title="Mark all read">
            <DoneAllIcon fontSize="small" />
          </IconButton>
          <IconButton size="small" onClick={onClose}>
            <CloseIcon fontSize="small" />
          </IconButton>
        </Box>
      </Box>

      {notifications.length === 0 ? (
        <Box sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            No notifications yet
          </Typography>
        </Box>
      ) : (
        <List disablePadding sx={{ overflow: 'auto', flexGrow: 1 }}>
          {notifications.map((n, idx) => (
            <Box key={n.id}>
              <ListItem disablePadding>
                <ListItemButton
                  onClick={() => {
                    if (!n.is_read) markRead(n.id);
                  }}
                  sx={{
                    px: 2,
                    py: 1.5,
                    bgcolor: n.is_read ? 'transparent' : 'rgba(139, 92, 246, 0.05)',
                    '&:hover': { bgcolor: 'action.hover' },
                  }}
                >
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                        <Typography variant="body2" fontWeight={n.is_read ? 400 : 600} sx={{ flex: 1 }}>
                          {n.title}
                        </Typography>
                        <Chip
                          label={n.category}
                          size="small"
                          color={getCategoryColor(n.category)}
                          variant="outlined"
                          sx={{ fontSize: '0.65rem', height: 20 }}
                        />
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                          {n.body}
                        </Typography>
                        <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.7rem' }}>
                          {formatTime(n.created_at)}
                        </Typography>
                      </Box>
                    }
                  />
                  {!n.is_read && (
                    <Box
                      sx={{
                        width: 8,
                        height: 8,
                        borderRadius: '50%',
                        bgcolor: 'primary.main',
                        ml: 1,
                        flexShrink: 0,
                      }}
                    />
                  )}
                </ListItemButton>
              </ListItem>
              {idx < notifications.length - 1 && <Divider />}
            </Box>
          ))}
        </List>
      )}

      <Box sx={{ p: 2, borderTop: '1px solid', borderColor: 'divider' }}>
        <Button fullWidth variant="text" size="small" sx={{ color: 'text.secondary' }}>
          View All Notifications
        </Button>
      </Box>
    </Drawer>
  );
}
