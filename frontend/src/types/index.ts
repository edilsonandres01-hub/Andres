export type Severity = 'critical' | 'high' | 'medium' | 'low' | 'info';
export type ConfidenceLevel = 'very_high' | 'high' | 'medium' | 'low' | 'very_low' | 'inconclusive';
export type Priority = 'immediate' | 'short_term' | 'medium_term' | 'long_term';

export interface DiagnosisRequest {
  video_id?: string;
  input_data: Record<string, any>;
  context?: Record<string, any>;
}

export interface Finding {
  finding_id: string;
  category: string;
  severity: Severity;
  description: string;
  rule_id: string;
}

export interface Recommendation {
  recommendation_id: string;
  priority: Priority;
  title: string;
  description: string;
  action_items: string[];
  expected_impact: string;
  effort_estimate: string;
}

export interface ConfidenceBreakdown {
  normalized_score: number;
  confidence_level: ConfidenceLevel;
  components: {
    rule_match_score: number;
    evidence_quality_score: number;
    severity_weight_score: number;
    consistency_score: number;
  };
}

export interface DiagnosisResult {
  diagnosis_id: string;
  status: string;
  video_id?: string;
  taxonomy_version: string;
  timestamp: string;
  summary: {
    total_findings: number;
    findings_by_severity: Record<string, number>;
    findings_by_category: Record<string, number>;
    confidence_level: ConfidenceLevel;
    confidence_score: number;
  };
  findings: Finding[];
  recommendations: Recommendation[];
  confidence: ConfidenceBreakdown;
  explanation: Record<string, any>;
  metadata: Record<string, any>;
}
