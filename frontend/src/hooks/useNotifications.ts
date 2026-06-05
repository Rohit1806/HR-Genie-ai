import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../config/axios';
import { useUIStore } from '../store/uiStore';

export function useNotifications(page = 1) {
  const setNotifications = useUIStore((s) => s.setNotifications);
  return useQuery({
    queryKey: ['notifications', page],
    queryFn: async () => {
      const res = await api.get('/ws/notifications', { params: { page, page_size: 20 } });
      setNotifications(res.data);
      return res.data;
    },
  });
}

export function useUnreadCount() {
  const setUnreadCount = useUIStore((s) => s.setUnreadCount);
  return useQuery({
    queryKey: ['notifications-count'],
    queryFn: async () => {
      const res = await api.get('/ws/notifications/count');
      setUnreadCount(res.data.count);
      return res.data.count;
    },
    refetchInterval: 30000, // Poll every 30s as backup
  });
}

export function useMarkRead() {
  const qc = useQueryClient();
  const markRead = useUIStore((s) => s.markRead);
  return useMutation({
    mutationFn: async (id: string) => {
      await api.patch(`/ws/notifications/${id}/read`);
    },
    onSuccess: (_, id) => {
      markRead(id);
      qc.invalidateQueries({ queryKey: ['notifications-count'] });
    },
  });
}

export function useMarkAllRead() {
  const qc = useQueryClient();
  const markAllRead = useUIStore((s) => s.markAllRead);
  return useMutation({
    mutationFn: async () => {
      await api.patch('/ws/notifications/read-all');
    },
    onSuccess: () => {
      markAllRead();
      qc.invalidateQueries({ queryKey: ['notifications'] });
      qc.invalidateQueries({ queryKey: ['notifications-count'] });
    },
  });
}
