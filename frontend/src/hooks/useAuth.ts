import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import api from '../config/axios';
import { useAuthStore } from '../store/authStore';

export function useLogin() {
  const setAuth = useAuthStore((s) => s.setAuth);
  const navigate = useNavigate();

  return useMutation({
    mutationFn: async (data: { email: string; password: string }) => {
      const res = await api.post('/auth/login', data);
      return res.data;
    },
    onSuccess: (data) => {
      setAuth(data.access_token, data.user);
      toast.success(`Welcome back, ${data.user.full_name}!`);
      navigate('/dashboard');
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Login failed');
    },
  });
}

export function useLogout() {
  const logout = useAuthStore((s) => s.logout);
  const navigate = useNavigate();

  return useMutation({
    mutationFn: async () => {
      await api.post('/auth/logout');
    },
    onSuccess: () => {
      logout();
      navigate('/login');
    },
    onError: () => {
      logout();
      navigate('/login');
    },
  });
}

export function useForgotPassword() {
  return useMutation({
    mutationFn: async (email: string) => {
      await api.post('/auth/forgot-password', { email });
    },
    onSuccess: () => {
      toast.success('If the email exists, a reset link has been sent.');
    },
  });
}

export function useResetPassword() {
  const navigate = useNavigate();
  return useMutation({
    mutationFn: async (data: { token: string; new_password: string }) => {
      await api.post('/auth/reset-password', data);
    },
    onSuccess: () => {
      toast.success('Password reset successfully. Please login.');
      navigate('/login');
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Reset failed');
    },
  });
}
