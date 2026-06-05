import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  alpha,
  Divider,
} from '@mui/material';
import {
  Add as RunIcon,
  CheckCircle as ApproveIcon,
  Visibility as ViewIcon,
} from '@mui/icons-material';
import { payrollApi, InitiateRunData } from '@/api/payroll.api';
import PageHeader from '@/components/ui/PageHeader';
import StatusPill from '@/components/ui/StatusPill';
import { toast } from 'react-hot-toast';

const months = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

export default function PayrollDashboard() {
  const queryClient = useQueryClient();
  const today = new Date();
  const [isInitiateOpen, setIsInitiateOpen] = useState(false);
  const [activeRunId, setActiveRunId] = useState<string | null>(null);
  const [initForm, setInitForm] = useState<InitiateRunData>({
    month: today.getMonth() + 1,
    year: today.getFullYear(),
  });

  // Query payroll runs
  const { data: runsData, isLoading: isLoadingRuns } = useQuery({
    queryKey: ['payroll-runs'],
    queryFn: () => payrollApi.listRuns(),
  });

  // Query payroll entries for the selected run
  const { data: entriesData, isLoading: isLoadingEntries } = useQuery({
    queryKey: ['payroll-entries', activeRunId],
    queryFn: () => payrollApi.getRunEntries(activeRunId || ''),
    enabled: !!activeRunId,
  });

  // Mutations
  const initiateMutation = useMutation({
    mutationFn: payrollApi.initiateRun,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['payroll-runs'] });
      toast.success('Payroll run initiated and calculated successfully!');
      setIsInitiateOpen(false);
      setActiveRunId(data.id); // View the run entries immediately
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to initiate payroll run.');
    },
  });

  const approveMutation = useMutation({
    mutationFn: payrollApi.approveRun,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payroll-runs'] });
      queryClient.invalidateQueries({ queryKey: ['payroll-entries', activeRunId] });
      toast.success('Payroll run approved successfully!');
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to approve payroll run.');
    },
  });

  const handleInitiate = (e: React.FormEvent) => {
    e.preventDefault();
    initiateMutation.mutate(initForm);
  };

  const handleApprove = () => {
    if (activeRunId && window.confirm('Are you sure you want to approve this payroll run? This will generate payslips for all employees.')) {
      approveMutation.mutate(activeRunId);
    }
  };

  const activeRun = runsData?.items?.find((r) => r.id === activeRunId);

  return (
    <Box>
      <PageHeader
        title="Payroll Dashboard"
        subtitle="Manage salary computation cycles, process runs, and approve payslip distributions."
        action={
          <Button
            variant="contained"
            color="primary"
            startIcon={<RunIcon />}
            onClick={() => setIsInitiateOpen(true)}
            sx={{
              background: 'linear-gradient(135deg, #8B5CF6, #6D28D9)',
              '&:hover': {
                background: 'linear-gradient(135deg, #7C3AED, #5B21B6)',
              },
            }}
          >
            Initiate Payroll Run
          </Button>
        }
      />

      <Grid container spacing={3}>
        {/* Runs List (Left) */}
        <Grid item xs={12} md={4}>
          <Typography variant="h6" fontWeight={700} sx={{ color: '#F8FAFC', mb: 2 }}>
            Execution Cycles
          </Typography>

          {isLoadingRuns ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress size={30} color="secondary" />
            </Box>
          ) : !runsData?.items || runsData.items.length === 0 ? (
            <Card sx={{ p: 3, background: '#1E293B', border: '1px dashed #334155', textAlign: 'center' }}>
              <Typography color="text.secondary">No payroll runs found.</Typography>
            </Card>
          ) : (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {runsData.items.map((run) => (
                <Card
                  key={run.id}
                  onClick={() => setActiveRunId(run.id)}
                  sx={{
                    background: activeRunId === run.id ? 'linear-gradient(145deg, #2D1B69, #0F172A)' : '#1E293B',
                    border: '1px solid',
                    borderColor: activeRunId === run.id ? '#8B5CF6' : '#334155',
                    borderRadius: '12px',
                    cursor: 'pointer',
                    transition: 'border-color 0.2s',
                    '&:hover': { borderColor: '#8B5CF6' },
                  }}
                >
                  <CardContent sx={{ p: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Typography variant="body1" fontWeight={700} sx={{ color: '#F8FAFC' }}>
                        {months[run.month - 1]} {run.year}
                      </Typography>
                      <StatusPill status={run.status} />
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      Net payout: <strong>₹{run.total_net ? run.total_net.toLocaleString() : '0'}</strong>
                    </Typography>
                  </CardContent>
                </Card>
              ))}
            </Box>
          )}
        </Grid>
 
        {/* Selected Run Details & Entries (Right) */}
        <Grid item xs={12} md={8}>
          {activeRunId ? (
            <Box>
              {activeRun && (
                <Card
                  sx={{
                    background: 'linear-gradient(135deg, #1E293B, #0F172A)',
                    border: '1px solid #334155',
                    borderRadius: '16px',
                    p: 3,
                    mb: 4,
                  }}
                >
                  <CardContent sx={{ p: 0 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                      <Typography variant="h5" fontWeight={700} sx={{ color: '#F8FAFC' }}>
                        Cycle Summary — {months[activeRun.month - 1]} {activeRun.year}
                      </Typography>
                      {activeRun.status === 'computed' && (
                        <Button
                          variant="contained"
                          color="success"
                          startIcon={<ApproveIcon />}
                          onClick={handleApprove}
                          disabled={approveMutation.isPending}
                          sx={{ textTransform: 'none', borderRadius: '8px' }}
                        >
                          Approve Payout
                        </Button>
                      )}
                    </Box>
 
                    <Grid container spacing={3} sx={{ mt: 1 }}>
                      <Grid item xs={6} sm={4}>
                        <Typography variant="caption" color="text.secondary">
                          TOTAL GROSS PAYOUT
                        </Typography>
                        <Typography variant="h5" fontWeight={800} sx={{ color: '#F8FAFC', mt: 0.5 }}>
                          ₹{activeRun.total_gross ? activeRun.total_gross.toLocaleString() : '0'}
                        </Typography>
                      </Grid>
                      <Grid item xs={6} sm={4}>
                        <Typography variant="caption" color="text.secondary">
                          TOTAL NET SALARY
                        </Typography>
                        <Typography variant="h5" fontWeight={800} sx={{ color: '#10B981', mt: 0.5 }}>
                          ₹{activeRun.total_net ? activeRun.total_net.toLocaleString() : '0'}
                        </Typography>
                      </Grid>
                      <Grid item xs={6} sm={4}>
                        <Typography variant="caption" color="text.secondary">
                          STATUS
                        </Typography>
                        <Box sx={{ mt: 1 }}>
                          <StatusPill status={activeRun.status} />
                        </Box>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              )}

              {/* Entries Table */}
              <Typography variant="h6" fontWeight={700} sx={{ color: '#F8FAFC', mb: 2 }}>
                Salary Calculations List
              </Typography>

              {isLoadingEntries ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
                  <CircularProgress color="secondary" />
                </Box>
              ) : !entriesData?.items || entriesData.items.length === 0 ? (
                <Card sx={{ p: 4, background: '#1E293B', border: '1px dashed #334155', textAlign: 'center' }}>
                  <Typography color="text.secondary">No calculation records generated for this run.</Typography>
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
                        <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }}>Gross</TableCell>
                        <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }}>LOP Ded.</TableCell>
                        <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }}>Tax / Deductions</TableCell>
                        <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }}>Net Payout</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {entriesData.items.map((row) => {
                        const taxAndDeds = row.pf_deduction + row.esi_deduction + row.tds_deduction;
                        return (
                          <TableRow
                            key={row.id}
                            sx={{ '&:hover': { bgcolor: alpha('#334155', 0.2) }, borderBottom: '1px solid #1E293B' }}
                          >
                            <TableCell>
                              <Typography variant="body2" fontWeight={600} sx={{ color: '#F8FAFC' }}>
                                {row.employee_name}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {row.employee_code}
                              </Typography>
                            </TableCell>
                            <TableCell sx={{ color: '#E2E8F0' }}>₹{row.gross_salary.toLocaleString()}</TableCell>
                            <TableCell sx={{ color: '#EF4444' }}>
                              {row.lop_deduction > 0 ? `₹${row.lop_deduction.toLocaleString()}` : '—'}
                            </TableCell>
                            <TableCell sx={{ color: '#94A3B8' }}>₹{taxAndDeds.toLocaleString()}</TableCell>
                            <TableCell sx={{ color: '#10B981', fontWeight: 700 }}>
                              ₹{row.net_salary.toLocaleString()}
                            </TableCell>
                          </TableRow>
                        );
                      })}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </Box>
          ) : (
            <Card
              sx={{
                p: 8,
                textAlign: 'center',
                background: alpha('#1E293B', 0.6),
                border: '1px dashed #334155',
                borderRadius: '16px',
              }}
            >
              <Typography color="text.secondary">Please select an execution cycle on the left to view details.</Typography>
            </Card>
          )}
        </Grid>
      </Grid>

      {/* Initiate Dialog */}
      <Dialog
        open={isInitiateOpen}
        onClose={() => setIsInitiateOpen(false)}
        PaperProps={{
          sx: {
            background: '#1E293B',
            border: '1px solid #334155',
            borderRadius: '16px',
            boxShadow: '0 20px 60px rgba(0,0,0,0.5)',
          },
        }}
      >
        <DialogTitle sx={{ color: '#F8FAFC', fontWeight: 700 }}>Initiate Payroll Run</DialogTitle>
        <form onSubmit={handleInitiate}>
          <DialogContent>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  select
                  fullWidth
                  label="Month"
                  value={initForm.month}
                  onChange={(e) => setInitForm((p) => ({ ...p, month: Number(e.target.value) }))}
                >
                  {months.map((m, i) => (
                    <MenuItem key={i + 1} value={i + 1}>
                      {m}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  select
                  fullWidth
                  label="Year"
                  value={initForm.year}
                  onChange={(e) => setInitForm((p) => ({ ...p, year: Number(e.target.value) }))}
                >
                  {[2025, 2026, 2027].map((y) => (
                    <MenuItem key={y} value={y}>
                      {y}
                    </MenuItem>
                  ))}
                </TextField>
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions sx={{ px: 3, pb: 3 }}>
            <Button
              onClick={() => setIsInitiateOpen(false)}
              sx={{ color: '#94A3B8', '&:hover': { background: alpha('#334155', 0.3) } }}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="contained"
              disabled={initiateMutation.isPending}
              sx={{
                background: 'linear-gradient(135deg, #8B5CF6, #6D28D9)',
                '&:hover': { background: 'linear-gradient(135deg, #7C3AED, #5B21B6)' },
              }}
            >
              {initiateMutation.isPending ? 'Calculating...' : 'Start Execution'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
}
