import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
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
  Divider,
} from '@mui/material';
import {
  Print as PrintIcon,
  Search as SearchIcon,
} from '@mui/icons-material';
import { payrollApi } from '@/api/payroll.api';
import PageHeader from '@/components/ui/PageHeader';

const months = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

export default function Payslips() {
  const today = new Date();
  const [selectedMonth, setSelectedMonth] = useState(today.getMonth() + 1);
  const [selectedYear, setSelectedYear] = useState(today.getFullYear());
  const [searchTrigger, setSearchTrigger] = useState({ month: selectedMonth, year: selectedYear });

  // Query payslip
  const { data: payslip, isLoading, error } = useQuery({
    queryKey: ['my-payslip', searchTrigger.month, searchTrigger.year],
    queryFn: () => payrollApi.getMyPayslip(searchTrigger.month, searchTrigger.year),
    retry: false, // Don't keep retrying if payslip doesn't exist
  });

  const handleFetch = (e: React.FormEvent) => {
    e.preventDefault();
    setSearchTrigger({ month: selectedMonth, year: selectedYear });
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <Box>
      {/* Hide PageHeader when printing */}
      <Box sx={{ display: 'block', '@media print': { display: 'none' } }}>
        <PageHeader
          title="My Payslips"
          subtitle="Access, view, and print your monthly compensation and tax deduction records."
        />

        {/* Selection Form */}
        <Card
          sx={{
            background: 'linear-gradient(135deg, #1E293B, #0F172A)',
            border: '1px solid #334155',
            borderRadius: '16px',
            p: 2,
            mb: 4,
          }}
        >
          <CardContent sx={{ p: 0 }}>
            <form onSubmit={handleFetch}>
              <Grid container spacing={2} alignItems="center">
                <Grid item xs={12} sm={4}>
                  <TextField
                    select
                    fullWidth
                    size="small"
                    label="Month"
                    value={selectedMonth}
                    onChange={(e) => setSelectedMonth(Number(e.target.value))}
                  >
                    {months.map((m, i) => (
                      <MenuItem key={i + 1} value={i + 1}>
                        {m}
                      </MenuItem>
                    ))}
                  </TextField>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <TextField
                    select
                    fullWidth
                    size="small"
                    label="Year"
                    value={selectedYear}
                    onChange={(e) => setSelectedYear(Number(e.target.value))}
                  >
                    {[2025, 2026, 2027].map((y) => (
                      <MenuItem key={y} value={y}>
                        {y}
                      </MenuItem>
                    ))}
                  </TextField>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Button
                    type="submit"
                    variant="contained"
                    fullWidth
                    startIcon={<SearchIcon />}
                    sx={{
                      background: 'linear-gradient(135deg, #8B5CF6, #6D28D9)',
                      textTransform: 'none',
                      borderRadius: '8px',
                      height: 40,
                      '&:hover': { background: 'linear-gradient(135deg, #7C3AED, #5B21B6)' },
                    }}
                  >
                    Fetch Payslip
                  </Button>
                </Grid>
              </Grid>
            </form>
          </CardContent>
        </Card>
      </Box>

      {/* Payslip Renderer */}
      {isLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 10 }}>
          <CircularProgress color="secondary" />
        </Box>
      ) : error ? (
        <Card
          sx={{
            py: 8,
            textAlign: 'center',
            background: alpha('#1E293B', 0.6),
            border: '1px dashed #334155',
            borderRadius: '16px',
          }}
        >
          <Typography variant="body1" color="text.secondary">
            No payslip found for {months[searchTrigger.month - 1]} {searchTrigger.year}.
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            This cycle may not have been finalized or approved by HR. Please contact support.
          </Typography>
        </Card>
      ) : payslip ? (
        <Box>
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 3, '@media print': { display: 'none' } }}>
            <Button
              variant="outlined"
              startIcon={<PrintIcon />}
              onClick={handlePrint}
              sx={{
                borderColor: alpha('#8B5CF6', 0.4),
                color: '#A78BFA',
                borderRadius: '8px',
                textTransform: 'none',
                '&:hover': {
                  borderColor: '#8B5CF6',
                  background: alpha('#8B5CF6', 0.05),
                },
              }}
            >
              Print Payslip
            </Button>
          </Box>

          {/* Payslip formal document container */}
          <Paper
            elevation={0}
            sx={{
              p: 4,
              border: '1px solid #334155',
              background: '#0F172A',
              borderRadius: '16px',
              color: '#F8FAFC',
              fontFamily: '"Courier New", Courier, monospace', // Mono style for formal slips
              '@media print': {
                border: 'none',
                background: '#FFF',
                color: '#000',
                p: 0,
              },
            }}
          >
            {/* Header */}
            <Box sx={{ textAlign: 'center', mb: 4 }}>
              <Typography variant="h5" fontWeight={800} sx={{ letterSpacing: 2, '@media print': { color: '#000' } }}>
                HRGENIE AI CORP
              </Typography>
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                Next-Generation AI HR Payout System
              </Typography>
              <Typography variant="body1" fontWeight={700} sx={{ mt: 2, color: '#A78BFA', '@media print': { color: '#000' } }}>
                PAYSLIP FOR THE MONTH OF {months[payslip.month - 1].toUpperCase()} {payslip.year}
              </Typography>
            </Box>

            <Divider sx={{ borderColor: '#334155', mb: 3, '@media print': { borderColor: '#000' } }} />

            {/* Profile */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">
                  Employee Name: <strong style={{ color: '#F8FAFC' }}>{payslip.employee_name}</strong>
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Employee ID: <strong style={{ color: '#F8FAFC' }}>{payslip.employee_code}</strong>
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">
                  Department: <strong style={{ color: '#F8FAFC' }}>{payslip.department}</strong>
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Designation: <strong style={{ color: '#F8FAFC' }}>{payslip.designation}</strong>
                </Typography>
              </Grid>
            </Grid>

            {/* Earnings vs Deductions Table */}
            <Grid container spacing={2}>
              {/* Earnings (Left) */}
              <Grid item xs={12} md={6}>
                <TableContainer component={Paper} sx={{ bgcolor: 'transparent', border: '1px solid #334155', '@media print': { borderColor: '#000' } }}>
                  <Table size="small">
                    <TableHead sx={{ bgcolor: alpha('#1E293B', 0.5) }}>
                      <TableRow>
                        <TableCell sx={{ color: '#F8FAFC', fontWeight: 700 }}>Earnings</TableCell>
                        <TableCell sx={{ color: '#F8FAFC', fontWeight: 700 }} align="right">Amount (₹)</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {Object.entries(payslip.earnings).map(([key, val]) => (
                        <TableRow key={key}>
                          <TableCell sx={{ color: '#94A3B8' }}>{key}</TableCell>
                          <TableCell sx={{ color: '#F8FAFC' }} align="right">{val.toLocaleString()}</TableCell>
                        </TableRow>
                      ))}
                      <TableRow sx={{ bgcolor: alpha('#1E293B', 0.3) }}>
                        <TableCell sx={{ color: '#F8FAFC', fontWeight: 700 }}>Gross Salary</TableCell>
                        <TableCell sx={{ color: '#F8FAFC', fontWeight: 700 }} align="right">
                          {payslip.gross_salary.toLocaleString()}
                        </TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
              </Grid>

              {/* Deductions (Right) */}
              <Grid item xs={12} md={6}>
                <TableContainer component={Paper} sx={{ bgcolor: 'transparent', border: '1px solid #334155', '@media print': { borderColor: '#000' } }}>
                  <Table size="small">
                    <TableHead sx={{ bgcolor: alpha('#1E293B', 0.5) }}>
                      <TableRow>
                        <TableCell sx={{ color: '#F8FAFC', fontWeight: 700 }}>Deductions</TableCell>
                        <TableCell sx={{ color: '#F8FAFC', fontWeight: 700 }} align="right">Amount (₹)</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {Object.entries(payslip.deductions).map(([key, val]) => (
                        <TableRow key={key}>
                          <TableCell sx={{ color: '#94A3B8' }}>{key}</TableCell>
                          <TableCell sx={{ color: '#F8FAFC' }} align="right">{val.toLocaleString()}</TableCell>
                        </TableRow>
                      ))}
                      <TableRow sx={{ bgcolor: alpha('#1E293B', 0.3) }}>
                        <TableCell sx={{ color: '#F8FAFC', fontWeight: 700 }}>Total Deductions</TableCell>
                        <TableCell sx={{ color: '#F8FAFC', fontWeight: 700 }} align="right">
                          {payslip.total_deductions.toLocaleString()}
                        </TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
              </Grid>
            </Grid>

            {/* Net Salary Summary */}
            <Box
              sx={{
                mt: 4,
                p: 3,
                border: '1px solid #8B5CF6',
                background: alpha('#8B5CF6', 0.05),
                borderRadius: '12px',
                textAlign: 'center',
                '@media print': {
                  borderColor: '#000',
                  color: '#000',
                  background: 'none',
                },
              }}
            >
              <Typography variant="h5" fontWeight={800} sx={{ color: '#10B981', '@media print': { color: '#000' } }}>
                NET PAYOUT: ₹{payslip.net_salary.toLocaleString()}
              </Typography>
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
                *This is a computer generated document and does not require a physical signature.
              </Typography>
            </Box>
          </Paper>
        </Box>
      ) : null}
    </Box>
  );
}
