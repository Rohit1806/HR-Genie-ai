export interface JobPostingSummary {
  id: string;
  title: string;
  department_name: string;
  location: string;
  status: JobStatus;
  openings_count: number;
  application_count: number;
  deadline: string;
  created_at: string;
}

export interface ApplicationSummary {
  id: string;
  candidate_name: string;
  candidate_email: string;
  stage: ApplicationStage;
  applied_at: string;
  overall_score: number | null;
}

export interface AIEvaluation {
  fit_score: number;
  skill_match_score: number;
  experience_score: number;
  overall_score: number;
  strengths: string[];
  weaknesses: string[];
  ai_summary: string;
  recommendation: string;
  confidence: number;
}

export interface CandidateRanking {
  application_id: string;
  candidate_name: string;
  overall_score: number;
  fit_score: number;
  recommendation: string;
  rank: number;
}

export type JobStatus = 'draft' | 'open' | 'paused' | 'closed';
export type ApplicationStage = 'applied' | 'ai_screening' | 'shortlisted' | 'interview' | 'technical' | 'hr_round' | 'offered' | 'hired' | 'rejected';
