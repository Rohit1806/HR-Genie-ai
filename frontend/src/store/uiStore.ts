import { create } from 'zustand';

interface Notification {
  id: string;
  title: string;
  body: string;
  category: string;
  action_url?: string;
  is_read: boolean;
  created_at: string;
}

interface UIState {
  sidebarOpen: boolean;
  sidebarCollapsed: boolean;
  notificationDrawerOpen: boolean;
  copilotOpen: boolean;
  notifications: Notification[];
  unreadCount: number;
  toggleSidebar: () => void;
  toggleSidebarCollapse: () => void;
  setNotificationDrawer: (open: boolean) => void;
  setCopilotOpen: (open: boolean) => void;
  addNotification: (notification: Notification) => void;
  markRead: (id: string) => void;
  markAllRead: () => void;
  setNotifications: (notifications: Notification[]) => void;
  setUnreadCount: (count: number) => void;
}

export const useUIStore = create<UIState>((set) => ({
  sidebarOpen: true,
  sidebarCollapsed: false,
  notificationDrawerOpen: false,
  copilotOpen: false,
  notifications: [],
  unreadCount: 0,
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  toggleSidebarCollapse: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
  setNotificationDrawer: (open) => set({ notificationDrawerOpen: open }),
  setCopilotOpen: (open) => set({ copilotOpen: open }),
  addNotification: (n) =>
    set((s) => ({
      notifications: [n, ...s.notifications],
      unreadCount: s.unreadCount + 1,
    })),
  markRead: (id) =>
    set((s) => ({
      notifications: s.notifications.map((n) =>
        n.id === id ? { ...n, is_read: true } : n
      ),
      unreadCount: Math.max(0, s.unreadCount - 1),
    })),
  markAllRead: () =>
    set((s) => ({
      notifications: s.notifications.map((n) => ({ ...n, is_read: true })),
      unreadCount: 0,
    })),
  setNotifications: (notifications) => set({ notifications }),
  setUnreadCount: (count) => set({ unreadCount: count }),
}));
