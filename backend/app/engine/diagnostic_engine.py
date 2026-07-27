"""
QA Guardian - Enterprise Diagnostic Engine v2.0.0
Motor de Diagnóstico Determinístico Completo
"""
import hashlib
import logging
import re
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

ENGINE_VERSION = "2.0.0"
TAXONOMY_VERSION = "2.0.0"


class RuleSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class RuleOperator(Enum):
    EQUALS = "eq"
    NOT_EQUALS = "neq"
    GREATER_THAN = "gt"
    LESS_THAN = "lt"
    GREATER_EQUAL = "gte"
    LESS_EQUAL = "lte"
    BETWEEN = "between"
    CONTAINS = "contains"
    IN_LIST = "in_list"
    EXISTS = "exists"
    NOT_EXISTS = "not_exists"
    MATCHES_REGEX = "matches_regex"


class ConfidenceLevel(Enum):
    VERY_HIGH = "very_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_LOW = "very_low"
    INCONCLUSIVE = "inconclusive"

    @classmethod
    def from_score(cls, score: float) -> "ConfidenceLevel":
        if score >= 0.90:
            return cls.VERY_HIGH
        elif score >= 0.75:
            return cls.HIGH
        elif score >= 0.50:
            return cls.MEDIUM
        elif score >= 0.25:
            return cls.LOW
        elif score >= 0.10:
            return cls.VERY_LOW
        else:
            return cls.INCONCLUSIVE


class DiagnosisStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    INCONCLUSIVE = "inconclusive"


@dataclass
class TaxonomyNode:
    id: str
    name: str
    description: str
    level: int
    parent_id: Optional[str] = None
    children: List["TaxonomyNode"] = field(default_factory=list)
    rules: List[str] = field(default_factory=list)
    ml_features: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "level": self.level,
            "parent_id": self.parent_id,
            "children": [c.to_dict() for c in self.children],
            "rules_count": len(self.rules),
            "ml_ready": len(self.ml_features) > 0,
        }


class EnterpriseTaxonomy:
    VERSION = TAXONOMY_VERSION

    def __init__(self):
        self.root = self._build()
        self.flat_index = {}
        self.rule_to_category = {}
        self._index()

    def _build(self) -> TaxonomyNode:
        visual = TaxonomyNode(
            id="VISUAL",
            name="Visual Diagnostics",
            description="Visual quality diagnostics",
            level=1,
            parent_id="ROOT",
        )
        vq = TaxonomyNode(
            id="VISUAL_QUALITY",
            name="Visual Quality",
            description="Visual quality assessment",
            level=2,
            parent_id="VISUAL",
            rules=["VQ-001", "VQ-002", "VQ-003", "VQ-004", "VQ-005"],
            ml_features=["psnr", "ssim", "blur_score", "noise_level", "bitrate"],
        )
        vq.children = [
            TaxonomyNode(id="VQ_BLUR", name="Blur Detection", description="", level=3, parent_id="VISUAL_QUALITY", rules=["VQ-001"]),
            TaxonomyNode(id="VQ_NOISE", name="Noise Detection", description="", level=3, parent_id="VISUAL_QUALITY", rules=["VQ-002"]),
            TaxonomyNode(id="VQ_COMPRESSION", name="Compression Artifacts", description="", level=3, parent_id="VISUAL_QUALITY", rules=["VQ-003"]),
            TaxonomyNode(id="VQ_COLOR", name="Color Accuracy", description="", level=3, parent_id="VISUAL_QUALITY", rules=["VQ-004"]),
            TaxonomyNode(id="VQ_BRIGHTNESS", name="Brightness & Contrast", description="", level=3, parent_id="VISUAL_QUALITY", rules=["VQ-005"]),
        ]
        visual.children = [vq]

        audio = TaxonomyNode(id="AUDIO", name="Audio Diagnostics", description="Audio quality diagnostics", level=1, parent_id="ROOT")
        aq = TaxonomyNode(
            id="AUDIO_QUALITY",
            name="Audio Quality",
            description="Audio quality assessment",
            level=2,
            parent_id="AUDIO",
            rules=["AQ-001", "AQ-002", "AQ-003"],
            ml_features=["snr", "thd", "lufs", "dynamic_range"],
        )
        aq.children = [
            TaxonomyNode(id="AQ_DISTORTION", name="Audio Distortion", description="", level=3, parent_id="AUDIO_QUALITY", rules=["AQ-001"]),
            TaxonomyNode(id="AQ_NOISE", name="Background Noise", description="", level=3, parent_id="AUDIO_QUALITY", rules=["AQ-002"]),
            TaxonomyNode(id="AQ_VOLUME", name="Volume Issues", description="", level=3, parent_id="AUDIO_QUALITY", rules=["AQ-003"]),
        ]
        audio.children = [aq]

        security = TaxonomyNode(id="SECURITY", name="Security Diagnostics", description="Security vulnerability assessment", level=1, parent_id="ROOT")
        sec_inj = TaxonomyNode(
            id="SECURITY_INJECTION",
            name="Injection Vulnerabilities",
            description="SQL Injection, XSS detection",
            level=2,
            parent_id="SECURITY",
            rules=["SEC-001", "SEC-002", "SEC-003", "SEC-004"],
            ml_features=["query_complexity", "input_sanitization_score"],
        )
        sec_inj.children = [
            TaxonomyNode(id="SI_SQL", name="SQL Injection", description="", level=3, parent_id="SECURITY_INJECTION", rules=["SEC-001"]),
            TaxonomyNode(id="SI_XSS", name="Cross-Site Scripting", description="", level=3, parent_id="SECURITY_INJECTION", rules=["SEC-002"]),
            TaxonomyNode(id="SI_CMD", name="Command Injection", description="", level=3, parent_id="SECURITY_INJECTION", rules=["SEC-003"]),
            TaxonomyNode(id="SI_PATH", name="Path Traversal", description="", level=3, parent_id="SECURITY_INJECTION", rules=["SEC-004"]),
        ]
        security.children = [sec_inj]

        perf = TaxonomyNode(id="PERFORMANCE", name="Performance Diagnostics", description="Performance assessment", level=1, parent_id="ROOT")
        perf_lat = TaxonomyNode(
            id="PERFORMANCE_LATENCY",
            name="Latency Issues",
            description="Response time and latency",
            level=2,
            parent_id="PERFORMANCE",
            rules=["PERF-001", "PERF-002"],
            ml_features=["response_time", "throughput", "error_rate"],
        )
        perf_lat.children = [
            TaxonomyNode(id="PL_RESPONSE", name="Response Time", description="", level=3, parent_id="PERFORMANCE_LATENCY", rules=["PERF-001"]),
            TaxonomyNode(id="PL_ERRORS", name="Error Rate", description="", level=3, parent_id="PERFORMANCE_LATENCY", rules=["PERF-002"]),
        ]
        perf.children = [perf_lat]

        acc = TaxonomyNode(id="ACCESSIBILITY", name="Accessibility Diagnostics", description="WCAG compliance", level=1, parent_id="ROOT")
        acc_con = TaxonomyNode(
            id="ACCESSIBILITY_CONTRAST",
            name="Contrast Issues",
            description="Color contrast compliance",
            level=2,
            parent_id="ACCESSIBILITY",
            rules=["ACC-001", "ACC-002"],
            ml_features=["contrast_ratio", "wcag_level_score"],
        )
        acc_con.children = [
            TaxonomyNode(id="AC_CONTRAST", name="Color Contrast", description="", level=3, parent_id="ACCESSIBILITY_CONTRAST", rules=["ACC-001"]),
            TaxonomyNode(id="AC_ALT_TEXT", name="Missing Alt Text", description="", level=3, parent_id="ACCESSIBILITY_CONTRAST", rules=["ACC-002"]),
        ]
        acc.children = [acc_con]

        return TaxonomyNode(
            id="ROOT",
            name="QA Guardian Diagnostic Taxonomy",
            description="Complete diagnostic taxonomy",
            level=0,
            children=[visual, audio, security, perf, acc],
        )

    def _index(self):
        def traverse(node: TaxonomyNode):
            self.flat_index[node.id] = node
            for rid in node.rules:
                self.rule_to_category[rid] = node.id
            for child in node.children:
                traverse(child)

        traverse(self.root)

    def get_category_by_rule(self, rule_id: str) -> Optional[TaxonomyNode]:
        cid = self.rule_to_category.get(rule_id)
        return self.flat_index.get(cid) if cid else None

    def to_dict(self) -> Dict:
        return {
            "version": self.VERSION,
            "taxonomy": self.root.to_dict(),
            "total_nodes": len(self.flat_index),
            "total_rules": len(self.rule_to_category),
        }


enterprise_taxonomy = EnterpriseTaxonomy()


@dataclass
class RuleCondition:
    field: str
    operator: RuleOperator
    value: Any = None
    description: str = ""
    weight: float = 1.0

    def evaluate(self, context: Dict) -> Tuple[bool, Dict]:
        actual = self._resolve(context, self.field)
        evidence = {
            "field": self.field,
            "operator": self.operator.value,
            "expected": str(self.value),
            "actual": str(actual),
        }
        try:
            if self.operator == RuleOperator.EQUALS:
                matched = actual == self.value
            elif self.operator == RuleOperator.NOT_EQUALS:
                matched = actual != self.value
            elif self.operator == RuleOperator.GREATER_THAN:
                matched = float(actual) > float(self.value)
            elif self.operator == RuleOperator.LESS_THAN:
                matched = float(actual) < float(self.value)
            elif self.operator == RuleOperator.GREATER_EQUAL:
                try:
                    matched = float(actual) >= float(self.value)
                except (TypeError, ValueError):
                    order = {"low": 0, "medium": 1, "high": 2}
                    matched = order.get(str(actual).lower(), -1) >= order.get(str(self.value).lower(), 99)
            elif self.operator == RuleOperator.LESS_EQUAL:
                matched = float(actual) <= float(self.value)
            elif self.operator == RuleOperator.BETWEEN:
                matched = float(self.value[0]) <= float(actual) <= float(self.value[1])
            elif self.operator == RuleOperator.CONTAINS:
                matched = str(self.value) in str(actual)
            elif self.operator == RuleOperator.IN_LIST:
                matched = actual in self.value
            elif self.operator == RuleOperator.EXISTS:
                matched = actual is not None
            elif self.operator == RuleOperator.NOT_EXISTS:
                matched = actual is None
            elif self.operator == RuleOperator.MATCHES_REGEX:
                matched = bool(re.match(str(self.value), str(actual)))
            else:
                matched = False
            evidence["matched"] = matched
            return matched, evidence
        except Exception as e:
            evidence["matched"] = False
            evidence["error"] = str(e)
            return False, evidence

    def _resolve(self, context: Dict, field_path: str) -> Any:
        for key in field_path.split("."):
            if isinstance(context, dict):
                context = context.get(key)
            else:
                return None
        return context


@dataclass
class DiagnosticRule:
    rule_id: str
    name: str
    description: str
    category_id: str
    severity: RuleSeverity
    conditions: List[RuleCondition]
    logic_operator: str = "AND"
    weight: float = 1.0
    diagnosis_template: str = ""
    recommendation_template: str = ""
    priority: int = 100
    enabled: bool = True
    tags: List[str] = field(default_factory=list)

    def evaluate(self, context: Dict) -> Tuple[bool, float, Dict]:
        if not self.enabled:
            return False, 0.0, {}
        results, evidences = [], []
        for c in self.conditions:
            m, e = c.evaluate(context)
            results.append(m)
            evidences.append(e)
        matched = all(results) if self.logic_operator == "AND" else any(results)
        total_w = sum(c.weight for c in self.conditions)
        conf = (
            (sum(c.weight for c, r in zip(self.conditions, results) if r) / total_w * self.weight)
            if matched and total_w > 0
            else 0.0
        )
        return matched, conf, {
            "rule_id": self.rule_id,
            "rule_name": self.name,
            "category_id": self.category_id,
            "severity": self.severity.value,
            "matched": matched,
            "confidence_contribution": conf,
            "conditions": evidences,
        }


class RulesRegistry:
    def __init__(self):
        self.rules: Dict[str, DiagnosticRule] = {}
        self.by_category: Dict[str, List[str]] = {}

    def register(self, rule: DiagnosticRule):
        self.rules[rule.rule_id] = rule
        self.by_category.setdefault(rule.category_id, []).append(rule.rule_id)

    def get_all(self) -> List[DiagnosticRule]:
        return sorted([r for r in self.rules.values() if r.enabled], key=lambda r: r.priority)

    def get_by_category(self, cid: str) -> List[DiagnosticRule]:
        return [self.rules[rid] for rid in self.by_category.get(cid, []) if rid in self.rules]


rules_registry = RulesRegistry()


@dataclass
class EvidenceQuality:
    completeness: float = 0.5
    reliability: float = 0.5
    relevance: float = 0.5
    consistency: float = 0.5
    timeliness: float = 0.5

    @property
    def overall(self) -> float:
        return (
            self.completeness * 0.25
            + self.reliability * 0.30
            + self.relevance * 0.25
            + self.consistency * 0.10
            + self.timeliness * 0.10
        )


@dataclass
class ConfidenceScore:
    rule_match_score: float = 0.0
    evidence_quality_score: float = 0.0
    severity_weight_score: float = 0.0
    consistency_score: float = 0.0
    raw_score: float = 0.0
    normalized_score: float = 0.0
    conflict_penalty: float = 0.0
    confidence_level: ConfidenceLevel = ConfidenceLevel.INCONCLUSIVE
    contributing_rules: List[str] = field(default_factory=list)

    @classmethod
    def calculate(
        cls,
        matched: List[Dict],
        total: int,
        eq: EvidenceQuality,
        conflicts: List = None,
        missing: List = None,
    ) -> "ConfidenceScore":
        conflicts = conflicts or []
        missing = missing or []
        rms = len(matched) / total if total > 0 else 0
        eqs = eq.overall
        sw = {"critical": 1.0, "high": 0.8, "medium": 0.5, "low": 0.3, "info": 0.1}
        sws = sum(sw.get(r.get("severity", "info"), 0.1) for r in matched) / len(matched) if matched else 0
        cats = set(r.get("category_id") for r in matched)
        cs = 1.0 / len(cats) if cats else 0
        raw = rms * 0.35 + eqs * 0.30 + sws * 0.20 + cs * 0.15
        cp = min(len(conflicts) * 0.08, 0.40)
        up = max((0.5 - rms) * 0.3, 0) if rms < 0.5 else 0
        mp = min(len(missing) * 0.05, 0.25)
        ns = max(raw - cp - up - mp, 0.0)
        return cls(
            rule_match_score=rms,
            evidence_quality_score=eqs,
            severity_weight_score=sws,
            consistency_score=cs,
            raw_score=raw,
            normalized_score=ns,
            conflict_penalty=cp,
            confidence_level=ConfidenceLevel.from_score(ns),
            contributing_rules=[r.get("rule_id", "") for r in matched],
        )

    def to_dict(self) -> Dict:
        return {
            "normalized_score": round(self.normalized_score, 4),
            "confidence_level": self.confidence_level.value,
            "components": {
                "rule_match_score": round(self.rule_match_score, 4),
                "evidence_quality_score": round(self.evidence_quality_score, 4),
                "severity_weight_score": round(self.severity_weight_score, 4),
                "consistency_score": round(self.consistency_score, 4),
            },
            "penalties": {"conflict": round(self.conflict_penalty, 4)},
        }


@dataclass
class Finding:
    finding_id: str
    category_id: str
    category_name: str
    severity: str
    description: str
    evidence: Dict
    rule_id: str
    confidence_contribution: float


@dataclass
class Recommendation:
    recommendation_id: str
    category_id: str
    priority: str
    title: str
    description: str
    action_items: List[str]
    expected_impact: str
    effort_estimate: str


@dataclass
class DiagnosisResult:
    diagnosis_id: str
    status: DiagnosisStatus
    video_id: Optional[str]
    taxonomy_version: str
    timestamp: str
    findings: List[Finding]
    total_findings: int
    findings_by_severity: Dict[str, int]
    findings_by_category: Dict[str, int]
    confidence: ConfidenceScore
    recommendations: List[Recommendation]
    explanation: Dict
    engine_version: str = ENGINE_VERSION
    processing_time_ms: float = 0.0
    rules_evaluated: int = 0
    rules_matched: int = 0
    ml_feature_vector: Optional[List[float]] = None
    ml_ready: bool = False

    def to_dict(self) -> Dict:
        return {
            "diagnosis_id": self.diagnosis_id,
            "status": self.status.value,
            "video_id": self.video_id,
            "taxonomy_version": self.taxonomy_version,
            "timestamp": self.timestamp,
            "summary": {
                "total_findings": self.total_findings,
                "findings_by_severity": self.findings_by_severity,
                "findings_by_category": self.findings_by_category,
                "confidence_level": self.confidence.confidence_level.value,
                "confidence_score": round(self.confidence.normalized_score, 4),
            },
            "findings": [
                {
                    "finding_id": f.finding_id,
                    "category": f.category_name,
                    "severity": f.severity,
                    "description": f.description,
                    "rule_id": f.rule_id,
                }
                for f in self.findings
            ],
            "recommendations": [
                {
                    "recommendation_id": r.recommendation_id,
                    "priority": r.priority,
                    "title": r.title,
                    "description": r.description,
                    "action_items": r.action_items,
                    "expected_impact": r.expected_impact,
                    "effort_estimate": r.effort_estimate,
                }
                for r in self.recommendations
            ],
            "confidence": self.confidence.to_dict(),
            "explanation": self.explanation,
            "metadata": {
                "engine_version": self.engine_version,
                "processing_time_ms": self.processing_time_ms,
                "rules_evaluated": self.rules_evaluated,
                "rules_matched": self.rules_matched,
                "ml_ready": self.ml_ready,
            },
        }


class DiagnosticMetrics:
    def __init__(self):
        self.total = 0
        self.successful = 0
        self.failed = 0
        self.inconclusive = 0
        self.scores = []
        self.counts = []

    def record(self, r: DiagnosisResult):
        self.total += 1
        if r.status == DiagnosisStatus.COMPLETED:
            self.successful += 1
        elif r.status == DiagnosisStatus.FAILED:
            self.failed += 1
        else:
            self.inconclusive += 1
        self.scores.append(r.confidence.normalized_score)
        self.counts.append(r.total_findings)

    def summary(self) -> Dict:
        return {
            "total": self.total,
            "successful": self.successful,
            "failed": self.failed,
            "inconclusive": self.inconclusive,
            "avg_confidence": sum(self.scores) / len(self.scores) if self.scores else 0,
            "avg_findings": sum(self.counts) / len(self.counts) if self.counts else 0,
        }


class DiagnosticEngine:
    """Motor de Diagnóstico Principal v2.0.0"""

    def __init__(self):
        self.taxonomy = enterprise_taxonomy
        self.registry = rules_registry
        self.metrics = DiagnosticMetrics()
        if not self.registry.rules:
            self._register_rules()
        logger.info(f"Engine v{ENGINE_VERSION} ready - {len(self.registry.rules)} rules loaded")

    def _register_rules(self):
        self.registry.register(
            DiagnosticRule(
                "SEC-001",
                "SQL Injection - Unsanitized Input",
                "Detects SQL injection",
                "SECURITY_INJECTION",
                RuleSeverity.CRITICAL,
                [
                    RuleCondition("security.sql_injection_risk", RuleOperator.EQUALS, "high"),
                    RuleCondition("security.unsanitized_inputs", RuleOperator.GREATER_THAN, 0),
                ],
                weight=1.0,
                tags=["security", "sql", "critical"],
                diagnosis_template="CRITICAL: SQL Injection vulnerability detected.",
            )
        )
        self.registry.register(
            DiagnosticRule(
                "SEC-002",
                "SQL Injection - Low Prepared Statements",
                "Low prepared statements usage",
                "SECURITY_INJECTION",
                RuleSeverity.HIGH,
                [RuleCondition("security.prepared_statements_usage", RuleOperator.LESS_THAN, 0.5)],
                weight=0.9,
                tags=["security", "sql"],
            )
        )
        self.registry.register(
            DiagnosticRule(
                "SEC-003",
                "XSS Vulnerability",
                "Cross-Site Scripting detected",
                "SECURITY_INJECTION",
                RuleSeverity.CRITICAL,
                [
                    RuleCondition("security.xss_risk", RuleOperator.EQUALS, "high"),
                    RuleCondition("security.output_escaping", RuleOperator.LESS_THAN, 0.8),
                ],
                weight=1.0,
                tags=["security", "xss"],
            )
        )
        self.registry.register(
            DiagnosticRule(
                "SEC-004",
                "Command Injection Risk",
                "Potential command injection",
                "SECURITY_INJECTION",
                RuleSeverity.CRITICAL,
                [RuleCondition("security.command_injection_risk", RuleOperator.GREATER_EQUAL, "medium")],
                weight=0.95,
                tags=["security", "injection"],
            )
        )
        self.registry.register(
            DiagnosticRule(
                "VQ-001",
                "Motion Blur",
                "Motion blur detected",
                "VISUAL_QUALITY",
                RuleSeverity.MEDIUM,
                [RuleCondition("visual.blur_score", RuleOperator.GREATER_THAN, 0.7)],
                weight=0.7,
                tags=["visual", "blur"],
            )
        )
        self.registry.register(
            DiagnosticRule(
                "VQ-002",
                "Excessive Noise",
                "Visual noise detected",
                "VISUAL_QUALITY",
                RuleSeverity.MEDIUM,
                [
                    RuleCondition("visual.noise_level", RuleOperator.GREATER_THAN, 0.6),
                    RuleCondition("visual.snr", RuleOperator.LESS_THAN, 30.0),
                ],
                logic_operator="OR",
                weight=0.7,
                tags=["visual", "noise"],
            )
        )
        self.registry.register(
            DiagnosticRule(
                "VQ-003",
                "Compression Artifacts",
                "Compression artifacts",
                "VISUAL_QUALITY",
                RuleSeverity.LOW,
                [
                    RuleCondition("visual.blockiness", RuleOperator.GREATER_THAN, 0.5),
                    RuleCondition("visual.bitrate", RuleOperator.LESS_THAN, 1000),
                ],
                weight=0.5,
                tags=["visual", "compression"],
            )
        )
        self.registry.register(
            DiagnosticRule(
                "VQ-004",
                "Color Inaccuracy",
                "Color reproduction issues",
                "VISUAL_QUALITY",
                RuleSeverity.LOW,
                [RuleCondition("visual.color_gamut", RuleOperator.LESS_THAN, 0.8)],
                weight=0.4,
                tags=["visual", "color"],
            )
        )
        self.registry.register(
            DiagnosticRule(
                "VQ-005",
                "Brightness Issues",
                "Brightness/contrast problems",
                "VISUAL_QUALITY",
                RuleSeverity.LOW,
                [RuleCondition("visual.contrast_ratio", RuleOperator.LESS_THAN, 4.5)],
                weight=0.5,
                tags=["visual", "brightness"],
            )
        )
        self.registry.register(
            DiagnosticRule(
                "AQ-001",
                "Audio Distortion",
                "Audio distortion detected",
                "AUDIO_QUALITY",
                RuleSeverity.HIGH,
                [
                    RuleCondition("audio.thd", RuleOperator.GREATER_THAN, 1.0),
                    RuleCondition("audio.clipping_score", RuleOperator.GREATER_THAN, 0.3),
                ],
                logic_operator="OR",
                weight=0.8,
                tags=["audio", "distortion"],
            )
        )
        self.registry.register(
            DiagnosticRule(
                "AQ-002",
                "Background Noise",
                "Background noise detected",
                "AUDIO_QUALITY",
                RuleSeverity.MEDIUM,
                [
                    RuleCondition("audio.noise_floor", RuleOperator.GREATER_THAN, -60.0),
                    RuleCondition("audio.snr", RuleOperator.LESS_THAN, 40.0),
                ],
                weight=0.7,
                tags=["audio", "noise"],
            )
        )
        self.registry.register(
            DiagnosticRule(
                "AQ-003",
                "Volume Issues",
                "Volume irregularities",
                "AUDIO_QUALITY",
                RuleSeverity.MEDIUM,
                [RuleCondition("audio.lufs", RuleOperator.BETWEEN, (-27.0, -14.0))],
                weight=0.6,
                tags=["audio", "volume"],
            )
        )
        self.registry.register(
            DiagnosticRule(
                "PERF-001",
                "High Response Time",
                "High API response times",
                "PERFORMANCE_LATENCY",
                RuleSeverity.HIGH,
                [
                    RuleCondition("performance.response_time_ms", RuleOperator.GREATER_THAN, 2000),
                    RuleCondition("performance.p95_response_time_ms", RuleOperator.GREATER_THAN, 5000),
                ],
                logic_operator="OR",
                weight=0.9,
                tags=["performance", "latency"],
            )
        )
        self.registry.register(
            DiagnosticRule(
                "PERF-002",
                "High Error Rate",
                "Elevated error rates",
                "PERFORMANCE_LATENCY",
                RuleSeverity.CRITICAL,
                [RuleCondition("performance.error_rate", RuleOperator.GREATER_THAN, 0.05)],
                weight=1.0,
                tags=["performance", "errors"],
            )
        )
        self.registry.register(
            DiagnosticRule(
                "ACC-001",
                "WCAG Contrast Issues",
                "Color contrast below WCAG AA",
                "ACCESSIBILITY_CONTRAST",
                RuleSeverity.HIGH,
                [
                    RuleCondition("accessibility.contrast_issues", RuleOperator.GREATER_THAN, 0),
                    RuleCondition("accessibility.wcag_level", RuleOperator.EQUALS, "A"),
                ],
                weight=0.9,
                tags=["accessibility", "wcag"],
            )
        )
        self.registry.register(
            DiagnosticRule(
                "ACC-002",
                "Missing Alt Text",
                "Images without alt text",
                "ACCESSIBILITY_CONTRAST",
                RuleSeverity.MEDIUM,
                [RuleCondition("accessibility.missing_alt_text", RuleOperator.GREATER_THAN, 0)],
                weight=0.7,
                tags=["accessibility", "alt-text"],
            )
        )

    def diagnose(self, input_data: Dict, video_id: str = None) -> DiagnosisResult:
        start = datetime.now(timezone.utc)
        did = f"DX-{hashlib.sha256(str(input_data).encode()).hexdigest()[:16]}"
        try:
            norm = self._normalize(input_data)
            rules = self.registry.get_all()
            matched, conflicts = [], []
            for rule in rules:
                m, c, e = rule.evaluate(norm)
                if m:
                    matched.append(
                        {
                            "rule_id": rule.rule_id,
                            "rule_name": rule.name,
                            "category_id": rule.category_id,
                            "severity": rule.severity.value,
                            "confidence_contribution": c,
                            "evidence": e,
                            "diagnosis_template": rule.diagnosis_template,
                        }
                    )
            eq = EvidenceQuality(
                completeness=0.9 if matched else 0.3,
                reliability=min(1.0, len(matched) / max(len(rules), 1)),
                relevance=0.8,
                consistency=1.0 if not conflicts else 0.5,
                timeliness=1.0,
            )
            conf = ConfidenceScore.calculate(matched, len(rules), eq, conflicts)
            findings = self._findings(matched, conf)
            fbs: Dict[str, int] = {}
            for f in findings:
                fbs[f.severity] = fbs.get(f.severity, 0) + 1
            fbc: Dict[str, int] = {}
            for f in findings:
                fbc[f.category_name] = fbc.get(f.category_name, 0) + 1
            recs = self._recommendations(findings)
            expl = {
                "reasoning_path": [
                    "Step 1: Input normalized",
                    f"Step 2: {len(rules)} rules evaluated",
                    f"Step 3: {len(matched)} rules matched",
                    f"Step 4: Confidence = {conf.normalized_score:.2f}",
                    f"Step 5: {len(findings)} findings generated",
                ],
                "confidence_breakdown": conf.to_dict(),
                "deterministic_mode": True,
            }
            mlf = self._ml_features(norm, matched, findings)
            elapsed = (datetime.now(timezone.utc) - start).total_seconds() * 1000
            status = DiagnosisStatus.COMPLETED if conf.normalized_score >= 0.1 else DiagnosisStatus.INCONCLUSIVE
            result = DiagnosisResult(
                diagnosis_id=did,
                status=status,
                video_id=video_id,
                taxonomy_version=TAXONOMY_VERSION,
                timestamp=start.isoformat(),
                findings=findings,
                total_findings=len(findings),
                findings_by_severity=fbs,
                findings_by_category=fbc,
                confidence=conf,
                recommendations=recs,
                explanation=expl,
                processing_time_ms=elapsed,
                rules_evaluated=len(rules),
                rules_matched=len(matched),
                ml_feature_vector=mlf,
                ml_ready=mlf is not None,
            )
            self.metrics.record(result)
            return result
        except Exception as e:
            logger.error(f"Diagnosis failed: {e}", exc_info=True)
            return DiagnosisResult(
                diagnosis_id=did,
                status=DiagnosisStatus.FAILED,
                video_id=video_id,
                taxonomy_version=TAXONOMY_VERSION,
                timestamp=datetime.now(timezone.utc).isoformat(),
                findings=[],
                total_findings=0,
                findings_by_severity={},
                findings_by_category={},
                confidence=ConfidenceScore(),
                recommendations=[],
                explanation={"error": str(e)},
            )

    def _normalize(self, data: Dict) -> Dict:
        r = {}
        for k, v in data.items():
            if isinstance(v, dict):
                r[k] = self._normalize(v)
            elif isinstance(v, str):
                try:
                    r[k] = float(v)
                except ValueError:
                    r[k] = v
            else:
                r[k] = v
        return r

    def _findings(self, matched: List[Dict], conf: ConfidenceScore) -> List[Finding]:
        so = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        fs = []
        for i, m in enumerate(matched):
            node = self.taxonomy.get_category_by_rule(m["rule_id"])
            name = node.name if node else m["category_id"]
            fs.append(
                Finding(
                    f"F-{i+1:04d}",
                    m["category_id"],
                    name,
                    m["severity"],
                    m.get("diagnosis_template") or f"Issue in {name}",
                    m.get("evidence", {}),
                    m["rule_id"],
                    m["confidence_contribution"],
                )
            )
        fs.sort(key=lambda f: (so.get(f.severity, 99), -f.confidence_contribution))
        return fs

    def _recommendations(self, findings: List[Finding]) -> List[Recommendation]:
        sp = {"critical": "immediate", "high": "short_term", "medium": "medium_term", "low": "long_term"}
        tmpl = {
            "SECURITY_INJECTION": (
                "Fix Security Vulnerabilities",
                "Address injection vulnerabilities",
                ["Implement parameterized queries", "Add input validation", "Conduct security review"],
            ),
            "VISUAL_QUALITY": (
                "Improve Visual Quality",
                "Address visual quality issues",
                ["Optimize encoding", "Apply noise reduction", "Calibrate colors"],
            ),
            "AUDIO_QUALITY": (
                "Enhance Audio Quality",
                "Resolve audio issues",
                ["Apply noise reduction", "Normalize audio", "Check equipment"],
            ),
            "PERFORMANCE_LATENCY": (
                "Optimize Performance",
                "Address performance issues",
                ["Optimize queries", "Implement caching", "Review infrastructure"],
            ),
            "ACCESSIBILITY_CONTRAST": (
                "Fix Accessibility",
                "Address WCAG compliance",
                ["Fix color contrast", "Add alt text", "Test with screen readers"],
            ),
        }
        recs, seen = [], set()
        for i, f in enumerate(findings):
            if f.category_id in seen:
                continue
            seen.add(f.category_id)
            t = tmpl.get(
                f.category_id,
                (f"Address {f.category_name}", f"Fix issue in {f.category_name}", ["Investigate", "Fix", "Verify"]),
            )
            recs.append(
                Recommendation(
                    f"REC-{i+1:04d}",
                    f.category_id,
                    sp.get(f.severity, "long_term"),
                    t[0],
                    t[1],
                    t[2],
                    f"Resolves {f.severity} issue",
                    "medium",
                )
            )
        return recs[:10]

    def _ml_features(self, data: Dict, matched: List[Dict], findings: List[Finding]) -> List[float]:
        feats = []
        for k in ["resolution", "frame_rate", "bitrate", "response_time", "error_rate"]:
            try:
                feats.append(float(data.get(k, 0)))
            except (TypeError, ValueError):
                feats.append(0.0)
        feats.extend([float(len(matched)), float(len(findings))])
        sev = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        for f in findings:
            sev[f.severity] = sev.get(f.severity, 0) + 1
        feats.extend(sev.values())
        while len(feats) < 20:
            feats.append(0.0)
        return feats[:20]


diagnostic_engine = DiagnosticEngine()
