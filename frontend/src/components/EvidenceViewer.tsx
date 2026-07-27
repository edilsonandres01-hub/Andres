import React from 'react';
import { Card, CardContent, Typography, Box, Chip, IconButton } from '@mui/material';
import { Close } from '@mui/icons-material';
import type { Finding } from '../types';

interface Props {
  finding: Finding;
  onClose: () => void;
}

export const EvidenceViewer: React.FC<Props> = ({ finding, onClose }) => (
  <Card sx={{ borderRadius: 2, boxShadow: 4 }}>
    <CardContent>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Evidence Details</Typography>
        <IconButton onClick={onClose} aria-label="Close">
          <Close />
        </IconButton>
      </Box>
      <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
        <Chip label={finding.severity.toUpperCase()} color="error" size="small" />
        <Chip label={finding.category} size="small" variant="outlined" />
      </Box>
      <Typography variant="body1" gutterBottom>
        {finding.description}
      </Typography>
      <Typography variant="body2" color="text.secondary">
        Rule ID: {finding.rule_id}
      </Typography>
    </CardContent>
  </Card>
);
