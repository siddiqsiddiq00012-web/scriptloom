import time
from typing import Dict, List


class PerformanceMonitor:
    def __init__(self):
        # subsystem_name -> list of durations (seconds)
        self.metrics: Dict[str, List[float]] = {
            "api_latency": [],
            "upload_duration": [],
            "ffprobe_duration": [],
            "ffmpeg_duration": [],
            "stt_duration": [],
            "embedding_duration": [],
        }

    def record_duration(self, subsystem: str, duration_seconds: float):
        if subsystem not in self.metrics:
            self.metrics[subsystem] = []
        self.metrics[subsystem].append(duration_seconds)
        # Keep last 1000 measurements
        if len(self.metrics[subsystem]) > 1000:
            self.metrics[subsystem].pop(0)

    def get_summary(self) -> Dict[str, dict]:
        summary = {}
        for subsystem, values in self.metrics.items():
            if values:
                summary[subsystem] = {
                    "count": len(values),
                    "avg_ms": round((sum(values) / len(values)) * 1000, 2),
                    "min_ms": round(min(values) * 1000, 2),
                    "max_ms": round(max(values) * 1000, 2),
                }
            else:
                summary[subsystem] = {"count": 0, "avg_ms": 0.0, "min_ms": 0.0, "max_ms": 0.0}
        return summary


# Global Performance Monitor Instance
performance_monitor = PerformanceMonitor()
