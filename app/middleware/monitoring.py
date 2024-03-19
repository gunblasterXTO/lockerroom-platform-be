from prometheus_client import Counter, Histogram


class MonitoringMiddleware:
    def __init__(self) -> None:
        self._counter = Counter(
            name="http_requests_total",
            documentation="Total HTTP requests",
            labelnames=["method", "endpoint", "status_code"],
        )
        self._histogram = Histogram(
            name="http_request_latency_seconds",
            documentation="HTTP request latency in seconds",
            labelnames=["method", "endpoint"],
        )

    def record_count(
        self, endpoint: str, method: str, status_code: int
    ) -> None:
        self._counter.labels(method, endpoint, status_code).inc()

    def record_histo(
        self, method: str, endpoint: str, duration: float
    ) -> None:
        self._histogram.labels(method, endpoint).observe(duration)
