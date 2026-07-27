import React from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardActions,
  Typography,
  Box,
  LinearProgress,
  Chip,
  Button,
  Grid,
} from '@mui/material';
import type { DiagnosisResult, Severity } from '../types';

interface Props {
  result: DiagnosisResult;
  onViewDetails: () => void;
}

const severityColors: Record<Severity, { bg: string; color: string }> = {
  critical: { bg: '#fee2e2', color: '#991b1b' },
  high: { bg: '#fed7aa', color: '#9a3412' },
  medium: { bg: '#fef3c7', color: '#92400e' },
  low: { bg: '#d1fae5', color: '#065f46' },
  info: { bg: '#dbeafe', color: '#1e40af' },
};

export const DiagnosisCard: React.FC<Props> = ({ result, onViewDetails }) => {
  const { summary, confidence } = result;

  return (
    <Card sx={{ maxWidth: 700, borderRadius: 3, boxShadow: 3 }}>
      <CardHeader
        title="Diagnosis Results"
        subheader={`ID: ${result.diagnosis_id} · ${new Date(result.timestamp).toLocaleString()}`}
      />
      <CardContent>
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
            Confidence Score: {Math.round(confidence.normalized_score * 100)}%
          </Typography>
          <LinearProgress
            variant="determinate"
            value={confidence.normalized_score * 100}
            sx={{
              height: 8,
              borderRadius: 4,
              backgroundColor: 'grey.200',
              '& .MuiLinearProgress-bar': {
                backgroundColor:
                  confidence.normalized_score >= 0.8
                    ? '#10b981'
                    : confidence.normalized_score >= 0.5
                      ? '#f59e0b'
                      : '#ef4444',
                borderRadius: 4,
              },
            }}
          />
        </Box>

        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
            Findings
          </Typography>
          <Grid container spacing={1}>
            {Object.entries(summary.findings_by_severity).map(([sev, count]) => (
              <Grid item key={sev}>
                <Chip
                  label={`${sev}: ${count}`}
                  size="small"
                  sx={{
                    backgroundColor: severityColors[sev as Severity]?.bg,
                    color: severityColors[sev as Severity]?.color,
                    fontWeight: 'bold',
                  }}
                />
              </Grid>
            ))}
          </Grid>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Total: {summary.total_findings} findings
          </Typography>
        </Box>

        {result.recommendations.slice(0, 3).map((rec) => (
          <Box key={rec.recommendation_id} sx={{ mb: 1, p: 1.5, backgroundColor: 'grey.50', borderRadius: 1 }}>
            <Typography variant="subtitle2" fontWeight="bold">
              {rec.priority === 'immediate' ? '[NOW]' : '[NEXT]'} {rec.title}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {rec.description}
            </Typography>
          </Box>
        ))}
      </CardContent>
      <CardActions sx={{ justifyContent: 'flex-end', p: 2 }}>
        <Button variant="contained" onClick={onViewDetails}>
          View Details
        </Button>
      </CardActions>
    </Card>
  );
};
