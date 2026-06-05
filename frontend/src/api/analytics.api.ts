import api from '../config/axios';

export interface DashboardStats {
  total_employees: number;
  new_hires_this_month: number;
  open_positions: number;
  pending_approvals: number;
  attendance_rate: number;
  attrition_rate: number;
}

export interface AdminDashboard extends DashboardStats {
  department_headcount: { department: string; count: number }[];
  monthly_hiring_trend: { month: string; hired: number; resigned: number }[];
  payroll_summary: { month: string; total_cost: number }[];
  upcoming_reviews: number;
}

export interface ManagerDashboard {
  team_size: number;
  present_today: number;
  on_leave_today: number;
  pending_leave_approvals: number;
  pending_regularizations: number;
  team_performance_avg: number;
  team_attendance_rate: number;
  upcoming_birthdays: { name: string; date: string }[];
  pending_reviews: number;
}

export interface HRDashboard extends DashboardStats {
  active_job_postings: number;
  applications_this_week: number;
  interviews_this_week: number;
  offers_pending: number;
  onboarding_in_progress: number;
  leave_requests_pending: number;
}

export interface EmployeeDashboard {
  attendance_summary: {
    present_days: number;
    absent_days: number;
    total_working_days: number;
  };
  leave_balances: { type: string; remaining: number; total: number }[];
  upcoming_holidays: { name: string; date: string }[];
  pending_goals: number;
  overall_performance_score: number | null;
  announcements: { id: string; title: string; body: string; created_at: string }[];
}

export interface WorkforceComposition {
  by_department: { department: string; count: number; percentage: number }[];
  by_gender: { gender: string; count: number; percentage: number }[];
  by_employment_type: { type: string; count: number; percentage: number }[];
  by_age_group: { group: string; count: number; percentage: number }[];
  by_tenure: { range: string; count: number; percentage: number }[];
}

export interface PayrollCostTrend {
  months: { month: string; gross: number; net: number; deductions: number }[];
  total_annual_cost: number;
  avg_monthly_cost: number;
}

export interface PerformanceDistribution {
  distribution: { range: string; count: number; percentage: number }[];
  avg_score: number;
  top_performers: { name: string; score: number; department: string }[];
  needs_improvement: { name: string; score: number; department: string }[];
}

export const analyticsApi = {
  getAdminDashboard: async (): Promise<AdminDashboard> => {
    const res = await api.get<AdminDashboard>('/analytics/dashboard/admin');
    return res.data;
  },

  getManagerDashboard: async (): Promise<ManagerDashboard> => {
    const res = await api.get<ManagerDashboard>('/analytics/dashboard/manager');
    return res.data;
  },

  getHRDashboard: async (): Promise<HRDashboard> => {
    const res = await api.get<HRDashboard>('/analytics/dashboard/hr');
    return res.data;
  },

  getEmployeeDashboard: async (): Promise<EmployeeDashboard> => {
    const res = await api.get<EmployeeDashboard>('/analytics/dashboard/employee');
    return res.data;
  },

  getWorkforceComposition: async (): Promise<WorkforceComposition> => {
    const res = await api.get<WorkforceComposition>('/analytics/workforce-composition');
    return res.data;
  },

  getPayrollCostTrend: async (year?: number): Promise<PayrollCostTrend> => {
    const res = await api.get<PayrollCostTrend>('/analytics/payroll-cost-trend', {
      params: { year },
    });
    return res.data;
  },

  getPerformanceDistribution: async (cycleId?: string): Promise<PerformanceDistribution> => {
    const res = await api.get<PerformanceDistribution>('/analytics/performance-distribution', {
      params: { cycle_id: cycleId },
    });
    return res.data;
  },

  getOverviewMetrics: async (): Promise<{ headcount: number }> => {
    const res = await api.get<{ headcount: number }>('/analytics/overview');
    return res.data;
  },
};
