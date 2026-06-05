import { useEffect, useRef, useCallback } from 'react';
import { useAuthStore } from '../store/authStore';
import { useUIStore } from '../store/uiStore';

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttempt = useRef(0);
  const maxReconnectDelay = 30000;
  const token = useAuthStore((s) => s.accessToken);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const addNotification = useUIStore((s) => s.addNotification);

  const connect = useCallback(() => {
    if (!token || !isAuthenticated) return;

    const wsUrl = `${((import.meta as any).env?.VITE_WS_URL) || 'ws://localhost:8000'}/api/v1/ws/notifications?token=${token}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('WebSocket connected');
      reconnectAttempt.current = 0;
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        addNotification(data);
      } catch (e) {
        console.error('WS message parse error:', e);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      // Exponential backoff reconnect
      const delay = Math.min(
        1000 * Math.pow(2, reconnectAttempt.current),
        maxReconnectDelay
      );
      reconnectAttempt.current += 1;
      setTimeout(connect, delay);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      ws.close();
    };

    wsRef.current = ws;
  }, [token, isAuthenticated, addNotification]);

  useEffect(() => {
    connect();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  return wsRef;
}
