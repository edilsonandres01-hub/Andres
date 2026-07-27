import React from 'react';
import { Box, Skeleton } from '@mui/material';

export const LoadingSkeleton: React.FC = () => (
  <Box sx={{ p: 4 }} role="status" aria-label="Loading">
    <Skeleton variant="rectangular" height={200} sx={{ borderRadius: 2, mb: 2 }} />
    <Skeleton variant="text" width="60%" height={32} />
    <Skeleton variant="text" width="80%" />
    <Skeleton variant="text" width="40%" />
    <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
      <Skeleton variant="rounded" width={80} height={24} />
      <Skeleton variant="rounded" width={80} height={24} />
      <Skeleton variant="rounded" width={80} height={24} />
    </Box>
  </Box>
);
