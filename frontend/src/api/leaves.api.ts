import api from '../config/axios';
import type {
  LeaveType,
  LeaveBalance,
  LeaveRequest,
} from '../types/leave.types';

export interface ApplyLeaveData {
  leave_type_id: string;
  from_date: string;
  to_date: string;
  reason: string;
  is_half_day?: boolean;
  half_day_period?: 'first_half' | 'second_half';
}

export interface ListRequestsParams {
  page?: number;
  page_size?: number;
  status?: string;
  year?: number;
}

export interface Holiday {
  id: string;
  name: string;
  date: string;
  is_optional: boolean;
  description?: string;
}

export const leavesApi = {
  getLeaveTypes: async (): Promise<LeaveType[]> => {
    const res = await api.get<LeaveType[]>('/leaves/types');
    return res.data;
  },

  getMyBalances: async (year?: number): Promise<LeaveBalance[]> => {
    const res = await api.get<LeaveBalance[]>('/leaves/my-balances', {
      params: { year },
    });
    return res.data;
  },

  applyLeave: async (data: ApplyLeaveData): Promise<LeaveRequest> => {
    const res = await api.post<LeaveRequest>('/leaves/apply', data);
    return res.data;
  },

  getMyRequests: async (params: ListRequestsParams = {}): Promise<{ items: LeaveRequest[]; total: number; page: number; page_size: number; total_pages: number }> => {
    const res = await api.get('/leaves/my-requests', { params });
    return res.data;
  },

  getPendingApprovals: async (params: { page?: number; page_size?: number } = {}): Promise<{ items: LeaveRequest[]; total: number; page: number; page_size: number; total_pages: number }> => {
    const res = await api.get('/leaves/pending-approvals', { params });
    return res.data;
  },

  approveLeave: async (id: string, remarks?: string): Promise<LeaveRequest> => {
    const res = await api.patch<LeaveRequest>(`/leaves/${id}/approve`, { remarks });
    return res.data;
  },

  rejectLeave: async (id: string, reason: string): Promise<LeaveRequest> => {
    const res = await api.patch<LeaveRequest>(`/leaves/${id}/reject`, { reason });
    return res.data;
  },

  cancelLeave: async (id: string): Promise<LeaveRequest> => {
    const res = await api.patch<LeaveRequest>(`/leaves/${id}/cancel`);
    return res.data;
  },

  getHolidays: async (year?: number): Promise<Holiday[]> => {
    const res = await api.get<Holiday[]>('/leaves/holidays', {
      params: { year },
    });
    return res.data;
  },
};
