import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  TextField,
  MenuItem,
  CircularProgress,
  Slider,
  Tabs,
  Tab,
  alpha,
  Divider,
} from '@mui/material';
import {
  RateReview as ReviewIcon,
  Send as SubmitIcon,
} from '@mui/icons-material';
import { performanceApi, SelfReviewData, ManagerReviewData } from '@/api/performance.api';
import { employeesApi } from '@/api/employees.api';
import PageHeader from '@/components/ui/PageHeader';
import { useAuthStore } from '@/store/authStore';
import { toast } from 'react-hot-toast';

const competencies = [
  { key: 'technical_capability', label: 'Technical / Functional Capability' },
  { key: 'collaboration', label: 'Collaboration & Teamwork' },
  { key: 'innovation', label: 'Innovation & Problem Solving' },
  { key: 'delivery', label: 'Execution & Delivery Speed' },
];

export default function Reviews() {
  const queryClient = useQueryClient();
  const currentUser = useAuthStore((s) => s.user);
  const isManager = currentUser?.role === 'admin' || currentUser?.role === 'senior_manager';

  const [activeTab, setActiveTab] = useState(0);
  const [selectedCycleId, setSelectedCycleId] = useState('');

  // Self evaluation form state
  const [selfRatings, setSelfRatings] = useState<Record<string, number>>({
    technical_capability: 3,
    collaboration: 3,
    innovation: 3,
    delivery: 3,
  });
  const [selfFeedback, setSelfFeedback] = useState('');

  // Manager evaluation form state
  const [targetEmployeeId, setTargetEmployeeId] = useState('');
  const [mgrRatings, setMgrRatings] = useState<Record<string, number>>({
    technical_capability: 3,
    collaboration: 3,
    innovation: 3,
    delivery: 3,
  });
  const [mgrFeedback, setMgrFeedback] = useState('');
  const [mgrOverall, setMgrOverall] = useState(3.0);

  // Queries
  const { data: cyclesData, isLoading: isLoadingCycles } = useQuery({
    queryKey: ['performance-cycles'],
    queryFn: () => performanceApi.listCycles(),
  });

  const { data: employeesData, isLoading: isLoadingEmployees } = useQuery({
    queryKey: ['employees-dropdown'],
    queryFn: () => employeesApi.listEmployees({ page_size: 100 }),
    enabled: isManager,
  });

  useEffect(() => {
    if (!selectedCycleId && cyclesData?.items && cyclesData.items.length > 0) {
      setSelectedCycleId(cyclesData.items[0].id);
    }
  }, [cyclesData, selectedCycleId]);

  // Mutations
  const selfReviewMutation = useMutation({
    mutationFn: performanceApi.submitSelfReview,
    onSuccess: () => {
      toast.success('Self-review submitted successfully!');
      setSelfFeedback('');
      queryClient.invalidateQueries({ queryKey: ['performance-scores'] });
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to submit self review.');
    },
  });

  const managerReviewMutation = useMutation({
    mutationFn: performanceApi.submitManagerReview,
    onSuccess: () => {
      toast.success('Manager evaluation submitted!');
      setTargetEmployeeId('');
      setMgrFeedback('');
      queryClient.invalidateQueries({ queryKey: ['performance-scores'] });
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to submit manager evaluation.');
    },
  });

  const handleSelfSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCycleId || !selfFeedback) {
      toast.error('Feedback comment is required.');
      return;
    }
    selfReviewMutation.mutate({
      cycle_id: selectedCycleId,
      ratings: selfRatings,
      feedback: selfFeedback,
      achievements: [],
      challenges: [],
    });
  };

  const handleManagerSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCycleId || !targetEmployeeId || !mgrFeedback) {
      toast.error('Please fill in all evaluation fields.');
      return;
    }
    managerReviewMutation.mutate({
      cycle_id: selectedCycleId,
      employee_id: targetEmployeeId,
      ratings: mgrRatings,
      feedback: mgrFeedback,
      strengths: [],
      areas_of_improvement: [],
      overall_score: mgrOverall,
    });
  };

  return (
    <Box>
      <PageHeader
        title="Performance Reviews"
        subtitle="Complete self-evaluations and manager feedback reviews for the cycle."
      />

      <Box sx={{ borderBottom: 1, borderColor: '#1E293B', mb: 4 }}>
        <Tabs
          value={activeTab}
          onChange={(_, val) => setActiveTab(val)}
          sx={{
            '& .MuiTab-root': { color: '#64748B', fontWeight: 600 },
            '& .Mui-selected': { color: '#A78BFA' },
            '& .MuiTabs-indicator': { bgcolor: '#8B5CF6' },
          }}
        >
          <Tab label="Self Review" />
          {isManager && <Tab label="Team Evaluations" />}
        </Tabs>
      </Box>

      {/* Select active cycle */}
      <Box sx={{ mb: 4, display: 'flex', gap: 2, alignItems: 'center' }}>
        <Typography variant="body1" sx={{ color: '#F8FAFC', fontWeight: 600 }}>
          Review Cycle:
        </Typography>
        {isLoadingCycles ? (
          <CircularProgress size={20} />
        ) : (
          <TextField
            select
            size="small"
            value={selectedCycleId}
            onChange={(e) => setSelectedCycleId(e.target.value)}
            sx={{ minWidth: 260, background: alpha('#1E293B', 0.6), borderRadius: '8px' }}
          >
            {(cyclesData?.items || []).map((c) => (
              <MenuItem key={c.id} value={c.id}>
                {c.name} ({c.cycle_type})
              </MenuItem>
            ))}
          </TextField>
        )}
      </Box>

      {/* Tab 0: Self Review */}
      {activeTab === 0 && (
        <Card
          sx={{
            background: 'linear-gradient(135deg, #1E293B, #0F172A)',
            border: '1px solid #334155',
            borderRadius: '16px',
            p: 3,
          }}
        >
          <CardContent>
            <form onSubmit={handleSelfSubmit}>
              <Typography variant="h6" fontWeight={700} sx={{ color: '#F8FAFC', mb: 4 }}>
                Self Assessment Form
              </Typography>

              <Grid container spacing={4}>
                {/* Competencies */}
                <Grid item xs={12} md={6}>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3.5 }}>
                    {competencies.map((comp) => (
                      <Box key={comp.key}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                          <Typography variant="body2" fontWeight={600} sx={{ color: '#E2E8F0' }}>
                            {comp.label}
                          </Typography>
                          <Typography variant="body2" fontWeight={700} sx={{ color: '#8B5CF6' }}>
                            {selfRatings[comp.key]} / 5
                          </Typography>
                        </Box>
                        <Slider
                          value={selfRatings[comp.key]}
                          min={1}
                          max={5}
                          step={1}
                          marks
                          onChange={(_, val) => setSelfRatings((p) => ({ ...p, [comp.key]: val as number }))}
                          sx={{ color: '#8B5CF6' }}
                        />
                      </Box>
                    ))}
                  </Box>
                </Grid>

                {/* Feedback */}
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    multiline
                    rows={8}
                    label="Self Assessment Narrative"
                    placeholder="Describe your achievements, completed tasks, goals met, and challenges faced during this performance period."
                    required
                    value={selfFeedback}
                    onChange={(e) => setSelfFeedback(e.target.value)}
                    sx={{ mb: 4 }}
                  />

                  <Button
                    type="submit"
                    variant="contained"
                    startIcon={<SubmitIcon />}
                    disabled={selfReviewMutation.isPending}
                    sx={{
                      background: 'linear-gradient(135deg, #8B5CF6, #6D28D9)',
                      textTransform: 'none',
                      borderRadius: '8px',
                      float: 'right',
                      '&:hover': { background: 'linear-gradient(135deg, #7C3AED, #5B21B6)' },
                    }}
                  >
                    {selfReviewMutation.isPending ? 'Submitting...' : 'Submit Evaluation'}
                  </Button>
                </Grid>
              </Grid>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Tab 1: Team Evaluations */}
      {activeTab === 1 && isManager && (
        <Card
          sx={{
            background: 'linear-gradient(135deg, #1E293B, #0F172A)',
            border: '1px solid #334155',
            borderRadius: '16px',
            p: 3,
          }}
        >
          <CardContent>
            <form onSubmit={handleManagerSubmit}>
              <Typography variant="h6" fontWeight={700} sx={{ color: '#F8FAFC', mb: 3 }}>
                Manager Evaluation Form
              </Typography>

              <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                  {isLoadingEmployees ? (
                    <CircularProgress size={20} />
                  ) : (
                    <TextField
                      select
                      fullWidth
                      label="Select Employee"
                      required
                      value={targetEmployeeId}
                      onChange={(e) => setTargetEmployeeId(e.target.value)}
                    >
                      {(employeesData?.items || []).map((emp) => (
                        <MenuItem key={emp.id} value={emp.id}>
                          {emp.full_name} ({emp.employee_code})
                        </MenuItem>
                      ))}
                    </TextField>
                  )}
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    type="number"
                    label="Overall Assessment Score (1.0 – 5.0)"
                    required
                    inputProps={{ step: 0.1, min: 1.0, max: 5.0 }}
                    value={mgrOverall}
                    onChange={(e) => setMgrOverall(parseFloat(e.target.value) || 3.0)}
                  />
                </Grid>

                <Grid item xs={12}>
                  <Divider sx={{ borderColor: '#334155', my: 2 }} />
                </Grid>

                {/* Competencies */}
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle1" fontWeight={600} sx={{ color: '#F8FAFC', mb: 3 }}>
                    Functional Ratings
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3.5 }}>
                    {competencies.map((comp) => (
                      <Box key={comp.key}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                          <Typography variant="body2" fontWeight={600} sx={{ color: '#E2E8F0' }}>
                            {comp.label}
                          </Typography>
                          <Typography variant="body2" fontWeight={700} sx={{ color: '#8B5CF6' }}>
                            {mgrRatings[comp.key]} / 5
                          </Typography>
                        </Box>
                        <Slider
                          value={mgrRatings[comp.key]}
                          min={1}
                          max={5}
                          step={1}
                          marks
                          onChange={(_, val) => setMgrRatings((p) => ({ ...p, [comp.key]: val as number }))}
                          sx={{ color: '#8B5CF6' }}
                        />
                      </Box>
                    ))}
                  </Box>
                </Grid>

                {/* Feedback */}
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle1" fontWeight={600} sx={{ color: '#F8FAFC', mb: 3 }}>
                    Written Appraisal Remarks
                  </Typography>
                  <TextField
                    fullWidth
                    multiline
                    rows={8}
                    label="Manager Evaluation Narrative"
                    placeholder="Provide actionable feedback, describe areas of strength, and target milestones for improvement."
                    required
                    value={mgrFeedback}
                    onChange={(e) => setMgrFeedback(e.target.value)}
                    sx={{ mb: 4 }}
                  />

                  <Button
                    type="submit"
                    variant="contained"
                    startIcon={<ReviewIcon />}
                    disabled={managerReviewMutation.isPending}
                    sx={{
                      background: 'linear-gradient(135deg, #10B981, #059669)',
                      textTransform: 'none',
                      borderRadius: '8px',
                      float: 'right',
                      '&:hover': { background: 'linear-gradient(135deg, #059669, #047857)' },
                    }}
                  >
                    {managerReviewMutation.isPending ? 'Submitting...' : 'Submit Evaluation'}
                  </Button>
                </Grid>
              </Grid>
            </form>
          </CardContent>
        </Card>
      )}
    </Box>
  );
}
