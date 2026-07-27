"""Diagnosis Service v2.0.0"""
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import logging
from app.engine.diagnostic_engine import diagnostic_engine

logger = logging.getLogger(__name__)


class DiagnosisService:
    def __init__(self):
        self.engine = diagnostic_engine

    async def create(self, video_id: str, input_data: Dict, context: Dict = None) -> Dict:
        if not input_data:
            raise ValueError("Input data required")
        result = self.engine.diagnose(input_data, video_id)
        return {
            **result.to_dict(),
            "api_version": "2.0.0",
            "request_timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def stats(self) -> Dict:
        return {
            "engine": {"version": "2.0.0", "rules": len(self.engine.registry.rules)},
            "metrics": self.engine.metrics.summary(),
        }

    def taxonomy(self) -> Dict:
        return self.engine.taxonomy.to_dict()

    def rules(self, category: str = None) -> list:
        rules = (
            self.engine.registry.get_by_category(category)
            if category
            else self.engine.registry.get_all()
        )
        return [
            {
                "rule_id": r.rule_id,
                "name": r.name,
                "category": r.category_id,
                "severity": r.severity.value,
                "tags": r.tags,
            }
            for r in rules
        ]

    def health(self) -> Dict:
        return {
            "status": "healthy",
            "version": "2.0.0",
            "rules": len(self.engine.registry.rules),
        }


diagnosis_service = DiagnosisService()
