export interface PerformanceCycle {
  id: string;
  name: string;
  cycle_type: string;
  start_date: string;
  end_date: string;
  review_start: string;
  review_end: string;
  status: CycleStatus;
}

export interface Goal {
  id: string;
  cycle_id: string;
  title: string;
  description: string;
  key_results: KeyResult[];
  weightage: number;
  status: GoalStatus;
  due_date: string;
  created_at: string;
}

export interface KeyResult {
  title: string;
  target: number;
  current: number;
  unit: string;
}

export interface PerformanceReview {
  id: string;
  cycle_id: string;
  employee_name: string;
  reviewer_name: string;
  review_type: string;
  ratings: Record<string, number>;
  feedback: string;
  overall_score: number;
  ai_summary: string | null;
  created_at: string;
}

export interface PerformanceScore {
  id: string;
  cycle_name: string;
  goal_score: number | null;
  self_score: number | null;
  manager_score: number | null;
  final_score: number | null;
  ai_promotion_score: number | null;
  ai_attrition_risk: number | null;
}

export type CycleStatus = 'upcoming' | 'active' | 'review' | 'completed';
export type GoalStatus = 'not_started' | 'in_progress' | 'completed' | 'deferred';
