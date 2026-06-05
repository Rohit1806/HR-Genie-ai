import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface UserContext {
  id: string;
  company_id: string;
  email: string;
  full_name: string;
  role: 'admin' | 'senior_manager' | 'hr_recruiter' | 'employee';
}

interface AuthState {
  accessToken: string | null;
  user: UserContext | null;
  isAuthenticated: boolean;
  setAuth: (token: string, user: UserContext) => void;
  setAccessToken: (token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      user: null,
      isAuthenticated: false,
      setAuth: (token, user) =>
        set({ accessToken: token, user, isAuthenticated: true }),
      setAccessToken: (token) => set({ accessToken: token }),
      logout: () =>
        set({ accessToken: null, user: null, isAuthenticated: false }),
    }),
    {
      name: 'hrgenie-auth',
      partialize: (state) => ({
        accessToken: state.accessToken,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
