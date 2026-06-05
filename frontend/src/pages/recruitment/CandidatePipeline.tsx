import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  Box,
  TextField,
  MenuItem,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Grid,
  Avatar,
  Chip,
  IconButton,
  alpha,
  Divider,
} from '@mui/material';
import {
  Close as CloseIcon,
  Phone as PhoneIcon,
  Email as EmailIcon,
  RecordVoiceOver as VoiceIcon,
  PictureAsPdf as PdfIcon,
  TrendingUp as PromoteIcon,
  CheckCircle as SuccessIcon,
} from '@mui/icons-material';
import { recruitmentApi } from '@/api/recruitment.api';
import PageHeader from '@/components/ui/PageHeader';
import CandidateKanban from '@/components/recruitment/CandidateKanban';
import AIScoreCard from '@/components/ai/AIScoreCard';
import { toast } from 'react-hot-toast';

// Stage mapper
const backendToUiStage: Record<string, string> = {
  applied: 'Applied',
  ai_screening: 'AI Screening',
  shortlisted: 'Shortlisted',
  interview: 'Interview',
  technical: 'Technical',
  hr_round: 'HR Round',
  offered: 'Offered',
  hired: 'Offered', // Map hired to Offered column in UI Kanban
  rejected: 'Applied', // Put rejected in Applied for now or handle as tag
};

const uiToBackendStage: Record<string, string> = {
  'Applied': 'applied',
  'AI Screening': 'ai_screening',
  'Shortlisted': 'shortlisted',
  'Interview': 'interview',
  'Technical': 'technical',
  'HR Round': 'hr_round',
  'Offered': 'offered',
};

export default function CandidatePipeline() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchParams, setSearchParams] = useSearchParams();
  const selectedJobId = searchParams.get('jobId') || '';
  const [selectedCandidateId, setSelectedCandidateId] = useState<string | null>(null);

  // 1. Fetch Job Postings for dropdown selector
  const { data: jobsData, isLoading: isLoadingJobs } = useQuery({
    queryKey: ['job-postings-dropdown'],
    queryFn: () => recruitmentApi.listJobPostings({ status: 'open' }),
  });

  // Set first job posting if none selected
  useEffect(() => {
    if (!selectedJobId && jobsData?.items && jobsData.items.length > 0) {
      setSearchParams({ jobId: jobsData.items[0].id });
    }
  }, [jobsData, selectedJobId, setSearchParams]);

  // 2. Fetch applications for the selected job
  const { data: appsData, isLoading: isLoadingApps } = useQuery({
    queryKey: ['applications', selectedJobId],
    queryFn: () => recruitmentApi.listApplications(selectedJobId),
    enabled: !!selectedJobId,
  });

  // 3. Fetch detailed application details (with AI Eval) for modal
  const { data: detailData, isLoading: isLoadingDetail } = useQuery({
    queryKey: ['application-detail', selectedCandidateId],
    queryFn: () => recruitmentApi.getApplication(selectedCandidateId || ''),
    enabled: !!selectedCandidateId,
  });

  // Mutation to transition stage
  const stageMutation = useMutation({
    mutationFn: ({ id, stage, notes }: { id: string; stage: string; notes?: string }) =>
      recruitmentApi.updateStage(id, stage, notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applications', selectedJobId] });
      queryClient.invalidateQueries({ queryKey: ['application-detail', selectedCandidateId] });
      toast.success('Candidate stage updated successfully!');
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to update candidate stage.');
    },
  });

  const handleJobChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchParams({ jobId: e.target.value });
  };

  const handleStageChange = (candidateId: string, newStageUi: string) => {
    const backendStage = uiToBackendStage[newStageUi];
    if (backendStage) {
      stageMutation.mutate({ id: candidateId, stage: backendStage });
    }
  };

  const handleCandidateClick = (candidate: any) => {
    setSelectedCandidateId(candidate.id);
  };

  // Convert API application summaries to Kanban format
  const kanbanCandidates = (appsData?.items || []).map((app: any) => ({
    id: app.id,
    name: app.candidate_name,
    email: app.candidate_email,
    ai_score: app.overall_score || 0,
    applied_date: app.applied_at || new Date().toISOString(),
    current_stage: backendToUiStage[app.stage] || 'Applied',
  }));

  return (
    <Box>
      <PageHeader
        title="Candidate Pipeline"
        subtitle="Manage candidates through the recruitment stages and analyze AI fit evaluations."
      />

      {/* Select Job Posting Dropdown */}
      <Box sx={{ mb: 4, display: 'flex', gap: 2, alignItems: 'center' }}>
        <Typography variant="body1" sx={{ color: '#F8FAFC', fontWeight: 600 }}>
          Position:
        </Typography>
        {isLoadingJobs ? (
          <CircularProgress size={20} />
        ) : (
          <TextField
            select
            size="small"
            value={selectedJobId}
            onChange={handleJobChange}
            sx={{
              minWidth: 260,
              background: alpha('#1E293B', 0.6),
              borderRadius: '8px',
            }}
          >
            {(jobsData?.items || []).map((job) => (
              <MenuItem key={job.id} value={job.id}>
                {job.title} ({job.department_name})
              </MenuItem>
            ))}
          </TextField>
        )}
      </Box>

      {/* Kanban Board */}
      {isLoadingApps ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 10 }}>
          <CircularProgress color="secondary" />
        </Box>
      ) : selectedJobId ? (
        <CandidateKanban
          candidates={kanbanCandidates}
          onStageChange={handleStageChange}
          onCandidateClick={handleCandidateClick}
        />
      ) : (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <Typography color="text.secondary">Please select a job opening to view the pipeline.</Typography>
        </Box>
      )}

      {/* Candidate Profile Details Dialog */}
      <Dialog
        open={Boolean(selectedCandidateId)}
        onClose={() => setSelectedCandidateId(null)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            background: '#0F172A',
            border: '1px solid #334155',
            borderRadius: '16px',
            boxShadow: '0 25px 50px rgba(0, 0, 0, 0.5)',
          },
        }}
      >
        <DialogTitle
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            color: '#F8FAFC',
            borderBottom: '1px solid #1E293B',
            pb: 2,
          }}
        >
          <Typography variant="h6" fontWeight={700}>
            Candidate Assessment
          </Typography>
          <IconButton onClick={() => setSelectedCandidateId(null)} sx={{ color: '#64748B' }}>
            <CloseIcon />
          </IconButton>
        </DialogTitle>

        <DialogContent sx={{ p: 3 }}>
          {isLoadingDetail ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
              <CircularProgress color="secondary" />
            </Box>
          ) : detailData ? (
            <Grid container spacing={3}>
              {/* Profile Details (Left) */}
              <Grid item xs={12} md={7}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                  <Avatar
                    sx={{
                      width: 56,
                      height: 56,
                      background: 'linear-gradient(135deg, #8B5CF6, #6D28D9)',
                      fontSize: '1.25rem',
                      fontWeight: 700,
                    }}
                  >
                    {detailData.candidate_name.split(' ').map((n: string) => n[0]).join('')}
                  </Avatar>
                  <Box>
                    <Typography variant="h5" fontWeight={700} sx={{ color: '#F8FAFC' }}>
                      {detailData.candidate_name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Applied: {new Date(detailData.applied_at).toLocaleDateString()}
                    </Typography>
                  </Box>
                </Box>

                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mb: 3 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, color: '#94A3B8' }}>
                    <EmailIcon fontSize="small" />
                    <Typography variant="body2">{detailData.candidate_email}</Typography>
                  </Box>
                  {(detailData as any).candidate_phone && (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, color: '#94A3B8' }}>
                      <PhoneIcon fontSize="small" />
                      <Typography variant="body2">{(detailData as any).candidate_phone}</Typography>
                    </Box>
                  )}
                </Box>

                <Divider sx={{ borderColor: '#1E293B', my: 2 }} />

                {/* Resume display */}
                <Typography variant="subtitle2" sx={{ color: '#F8FAFC', mb: 1, fontWeight: 700 }}>
                  Resume & Cover Letter
                </Typography>
                <Box
                  sx={{
                    p: 2,
                    background: '#1E293B',
                    borderRadius: '10px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    mb: 3,
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                    <PdfIcon sx={{ color: '#EF4444', fontSize: 28 }} />
                    <Box>
                      <Typography variant="body2" sx={{ color: '#E2E8F0', fontWeight: 600 }}>
                        Resume.pdf
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Submitted during application
                      </Typography>
                    </Box>
                  </Box>
                  <Button variant="outlined" size="small" sx={{ textTransform: 'none', color: '#A78BFA', borderColor: '#8B5CF6' }}>
                    View PDF
                  </Button>
                </Box>

                <Typography variant="subtitle2" sx={{ color: '#F8FAFC', mb: 1, fontWeight: 700 }}>
                  AI Summary & Recommendation
                </Typography>
                <Typography variant="body2" sx={{ color: '#94A3B8', mb: 3, lineHeight: 1.6 }}>
                  {detailData.ai_evaluation?.ai_summary ||
                    'AI screening has not evaluated this candidate yet. Try triggering voice screening or check again later.'}
                </Typography>

                <Box sx={{ display: 'flex', gap: 2 }}>
                  <Button
                    variant="contained"
                    startIcon={<VoiceIcon />}
                    onClick={() => navigate(`/recruitment/voice-screening?applicationId=${detailData.id}`)}
                    sx={{
                      background: 'linear-gradient(135deg, #A78BFA, #7C3AED)',
                      textTransform: 'none',
                      borderRadius: '8px',
                      '&:hover': {
                        background: 'linear-gradient(135deg, #8B5CF6, #6D28D9)',
                      },
                    }}
                  >
                    AI Voice Screening
                  </Button>
                </Box>
              </Grid>

              {/* AI Scores Column (Right) */}
              <Grid item xs={12} md={5}>
                {detailData.ai_evaluation ? (
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                    <AIScoreCard
                      title="AI Compatibility Score"
                      overallScore={detailData.ai_evaluation.overall_score}
                      subMetrics={[
                        { label: 'Role Fit Score', score: detailData.ai_evaluation.fit_score },
                        { label: 'Skill Match Score', score: detailData.ai_evaluation.skill_match_score },
                        { label: 'Experience Match', score: detailData.ai_evaluation.experience_score },
                      ]}
                    />

                    {/* Strengths & Weaknesses */}
                    <Box
                      sx={{
                        p: 2.5,
                        background: alpha('#1E293B', 0.4),
                        border: '1px solid #334155',
                        borderRadius: '12px',
                      }}
                    >
                      <Typography variant="subtitle2" sx={{ color: '#22C55E', fontWeight: 700, mb: 1.5 }}>
                        Key Strengths
                      </Typography>
                      {detailData.ai_evaluation.strengths.map((str: string, index: number) => (
                        <Box key={index} sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, mb: 1 }}>
                          <PromoteIcon sx={{ color: '#22C55E', fontSize: 16, mt: 0.2 }} />
                          <Typography variant="body2" sx={{ color: '#E2E8F0' }}>
                            {str}
                          </Typography>
                        </Box>
                      ))}

                      <Typography variant="subtitle2" sx={{ color: '#EF4444', fontWeight: 700, mt: 3, mb: 1.5 }}>
                        Areas of Caution
                      </Typography>
                      {detailData.ai_evaluation.weaknesses.map((weak: string, index: number) => (
                        <Box key={index} sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, mb: 1 }}>
                          <CloseIcon sx={{ color: '#EF4444', fontSize: 16, mt: 0.2 }} />
                          <Typography variant="body2" sx={{ color: '#E2E8F0' }}>
                            {weak}
                          </Typography>
                        </Box>
                      ))}
                    </Box>
                  </Box>
                ) : (
                  <Box
                    sx={{
                      p: 4,
                      background: alpha('#1E293B', 0.3),
                      border: '1px dashed #334155',
                      borderRadius: '12px',
                      textAlign: 'center',
                    }}
                  >
                    <Typography color="text.secondary" variant="body2">
                      No AI insights generated yet.
                    </Typography>
                  </Box>
                )}
              </Grid>
            </Grid>
          ) : null}
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3, borderTop: '1px solid #1E293B', pt: 2 }}>
          <Button
            onClick={() => setSelectedCandidateId(null)}
            sx={{ color: '#94A3B8', '&:hover': { background: alpha('#334155', 0.3) } }}
          >
            Close
          </Button>

          {detailData && detailData.stage !== 'rejected' && (
            <Button
              variant="outlined"
              color="error"
              onClick={() => {
                stageMutation.mutate({ id: detailData.id, stage: 'rejected' });
                setSelectedCandidateId(null);
              }}
              sx={{ textTransform: 'none', borderRadius: '8px' }}
            >
              Reject Candidate
            </Button>
          )}

          {detailData && detailData.stage === 'applied' && (
            <Button
              variant="contained"
              onClick={() => {
                stageMutation.mutate({ id: detailData.id, stage: 'ai_screening' });
                setSelectedCandidateId(null);
              }}
              sx={{
                background: 'linear-gradient(135deg, #10B981, #059669)',
                textTransform: 'none',
                borderRadius: '8px',
                '&:hover': {
                  background: 'linear-gradient(135deg, #059669, #047857)',
                },
              }}
            >
              Shortlist for AI screening
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
}
