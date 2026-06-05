import api from '../config/axios';
import type {
  LoginRequest,
  LoginResponse,
  TokenRefreshResponse,
  ForgotPasswordRequest,
  ResetPasswordRequest,
  UserContext,
} from '../types/auth.types';

export const authApi = {
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const res = await api.post<LoginResponse>('/auth/login', data);
    return res.data;
  },

  logout: async (): Promise<void> => {
    await api.post('/auth/logout');
  },

  refresh: async (): Promise<TokenRefreshResponse> => {
    const res = await api.post<TokenRefreshResponse>('/auth/refresh');
    return res.data;
  },

  forgotPassword: async (data: ForgotPasswordRequest): Promise<void> => {
    await api.post('/auth/forgot-password', data);
  },

  resetPassword: async (data: ResetPasswordRequest): Promise<void> => {
    await api.post('/auth/reset-password', data);
  },

  getMe: async (): Promise<UserContext> => {
    const res = await api.get<UserContext>('/auth/me');
    return res.data;
  },
};
