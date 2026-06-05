import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
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
  Button,
  Tabs,
  Tab,
  alpha,
  Divider,
} from '@mui/material';
import {
  Done as ApproveIcon,
  Close as RejectIcon,
  FilterList as FilterIcon,
} from '@mui/icons-material';
import { attendanceApi } from '@/api/attendance.api';
import PageHeader from '@/components/ui/PageHeader';
import StatusPill from '@/components/ui/StatusPill';
import { toast } from 'react-hot-toast';

export default function TeamAttendance() {
  const queryClient = useQueryClient();
  const todayStr = new Date().toISOString().split('T')[0];

  const [activeTab, setActiveTab] = useState(0);
  const [selectedDate, setSelectedDate] = useState(todayStr);
  const [selectedDept, setSelectedDept] = useState('all');

  // 1. Query Team Attendance records
  const { data: teamRecords, isLoading: isLoadingTeam } = useQuery({
    queryKey: ['team-attendance', selectedDate, selectedDept],
    queryFn: () => attendanceApi.getTeamAttendance(selectedDate),
  });

  // 2. Query Pending Regularization Requests
  const { data: pendingRequests, isLoading: isLoadingPending } = useQuery({
    queryKey: ['pending-regularizations'],
    queryFn: () => attendanceApi.getPendingRegularizations(),
  });

  // Mutations
  const approveMutation = useMutation({
    mutationFn: attendanceApi.approveRegularization,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pending-regularizations'] });
      queryClient.invalidateQueries({ queryKey: ['team-attendance'] });
      toast.success('Regularization request approved!');
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to approve regularization.');
    },
  });

  const rejectMutation = useMutation({
    mutationFn: ({ id }: { id: string }) => attendanceApi.rejectRegularization(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pending-regularizations'] });
      toast.success('Regularization request rejected!');
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Failed to reject regularization.');
    },
  });

  const handleApprove = (id: string) => {
    approveMutation.mutate(id);
  };

  const handleReject = (id: string) => {
    rejectMutation.mutate({ id });
  };

  // Compute KPI counts dynamically based on records
  const records = teamRecords || [];
  const presentCount = records.filter(r => r.status === 'present' || r.status === 'late').length;
  const lateCount = records.filter(r => r.status === 'late').length;
  const leaveCount = records.filter(r => r.status === 'on_leave').length;
  const absentCount = records.filter(r => r.status === 'absent').length;

  return (
    <Box>
      <PageHeader
        title="Team Attendance & Requests"
        subtitle="Monitor daily logs, filter by department, and manage regularization workflows."
      />

      <Box sx={{ borderBottom: 1, borderColor: '#1E293B', mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={(_, val) => setActiveTab(val)}
          sx={{
            '& .MuiTab-root': { color: '#64748B', fontWeight: 600 },
            '& .Mui-selected': { color: '#A78BFA' },
            '& .MuiTabs-indicator': { bgcolor: '#8B5CF6' },
          }}
        >
          <Tab label="Team Dashboard" />
          <Tab
            label={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                Pending Approvals
                {pendingRequests && pendingRequests.length > 0 && (
                  <Box
                    sx={{
                      px: 0.8,
                      py: 0.2,
                      borderRadius: '50%',
                      background: '#EF4444',
                      color: '#FFF',
                      fontSize: '0.65rem',
                      fontWeight: 700,
                    }}
                  >
                    {pendingRequests.length}
                  </Box>
                )}
              </Box>
            }
          />
        </Tabs>
      </Box>

      {/* Tab 0: Team Dashboard */}
      {activeTab === 0 && (
        <Box>
          {/* KPI Dashboard Cards */}
          <Grid container spacing={2} sx={{ mb: 4 }}>
            {[
              { label: 'Total Present', value: presentCount, color: '#10B981', border: '1px solid #10B981' },
              { label: 'Late Clock Ins', value: lateCount, color: '#F59E0B', border: '1px solid #F59E0B' },
              { label: 'On Leave', value: leaveCount, color: '#EC4899', border: '1px solid #EC4899' },
              { label: 'Absent', value: absentCount, color: '#EF4444', border: '1px solid #EF4444' },
            ].map((card, idx) => (
              <Grid item xs={6} sm={3} key={idx}>
                <Card
                  sx={{
                    background: 'linear-gradient(135deg, #1E293B, #0F172A)',
                    border: '1px solid #334155',
                    borderRadius: '12px',
                  }}
                >
                  <CardContent sx={{ py: 2, px: 3, textAlign: 'center' }}>
                    <Typography variant="h4" fontWeight={800} sx={{ color: card.color }}>
                      {card.value}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {card.label}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>

          {/* Filters */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={4} md={3}>
              <TextField
                fullWidth
                size="small"
                type="date"
                label="Date"
                InputLabelProps={{ shrink: true }}
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                sx={{ background: alpha('#1E293B', 0.6), borderRadius: '8px' }}
              />
            </Grid>
            <Grid item xs={12} sm={4} md={3}>
              <TextField
                select
                fullWidth
                size="small"
                label="Department"
                value={selectedDept}
                onChange={(e) => setSelectedDept(e.target.value)}
                sx={{ background: alpha('#1E293B', 0.6), borderRadius: '8px' }}
              >
                <MenuItem value="all">All Departments</MenuItem>
                <MenuItem value="engineering">Engineering</MenuItem>
                <MenuItem value="hr">Human Resources</MenuItem>
                <MenuItem value="finance">Finance</MenuItem>
                <MenuItem value="sales">Sales</MenuItem>
              </TextField>
            </Grid>
          </Grid>

          {/* Logs Table */}
          {isLoadingTeam ? (
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
                    <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }}>Employee</TableCell>
                    <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }}>Department</TableCell>
                    <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }}>Clock In</TableCell>
                    <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }}>Clock Out</TableCell>
                    <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }}>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {records.map((row) => (
                    <TableRow
                      key={row.employee_id}
                      sx={{ '&:hover': { bgcolor: alpha('#334155', 0.2) }, borderBottom: '1px solid #1E293B' }}
                    >
                      <TableCell sx={{ color: '#F8FAFC', fontWeight: 600 }}>{row.employee_name}</TableCell>
                      <TableCell sx={{ color: '#E2E8F0' }}>{row.department || '—'}</TableCell>
                      <TableCell sx={{ color: '#E2E8F0' }}>
                        {row.clock_in ? new Date(row.clock_in).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '—'}
                      </TableCell>
                      <TableCell sx={{ color: '#E2E8F0' }}>
                        {row.clock_out ? new Date(row.clock_out).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '—'}
                      </TableCell>
                      <TableCell>
                        <StatusPill status={row.status} />
                      </TableCell>
                    </TableRow>
                  ))}
                  {records.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={5} align="center" sx={{ py: 6, color: '#64748B', fontStyle: 'italic' }}>
                        No records logged for this date.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Box>
      )}

      {/* Tab 1: Pending Approvals */}
      {activeTab === 1 && (
        <Box>
          {isLoadingPending ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
              <CircularProgress color="secondary" />
            </Box>
          ) : !pendingRequests || pendingRequests.length === 0 ? (
            <Card
              sx={{
                p: 6,
                textAlign: 'center',
                background: alpha('#1E293B', 0.6),
                border: '1px dashed #334155',
                borderRadius: '16px',
              }}
            >
              <Typography color="text.secondary" variant="body1">
                No pending regularization requests.
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                You are all caught up! Regularization requests submitted by your team will appear here.
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
                    <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }}>Target Date</TableCell>
                    <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }}>Requested Shift</TableCell>
                    <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }}>Reason</TableCell>
                    <TableCell sx={{ color: '#94A3B8', fontWeight: 700 }} align="center">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {pendingRequests.map((req) => (
                    <TableRow
                      key={req.id}
                      sx={{ '&:hover': { bgcolor: alpha('#334155', 0.2) }, borderBottom: '1px solid #1E293B' }}
                    >
                      <TableCell sx={{ color: '#F8FAFC', fontWeight: 600 }}>{req.employee_name}</TableCell>
                      <TableCell sx={{ color: '#E2E8F0' }}>
                        {new Date(req.date).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' })}
                      </TableCell>
                      <TableCell sx={{ color: '#E2E8F0' }}>
                        {new Date(req.requested_clock_in).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        {' - '}
                        {new Date(req.requested_clock_out).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </TableCell>
                      <TableCell sx={{ color: '#94A3B8', maxWidth: 200, wordWrap: 'break-word' }}>
                        {req.reason}
                      </TableCell>
                      <TableCell align="center">
                        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1 }}>
                          <Button
                            variant="contained"
                            color="success"
                            size="small"
                            startIcon={<ApproveIcon />}
                            onClick={() => handleApprove(req.id)}
                            disabled={approveMutation.isPending}
                            sx={{ textTransform: 'none', borderRadius: '6px' }}
                          >
                            Approve
                          </Button>
                          <Button
                            variant="outlined"
                            color="error"
                            size="small"
                            startIcon={<RejectIcon />}
                            onClick={() => handleReject(req.id)}
                            disabled={rejectMutation.isPending}
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
        </Box>
      )}
    </Box>
  );
}
