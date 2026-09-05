"""Performance, error metrics, and operational telemetry collector."""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from threading import Lock


@dataclass
class EndpointStats:
    """Statistics for an API route."""
    total_requests: int = 0
    total_errors: int = 0
    total_duration_ms: float = 0.0
    min_duration_ms: float = float("inf")
    max_duration_ms: float = 0.0
    status_codes: dict[int, int] = field(default_factory=lambda: defaultdict(int))

    def record(self, status_code: int, duration_ms: float):
        self.total_requests += 1
        self.status_codes[status_code] += 1
        if status_code >= 400:
            self.total_errors += 1
        self.total_duration_ms += duration_ms
        self.min_duration_ms = min(self.min_duration_ms, duration_ms)
        self.max_duration_ms = max(self.max_duration_ms, duration_ms)

    @property
    def avg_duration_ms(self) -> float:
        return round(self.total_duration_ms / self.total_requests, 2) if self.total_requests > 0 else 0.0


class MetricsCollector:
    """Thread-safe application metrics and performance telemetry collector."""

    def __init__(self):
        self._lock = Lock()
        self._start_time = time.time()
        self._endpoint_stats: dict[str, EndpointStats] = defaultdict(EndpointStats)
        self._total_documents_processed: int = 0
        self._total_tax_calculations: int = 0
        self._error_counts: dict[str, int] = defaultdict(int)

    def record_request(self, method: str, path: str, status_code: int, duration_ms: float):
        """Record an incoming HTTP request execution."""
        key = f"{method} {path}"
        with self._lock:
            self._endpoint_stats[key].record(status_code, duration_ms)

    def increment_document_processed(self):
        """Increment count of Form 16 documents parsed and processed."""
        with self._lock:
            self._total_documents_processed += 1

    def increment_tax_calculation(self):
        """Increment count of deterministic tax calculations performed."""
        with self._lock:
            self._total_tax_calculations += 1

    def record_error(self, error_code: str):
        """Record a domain or system error code occurrence."""
        with self._lock:
            self._error_counts[error_code] += 1

    def get_metrics_summary(self) -> dict:
        """Return structured metrics dictionary snapshot."""
        with self._lock:
            uptime_seconds = round(time.time() - self._start_time, 2)
            total_requests = sum(stat.total_requests for stat in self._endpoint_stats.values())
            total_errors = sum(stat.total_errors for stat in self._endpoint_stats.values())

            endpoints_data = {
                route: {
                    "requests": stat.total_requests,
                    "errors": stat.total_errors,
                    "avg_latency_ms": stat.avg_duration_ms,
                    "min_latency_ms": round(stat.min_duration_ms, 2) if stat.min_duration_ms != float("inf") else 0.0,
                    "max_latency_ms": round(stat.max_duration_ms, 2),
                    "status_breakdown": dict(stat.status_codes),
                }
                for route, stat in self._endpoint_stats.items()
            }

            return {
                "uptime_seconds": uptime_seconds,
                "total_requests": total_requests,
                "total_errors": total_errors,
                "documents_processed": self._total_documents_processed,
                "tax_calculations_performed": self._total_tax_calculations,
                "error_breakdown": dict(self._error_counts),
                "endpoints": endpoints_data,
            }

    def reset(self):
        """Reset all metric counters (useful for testing)."""
        with self._lock:
            self._start_time = time.time()
            self._endpoint_stats.clear()
            self._total_documents_processed = 0
            self._total_tax_calculations = 0
            self._error_counts.clear()


# Global Singleton Metrics Collector
metrics_collector = MetricsCollector()
