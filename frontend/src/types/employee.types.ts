export interface EmployeeSummary {
  id: string;
  employee_code: string;
  full_name: string;
  department_name: string;
  designation_title: string;
  employment_status: EmploymentStatus;
  profile_photo_url: string | null;
  date_of_joining: string;
}

export interface EmployeeDetail extends EmployeeSummary {
  first_name: string;
  last_name: string;
  personal_email: string;
  phone: string;
  date_of_birth: string;
  gender: string;
  address: Record<string, any> | null;
  emergency_contact: Record<string, any> | null;
  employment_type: EmploymentType;
  reporting_manager_name: string | null;
  work_location: string | null;
  skills: SkillEntry[];
  documents: DocumentEntry[];
  history: HistoryEntry[];
}

export interface HistoryEntry {
  id: string;
  event_type: string;
  previous_value: Record<string, any> | null;
  new_value: Record<string, any> | null;
  effective_date: string;
  reason: string | null;
}

export interface EmployeeListResponse {
  items: EmployeeSummary[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface SkillEntry {
  id: string;
  name: string;
  category: string | null;
  proficiency: string | null;
  years_experience: number | null;
}

export interface DocumentEntry {
  id: string;
  document_type: string;
  file_name: string;
  file_url: string;
  file_size_bytes: number;
  created_at: string;
}

export interface OrgChartNode {
  id: string;
  name: string;
  designation: string;
  department: string;
  photo_url: string | null;
  children: OrgChartNode[];
}

export type EmploymentStatus = 'active' | 'on_leave' | 'notice_period' | 'terminated';
export type EmploymentType = 'full_time' | 'part_time' | 'contract' | 'intern';
