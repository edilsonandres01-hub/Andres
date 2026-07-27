import React from 'react';
import { Box, Typography, Button } from '@mui/material';

interface ErrorStateProps {
  error: string;
  onRetry: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({ error, onRetry }) => (
  <Box sx={{ textAlign: 'center', py: 8 }} role="alert">
    <Typography variant="h5" gutterBottom color="error">
      Diagnosis Failed
    </Typography>
    <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
      {error}
    </Typography>
    <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
      <Button variant="contained" onClick={onRetry}>
        Retry
      </Button>
      <Button variant="outlined" onClick={() => navigator.clipboard.writeText(error)}>
        Copy Error
      </Button>
    </Box>
  </Box>
);
