import React, { useState, useEffect } from 'react';
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
  CircularProgress,
  IconButton,
  Slider,
  alpha,
  LinearProgress,
  Divider,
} from '@mui/material';
import {
  Add as AddIcon,
  TrackChanges as TargetIcon,
  CalendarToday as CalendarIcon,
  CheckCircle as CompleteIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';
import { performanceApi, CreateGoalData, UpdateGoalData } from '@/api/performance.api';
import PageHeader from '@/components/ui/PageHeader';
import StatusPill from '@/components/ui/StatusPill';
import { toast } from 'react-hot-toast';

export default function Goals() {
  const queryClient = useQueryClient();
  const [selectedCycleId, setSelectedCycleId] = useState<string>('');
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [formData, setFormData] = useState<CreateGoalData>({
    cycle_id: '',
    title: '',
    description: '',
    key_results: [{ title: '', target: 100, unit: '%' }],
    weightage: 10,
    due_date: '',
  });

  // Query performance cycles
  const { data: cyclesData, isLoading: isLoadingCycles } = useQuery({
    queryKey: ['performance-cycles'],
    queryFn: () => performanceApi.listCycles(),
  });

  // Set first cycle as active by default
  useEffect(() => {
    if (!selectedCycleId && cyclesData?.items && cyclesData.items.length > 0) {
      setSelectedCycleId(cyclesData.items[0].id);
    }
  }, [cyclesData, selectedCycleId]);

  // Query goals
  const { data: goals, isLoading: isLoadingGoals } = useQuery({
    queryKey: ['my-goals', selectedCycleId],
    queryFn: () => performanceApi.getMyGoals(selectedCycleId),
    enabled: !!selectedCycleId,
  });

  // Mutations
  const createMutation = useMutation({
    mutationFn: performanceApi.createGoal,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-goals', selectedCycleId] });
      toast.success('Goal created successfully!');
      setIsCreateOpen(false);
      setFormData({
        cycle_id: selectedCycleId,
        title: '',
        description: '',
        key_results: [{ title: '', target: 100, unit: '%' }],
        weightage: 10,
        due_date: '',
      });
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to create goal.');
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateGoalData }) =>
      performanceApi.updateGoal(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-goals', selectedCycleId] });
      toast.success('Goal progress updated!');
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to update goal progress.');
    },
  });

  const handleCreateSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.title || !formData.due_date) {
      toast.error('Please fill in all required fields.');
      return;
    }
    // Clean key results
    const key_results = formData.key_results.filter((kr) => kr.title.trim() !== '');
    if (key_results.length === 0) {
      toast.error('Please add at least one Key Result.');
      return;
    }

    createMutation.mutate({
      ...formData,
      cycle_id: selectedCycleId,
      key_results,
    });
  };

  const handleKRChange = (index: number, field: string, value: any) => {
    const list = [...formData.key_results];
    list[index] = { ...list[index], [field]: value };
    setFormData((prev) => ({ ...prev, key_results: list }));
  };

  const addKRItem = () => {
    setFormData((prev) => ({
      ...prev,
      key_results: [...prev.key_results, { title: '', target: 100, unit: '%' }],
    }));
  };

  const removeKRItem = (index: number) => {
    const list = [...formData.key_results];
    if (list.length > 1) {
      list.splice(index, 1);
      setFormData((prev) => ({ ...prev, key_results: list }));
    }
  };

  const handleProgressChange = (goal: any, krIndex: number, newVal: number) => {
    const updatedKrs = [...goal.key_results];
    updatedKrs[krIndex] = { ...updatedKrs[krIndex], current: newVal };

    // Automatically complete goal if all key results are met
    const allDone = updatedKrs.every((kr) => kr.current >= kr.target);
    const status = allDone ? 'completed' : 'in_progress';

    updateMutation.mutate({
      id: goal.id,
      data: {
        key_results: updatedKrs,
        status: status,
      },
    });
  };

  // Compute overall completion of all goals
  const computeGoalCompletion = (goal: any) => {
    if (!goal.key_results || goal.key_results.length === 0) return 0;
    const totals = goal.key_results.map((kr: any) => Math.min(100, (kr.current / kr.target) * 100));
    return Math.round(totals.reduce((a: number, b: number) => a + b, 0) / totals.length);
  };

  return (
    <Box>
      <PageHeader
        title="Goals & Targets"
        subtitle="Define, review, and track key performance targets (OKRs) for the active cycle."
        action={
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={() => setIsCreateOpen(true)}
            disabled={!selectedCycleId}
            sx={{
              background: 'linear-gradient(135deg, #8B5CF6, #6D28D9)',
              '&:hover': {
                background: 'linear-gradient(135deg, #7C3AED, #5B21B6)',
              },
            }}
          >
            Create Goal
          </Button>
        }
      />

      {/* Select Performance Cycle */}
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

      {/* Goals List */}
      {isLoadingGoals ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress color="secondary" />
        </Box>
      ) : !goals || goals.length === 0 ? (
        <Card
          sx={{
            py: 8,
            textAlign: 'center',
            background: alpha('#1E293B', 0.6),
            border: '1px dashed #334155',
            borderRadius: '16px',
          }}
        >
          <Typography color="text.secondary">No performance goals set for this cycle yet.</Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Click 'Create Goal' to outline your first targets.
          </Typography>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {goals.map((goal) => {
            const completion = computeGoalCompletion(goal);
            return (
              <Grid item xs={12} key={goal.id}>
                <Card
                  sx={{
                    background: 'linear-gradient(145deg, #1E293B, #0F172A)',
                    border: '1px solid #334155',
                    borderRadius: '16px',
                    transition: 'border-color 0.2s',
                    '&:hover': { borderColor: '#8B5CF6' },
                  }}
                >
                  <CardContent sx={{ p: 3 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                      <Box>
                        <Typography variant="h6" fontWeight={700} sx={{ color: '#F8FAFC' }}>
                          {goal.title}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                          {goal.description || 'No description provided.'}
                        </Typography>
                      </Box>

                      <Box sx={{ display: 'flex', gap: 1.5, alignItems: 'center' }}>
                        <Chip
                          label={`WEIGHT: ${goal.weightage}%`}
                          size="small"
                          sx={{
                            fontWeight: 700,
                            bgcolor: alpha('#8B5CF6', 0.15),
                            color: '#A78BFA',
                          }}
                        />
                        <StatusPill status={goal.status} />
                      </Box>
                    </Box>

                    {/* Progress Slider */}
                    <Box sx={{ mb: 4 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="caption" color="text.secondary">
                          Goal Progress
                        </Typography>
                        <Typography variant="caption" fontWeight={700} sx={{ color: '#8B5CF6' }}>
                          {completion}% Completed
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={completion}
                        sx={{
                          height: 8,
                          borderRadius: 4,
                          bgcolor: '#1E293B',
                          '& .MuiLinearProgress-bar': {
                            background: 'linear-gradient(90deg, #8B5CF6, #10B981)',
                          },
                        }}
                      />
                    </Box>

                    {/* Key Results Checklist */}
                    <Typography variant="subtitle2" sx={{ color: '#F8FAFC', mb: 2, fontWeight: 700 }}>
                      Key Results Progress Tracking
                    </Typography>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
                      {goal.key_results.map((kr: any, idx: number) => (
                        <Box
                          key={idx}
                          sx={{
                            p: 2,
                            background: '#0F172A',
                            border: '1px solid #1E293B',
                            borderRadius: '10px',
                          }}
                        >
                          <Grid container spacing={2} alignItems="center">
                            <Grid item xs={12} sm={4}>
                              <Typography variant="body2" fontWeight={600} sx={{ color: '#E2E8F0' }}>
                                {kr.title}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                Target: {kr.target} {kr.unit || '%'}
                              </Typography>
                            </Grid>
                            <Grid item xs={12} sm={6}>
                              <Slider
                                value={kr.current || 0}
                                min={0}
                                max={kr.target}
                                valueLabelDisplay="auto"
                                onChangeCommitted={(_, val) => handleProgressChange(goal, idx, val as number)}
                                sx={{ color: '#8B5CF6' }}
                              />
                            </Grid>
                            <Grid item xs={12} sm={2}>
                              <Box sx={{ textAlign: 'right' }}>
                                <Typography variant="body2" fontWeight={700} sx={{ color: '#10B981' }}>
                                  {kr.current || 0} / {kr.target} {kr.unit || '%'}
                                </Typography>
                              </Box>
                            </Grid>
                          </Grid>
                        </Box>
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            );
          })}
        </Grid>
      )}

      {/* Create Goal Dialog */}
      <Dialog
        open={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        maxWidth="sm"
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
        <DialogTitle sx={{ color: '#F8FAFC', fontWeight: 700 }}>Create Cycle Goal</DialogTitle>
        <form onSubmit={handleCreateSubmit}>
          <DialogContent>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Goal Title"
                  required
                  value={formData.title}
                  onChange={(e) => setFormData((p) => ({ ...p, title: e.target.value }))}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={2}
                  label="Description"
                  value={formData.description}
                  onChange={(e) => setFormData((p) => ({ ...p, description: e.target.value }))}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="number"
                  label="Weightage (%)"
                  required
                  value={formData.weightage}
                  onChange={(e) => setFormData((p) => ({ ...p, weightage: parseFloat(e.target.value) || 10 }))}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="date"
                  label="Due Date"
                  InputLabelProps={{ shrink: true }}
                  required
                  value={formData.due_date}
                  onChange={(e) => setFormData((p) => ({ ...p, due_date: e.target.value }))}
                />
              </Grid>

              {/* Dynamic Key Results List */}
              <Grid item xs={12}>
                <Divider sx={{ borderColor: '#334155', my: 1.5 }} />
                <Typography variant="subtitle2" sx={{ color: '#F8FAFC', mb: 1 }}>
                  Key Results Definition
                </Typography>
                {formData.key_results.map((kr, idx) => (
                  <Box key={idx} sx={{ display: 'flex', gap: 1, mb: 1 }}>
                    <TextField
                      fullWidth
                      size="small"
                      label="KR Metric Title"
                      placeholder="e.g. Close support tickets"
                      value={kr.title}
                      onChange={(e) => handleKRChange(idx, 'title', e.target.value)}
                    />
                    <TextField
                      size="small"
                      type="number"
                      label="Target"
                      sx={{ width: 100 }}
                      value={kr.target}
                      onChange={(e) => handleKRChange(idx, 'target', parseFloat(e.target.value) || 100)}
                    />
                    <IconButton
                      color="error"
                      onClick={() => removeKRItem(idx)}
                      disabled={formData.key_results.length <= 1}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                ))}
                <Button size="small" onClick={addKRItem} sx={{ color: '#A78BFA' }}>
                  + Add Key Result
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
                '&:hover': { background: 'linear-gradient(135deg, #7C3AED, #5B21B6)' },
              }}
            >
              {createMutation.isPending ? 'Creating...' : 'Create Goal'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
}
