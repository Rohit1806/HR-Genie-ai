import api from '../config/axios';
import type {
  PayrollRun,
  PayrollEntry,
  Payslip,
} from '../types/payroll.types';

export interface InitiateRunData {
  month: number;
  year: number;
}

export interface ListRunsParams {
  page?: number;
  page_size?: number;
  status?: string;
  year?: number;
}

export const payrollApi = {
  initiateRun: async (data: InitiateRunData): Promise<PayrollRun> => {
    const res = await api.post<PayrollRun>('/payroll/runs', data);
    return res.data;
  },

  getRunStatus: async (runId: string): Promise<PayrollRun> => {
    const res = await api.get<PayrollRun>(`/payroll/runs/${runId}`);
    return res.data;
  },

  listRuns: async (params: ListRunsParams = {}): Promise<{ items: PayrollRun[]; total: number; page: number; page_size: number; total_pages: number }> => {
    const res = await api.get('/payroll/runs', { params });
    return res.data;
  },

  getRunEntries: async (runId: string, params: { page?: number; page_size?: number; search?: string } = {}): Promise<{ items: PayrollEntry[]; total: number; page: number; page_size: number; total_pages: number }> => {
    const res = await api.get(`/payroll/runs/${runId}/entries`, { params });
    return res.data;
  },

  approveRun: async (runId: string): Promise<PayrollRun> => {
    const res = await api.patch<PayrollRun>(`/payroll/runs/${runId}/approve`);
    return res.data;
  },

  getMyPayslip: async (month: number, year: number): Promise<Payslip> => {
    const res = await api.get<Payslip>('/payroll/my-payslip', {
      params: { month, year },
    });
    return res.data;
  },
};
