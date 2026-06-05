import api from '../config/axios';
import type {
  MonthlyAttendance,
  TeamAttendanceRecord,
} from '../types/attendance.types';

export interface ClockInData {
  latitude?: number;
  longitude?: number;
  notes?: string;
}

export interface ClockOutData {
  latitude?: number;
  longitude?: number;
  notes?: string;
}

export interface RegularizationRequest {
  date: string;
  clock_in: string;
  clock_out: string;
  reason: string;
}

export interface PendingRegularization {
  id: string;
  employee_id: string;
  employee_name: string;
  date: string;
  requested_clock_in: string;
  requested_clock_out: string;
  reason: string;
  status: 'pending' | 'approved' | 'rejected';
  created_at: string;
}

export const attendanceApi = {
  clockIn: async (data: ClockInData = {}): Promise<{ id: string; clock_in: string; date: string }> => {
    const res = await api.post('/attendance/clock-in', data);
    return res.data;
  },

  clockOut: async (data: ClockOutData = {}): Promise<{ id: string; clock_out: string; total_hours: number }> => {
    const res = await api.post('/attendance/clock-out', data);
    return res.data;
  },

  getMyAttendance: async (month: number, year: number): Promise<MonthlyAttendance> => {
    const res = await api.get<MonthlyAttendance>('/attendance/my', {
      params: { month, year },
    });
    return res.data;
  },

  getTeamAttendance: async (date: string): Promise<TeamAttendanceRecord[]> => {
    const res = await api.get<TeamAttendanceRecord[]>('/attendance/team', {
      params: { date },
    });
    return res.data;
  },

  createRegularization: async (data: RegularizationRequest): Promise<PendingRegularization> => {
    const res = await api.post<PendingRegularization>('/attendance/regularization', data);
    return res.data;
  },

  getPendingRegularizations: async (): Promise<PendingRegularization[]> => {
    const res = await api.get<PendingRegularization[]>('/attendance/regularization/pending');
    return res.data;
  },

  approveRegularization: async (id: string): Promise<PendingRegularization> => {
    const res = await api.patch<PendingRegularization>(`/attendance/regularization/${id}/approve`);
    return res.data;
  },

  rejectRegularization: async (id: string, reason?: string): Promise<PendingRegularization> => {
    const res = await api.patch<PendingRegularization>(`/attendance/regularization/${id}/reject`, { reason });
    return res.data;
  },
};
