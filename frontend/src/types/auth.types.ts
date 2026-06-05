export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: UserContext;
}

export interface UserContext {
  id: string;
  company_id: string;
  email: string;
  full_name: string;
  role: 'admin' | 'senior_manager' | 'hr_recruiter' | 'employee';
}

export interface TokenRefreshResponse {
  access_token: string;
  token_type: string;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ResetPasswordRequest {
  token: string;
  new_password: string;
}
