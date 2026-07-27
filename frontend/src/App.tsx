import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Tabs,
  Tab,
  TextField,
  Button,
  Grid,
} from '@mui/material';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { DiagnosisCard } from './components/DiagnosisCard';
import { Timeline } from './components/Timeline';
import { EvidenceViewer } from './components/EvidenceViewer';
import { LogViewer } from './components/LogViewer';
import { LoadingSkeleton } from './components/LoadingSkeleton';
import { EmptyState } from './components/EmptyState';
import { ErrorState } from './components/ErrorState';
import { useDiagnosis } from './hooks/useDiagnosis';
import type { Finding } from './types';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#0f4c81' },
    background: { default: '#f3f6f9' },
  },
  typography: {
    fontFamily: '"IBM Plex Sans", "Segoe UI", sans-serif',
  },
});

const sampleInput = JSON.stringify(
  {
    security: {
      sql_injection_risk: 'high',
      unsanitized_inputs: 5,
      prepared_statements_usage: 0.2,
      xss_risk: 'low',
      output_escaping: 0.9,
      command_injection_risk: 'low',
    },
  },
  null,
  2
);

export default function App() {
  const { result, loading, error, diagnose, reset } = useDiagnosis();
  const [input, setInput] = useState(sampleInput);
  const [tab, setTab] = useState(0);
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(null);

  const handleSubmit = async () => {
    try {
      const parsed = JSON.parse(input);
      await diagnose({ input_data: parsed });
    } catch (e: any) {
      alert(`Invalid JSON: ${e.message}`);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box
        sx={{
          minHeight: '100vh',
          background: 'linear-gradient(160deg, #e8f1f8 0%, #f7fafc 45%, #dfeaf3 100%)',
        }}
      >
        <Container maxWidth="lg" sx={{ py: 4 }}>
          <Typography variant="h3" fontWeight="bold" gutterBottom>
            QA Guardian
          </Typography>
          <Typography variant="subtitle1" color="text.secondary" gutterBottom>
            Enterprise Diagnostic Engine v2.0.0
          </Typography>

          <Paper sx={{ p: 3, mb: 4 }}>
            <Typography variant="h6" gutterBottom>
              Input Data
            </Typography>
            <TextField
              multiline
              rows={10}
              fullWidth
              value={input}
              onChange={(e) => setInput(e.target.value)}
              sx={{ fontFamily: 'monospace', mb: 2 }}
            />
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button variant="contained" onClick={handleSubmit} disabled={loading}>
                {loading ? 'Analyzing...' : 'Run Diagnosis'}
              </Button>
              <Button variant="outlined" onClick={reset}>
                Reset
              </Button>
            </Box>
          </Paper>

          {loading && <LoadingSkeleton />}
          {error && !loading && <ErrorState error={error} onRetry={handleSubmit} />}
          {!result && !loading && !error && <EmptyState onAction={() => setInput(sampleInput)} />}

          {result && (
            <Box>
              <DiagnosisCard result={result} onViewDetails={() => setTab(0)} />

              <Paper sx={{ mt: 3 }}>
                <Tabs value={tab} onChange={(_, v) => setTab(v)}>
                  <Tab label={`Findings (${result.findings.length})`} />
                  <Tab label="Evidence" disabled={!selectedFinding} />
                  <Tab label="Logs" />
                </Tabs>

                <Box sx={{ p: 3 }}>
                  {tab === 0 && (
                    <Grid container spacing={3}>
                      <Grid item xs={12} md={8}>
                        <Timeline
                          findings={result.findings}
                          selectedId={selectedFinding?.finding_id}
                          onSelect={(f) => {
                            setSelectedFinding(f);
                            setTab(1);
                          }}
                        />
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <Typography variant="h6" gutterBottom>
                          Recommendations
                        </Typography>
                        {result.recommendations.map((rec) => (
                          <Box key={rec.recommendation_id} sx={{ mb: 1, p: 1.5, bgcolor: 'grey.50', borderRadius: 1 }}>
                            <Typography variant="subtitle2">{rec.title}</Typography>
                            <Typography variant="caption">{rec.description}</Typography>
                          </Box>
                        ))}
                      </Grid>
                    </Grid>
                  )}

                  {tab === 1 && selectedFinding && (
                    <EvidenceViewer finding={selectedFinding} onClose={() => setSelectedFinding(null)} />
                  )}

                  {tab === 2 && (
                    <LogViewer
                      logs={[
                        { timestamp: new Date().toISOString(), level: 'INFO', message: 'Diagnosis started' },
                        {
                          timestamp: new Date().toISOString(),
                          level: 'INFO',
                          message: `Rules evaluated: ${result.metadata.rules_evaluated}`,
                        },
                        {
                          timestamp: new Date().toISOString(),
                          level: 'INFO',
                          message: `Rules matched: ${result.metadata.rules_matched}`,
                        },
                        {
                          timestamp: new Date().toISOString(),
                          level: 'INFO',
                          message: `Confidence: ${result.confidence.normalized_score}`,
                        },
                        { timestamp: new Date().toISOString(), level: 'INFO', message: 'Diagnosis completed' },
                      ]}
                    />
                  )}
                </Box>
              </Paper>
            </Box>
          )}
        </Container>
      </Box>
    </ThemeProvider>
  );
}
