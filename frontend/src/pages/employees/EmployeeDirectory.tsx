import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Button,
  Grid,
  TextField,
  MenuItem,
  InputAdornment,
  Avatar,
  Typography,
} from '@mui/material';
import { Add as AddIcon, Search as SearchIcon } from '@mui/icons-material';
import { useAuthStore } from '@/store/authStore';
import { employeesApi } from '@/api/employees.api';
import PageHeader from '@/components/ui/PageHeader';
import DataTable from '@/components/ui/DataTable';
import StatusPill from '@/components/ui/StatusPill';
import { GridColDef, GridRenderCellParams, GridRowParams } from '@mui/x-data-grid';

export default function EmployeeDirectory() {
  const navigate = useNavigate();
  const currentUser = useAuthStore((s) => s.user);
  
  const [search, setSearch] = useState('');
  const [department, setDepartment] = useState('all');
  const [status, setStatus] = useState('all');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  const isHRorAdmin = currentUser?.role === 'admin' || currentUser?.role === 'hr_recruiter';

  // Fetch employees list
  const { data, isLoading } = useQuery({
    queryKey: ['employees', search, department, status, page, pageSize],
    queryFn: () =>
      employeesApi.listEmployees({
        page,
        page_size: pageSize,
        search: search || undefined,
        department_id: department !== 'all' ? department : undefined,
        employment_status: status !== 'all' ? status : undefined,
      }),
  });

  const handleRowClick = (params: GridRowParams) => {
    navigate(`/employees/${params.id}`);
  };

  const columns: GridColDef[] = [
    {
      field: 'full_name',
      headerName: 'Employee',
      flex: 1.5,
      renderCell: (params: GridRenderCellParams) => (
        <Box display="flex" alignItems="center" gap={1.5} sx={{ height: '100%' }}>
          <Avatar
            src={params.row.profile_photo_url || undefined}
            sx={{ width: 32, height: 32, bgcolor: 'primary.main', fontSize: '0.85rem' }}
          >
            {params.value ? String(params.value).split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase() : 'EE'}
          </Avatar>
          <Box>
            <Typography variant="body2" fontWeight={600} color="text.primary">
              {params.value}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {params.row.employee_code}
            </Typography>
          </Box>
        </Box>
      ),
    },
    {
      field: 'designation_title',
      headerName: 'Designation',
      flex: 1.2,
      valueGetter: (params: any) => params.row?.designation_title || '—',
    },
    {
      field: 'department_name',
      headerName: 'Department',
      flex: 1.2,
      valueGetter: (params: any) => params.row?.department_name || '—',
    },
    {
      field: 'date_of_joining',
      headerName: 'Joining Date',
      flex: 1.0,
      valueGetter: (params: any) =>
        params.row?.date_of_joining ? new Date(params.row.date_of_joining).toLocaleDateString() : '—',
    },
    {
      field: 'employment_status',
      headerName: 'Status',
      flex: 1.0,
      renderCell: (params: GridRenderCellParams) => {
        const val = String(params.value || 'active');
        return <StatusPill status={val} />;
      },
    },
  ];

  return (
    <Box>
      <PageHeader
        title="Employee Directory"
        subtitle="Manage and view all employee profiles, roles, and status."
        action={
          isHRorAdmin ? (
            <Button
              variant="contained"
              color="primary"
              startIcon={<AddIcon />}
              onClick={() => navigate('/employees/new')}
            >
              Add Employee
            </Button>
          ) : undefined
        }
      />

      {/* Filters */}
      <Grid container spacing={2} sx={{ mb: 3, mt: 1 }}>
        <Grid item xs={12} sm={6} md={4}>
          <TextField
            fullWidth
            size="small"
            placeholder="Search by name, code..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon fontSize="small" sx={{ color: 'text.secondary' }} />
                </InputAdornment>
              ),
            }}
          />
        </Grid>
        <Grid item xs={12} sm={3} md={2.5}>
          <TextField
            select
            fullWidth
            size="small"
            label="Department"
            value={department}
            onChange={(e) => setDepartment(e.target.value)}
          >
            <MenuItem value="all">All Departments</MenuItem>
            {/* Standard pre-seeded options for UI completeness */}
            <MenuItem value="engineering">Engineering</MenuItem>
            <MenuItem value="hr">Human Resources</MenuItem>
            <MenuItem value="finance">Finance</MenuItem>
            <MenuItem value="sales">Sales</MenuItem>
          </TextField>
        </Grid>
        <Grid item xs={12} sm={3} md={2.5}>
          <TextField
            select
            fullWidth
            size="small"
            label="Status"
            value={status}
            onChange={(e) => setStatus(e.target.value)}
          >
            <MenuItem value="all">All Statuses</MenuItem>
            <MenuItem value="active">Active</MenuItem>
            <MenuItem value="on_leave">On Leave</MenuItem>
            <MenuItem value="notice_period">Notice Period</MenuItem>
            <MenuItem value="terminated">Terminated</MenuItem>
          </TextField>
        </Grid>
      </Grid>

      {/* Data Table */}
      <DataTable
        rows={(data?.items as unknown as Record<string, unknown>[]) || []}
        columns={columns}
        loading={isLoading}
        emptyMessage="No employees found in the directory"
        onRowClick={handleRowClick}
        showExport
        pageSize={pageSize}
      />
    </Box>
  );
}
