export interface LeaveType {
  id: string;
  name: string;
  code: string;
  annual_quota: number;
  is_paid: boolean;
  carry_forward: boolean;
}

export interface LeaveBalance {
  id: string;
  leave_type: LeaveType;
  year: number;
  allocated: number;
  used: number;
  pending: number;
  remaining: number;
}

export interface LeaveRequest {
  id: string;
  employee_id: string;
  employee_name: string;
  leave_type_name: string;
  from_date: string;
  to_date: string;
  days_count: number;
  reason: string;
  status: LeaveStatus;
  created_at: string;
}

export type LeaveStatus = 'pending' | 'approved' | 'rejected' | 'cancelled';
