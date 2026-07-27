import React from 'react';
import { Box, Typography, Chip } from '@mui/material';
import type { Finding, Severity } from '../types';

interface Props {
  findings: Finding[];
  selectedId?: string;
  onSelect: (f: Finding) => void;
}

const severityIcons: Record<Severity, string> = {
  critical: 'CRIT',
  high: 'HIGH',
  medium: 'MED',
  low: 'LOW',
  info: 'INFO',
};

export const Timeline: React.FC<Props> = ({ findings, selectedId, onSelect }) => (
  <Box sx={{ position: 'relative', pl: 4 }}>
    <Box sx={{ position: 'absolute', left: 16, top: 0, bottom: 0, width: 2, bgcolor: 'grey.300' }} />
    {findings.map((finding) => (
      <Box
        key={finding.finding_id}
        onClick={() => onSelect(finding)}
        sx={{
          mb: 2,
          p: 2,
          borderRadius: 2,
          cursor: 'pointer',
          border: '1px solid',
          borderColor: selectedId === finding.finding_id ? 'primary.main' : 'grey.200',
          backgroundColor: selectedId === finding.finding_id ? 'primary.50' : 'white',
          '&:hover': { boxShadow: 2 },
          transition: 'all 0.2s',
        }}
      >
        <Typography variant="subtitle2" fontWeight="bold">
          [{severityIcons[finding.severity as Severity]}] {finding.description}
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
          <Chip label={finding.severity} size="small" />
          <Chip label={finding.category} size="small" variant="outlined" />
        </Box>
      </Box>
    ))}
  </Box>
);
