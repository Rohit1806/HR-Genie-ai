export interface PayrollRun {
  id: string;
  month: number;
  year: number;
  status: PayrollStatus;
  total_gross: number;
  total_net: number;
  initiated_by: string;
  created_at: string;
}

export interface PayrollEntry {
  id: string;
  employee_id: string;
  employee_name: string;
  employee_code: string;
  gross_salary: number;
  basic: number;
  hra: number;
  allowances: Record<string, number>;
  pf_deduction: number;
  esi_deduction: number;
  tds_deduction: number;
  lop_days: number;
  lop_deduction: number;
  net_salary: number;
}

export interface Payslip {
  month: number;
  year: number;
  employee_name: string;
  employee_code: string;
  department: string;
  designation: string;
  earnings: Record<string, number>;
  deductions: Record<string, number>;
  gross_salary: number;
  total_deductions: number;
  net_salary: number;
}

export type PayrollStatus = 'draft' | 'computing' | 'computed' | 'approved' | 'paid';
