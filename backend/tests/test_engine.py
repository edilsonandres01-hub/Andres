"""Tests del Motor de Diagnóstico"""
import json
from app.engine.diagnostic_engine import DiagnosticEngine


class TestDiagnosticEngine:
    def setup_method(self):
        # Fresh engine with shared registry already populated once
        self.engine = DiagnosticEngine()

    def test_init(self):
        assert len(self.engine.registry.rules) == 16

    def test_sql_injection(self):
        r = self.engine.diagnose(
            {
                "security": {
                    "sql_injection_risk": "high",
                    "unsanitized_inputs": 5,
                    "prepared_statements_usage": 0.2,
                    "xss_risk": "low",
                    "output_escaping": 0.9,
                    "command_injection_risk": "low",
                }
            }
        )
        assert r.total_findings > 0
        assert r.confidence.normalized_score > 0.4

    def test_clean(self):
        r = self.engine.diagnose(
            {
                "security": {
                    "sql_injection_risk": "low",
                    "unsanitized_inputs": 0,
                    "prepared_statements_usage": 1.0,
                    "xss_risk": "low",
                    "output_escaping": 1.0,
                    "command_injection_risk": "low",
                }
            }
        )
        assert r.total_findings == 0

    def test_visual(self):
        r = self.engine.diagnose(
            {
                "visual": {
                    "blur_score": 0.85,
                    "noise_level": 0.75,
                    "snr": 25.0,
                    "blockiness": 0.8,
                    "bitrate": 500,
                }
            }
        )
        assert r.total_findings >= 1

    def test_serialization(self):
        r = self.engine.diagnose(
            {
                "security": {
                    "sql_injection_risk": "high",
                    "unsanitized_inputs": 3,
                    "prepared_statements_usage": 0.4,
                }
            }
        )
        d = r.to_dict()
        assert "diagnosis_id" in d
        json.dumps(d)
