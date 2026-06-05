import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Grid,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  alpha,
} from '@mui/material';
import {
  Add as AddIcon,
  Cancel as CancelIcon,
} from '@mui/icons-material';
import { leavesApi } from '@/api/leaves.api';
import PageHeader from '@/components/ui/PageHeader';
import StatusPill from '@/components/ui/StatusPill';
import { toast } from 'react-hot-toast';

export default function MyLeaves() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const currentYear = new Date().getFullYear();

  // Query balances
  const { data: balances, isLoading: isLoadingBalances } = useQuery({
    queryKey: ['my-leave-balances', currentYear],
    queryFn: () => leavesApi.getMyBalances(currentYear),
  });

  // Query requests
  const { data: requestsData, isLoading: isLoadingRequests } = useQuery({
    queryKey: ['my-leave-requests'],
    queryFn: () => leavesApi.getMyRequests(),
  });

  // Mutation to cancel leave
  const cancelMutation = useMutation({
    mutationFn: leavesApi.cancelLeave,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-leave-requests'] });
      queryClient.invalidateQueries({ queryKey: ['my-leave-balances'] });
      toast.success('Leave request cancelled successfully.');
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to cancel leave request.');
    },
  });

  const handleCancel = (id: string) => {
    if (window.confirm('Are you sure you want to cancel this pending leave request?')) {
      cancelMutation.mutate(id);
    }
  };

  return (
    <Box>
      <PageHeader
        title="My Leaves"
        subtitle="Monitor your leave balances, view submission history, and submit new leave requests."
        action={
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={() => navigate('/leaves/apply')}
            sx={{
              background: 'linear-gradient(135deg, #8B5CF6, #6D28D9)',
              '&:hover': {
                background: 'linear-gradient(135deg, #7C3AED, #5B21B6)',
              },
            }}
          >
            Apply Leave
          </Button>
        }
      />

      {/* Balances Grid */}
      <Typography variant="h6" fontWeight={700} sx={{ color: '#F8FAFC', mb: 2 }}>
        Leave Balances ({currentYear})
      </Typography>

      {isLoadingBalances ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress size={30} color="secondary" />
        </Box>
      ) : !balances || balances.length === 0 ? (
        <Card sx={{ p: 3, mb: 4, background: '#1E293B', border: '1px dashed #334155', textAlign: 'center' }}>
          <Typography color="text.secondary">No leave balances found for this year.</Typography>
        </Card>
      ) : (
        <Grid container spacing={3} sx={{ mb: 5 }}>
          {balances.map((bal: any) => {
            const available = bal.total - bal.used - bal.pending;
            return (
              <Grid item xs={12} sm={6} md={3} key={bal.id || bal.leave_type_id}>
                <Card
                  sx={{
                    background: 'linear-gradient(135deg, #1E293B, #0F172A)',
                    border: '1px solid #334155',
                    borderRadius: '16px',
                    position: 'relative',
                    overflow: 'hidden',
                  }}
                >
                  {/* Color bar */}
                  <Box
                    sx={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      height: '4px',
                      bgcolor: '#8B5CF6',
                    }}
                  />
                  <CardContent sx={{ pt: 3 }}>
                    <Typography variant="subtitle2" color="text.secondary" fontWeight={600} gutterBottom>
                      {bal.leave_type_name}
                    </Typography>
                    <Typography variant="h4" fontWeight={800} sx={{ color: '#F8FAFC', mb: 2 }}>
                      {available} / {bal.total}
                      <Typography variant="caption" sx={{ color: '#94A3B8', ml: 1, fontWeight: 500 }}>
                        Days Available
                      </Typography>
                    </Typography>

                    <Grid container spacing={1} sx={{ pt: 1, borderTop: '1px solid #1E293B' }}>
                      <Grid item xs={6}>
                        <Typography variant="caption" color="text.secondary">
                          Used: <strong>{bal.used}</strong>
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="caption" color="text.secondary">
                          Pending: <strong>{bal.pending}</strong>
                        </Typography>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
            );
          })}
        </Grid>
      )}

      {/* History Requests */}
      <Typography variant="h6" fontWeight={700} sx={{ color: '#F8FAFC', mb: 2 }}>
        Leave Request History
      </Typography>

      {isLoadingRequests ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
          <CircularProgress color="secondary" />
        </Box>
      ) : !requestsData?.items || requestsData.items.length === 0 ? (
        <Card
          sx={{
            py: 6,
            textAlign: 'center',
            background: alpha('#1E293B', 0.6),
            border: '1px dashed #334155',
            borderRadius: '16px',
          }}
        >
          <Typography color="text.secondary">No leave requests found.</Typography>
        </Card>
      ) : (
        <TableContainer
          component={Paper}
          sx={{
            background: alpha('#1E293B', 0.6),
            border: '1px solid #334155',
            borderRadius: '16px',
            overflow: 'hidden',
          }}
        >
          <Table>
            <TableHead sx={{ bgcolor: '#0F172A' }}>
              <TableRow>
                <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }}>Leave Type</TableCell>
                <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }}>From Date</TableCell>
                <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }}>To Date</TableCell>
                <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }}>Days</TableCell>
                <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }}>Reason</TableCell>
                <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }}>Status</TableCell>
                <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }} align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {requestsData.items.map((row: any) => (
                <TableRow
                  key={row.id}
                  sx={{ '&:hover': { bgcolor: alpha('#334155', 0.2) }, borderBottom: '1px solid #1E293B' }}
                >
                  <TableCell sx={{ color: '#F8FAFC', fontWeight: 600 }}>{row.leave_type}</TableCell>
                  <TableCell sx={{ color: '#E2E8F0' }}>
                    {new Date(row.from_date).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' })}
                  </TableCell>
                  <TableCell sx={{ color: '#E2E8F0' }}>
                    {new Date(row.to_date).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' })}
                  </TableCell>
                  <TableCell sx={{ color: '#E2E8F0' }}>{row.days_count} days</TableCell>
                  <TableCell sx={{ color: '#94A3B8', maxWidth: 200, wordWrap: 'break-word' }}>{row.reason}</TableCell>
                  <TableCell>
                    <StatusPill status={row.status} />
                  </TableCell>
                  <TableCell align="center">
                    {row.status === 'pending' && (
                      <Button
                        variant="outlined"
                        color="error"
                        size="small"
                        startIcon={<CancelIcon />}
                        onClick={() => handleCancel(row.id)}
                        disabled={cancelMutation.isPending}
                        sx={{ textTransform: 'none', borderRadius: '6px' }}
                      >
                        Cancel
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
}
