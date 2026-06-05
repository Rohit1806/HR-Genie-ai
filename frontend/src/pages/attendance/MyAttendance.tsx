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
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  alpha,
} from '@mui/material';
import {
  PlayArrow as ClockInIcon,
  Stop as ClockOutIcon,
  DateRange as DateIcon,
  History as HistoryIcon,
  Add as ReqIcon,
} from '@mui/icons-material';
import { attendanceApi, RegularizationRequest } from '@/api/attendance.api';
import PageHeader from '@/components/ui/PageHeader';
import StatusPill from '@/components/ui/StatusPill';
import { toast } from 'react-hot-toast';

const months = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

export default function MyAttendance() {
  const queryClient = useQueryClient();
  const today = new Date();
  const [selectedMonth, setSelectedMonth] = useState(today.getMonth() + 1);
  const [selectedYear, setSelectedYear] = useState(today.getFullYear());
  const [isRegularizeOpen, setIsRegularizeOpen] = useState(false);
  const [regForm, setRegForm] = useState<RegularizationRequest>({
    date: '',
    clock_in: '',
    clock_out: '',
    reason: '',
  });

  // Query my attendance
  const { data, isLoading } = useQuery({
    queryKey: ['my-attendance', selectedMonth, selectedYear],
    queryFn: () => attendanceApi.getMyAttendance(selectedMonth, selectedYear),
  });

  // Check if clocked in today
  const todayStr = today.toISOString().split('T')[0];
  const todayLog = data?.records?.find((r) => r.date === todayStr);
  const isClockedIn = todayLog && todayLog.clock_in && !todayLog.clock_out;
  const isClockedOut = todayLog && todayLog.clock_in && todayLog.clock_out;

  // Mutations
  const clockInMutation = useMutation({
    mutationFn: () => attendanceApi.clockIn(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-attendance'] });
      toast.success('Successfully clocked in!');
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to clock in.');
    },
  });

  const clockOutMutation = useMutation({
    mutationFn: () => attendanceApi.clockOut(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-attendance'] });
      toast.success('Successfully clocked out!');
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to clock out.');
    },
  });

  const regularizationMutation = useMutation({
    mutationFn: attendanceApi.createRegularization,
    onSuccess: () => {
      toast.success('Regularization request submitted!');
      setIsRegularizeOpen(false);
      setRegForm({ date: '', clock_in: '', clock_out: '', reason: '' });
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to submit regularization request.');
    },
  });

  const handleRegularizeSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!regForm.date || !regForm.clock_in || !regForm.clock_out || !regForm.reason) {
      toast.error('All fields are required.');
      return;
    }

    // Convert date + time to ISO strings
    const clockInDateTime = new Date(`${regForm.date}T${regForm.clock_in}:00`).toISOString();
    const clockOutDateTime = new Date(`${regForm.date}T${regForm.clock_out}:00`).toISOString();

    regularizationMutation.mutate({
      ...regForm,
      clock_in: clockInDateTime,
      clock_out: clockOutDateTime,
    });
  };

  return (
    <Box>
      <PageHeader
        title="My Attendance"
        subtitle="Track your daily work hours, log clock-in/out, and manage regularization requests."
        action={
          <Button
            variant="outlined"
            startIcon={<ReqIcon />}
            onClick={() => setIsRegularizeOpen(true)}
            sx={{
              borderColor: alpha('#8B5CF6', 0.4),
              color: '#A78BFA',
              textTransform: 'none',
              borderRadius: '8px',
              '&:hover': {
                borderColor: '#8B5CF6',
                background: alpha('#8B5CF6', 0.05),
              },
            }}
          >
            Regularize Attendance
          </Button>
        }
      />

      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Clock Controls Card */}
        <Grid item xs={12} md={4}>
          <Card
            sx={{
              background: 'linear-gradient(135deg, #1E293B, #0F172A)',
              borderRadius: '16px',
              border: '1px solid #334155',
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              p: 2,
            }}
          >
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                CURRENT STATUS
              </Typography>
              <Chip
                label={isClockedIn ? 'CLOCKED IN' : isClockedOut ? 'CLOCKED OUT' : 'NOT CLOCKED IN'}
                color={isClockedIn ? 'success' : isClockedOut ? 'secondary' : 'default'}
                sx={{ fontWeight: 700, mb: 3 }}
              />

              <Typography variant="h3" fontWeight={700} sx={{ color: '#F8FAFC', mb: 0.5 }}>
                {today.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
                {today.toLocaleDateString([], { weekday: 'long', month: 'short', day: 'numeric' })}
              </Typography>

              <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2 }}>
                {!isClockedIn && !isClockedOut && (
                  <Button
                    variant="contained"
                    startIcon={<ClockInIcon />}
                    onClick={() => clockInMutation.mutate()}
                    disabled={clockInMutation.isPending}
                    sx={{
                      background: 'linear-gradient(135deg, #10B981, #059669)',
                      px: 4,
                      py: 1.5,
                      borderRadius: '10px',
                      fontWeight: 600,
                      textTransform: 'none',
                      '&:hover': { background: 'linear-gradient(135deg, #059669, #047857)' },
                    }}
                  >
                    Clock In
                  </Button>
                )}

                {isClockedIn && (
                  <Button
                    variant="contained"
                    startIcon={<ClockOutIcon />}
                    onClick={() => clockOutMutation.mutate()}
                    disabled={clockOutMutation.isPending}
                    sx={{
                      background: 'linear-gradient(135deg, #EF4444, #DC2626)',
                      px: 4,
                      py: 1.5,
                      borderRadius: '10px',
                      fontWeight: 600,
                      textTransform: 'none',
                      '&:hover': { background: 'linear-gradient(135deg, #DC2626, #B91C1C)' },
                    }}
                  >
                    Clock Out
                  </Button>
                )}

                {isClockedOut && (
                  <Typography variant="body2" color="success.main" fontWeight={600}>
                    Attendance submitted for today!
                  </Typography>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Attendance Summary Dashboard */}
        <Grid item xs={12} md={8}>
          <Card
            sx={{
              background: 'linear-gradient(135deg, #1E293B, #0F172A)',
              borderRadius: '16px',
              border: '1px solid #334155',
            }}
          >
            <CardContent sx={{ p: 3 }}>
              <Typography variant="subtitle1" fontWeight={700} sx={{ color: '#F8FAFC', mb: 3 }}>
                Attendance Summary — {months[selectedMonth - 1]} {selectedYear}
              </Typography>

              {isLoading ? (
                <Box sx={{ py: 4, display: 'flex', justifyContent: 'center' }}>
                  <CircularProgress size={30} color="secondary" />
                </Box>
              ) : (
                <Grid container spacing={2}>
                  {[
                    { label: 'Present Days', value: data?.summary?.present_days || 0, color: '#10B981' },
                    { label: 'Absent Days', value: data?.summary?.absent_days || 0, color: '#EF4444' },
                    { label: 'Late Clock Ins', value: data?.summary?.late_days || 0, color: '#F59E0B' },
                    { label: 'Half Days', value: data?.summary?.half_days || 0, color: '#3B82F6' },
                    { label: 'On Leave', value: data?.summary?.leave_days || 0, color: '#EC4899' },
                    { label: 'Avg Work Hours', value: `${data?.summary?.avg_hours || 0} hrs`, color: '#8B5CF6' },
                  ].map((stat, idx) => (
                    <Grid item xs={6} sm={4} key={idx}>
                      <Box
                        sx={{
                          p: 2,
                          background: '#0F172A',
                          border: '1px solid #1E293B',
                          borderRadius: '12px',
                          textAlign: 'center',
                        }}
                      >
                        <Typography variant="h5" fontWeight={800} sx={{ color: stat.color, mb: 0.5 }}>
                          {stat.value}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {stat.label}
                        </Typography>
                      </Box>
                    </Grid>
                  ))}
                </Grid>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Monthly Log Filter */}
      <Box sx={{ mb: 3, display: 'flex', gap: 2 }}>
        <TextField
          select
          size="small"
          label="Month"
          value={selectedMonth}
          onChange={(e) => setSelectedMonth(Number(e.target.value))}
          sx={{ minWidth: 140, background: alpha('#1E293B', 0.6), borderRadius: '8px' }}
        >
          {months.map((m, i) => (
            <MenuItem key={i + 1} value={i + 1}>
              {m}
            </MenuItem>
          ))}
        </TextField>

        <TextField
          select
          size="small"
          label="Year"
          value={selectedYear}
          onChange={(e) => setSelectedYear(Number(e.target.value))}
          sx={{ minWidth: 100, background: alpha('#1E293B', 0.6), borderRadius: '8px' }}
        >
          {[2025, 2026, 2027].map((y) => (
            <MenuItem key={y} value={y}>
              {y}
            </MenuItem>
          ))}
        </TextField>
      </Box>

      {/* Logs Table */}
      {isLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
          <CircularProgress color="secondary" />
        </Box>
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
                <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }}>Date</TableCell>
                <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }}>Clock In</TableCell>
                <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }}>Clock Out</TableCell>
                <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }}>Work Hours</TableCell>
                <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }}>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {(data?.records || []).map((row) => (
                <TableRow
                  key={row.id}
                  sx={{ '&:hover': { bgcolor: alpha('#334155', 0.2) }, borderBottom: '1px solid #1E293B' }}
                >
                  <TableCell sx={{ color: '#F8FAFC' }}>
                    {new Date(row.date).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' })}
                  </TableCell>
                  <TableCell sx={{ color: '#E2E8F0' }}>
                    {row.clock_in ? new Date(row.clock_in).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '—'}
                  </TableCell>
                  <TableCell sx={{ color: '#E2E8F0' }}>
                    {row.clock_out ? new Date(row.clock_out).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '—'}
                  </TableCell>
                  <TableCell sx={{ color: '#E2E8F0' }}>
                    {row.total_hours !== null ? `${row.total_hours} hrs` : '—'}
                  </TableCell>
                  <TableCell>
                    <StatusPill status={row.status} />
                  </TableCell>
                </TableRow>
              ))}
              {(data?.records || []).length === 0 && (
                <TableRow>
                  <TableCell colSpan={5} align="center" sx={{ py: 6, color: '#64748B', fontStyle: 'italic' }}>
                    No attendance records logged for this month.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Regularize Dialog */}
      <Dialog
        open={isRegularizeOpen}
        onClose={() => setIsRegularizeOpen(false)}
        PaperProps={{
          sx: {
            background: '#1E293B',
            border: '1px solid #334155',
            borderRadius: '16px',
            boxShadow: '0 20px 60px rgba(0,0,0,0.5)',
          },
        }}
      >
        <DialogTitle sx={{ color: '#F8FAFC', fontWeight: 700 }}>Request Regularization</DialogTitle>
        <form onSubmit={handleRegularizeSubmit}>
          <DialogContent>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  type="date"
                  label="Date"
                  InputLabelProps={{ shrink: true }}
                  required
                  value={regForm.date}
                  onChange={(e) => setRegForm((p) => ({ ...p, date: e.target.value }))}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="time"
                  label="Requested Clock In"
                  InputLabelProps={{ shrink: true }}
                  required
                  value={regForm.clock_in}
                  onChange={(e) => setRegForm((p) => ({ ...p, clock_in: e.target.value }))}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  type="time"
                  label="Requested Clock Out"
                  InputLabelProps={{ shrink: true }}
                  required
                  value={regForm.clock_out}
                  onChange={(e) => setRegForm((p) => ({ ...p, clock_out: e.target.value }))}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Reason for Regularization"
                  required
                  value={regForm.reason}
                  onChange={(e) => setRegForm((p) => ({ ...p, reason: e.target.value }))}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions sx={{ px: 3, pb: 3 }}>
            <Button
              onClick={() => setIsRegularizeOpen(false)}
              sx={{ color: '#94A3B8', '&:hover': { background: alpha('#334155', 0.3) } }}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="contained"
              disabled={regularizationMutation.isPending}
              sx={{
                background: 'linear-gradient(135deg, #8B5CF6, #6D28D9)',
                '&:hover': { background: 'linear-gradient(135deg, #7C3AED, #5B21B6)' },
              }}
            >
              {regularizationMutation.isPending ? 'Submitting...' : 'Submit Request'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
}
