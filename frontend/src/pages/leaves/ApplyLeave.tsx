import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Grid,
  Card,
  CardContent,
  Typography,
  TextField,
  MenuItem,
  CircularProgress,
  alpha,
} from '@mui/material';
import {
  Send as SubmitIcon,
  Cancel as CancelIcon,
} from '@mui/icons-material';
import { leavesApi, ApplyLeaveData } from '@/api/leaves.api';
import PageHeader from '@/components/ui/PageHeader';
import { toast } from 'react-hot-toast';

export default function ApplyLeave() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const currentYear = new Date().getFullYear();

  const [formData, setFormData] = useState<ApplyLeaveData>({
    leave_type_id: '',
    from_date: '',
    to_date: '',
    reason: '',
  });

  // Query leave types
  const { data: leaveTypes, isLoading: isLoadingTypes } = useQuery({
    queryKey: ['leave-types'],
    queryFn: () => leavesApi.getLeaveTypes(),
  });

  // Query balances to display context
  const { data: balances } = useQuery({
    queryKey: ['my-leave-balances', currentYear],
    queryFn: () => leavesApi.getMyBalances(currentYear),
  });

  // Mutation to apply leave
  const applyMutation = useMutation({
    mutationFn: leavesApi.applyLeave,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-leave-requests'] });
      queryClient.invalidateQueries({ queryKey: ['my-leave-balances'] });
      toast.success('Leave applied successfully!');
      navigate('/leaves');
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to apply leave.');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.leave_type_id || !formData.from_date || !formData.to_date || !formData.reason) {
      toast.error('All fields are required.');
      return;
    }
    if (new Date(formData.from_date) > new Date(formData.to_date)) {
      toast.error('From Date cannot be later than To Date.');
      return;
    }
    applyMutation.mutate(formData);
  };

  // Find balance for selected leave type
  const selectedBalance = balances?.find((b) => b.leave_type.id === formData.leave_type_id);
  const availableDays = selectedBalance
    ? selectedBalance.allocated - selectedBalance.used - selectedBalance.pending
    : 0;

  // Calculate requested days
  let requestedDays = 0;
  if (formData.from_date && formData.to_date) {
    const from = new Date(formData.from_date);
    const to = new Date(formData.to_date);
    requestedDays = Math.round((to.getTime() - from.getTime()) / (1000 * 3600 * 24)) + 1;
  }

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto' }}>
      <PageHeader
        title="Apply Leave"
        subtitle="Submit a new request for leave approval to your manager."
      />

      <Card
        sx={{
          background: 'linear-gradient(135deg, #1E293B, #0F172A)',
          border: '1px solid #334155',
          borderRadius: '16px',
          p: 3,
        }}
      >
        <CardContent>
          {isLoadingTypes ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
              <CircularProgress color="secondary" />
            </Box>
          ) : (
            <form onSubmit={handleSubmit}>
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <TextField
                    select
                    fullWidth
                    label="Leave Type"
                    required
                    value={formData.leave_type_id}
                    onChange={(e) => setFormData((p) => ({ ...p, leave_type_id: e.target.value }))}
                  >
                    {(leaveTypes || []).map((t) => (
                      <MenuItem key={t.id} value={t.id}>
                        {t.name} ({t.code})
                      </MenuItem>
                    ))}
                  </TextField>
                </Grid>

                {formData.leave_type_id && (
                  <Grid item xs={12}>
                    <Box
                      sx={{
                        p: 2,
                        background: alpha('#8B5CF6', 0.1),
                        border: '1px solid #8B5CF6',
                        borderRadius: '8px',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                      }}
                    >
                      <Typography variant="body2" sx={{ color: '#E2E8F0' }}>
                        Selected Balance Details:
                      </Typography>
                      <Typography variant="body2" fontWeight={700} sx={{ color: '#A78BFA' }}>
                        {availableDays} Days Available
                      </Typography>
                    </Box>
                  </Grid>
                )}

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    type="date"
                    label="From Date"
                    InputLabelProps={{ shrink: true }}
                    required
                    value={formData.from_date}
                    onChange={(e) => setFormData((p) => ({ ...p, from_date: e.target.value }))}
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    type="date"
                    label="To Date"
                    InputLabelProps={{ shrink: true }}
                    required
                    value={formData.to_date}
                    onChange={(e) => setFormData((p) => ({ ...p, to_date: e.target.value }))}
                  />
                </Grid>

                {requestedDays > 0 && (
                  <Grid item xs={12}>
                    <Typography variant="body2" sx={{ color: '#94A3B8' }}>
                      Total leave days requested:{' '}
                      <strong style={{ color: requestedDays > availableDays ? '#EF4444' : '#10B981' }}>
                        {requestedDays} {requestedDays === 1 ? 'day' : 'days'}
                      </strong>
                    </Typography>
                    {requestedDays > availableDays && (
                      <Typography variant="caption" sx={{ color: '#EF4444', display: 'block', mt: 0.5 }}>
                        Warning: This exceeds your available balance for this leave type!
                      </Typography>
                    )}
                  </Grid>
                )}

                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    multiline
                    rows={4}
                    label="Reason for Leave"
                    required
                    value={formData.reason}
                    onChange={(e) => setFormData((p) => ({ ...p, reason: e.target.value }))}
                  />
                </Grid>

                <Grid item xs={12} sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', mt: 2 }}>
                  <Button
                    variant="outlined"
                    startIcon={<CancelIcon />}
                    onClick={() => navigate('/leaves')}
                    sx={{
                      color: '#94A3B8',
                      borderColor: '#475569',
                      textTransform: 'none',
                      borderRadius: '8px',
                      '&:hover': { background: alpha('#334155', 0.3) },
                    }}
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    variant="contained"
                    startIcon={<SubmitIcon />}
                    disabled={applyMutation.isPending || (requestedDays > 0 && requestedDays > availableDays)}
                    sx={{
                      background: 'linear-gradient(135deg, #8B5CF6, #6D28D9)',
                      textTransform: 'none',
                      borderRadius: '8px',
                      '&:hover': {
                        background: 'linear-gradient(135deg, #7C3AED, #5B21B6)',
                      },
                    }}
                  >
                    {applyMutation.isPending ? 'Submitting...' : 'Apply Leave'}
                  </Button>
                </Grid>
              </Grid>
            </form>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}
