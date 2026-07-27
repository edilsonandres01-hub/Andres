import React from 'react';
import { Box, Typography, Button } from '@mui/material';

interface EmptyStateProps {
  onAction: () => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ onAction }) => (
  <Box sx={{ textAlign: 'center', py: 8 }} role="status">
    <Typography variant="h5" gutterBottom>
      No Diagnoses Yet
    </Typography>
    <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
      Paste diagnostic input JSON and run your first analysis with QA Guardian
    </Typography>
    <Button variant="contained" onClick={onAction}>
      Prepare Sample Input
    </Button>
  </Box>
);
