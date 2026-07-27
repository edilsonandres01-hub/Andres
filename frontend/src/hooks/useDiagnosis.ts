import { useState, useCallback } from 'react';
import axios from 'axios';
import type { DiagnosisResult, DiagnosisRequest } from '../types';

const API_BASE = '/api/v1/diagnosis';

export function useDiagnosis() {
  const [result, setResult] = useState<DiagnosisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const diagnose = useCallback(async (request: DiagnosisRequest) => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await axios.post<DiagnosisResult>(`${API_BASE}/`, request);
      setResult(data);
      return data;
    } catch (err: any) {
      const message = err.response?.data?.detail || err.message || 'Unknown error';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
    setLoading(false);
  }, []);

  return { result, loading, error, diagnose, reset };
}
