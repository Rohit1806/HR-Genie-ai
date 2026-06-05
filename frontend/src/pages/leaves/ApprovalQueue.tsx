import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Box,
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
  Button,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  alpha,
} from '@mui/material';
import {
  Check as ApproveIcon,
  Close as RejectIcon,
} from '@mui/icons-material';
import { leavesApi } from '@/api/leaves.api';
import PageHeader from '@/components/ui/PageHeader';
import { toast } from 'react-hot-toast';

export default function ApprovalQueue() {
  const queryClient = useQueryClient();
  const [selectedRequest, setSelectedRequest] = useState<any | null>(null);
  const [actionType, setActionType] = useState<'approve' | 'reject' | null>(null);
  const [comment, setComment] = useState('');

  // Query pending approvals
  const { data: pendingData, isLoading } = useQuery({
    queryKey: ['pending-leave-approvals'],
    queryFn: () => leavesApi.getPendingApprovals(),
  });

  // Mutations
  const approveMutation = useMutation({
    mutationFn: ({ id, remarks }: { id: string; remarks?: string }) =>
      leavesApi.approveLeave(id, remarks),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pending-leave-approvals'] });
      toast.success('Leave request approved.');
      handleClose();
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to approve request.');
    },
  });

  const rejectMutation = useMutation({
    mutationFn: ({ id, reason }: { id: string; reason: string }) =>
      leavesApi.rejectLeave(id, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pending-leave-approvals'] });
      toast.success('Leave request rejected.');
      handleClose();
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to reject request.');
    },
  });

  const handleOpenAction = (req: any, type: 'approve' | 'reject') => {
    setSelectedRequest(req);
    setActionType(type);
    setComment('');
  };

  const handleClose = () => {
    setSelectedRequest(null);
    setActionType(null);
    setComment('');
  };

  const handleConfirmAction = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedRequest || !actionType) return;

    if (actionType === 'approve') {
      approveMutation.mutate({ id: selectedRequest.id, remarks: comment });
    } else {
      if (!comment) {
        toast.error('Please provide a reason for rejection.');
        return;
      }
      rejectMutation.mutate({ id: selectedRequest.id, reason: comment });
    }
  };

  const requests = pendingData?.items || [];

  return (
    <Box>
      <PageHeader
        title="Leave Approval Queue"
        subtitle="Review and process leave requests submitted by your team members."
      />

      {isLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
          <CircularProgress color="secondary" />
        </Box>
      ) : requests.length === 0 ? (
        <Card
          sx={{
            py: 6,
            textAlign: 'center',
            background: alpha('#1E293B', 0.6),
            border: '1px dashed #334155',
            borderRadius: '16px',
          }}
        >
          <Typography color="text.secondary">No pending leave requests found.</Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            You are all caught up! Leave requests submitted by your direct reports will show up here.
          </Typography>
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
                <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }}>Employee</TableCell>
                <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }}>Leave Type</TableCell>
                <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }}>From Date</TableCell>
                <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }}>To Date</TableCell>
                <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }}>Days</TableCell>
                <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }}>Reason</TableCell>
                <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }} align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {requests.map((row: any) => (
                <TableRow
                  key={row.id}
                  sx={{ '&:hover': { bgcolor: alpha('#334155', 0.2) }, borderBottom: '1px solid #1E293B' }}
                >
                  <TableCell sx={{ color: '#F8FAFC', fontWeight: 600 }}>{row.employee_name}</TableCell>
                  <TableCell sx={{ color: '#E2E8F0' }}>{row.leave_type}</TableCell>
                  <TableCell sx={{ color: '#E2E8F0' }}>
                    {new Date(row.from_date).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' })}
                  </TableCell>
                  <TableCell sx={{ color: '#E2E8F0' }}>
                    {new Date(row.to_date).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' })}
                  </TableCell>
                  <TableCell sx={{ color: '#E2E8F0' }}>{row.days_count} days</TableCell>
                  <TableCell sx={{ color: '#94A3B8', maxWidth: 220, wordWrap: 'break-word' }}>{row.reason}</TableCell>
                  <TableCell align="center">
                    <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1 }}>
                      <Button
                        variant="contained"
                        color="success"
                        size="small"
                        startIcon={<ApproveIcon />}
                        onClick={() => handleOpenAction(row, 'approve')}
                        sx={{ textTransform: 'none', borderRadius: '6px' }}
                      >
                        Approve
                      </Button>
                      <Button
                        variant="outlined"
                        color="error"
                        size="small"
                        startIcon={<RejectIcon />}
                        onClick={() => handleOpenAction(row, 'reject')}
                        sx={{ textTransform: 'none', borderRadius: '6px' }}
                      >
                        Reject
                      </Button>
                    </Box>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Approve/Reject Confirmation Dialog */}
      <Dialog
        open={Boolean(selectedRequest)}
        onClose={handleClose}
        PaperProps={{
          sx: {
            background: '#1E293B',
            border: '1px solid #334155',
            borderRadius: '16px',
            boxShadow: '0 20px 60px rgba(0,0,0,0.5)',
          },
        }}
      >
        <DialogTitle sx={{ color: '#F8FAFC', fontWeight: 700 }}>
          {actionType === 'approve' ? 'Approve Leave Request' : 'Reject Leave Request'}
        </DialogTitle>
        <form onSubmit={handleConfirmAction}>
          <DialogContent>
            <Typography variant="body2" sx={{ color: '#94A3B8', mb: 2 }}>
              Are you sure you want to {actionType} the leave request of{' '}
              <strong>{selectedRequest?.employee_name}</strong> for {selectedRequest?.days_count} days?
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={3}
              label={actionType === 'approve' ? 'Remarks (Optional)' : 'Reason for Rejection (Required)'}
              required={actionType === 'reject'}
              value={comment}
              onChange={(e) => setComment(e.target.value)}
            />
          </DialogContent>
          <DialogActions sx={{ px: 3, pb: 3 }}>
            <Button
              onClick={handleClose}
              sx={{ color: '#94A3B8', '&:hover': { background: alpha('#334155', 0.3) } }}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="contained"
              color={actionType === 'approve' ? 'success' : 'error'}
              disabled={approveMutation.isPending || rejectMutation.isPending}
              sx={{
                borderRadius: '8px',
                textTransform: 'none',
              }}
            >
              {actionType === 'approve' ? 'Confirm Approval' : 'Confirm Rejection'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
}
