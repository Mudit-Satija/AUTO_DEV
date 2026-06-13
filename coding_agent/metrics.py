"""Metrics Collection — instrumentation for generation pipeline observability."""

import time
import json
import threading
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path


@dataclass
class BundleMetrics:
    bundle_name: str
    bundle_type: str
    files_included: List[str]
    file_count: int
    prompt_length: int
    estimated_tokens: int
    model_used: str
    generation_start_time: float
    generation_end_time: float
    generation_duration_ms: int
    validation_result: bool
    validation_errors: List[str]
    status: str  # "Success", "Failed", "Timeout"
    exception: Optional[str] = None
    likely_cause: Optional[str] = None


@dataclass
class GlobalMetrics:
    total_files_planned: int
    total_files_generated: int
    total_bundles: int
    total_prompt_characters: int
    total_estimated_tokens: int
    total_generation_time_ms: int
    validation_time_ms: int
    zip_creation_time_ms: int
    overall_status: str
    bundle_metrics: List[BundleMetrics] = field(default_factory=list)
    pipeline_start_time: float = field(default_factory=time.perf_counter)
    pipeline_end_time: float = 0.0


class MetricsCollector:
    def __init__(self):
        self.global_metrics = GlobalMetrics(
            total_files_planned=0,
            total_files_generated=0,
            total_bundles=0,
            total_prompt_characters=0,
            total_estimated_tokens=0,
            total_generation_time_ms=0,
            validation_time_ms=0,
            zip_creation_time_ms=0,
            overall_status="InProgress",
        )
        self._thread_local = threading.local()
        self._lock = threading.Lock()

    def start_pipeline(self, total_files_planned: int):
        self.global_metrics.total_files_planned = total_files_planned
        self.global_metrics.pipeline_start_time = time.perf_counter()

    def end_pipeline(self, overall_status: str):
        self.global_metrics.pipeline_end_time = time.perf_counter()
        self.global_metrics.overall_status = overall_status

    def _get_current_bundle(self) -> Optional[BundleMetrics]:
        return getattr(self._thread_local, 'current_bundle', None)

    def _set_current_bundle(self, bundle: Optional[BundleMetrics]):
        self._thread_local.current_bundle = bundle

    def start_bundle(self, bundle_name: str, bundle_type: str, file_blueprints: List[Dict], model_used: str):
        bundle = BundleMetrics(
            bundle_name=bundle_name,
            bundle_type=bundle_type,
            files_included=[bp.get("path", "unknown") for bp in file_blueprints],
            file_count=len(file_blueprints),
            prompt_length=0,
            estimated_tokens=0,
            model_used=model_used,
            generation_start_time=time.perf_counter(),
            generation_end_time=0.0,
            generation_duration_ms=0,
            validation_result=False,
            validation_errors=[],
            status="InProgress",
        )
        self._set_current_bundle(bundle)

    def record_prompt(self, prompt: str):
        bundle = self._get_current_bundle()
        if bundle:
            bundle.prompt_length = len(prompt)
            bundle.estimated_tokens = len(prompt) // 4
            with self._lock:
                self.global_metrics.total_prompt_characters += len(prompt)
                self.global_metrics.total_estimated_tokens += bundle.estimated_tokens

    def end_bundle(self, validation_result: bool, validation_errors: List[str], exception: Optional[str] = None):
        bundle = self._get_current_bundle()
        if not bundle:
            return

        bundle.generation_end_time = time.perf_counter()
        bundle.generation_duration_ms = int(
            (bundle.generation_end_time - bundle.generation_start_time) * 1000
        )
        bundle.validation_result = validation_result
        bundle.validation_errors = validation_errors
        bundle.exception = exception

        if exception:
            bundle.status = "Failed"
            bundle.likely_cause = self._infer_cause(exception, validation_errors)
        elif not validation_result:
            bundle.status = "Failed"
            bundle.likely_cause = self._infer_cause(None, validation_errors)
        elif bundle.generation_duration_ms > 250000:
            bundle.status = "Timeout"
            bundle.likely_cause = "NVIDIA API 300s timeout exceeded"
        else:
            bundle.status = "Success"

        with self._lock:
            self.global_metrics.total_bundles += 1
            self.global_metrics.total_files_generated += bundle.file_count
            self.global_metrics.total_generation_time_ms += bundle.generation_duration_ms
            self.global_metrics.bundle_metrics.append(bundle)
        self._set_current_bundle(None)

    def record_validation_time(self, duration_ms: int):
        with self._lock:
            self.global_metrics.validation_time_ms += duration_ms

    def record_zip_time(self, duration_ms: int):
        with self._lock:
            self.global_metrics.zip_creation_time_ms += duration_ms

    def _infer_cause(self, exception: Optional[str], validation_errors: List[str]) -> str:
        if exception:
            exc_str = str(exception).lower()
            if "timeout" in exc_str or "timed out" in exc_str:
                return "Timeout"
            if "import" in exc_str or "module" in exc_str:
                return "Missing Imports"
            if "validation" in exc_str:
                return "Validation Failure"
            if "parse" in exc_str or "json" in exc_str:
                return "Parsing Failure"
            return "Exception"
        if validation_errors:
            for err in validation_errors:
                err_lower = err.lower()
                if "import" in err_lower or "module" in err_lower:
                    return "Missing Imports"
                if "syntax" in err_lower:
                    return "Syntax Error"
                if "validation" in err_lower or "missing" in err_lower:
                    return "Validation Failure"
        return "Unknown"

    def get_summary(self) -> Dict[str, Any]:
        return {
            "pipeline_metrics": asdict(self.global_metrics),
            "bottleneck_analysis": self._analyze_bottlenecks(),
            "timeout_risk_analysis": self._analyze_timeout_risk(),
            "recommendations": self._generate_recommendations(),
        }

    def _analyze_bottlenecks(self) -> Dict[str, Any]:
        if not self.global_metrics.bundle_metrics:
            return {"status": "No bundle metrics available"}

        sorted_bundles = sorted(
            self.global_metrics.bundle_metrics,
            key=lambda b: b.generation_duration_ms,
            reverse=True
        )

        slowest = sorted_bundles[0] if sorted_bundles else None
        fastest = sorted_bundles[-1] if sorted_bundles else None

        return {
            "slowest_bundle": {
                "name": slowest.bundle_name if slowest else None,
                "duration_ms": slowest.generation_duration_ms if slowest else 0,
                "file_count": slowest.file_count if slowest else 0,
                "prompt_length": slowest.prompt_length if slowest else 0,
            } if slowest else None,
            "fastest_bundle": {
                "name": fastest.bundle_name if fastest else None,
                "duration_ms": fastest.generation_duration_ms if fastest else 0,
                "file_count": fastest.file_count if fastest else 0,
                "prompt_length": fastest.prompt_length if fastest else 0,
            } if fastest else None,
            "avg_duration_ms": sum(b.generation_duration_ms for b in self.global_metrics.bundle_metrics) / len(self.global_metrics.bundle_metrics) if self.global_metrics.bundle_metrics else 0,
            "total_bundles": len(self.global_metrics.bundle_metrics),
        }

    def _analyze_timeout_risk(self) -> Dict[str, Any]:
        if not self.global_metrics.bundle_metrics:
            return {"status": "No bundle metrics available"}

        high_risk = [b for b in self.global_metrics.bundle_metrics if b.generation_duration_ms > 200000]
        medium_risk = [b for b in self.global_metrics.bundle_metrics if 100000 < b.generation_duration_ms <= 200000]
        low_risk = [b for b in self.global_metrics.bundle_metrics if b.generation_duration_ms <= 100000]

        return {
            "high_risk_bundles": [{"name": b.bundle_name, "duration_ms": b.generation_duration_ms, "prompt_chars": b.prompt_length} for b in high_risk],
            "medium_risk_bundles": [{"name": b.bundle_name, "duration_ms": b.generation_duration_ms, "prompt_chars": b.prompt_length} for b in medium_risk],
            "low_risk_bundles": [{"name": b.bundle_name, "duration_ms": b.generation_duration_ms, "prompt_chars": b.prompt_length} for b in low_risk],
            "nvidia_timeout_limit_ms": 300000,
            "recommendation": "Consider reducing bundle size for high-risk bundles" if high_risk else "All bundles within safe timeout margin",
        }

    def _generate_recommendations(self) -> List[str]:
        recs = []

        if not self.global_metrics.bundle_metrics:
            return ["No metrics available for recommendations"]

        high_risk = [b for b in self.global_metrics.bundle_metrics if b.generation_duration_ms > 200000]
        if high_risk:
            recs.append(f"Reduce bundle size for {len(high_risk)} high-risk bundles (duration > 200s)")

        failed = [b for b in self.global_metrics.bundle_metrics if b.status == "Failed"]
        if failed:
            recs.append(f"Investigate {len(failed)} failed bundles: {', '.join(b.bundle_name for b in failed)}")

        timeouts = [b for b in self.global_metrics.bundle_metrics if b.status == "Timeout"]
        if timeouts:
            recs.append(f"Reduce bundle size for {len(timeouts)} timed-out bundles")

        large_prompts = [b for b in self.global_metrics.bundle_metrics if b.prompt_length > 50000]
        if large_prompts:
            recs.append(f"Reduce prompt size for {len(large_prompts)} bundles with >50k char prompts")

        if not recs:
            recs.append("All metrics within normal ranges")

        return recs

    def save_to_file(self, output_path: str):
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(self.get_summary(), f, indent=2, default=str)


_global_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    global _global_collector
    if _global_collector is None:
        _global_collector = MetricsCollector()
    return _global_collector


def reset_metrics_collector():
    global _global_collector
    _global_collector = MetricsCollector()