import api from '../config/axios';
import type {
  JobPostingSummary,
  ApplicationSummary,
  AIEvaluation,
  CandidateRanking,
} from '../types/recruitment.types';

export interface CreateJobPostingData {
  title: string;
  department_id: string;
  description: string;
  requirements: string[];
  preferred_skills: string[];
  location: string;
  employment_type: string;
  salary_range_min?: number;
  salary_range_max?: number;
  openings_count: number;
  deadline: string;
}

export interface UpdateJobPostingData extends Partial<CreateJobPostingData> {
  status?: string;
}

export interface SubmitApplicationData {
  job_posting_id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  linkedin_url?: string;
  source?: string;
  current_ctc?: number;
  expected_ctc?: number;
  notice_period_days?: number;
  resume_file?: File;
}

export interface ListJobPostingsParams {
  page?: number;
  page_size?: number;
  status?: string;
  department_id?: string;
  search?: string;
}

export interface ListApplicationsParams {
  page?: number;
  page_size?: number;
  stage?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface InterviewQuestion {
  question: string;
  category: string;
  difficulty: string;
  expected_answer_points: string[];
}

export const recruitmentApi = {
  listJobPostings: async (params: ListJobPostingsParams = {}): Promise<{ items: JobPostingSummary[]; total: number; page: number; page_size: number; total_pages: number }> => {
    const res = await api.get('/recruitment/jobs', { params });
    return res.data;
  },

  createJobPosting: async (data: CreateJobPostingData): Promise<JobPostingSummary> => {
    const res = await api.post<JobPostingSummary>('/recruitment/jobs', data);
    return res.data;
  },

  getJobPosting: async (id: string): Promise<JobPostingSummary & { description: string; requirements: string[]; preferred_skills: string[] }> => {
    const res = await api.get(`/recruitment/jobs/${id}`);
    return res.data;
  },

  updateJobPosting: async (id: string, data: UpdateJobPostingData): Promise<JobPostingSummary> => {
    const res = await api.patch<JobPostingSummary>(`/recruitment/jobs/${id}`, data);
    return res.data;
  },

  submitApplication: async (data: SubmitApplicationData): Promise<ApplicationSummary> => {
    const formData = new FormData();
    formData.append('job_posting_id', data.job_posting_id);
    formData.append('first_name', data.first_name);
    formData.append('last_name', data.last_name);
    formData.append('email', data.email);
    if (data.phone) formData.append('phone', data.phone);
    if (data.linkedin_url) formData.append('linkedin_url', data.linkedin_url);
    if (data.source) formData.append('source', data.source);
    if (data.current_ctc !== undefined) formData.append('current_ctc', String(data.current_ctc));
    if (data.expected_ctc !== undefined) formData.append('expected_ctc', String(data.expected_ctc));
    if (data.notice_period_days !== undefined) formData.append('notice_period_days', String(data.notice_period_days));
    if (data.resume_file) formData.append('file', data.resume_file);
    const res = await api.post<ApplicationSummary>('/recruitment/applications', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  listApplications: async (jobId?: string, params: ListApplicationsParams = {}): Promise<{ items: ApplicationSummary[]; total: number; page: number; page_size: number; total_pages: number }> => {
    const res = await api.get('/recruitment/applications', { params: { job_posting_id: jobId, ...params } });
    return res.data;
  },

  getApplication: async (applicationId: string): Promise<ApplicationSummary & { ai_evaluation: AIEvaluation | null }> => {
    const res = await api.get(`/recruitment/applications/${applicationId}`);
    return res.data;
  },

  updateStage: async (applicationId: string, stage: string, rejectionReason?: string): Promise<ApplicationSummary> => {
    const res = await api.patch<ApplicationSummary>(`/recruitment/applications/${applicationId}/stage`, { stage, rejection_reason: rejectionReason });
    return res.data;
  },

  getRankedCandidates: async (jobId: string): Promise<CandidateRanking[]> => {
    const res = await api.get<CandidateRanking[]>(`/recruitment/jobs/${jobId}/ranked-candidates`);
    return res.data;
  },

  getInterviewQuestions: async (applicationId: string): Promise<InterviewQuestion[]> => {
    const res = await api.get<InterviewQuestion[]>(`/recruitment/applications/${applicationId}/interview-questions`);
    return res.data;
  },

  generateInterviewQuestions: async (applicationId: string, focusAreas?: string[]): Promise<InterviewQuestion[]> => {
    const res = await api.post<InterviewQuestion[]>(`/recruitment/applications/${applicationId}/interview-questions/generate`, { focus_areas: focusAreas });
    return res.data;
  },

  uploadVoiceScreening: async (applicationId: string, file: File): Promise<any> => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await api.post(`/recruitment/applications/${applicationId}/voice-screening`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  getVoiceScreenings: async (applicationId: string): Promise<any[]> => {
    const res = await api.get(`/recruitment/applications/${applicationId}/voice-screenings`);
    return res.data;
  },

  uploadResumeOnly: async (jobPostingId: string, file: File): Promise<any> => {
    const formData = new FormData();
    formData.append('job_posting_id', jobPostingId);
    formData.append('file', file);
    const res = await api.post('/recruitment/applications/upload-resume', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },
};
