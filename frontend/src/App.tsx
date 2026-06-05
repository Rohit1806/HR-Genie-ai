import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import AppShell from './components/layout/AppShell';
// Auth pages
import Login from './pages/auth/Login';
import ForgotPassword from './pages/auth/ForgotPassword';
import ResetPassword from './pages/auth/ResetPassword';
// Dashboard
import DashboardRouter from './pages/dashboard/DashboardRouter';
// Employees
import EmployeeDirectory from './pages/employees/EmployeeDirectory';
import EmployeeProfile from './pages/employees/EmployeeProfile';
import OnboardingWizard from './pages/employees/OnboardingWizard';
// Recruitment
import JobPostings from './pages/recruitment/JobPostings';
import CandidatePipeline from './pages/recruitment/CandidatePipeline';
import VoiceScreening from './pages/recruitment/VoiceScreening';
// Attendance
import MyAttendance from './pages/attendance/MyAttendance';
import TeamAttendance from './pages/attendance/TeamAttendance';
// Leaves
import MyLeaves from './pages/leaves/MyLeaves';
import ApplyLeave from './pages/leaves/ApplyLeave';
import ApprovalQueue from './pages/leaves/ApprovalQueue';
// Payroll
import PayrollDashboard from './pages/payroll/PayrollDashboard';
import Payslips from './pages/payroll/Payslips';
// Performance
import Goals from './pages/performance/Goals';
import Reviews from './pages/performance/Reviews';
import AIInsights from './pages/performance/AIInsights';
// Analytics & Settings
import AnalyticsDashboard from './pages/analytics/AnalyticsDashboard';
import Settings from './pages/settings/Settings';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/login" element={<Login />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/reset-password" element={<ResetPassword />} />

      {/* Protected */}
      <Route path="/" element={<ProtectedRoute><AppShell /></ProtectedRoute>}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardRouter />} />
        <Route path="employees" element={<EmployeeDirectory />} />
        <Route path="employees/new" element={<OnboardingWizard />} />
        <Route path="employees/:id" element={<EmployeeProfile />} />
        <Route path="recruitment" element={<JobPostings />} />
        <Route path="recruitment/pipeline" element={<CandidatePipeline />} />
        <Route path="recruitment/voice-screening" element={<VoiceScreening />} />
        <Route path="attendance" element={<MyAttendance />} />
        <Route path="attendance/team" element={<TeamAttendance />} />
        <Route path="leaves" element={<MyLeaves />} />
        <Route path="leaves/apply" element={<ApplyLeave />} />
        <Route path="leaves/approvals" element={<ApprovalQueue />} />
        <Route path="payroll" element={<PayrollDashboard />} />
        <Route path="payroll/payslips" element={<Payslips />} />
        <Route path="performance/goals" element={<Goals />} />
        <Route path="performance/reviews" element={<Reviews />} />
        <Route path="performance/ai-insights" element={<AIInsights />} />
        <Route path="analytics" element={<AnalyticsDashboard />} />
        <Route path="settings" element={<Settings />} />
      </Route>

      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
