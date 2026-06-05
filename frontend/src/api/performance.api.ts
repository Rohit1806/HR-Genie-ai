import api from '../config/axios';
import type {
  PerformanceCycle,
  Goal,
  PerformanceReview,
  PerformanceScore,
} from '../types/performance.types';

export interface CreateCycleData {
  name: string;
  cycle_type: string;
  start_date: string;
  end_date: string;
  review_start: string;
  review_end: string;
}

export interface CreateGoalData {
  cycle_id: string;
  title: string;
  description: string;
  key_results: { title: string; target: number; unit: string }[];
  weightage: number;
  due_date: string;
}

export interface UpdateGoalData {
  title?: string;
  description?: string;
  key_results?: { title: string; target: number; current: number; unit: string }[];
  weightage?: number;
  status?: string;
  due_date?: string;
}

export interface SelfReviewData {
  cycle_id: string;
  ratings: Record<string, number>;
  feedback: string;
  achievements: string[];
  challenges: string[];
}

export interface ManagerReviewData {
  cycle_id: string;
  employee_id: string;
  ratings: Record<string, number>;
  feedback: string;
  strengths: string[];
  areas_of_improvement: string[];
  overall_score: number;
}

export const performanceApi = {
  listCycles: async (params: { status?: string; page?: number; page_size?: number } = {}): Promise<{ items: PerformanceCycle[]; total: number; page: number; page_size: number; total_pages: number }> => {
    const res = await api.get('/performance/cycles', { params });
    return res.data;
  },

  createCycle: async (data: CreateCycleData): Promise<PerformanceCycle> => {
    const res = await api.post<PerformanceCycle>('/performance/cycles', data);
    return res.data;
  },

  getMyGoals: async (cycleId: string): Promise<Goal[]> => {
    const res = await api.get<Goal[]>('/performance/goals', {
      params: { cycle_id: cycleId },
    });
    return res.data;
  },

  createGoal: async (data: CreateGoalData): Promise<Goal> => {
    const res = await api.post<Goal>('/performance/goals', data);
    return res.data;
  },

  updateGoal: async (id: string, data: UpdateGoalData): Promise<Goal> => {
    const res = await api.patch<Goal>(`/performance/goals/${id}`, data);
    return res.data;
  },

  submitSelfReview: async (data: SelfReviewData): Promise<PerformanceReview> => {
    const res = await api.post<PerformanceReview>('/performance/reviews/self', data);
    return res.data;
  },

  submitManagerReview: async (data: ManagerReviewData): Promise<PerformanceReview> => {
    const res = await api.post<PerformanceReview>('/performance/reviews/manager', data);
    return res.data;
  },

  getScores: async (cycleId?: string): Promise<PerformanceScore[]> => {
    const res = await api.get<PerformanceScore[]>('/performance/scores', {
      params: { cycle_id: cycleId },
    });
    return res.data;
  },

  getAIInsights: async (cycleId: string): Promise<{ promotion_score: number; attrition_risk: number; summary: string; recommendations: string[] }> => {
    const res = await api.get('/performance/insights', {
      params: { cycle_id: cycleId },
    });
    return res.data;
  },
};
