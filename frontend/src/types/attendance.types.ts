export interface AttendanceRecord {
  id: string;
  date: string;
  clock_in: string | null;
  clock_out: string | null;
  total_hours: number | null;
  status: AttendanceStatus;
}

export interface AttendanceSummary {
  present_days: number;
  absent_days: number;
  late_days: number;
  half_days: number;
  leave_days: number;
  holidays: number;
  avg_hours: number;
  total_working_days: number;
}

export interface MonthlyAttendance {
  records: AttendanceRecord[];
  summary: AttendanceSummary;
}

export interface TeamAttendanceRecord {
  employee_id: string;
  employee_name: string;
  department: string;
  status: AttendanceStatus;
  clock_in: string | null;
  clock_out: string | null;
}

export type AttendanceStatus = 'present' | 'absent' | 'late' | 'half_day' | 'on_leave' | 'holiday';
