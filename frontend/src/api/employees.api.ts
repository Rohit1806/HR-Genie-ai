import api from '../config/axios';
import type {
  EmployeeSummary,
  EmployeeDetail,
  EmployeeListResponse,
  OrgChartNode,
  DocumentEntry,
} from '../types/employee.types';

export interface ListEmployeesParams {
  page?: number;
  page_size?: number;
  search?: string;
  department_id?: string;
  employment_status?: string;
  employment_type?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface CreateEmployeeData {
  first_name: string;
  last_name: string;
  personal_email: string;
  phone: string;
  date_of_birth: string;
  gender: string;
  department_id: string;
  designation_id: string;
  employment_type: string;
  date_of_joining: string;
  reporting_manager_id?: string;
  work_location?: string;
  address?: Record<string, any>;
  emergency_contact?: Record<string, any>;
}

export interface UpdateEmployeeData extends Partial<CreateEmployeeData> {
  employment_status?: string;
}

export const employeesApi = {
  listEmployees: async (params: ListEmployeesParams = {}): Promise<EmployeeListResponse> => {
    const res = await api.get<EmployeeListResponse>('/employees', { params });
    return res.data;
  },

  getEmployee: async (id: string): Promise<EmployeeDetail> => {
    const res = await api.get<EmployeeDetail>(`/employees/${id}`);
    return res.data;
  },

  createEmployee: async (data: CreateEmployeeData): Promise<EmployeeDetail> => {
    const res = await api.post<EmployeeDetail>('/employees', data);
    return res.data;
  },

  updateEmployee: async (id: string, data: UpdateEmployeeData): Promise<EmployeeDetail> => {
    const res = await api.patch<EmployeeDetail>(`/employees/${id}`, data);
    return res.data;
  },

  deleteEmployee: async (id: string, reason: string, terminationDate: string): Promise<void> => {
    await api.delete(`/employees/${id}`, {
      params: {
        reason,
        termination_date: terminationDate,
      },
    });
  },

  addSkill: async (
    id: string,
    skillName: string,
    proficiencyLevel: string,
    yearsExperience?: number
  ): Promise<any> => {
    const formData = new FormData();
    formData.append('skill_name', skillName);
    formData.append('proficiency_level', proficiencyLevel);
    if (yearsExperience !== undefined) {
      formData.append('years_experience', String(yearsExperience));
    }
    const res = await api.post(`/employees/${id}/skills`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  getOrgChart: async (): Promise<OrgChartNode> => {
    const res = await api.get<OrgChartNode>('/employees/org-chart');
    return res.data;
  },

  uploadDocument: async (employeeId: string, file: File, documentType: string): Promise<DocumentEntry> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', documentType);
    const res = await api.post<DocumentEntry>(`/employees/${employeeId}/documents`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  getDocuments: async (employeeId: string): Promise<DocumentEntry[]> => {
    const res = await api.get<DocumentEntry[]>(`/employees/${employeeId}/documents`);
    return res.data;
  },
};
