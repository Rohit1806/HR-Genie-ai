import React, { useCallback } from 'react';
import { Box, Typography, Button, alpha, LinearProgress } from '@mui/material';
import { DataGrid, GridColDef, GridRowParams, GridToolbarContainer } from '@mui/x-data-grid';
import { FileDownload as FileDownloadIcon, SearchOff as SearchOffIcon } from '@mui/icons-material';

interface DataTableProps {
  rows: Record<string, unknown>[];
  columns: GridColDef[];
  loading?: boolean;
  emptyMessage?: string;
  onRowClick?: (params: GridRowParams) => void;
  showExport?: boolean;
  pageSize?: number;
  getRowId?: (row: Record<string, unknown>) => string | number;
}

function CustomToolbar({ showExport }: { showExport: boolean }) {
  const handleExportCSV = () => {
    // CSV export logic
  };

  return showExport ? (
    <GridToolbarContainer sx={{ px: 2, py: 1, borderBottom: '1px solid #334155' }}>
      <Box sx={{ flex: 1 }} />
      <Button
        size="small"
        startIcon={<FileDownloadIcon sx={{ fontSize: '16px !important' }} />}
        onClick={handleExportCSV}
        sx={{
          color: '#94A3B8',
          textTransform: 'none',
          fontSize: '0.8rem',
          '&:hover': { background: alpha('#8B5CF6', 0.08), color: '#8B5CF6' },
        }}
      >
        Export CSV
      </Button>
    </GridToolbarContainer>
  ) : null;
}

function CustomNoRowsOverlay({ message }: { message: string }) {
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100%',
        py: 6,
      }}
    >
      <SearchOffIcon sx={{ fontSize: 56, color: '#334155', mb: 2 }} />
      <Typography variant="body1" sx={{ color: '#64748B', fontWeight: 500 }}>
        {message}
      </Typography>
      <Typography variant="body2" sx={{ color: '#475569', mt: 0.5 }}>
        Try adjusting your filters or search query
      </Typography>
    </Box>
  );
}

export const DataTable: React.FC<DataTableProps> = ({
  rows,
  columns,
  loading = false,
  emptyMessage = 'No data found',
  onRowClick,
  showExport = false,
  pageSize = 10,
  getRowId,
}) => {
  const handleRowClick = useCallback(
    (params: GridRowParams) => {
      if (onRowClick) onRowClick(params);
    },
    [onRowClick]
  );

  return (
    <Box
      sx={{
        width: '100%',
        background: alpha('#1E293B', 0.7),
        backdropFilter: 'blur(20px)',
        borderRadius: '16px',
        border: '1px solid',
        borderColor: alpha('#334155', 0.5),
        overflow: 'hidden',
        animation: 'fadeIn 0.5s ease-out',
        '@keyframes fadeIn': {
          from: { opacity: 0, transform: 'translateY(8px)' },
          to: { opacity: 1, transform: 'translateY(0)' },
        },
        '& .MuiDataGrid-root': {
          border: 'none',
          fontSize: '0.875rem',
        },
        '& .MuiDataGrid-columnHeaders': {
          background: alpha('#0F172A', 0.5),
          borderBottom: '1px solid #334155',
          '& .MuiDataGrid-columnHeaderTitle': {
            color: '#94A3B8',
            fontWeight: 600,
            fontSize: '0.8rem',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
          },
        },
        '& .MuiDataGrid-columnSeparator': {
          color: '#334155',
        },
        '& .MuiDataGrid-row': {
          borderBottom: '1px solid',
          borderColor: alpha('#334155', 0.3),
          color: '#F8FAFC',
          transition: 'background 0.15s ease',
          cursor: onRowClick ? 'pointer' : 'default',
          '&:hover': {
            background: alpha('#8B5CF6', 0.04),
          },
          '&.Mui-selected': {
            background: alpha('#8B5CF6', 0.08),
            '&:hover': {
              background: alpha('#8B5CF6', 0.12),
            },
          },
        },
        '& .MuiDataGrid-cell': {
          borderBottom: 'none',
          color: '#E2E8F0',
          py: 1.5,
        },
        '& .MuiDataGrid-footerContainer': {
          borderTop: '1px solid #334155',
          background: alpha('#0F172A', 0.3),
        },
        '& .MuiTablePagination-root': {
          color: '#94A3B8',
        },
        '& .MuiTablePagination-selectIcon': {
          color: '#94A3B8',
        },
        '& .MuiIconButton-root': {
          color: '#94A3B8',
          '&.Mui-disabled': { color: '#475569' },
        },
        '& .MuiCheckbox-root': {
          color: '#475569',
          '&.Mui-checked': { color: '#8B5CF6' },
        },
        '& .MuiDataGrid-overlay': {
          background: 'transparent',
        },
      }}
    >
      <DataGrid
        rows={rows}
        columns={columns}
        loading={loading}
        onRowClick={handleRowClick}
        getRowId={getRowId as (row: Record<string, unknown>) => string | number}
        initialState={{
          pagination: { paginationModel: { pageSize } },
        }}
        pageSizeOptions={[5, 10, 25, 50]}
        disableRowSelectionOnClick
        autoHeight
        slots={{
          toolbar: () => <CustomToolbar showExport={showExport} />,
          noRowsOverlay: () => <CustomNoRowsOverlay message={emptyMessage} />,
          loadingOverlay: LinearProgress as React.JSXElementConstructor<unknown>,
        }}
        slotProps={{
          loadingOverlay: {
            sx: { '& .MuiLinearProgress-bar': { background: 'linear-gradient(90deg, #8B5CF6, #A78BFA)' } },
          } as Record<string, unknown>,
        }}
        sx={{
          minHeight: 300,
        }}
      />
    </Box>
  );
};

export default DataTable;
