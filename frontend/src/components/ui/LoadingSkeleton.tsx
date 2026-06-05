import React from 'react';
import { Box, Skeleton, alpha, Grid } from '@mui/material';

interface LoadingSkeletonProps {
  variant: 'card' | 'table' | 'list' | 'profile';
  count?: number;
}

const shimmerAnimation = {
  animation: 'shimmer 2s ease-in-out infinite',
  '@keyframes shimmer': {
    '0%': { opacity: 0.5 },
    '50%': { opacity: 1 },
    '100%': { opacity: 0.5 },
  },
};

const CardSkeleton: React.FC = () => (
  <Box
    sx={{
      p: 3,
      background: alpha('#1E293B', 0.7),
      borderRadius: '16px',
      border: '1px solid',
      borderColor: alpha('#334155', 0.5),
      ...shimmerAnimation,
    }}
  >
    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
      <Skeleton
        variant="rounded"
        width={44}
        height={44}
        sx={{ bgcolor: alpha('#334155', 0.5), borderRadius: '12px' }}
      />
      <Skeleton
        variant="rounded"
        width={60}
        height={24}
        sx={{ bgcolor: alpha('#334155', 0.5), borderRadius: '8px' }}
      />
    </Box>
    <Skeleton
      variant="text"
      width="60%"
      height={36}
      sx={{ bgcolor: alpha('#334155', 0.5), mb: 0.5 }}
    />
    <Skeleton
      variant="text"
      width="40%"
      height={20}
      sx={{ bgcolor: alpha('#334155', 0.5) }}
    />
  </Box>
);

const TableSkeleton: React.FC = () => (
  <Box
    sx={{
      background: alpha('#1E293B', 0.7),
      borderRadius: '16px',
      border: '1px solid',
      borderColor: alpha('#334155', 0.5),
      overflow: 'hidden',
      ...shimmerAnimation,
    }}
  >
    {/* Header */}
    <Box
      sx={{
        display: 'flex',
        gap: 3,
        px: 3,
        py: 2,
        background: alpha('#0F172A', 0.5),
        borderBottom: '1px solid #334155',
      }}
    >
      {[120, 100, 80, 140, 60, 100].map((w, i) => (
        <Skeleton
          key={i}
          variant="text"
          width={w}
          height={16}
          sx={{ bgcolor: alpha('#334155', 0.5) }}
        />
      ))}
    </Box>

    {/* Rows */}
    {Array.from({ length: 5 }).map((_, rowIdx) => (
      <Box
        key={rowIdx}
        sx={{
          display: 'flex',
          gap: 3,
          px: 3,
          py: 2,
          borderBottom: rowIdx < 4 ? '1px solid' : 'none',
          borderColor: alpha('#334155', 0.3),
          alignItems: 'center',
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, width: 120 }}>
          <Skeleton
            variant="circular"
            width={32}
            height={32}
            sx={{ bgcolor: alpha('#334155', 0.5) }}
          />
          <Skeleton
            variant="text"
            width={80}
            height={16}
            sx={{ bgcolor: alpha('#334155', 0.5) }}
          />
        </Box>
        {[100, 80, 140, 60, 100].map((w, i) => (
          <Skeleton
            key={i}
            variant="text"
            width={w}
            height={16}
            sx={{ bgcolor: alpha('#334155', 0.5) }}
          />
        ))}
      </Box>
    ))}
  </Box>
);

const ListSkeleton: React.FC = () => (
  <Box sx={{ ...shimmerAnimation }}>
    {Array.from({ length: 4 }).map((_, i) => (
      <Box
        key={i}
        sx={{
          display: 'flex',
          gap: 2,
          p: 2,
          mb: 1,
          background: alpha('#1E293B', 0.5),
          borderRadius: '12px',
          alignItems: 'center',
        }}
      >
        <Skeleton
          variant="circular"
          width={40}
          height={40}
          sx={{ bgcolor: alpha('#334155', 0.5) }}
        />
        <Box sx={{ flex: 1 }}>
          <Skeleton
            variant="text"
            width="50%"
            height={18}
            sx={{ bgcolor: alpha('#334155', 0.5), mb: 0.5 }}
          />
          <Skeleton
            variant="text"
            width="30%"
            height={14}
            sx={{ bgcolor: alpha('#334155', 0.5) }}
          />
        </Box>
        <Skeleton
          variant="rounded"
          width={60}
          height={24}
          sx={{ bgcolor: alpha('#334155', 0.5), borderRadius: '20px' }}
        />
      </Box>
    ))}
  </Box>
);

const ProfileSkeleton: React.FC = () => (
  <Box sx={{ display: 'flex', gap: 3, ...shimmerAnimation }}>
    {/* Left Panel */}
    <Box
      sx={{
        width: '30%',
        p: 3,
        background: alpha('#1E293B', 0.7),
        borderRadius: '16px',
        border: '1px solid',
        borderColor: alpha('#334155', 0.5),
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
      }}
    >
      <Skeleton
        variant="circular"
        width={96}
        height={96}
        sx={{ bgcolor: alpha('#334155', 0.5), mb: 2 }}
      />
      <Skeleton
        variant="text"
        width={140}
        height={24}
        sx={{ bgcolor: alpha('#334155', 0.5), mb: 0.5 }}
      />
      <Skeleton
        variant="text"
        width={100}
        height={16}
        sx={{ bgcolor: alpha('#334155', 0.5), mb: 1 }}
      />
      <Skeleton
        variant="rounded"
        width={80}
        height={24}
        sx={{ bgcolor: alpha('#334155', 0.5), borderRadius: '20px' }}
      />
    </Box>

    {/* Right Panel */}
    <Box sx={{ flex: 1 }}>
      <Box
        sx={{
          p: 3,
          background: alpha('#1E293B', 0.7),
          borderRadius: '16px',
          border: '1px solid',
          borderColor: alpha('#334155', 0.5),
        }}
      >
        <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
          {[80, 80, 80, 80].map((w, i) => (
            <Skeleton
              key={i}
              variant="rounded"
              width={w}
              height={32}
              sx={{ bgcolor: alpha('#334155', 0.5), borderRadius: '8px' }}
            />
          ))}
        </Box>
        <Grid container spacing={2}>
          {Array.from({ length: 6 }).map((_, i) => (
            <Grid item xs={6} key={i}>
              <Skeleton
                variant="text"
                width="40%"
                height={14}
                sx={{ bgcolor: alpha('#334155', 0.5), mb: 0.5 }}
              />
              <Skeleton
                variant="text"
                width="70%"
                height={18}
                sx={{ bgcolor: alpha('#334155', 0.5) }}
              />
            </Grid>
          ))}
        </Grid>
      </Box>
    </Box>
  </Box>
);

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({
  variant,
  count = 1,
}) => {
  const renderVariant = () => {
    switch (variant) {
      case 'card':
        return (
          <Grid container spacing={2}>
            {Array.from({ length: count }).map((_, i) => (
              <Grid item xs={12} sm={6} md={3} key={i}>
                <CardSkeleton />
              </Grid>
            ))}
          </Grid>
        );
      case 'table':
        return <TableSkeleton />;
      case 'list':
        return <ListSkeleton />;
      case 'profile':
        return <ProfileSkeleton />;
      default:
        return null;
    }
  };

  return <>{renderVariant()}</>;
};

export default LoadingSkeleton;
