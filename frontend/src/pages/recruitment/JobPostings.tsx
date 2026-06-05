import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Box,
  Button,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  IconButton,
  Tooltip,
  CircularProgress,
  alpha,
} from '@mui/material';
import {
  Add as AddIcon,
  LocationOn as LocationIcon,
  Business as BusinessIcon,
  People as PeopleIcon,
  CalendarToday as CalendarIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
  Pause as PauseIcon,
  PlayArrow as PlayIcon,
  CheckCircle as ActiveIcon,
} from '@mui/icons-material';
import { recruitmentApi, CreateJobPostingData } from '@/api/recruitment.api';
import PageHeader from '@/components/ui/PageHeader';
import { toast } from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';

const jobStatusColors: Record<string, 'default' | 'primary' | 'warning' | 'error'> = {
  draft: 'default',
  open: 'primary',
  paused: 'warning',
  closed: 'error',
};

const jobStatuses = ['draft', 'open', 'paused', 'closed'];

export default function JobPostings() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [formData, setFormData] = useState<CreateJobPostingData>({
    title: '',
    department_id: '', // Using department UUID from backend or pre-seeded ones
    description: '',
    requirements: [''],
    preferred_skills: [''],
    location: '',
    employment_type: 'full_time',
    salary_range_min: undefined,
    salary_range_max: undefined,
    openings_count: 1,
    deadline: '',
  });

  // Query jobs
  const { data, isLoading } = useQuery({
    queryKey: ['job-postings', statusFilter],
    queryFn: () => recruitmentApi.listJobPostings({ status: statusFilter !== 'all' ? statusFilter : undefined }),
  });

  // Mutation to create a job
  const createMutation = useMutation({
    mutationFn: recruitmentApi.createJobPosting,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['job-postings'] });
      toast.success('Job posting created successfully!');
      setIsCreateOpen(false);
      // Reset form
      setFormData({
        title: '',
        department_id: '',
        description: '',
        requirements: [''],
        preferred_skills: [''],
        location: '',
        employment_type: 'full_time',
        salary_range_min: undefined,
        salary_range_max: undefined,
        openings_count: 1,
        deadline: '',
      });
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to create job posting.');
    },
  });

  // Mutation to update job status
  const updateStatusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      recruitmentApi.updateJobPosting(id, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['job-postings'] });
      toast.success('Job status updated successfully!');
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to update job status.');
    },
  });

  const handleCreateSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.title || !formData.description || !formData.location) {
      toast.error('Please fill in all required fields.');
      return;
    }
    // Clean up requirements and skills lists
    const requirements = formData.requirements.filter((r) => r.trim() !== '');
    const preferred_skills = formData.preferred_skills.filter((s) => s.trim() !== '');

    // For demonstration, use a default department UUID if empty
    // (the backend checks department_id, which needs to be a valid UUID in the DB)
    const department_id = formData.department_id || '9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d';

    createMutation.mutate({
      ...formData,
      department_id,
      requirements,
      preferred_skills,
    });
  };

  const handleArrayChange = (
    field: 'requirements' | 'preferred_skills',
    index: number,
    value: string
  ) => {
    const list = [...formData[field]];
    list[index] = value;
    setFormData((prev) => ({ ...prev, [field]: list }));
  };

  const addArrayItem = (field: 'requirements' | 'preferred_skills') => {
    setFormData((prev) => ({ ...prev, [field]: [...prev[field], ''] }));
  };

  const removeArrayItem = (field: 'requirements' | 'preferred_skills', index: number) => {
    const list = [...formData[field]];
    if (list.length > 1) {
      list.splice(index, 1);
      setFormData((prev) => ({ ...prev, [field]: list }));
    }
  };

  return (
    <Box>
      <PageHeader
        title="Job Postings"
        subtitle="Create, manage, and monitor employment opportunities and candidate pipelines."
        action={
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={() => setIsCreateOpen(true)}
            sx={{
              background: 'linear-gradient(135deg, #8B5CF6, #6D28D9)',
              '&:hover': {
                background: 'linear-gradient(135deg, #7C3AED, #5B21B6)',
              },
            }}
          >
            Create Job posting
          </Button>
        }
      />

      {/* Filter Chips */}
      <Box sx={{ mb: 4, display: 'flex', gap: 1.5 }}>
        <Chip
          label="All Jobs"
          onClick={() => setStatusFilter('all')}
          color={statusFilter === 'all' ? 'primary' : 'default'}
          sx={{ cursor: 'pointer' }}
        />
        {jobStatuses.map((status) => (
          <Chip
            key={status}
            label={status.charAt(0).toUpperCase() + status.slice(1)}
            onClick={() => setStatusFilter(status)}
            color={statusFilter === status ? jobStatusColors[status] : 'default'}
            sx={{ cursor: 'pointer' }}
          />
        ))}
      </Box>

      {/* Jobs Grid */}
      {isLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 10 }}>
          <CircularProgress color="secondary" />
        </Box>
      ) : !data?.items || data.items.length === 0 ? (
        <Card
          sx={{
            py: 8,
            textAlign: 'center',
            background: alpha('#1E293B', 0.6),
            border: '1px dashed #334155',
            borderRadius: '16px',
          }}
        >
          <Typography variant="h6" color="text.secondary">
            No job postings found
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Click the 'Create Job Posting' button to add your first job opening.
          </Typography>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {data.items.map((job) => (
            <Grid item xs={12} md={6} lg={4} key={job.id}>
              <Card
                sx={{
                  background: 'linear-gradient(145deg, #1E293B, #0F172A)',
                  borderRadius: '16px',
                  border: '1px solid',
                  borderColor: alpha('#334155', 0.6),
                  boxShadow: '0 4px 20px rgba(0, 0, 0, 0.25)',
                  transition: 'transform 0.2s, border-color 0.2s',
                  position: 'relative',
                  overflow: 'hidden',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    borderColor: '#8B5CF6',
                  },
                }}
              >
                {/* Status bar accent */}
                <Box
                  sx={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    height: '4px',
                    bgcolor:
                      job.status === 'open'
                        ? '#22C55E'
                        : job.status === 'paused'
                        ? '#F59E0B'
                        : job.status === 'closed'
                        ? '#EF4444'
                        : '#64748B',
                  }}
                />

                <CardContent sx={{ pt: 3, pb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Typography variant="h6" fontWeight={700} sx={{ color: '#F8FAFC', flex: 1, mr: 1 }}>
                      {job.title}
                    </Typography>
                    <Chip
                      label={job.status.toUpperCase()}
                      size="small"
                      color={jobStatusColors[job.status]}
                      sx={{ fontWeight: 700, fontSize: '0.65rem' }}
                    />
                  </Box>

                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5, mb: 3 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, color: '#94A3B8' }}>
                      <BusinessIcon fontSize="small" />
                      <Typography variant="body2">{job.department_name || 'General'}</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, color: '#94A3B8' }}>
                      <LocationIcon fontSize="small" />
                      <Typography variant="body2">{job.location}</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, color: '#94A3B8' }}>
                      <PeopleIcon fontSize="small" />
                      <Typography variant="body2">
                        {job.application_count} Applicants / {job.openings_count} Openings
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, color: '#94A3B8' }}>
                      <CalendarIcon fontSize="small" />
                      <Typography variant="body2">
                        Deadline: {job.deadline ? new Date(job.deadline).toLocaleDateString() : 'None'}
                      </Typography>
                    </Box>
                  </Box>

                  {/* Actions */}
                  <Box
                    sx={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      pt: 2,
                      borderTop: '1px solid',
                      borderColor: alpha('#334155', 0.5),
                    }}
                  >
                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={<ViewIcon />}
                      onClick={() => navigate(`/recruitment/pipeline?jobId=${job.id}`)}
                      sx={{
                        borderColor: alpha('#8B5CF6', 0.4),
                        color: '#A78BFA',
                        textTransform: 'none',
                        borderRadius: '8px',
                        '&:hover': {
                          borderColor: '#8B5CF6',
                          background: alpha('#8B5CF6', 0.1),
                        },
                      }}
                    >
                      Pipeline
                    </Button>

                    <Box>
                      {job.status === 'open' ? (
                        <Tooltip title="Pause Job Posting">
                          <IconButton
                            size="small"
                            onClick={() => updateStatusMutation.mutate({ id: job.id, status: 'paused' })}
                            sx={{ color: '#F59E0B', '&:hover': { background: alpha('#F59E0B', 0.1) } }}
                          >
                            <PauseIcon />
                          </IconButton>
                        </Tooltip>
                      ) : (
                        <Tooltip title="Open Job Posting">
                          <IconButton
                            size="small"
                            onClick={() => updateStatusMutation.mutate({ id: job.id, status: 'open' })}
                            sx={{ color: '#22C55E', '&:hover': { background: alpha('#22C55E', 0.1) } }}
                          >
                            <PlayIcon />
                          </IconButton>
                        </Tooltip>
                      )}
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Create Job Posting Dialog */}
      <Dialog
        open={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            background: '#1E293B',
            border: '1px solid #334155',
            borderRadius: '16px',
            boxShadow: '0 20px 60px rgba(0,0,0,0.5)',
          },
        }}
      >
        <DialogTitle sx={{ color: '#F8FAFC', fontWeight: 700, pb: 1 }}>
          Create Job Posting
        </DialogTitle>
        <form onSubmit={handleCreateSubmit}>
          <DialogContent sx={{ pt: 1 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Job Title"
                  required
                  value={formData.title}
                  onChange={(e) => setFormData((p) => ({ ...p, title: e.target.value }))}
                  sx={{ mb: 2 }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Location"
                  required
                  value={formData.location}
                  onChange={(e) => setFormData((p) => ({ ...p, location: e.target.value }))}
                  sx={{ mb: 2 }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  select
                  fullWidth
                  label="Employment Type"
                  value={formData.employment_type}
                  onChange={(e) => setFormData((p) => ({ ...p, employment_type: e.target.value }))}
                  sx={{ mb: 2 }}
                >
                  <MenuItem value="full_time">Full Time</MenuItem>
                  <MenuItem value="part_time">Part Time</MenuItem>
                  <MenuItem value="contract">Contract</MenuItem>
                  <MenuItem value="internship">Internship</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Openings Count"
                  value={formData.openings_count}
                  onChange={(e) => setFormData((p) => ({ ...p, openings_count: parseInt(e.target.value) || 1 }))}
                  sx={{ mb: 2 }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Salary Min"
                  value={formData.salary_range_min || ''}
                  onChange={(e) => setFormData((p) => ({ ...p, salary_range_min: parseFloat(e.target.value) || undefined }))}
                  sx={{ mb: 2 }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Salary Max"
                  value={formData.salary_range_max || ''}
                  onChange={(e) => setFormData((p) => ({ ...p, salary_range_max: parseFloat(e.target.value) || undefined }))}
                  sx={{ mb: 2 }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="date"
                  label="Deadline"
                  InputLabelProps={{ shrink: true }}
                  value={formData.deadline}
                  onChange={(e) => setFormData((p) => ({ ...p, deadline: e.target.value }))}
                  sx={{ mb: 2 }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Department (Optional UUID)"
                  value={formData.department_id}
                  placeholder="e.g. 9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"
                  onChange={(e) => setFormData((p) => ({ ...p, department_id: e.target.value }))}
                  sx={{ mb: 2 }}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={4}
                  label="Job Description"
                  required
                  value={formData.description}
                  onChange={(e) => setFormData((p) => ({ ...p, description: e.target.value }))}
                  sx={{ mb: 2 }}
                />
              </Grid>

              {/* Requirements Dynamic List */}
              <Grid item xs={12}>
                <Typography variant="subtitle2" sx={{ color: '#F8FAFC', mb: 1 }}>
                  Requirements
                </Typography>
                {formData.requirements.map((req, idx) => (
                  <Box key={idx} sx={{ display: 'flex', gap: 1, mb: 1 }}>
                    <TextField
                      fullWidth
                      size="small"
                      placeholder={`Requirement #${idx + 1}`}
                      value={req}
                      onChange={(e) => handleArrayChange('requirements', idx, e.target.value)}
                    />
                    <Button
                      variant="outlined"
                      color="error"
                      onClick={() => removeArrayItem('requirements', idx)}
                      disabled={formData.requirements.length <= 1}
                    >
                      Delete
                    </Button>
                  </Box>
                ))}
                <Button size="small" onClick={() => addArrayItem('requirements')} sx={{ color: '#A78BFA' }}>
                  + Add Requirement
                </Button>
              </Grid>

              {/* Preferred Skills Dynamic List */}
              <Grid item xs={12} sx={{ mt: 2 }}>
                <Typography variant="subtitle2" sx={{ color: '#F8FAFC', mb: 1 }}>
                  Preferred Skills
                </Typography>
                {formData.preferred_skills.map((skill, idx) => (
                  <Box key={idx} sx={{ display: 'flex', gap: 1, mb: 1 }}>
                    <TextField
                      fullWidth
                      size="small"
                      placeholder={`Skill #${idx + 1}`}
                      value={skill}
                      onChange={(e) => handleArrayChange('preferred_skills', idx, e.target.value)}
                    />
                    <Button
                      variant="outlined"
                      color="error"
                      onClick={() => removeArrayItem('preferred_skills', idx)}
                      disabled={formData.preferred_skills.length <= 1}
                    >
                      Delete
                    </Button>
                  </Box>
                ))}
                <Button size="small" onClick={() => addArrayItem('preferred_skills')} sx={{ color: '#A78BFA' }}>
                  + Add Preferred Skill
                </Button>
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions sx={{ px: 3, pb: 3 }}>
            <Button
              onClick={() => setIsCreateOpen(false)}
              sx={{ color: '#94A3B8', '&:hover': { background: alpha('#334155', 0.3) } }}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="contained"
              disabled={createMutation.isPending}
              sx={{
                background: 'linear-gradient(135deg, #8B5CF6, #6D28D9)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #7C3AED, #5B21B6)',
                },
              }}
            >
              {createMutation.isPending ? 'Creating...' : 'Create Job'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
}
