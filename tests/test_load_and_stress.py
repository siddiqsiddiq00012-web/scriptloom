import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from backend.main import app
from backend.services.cache_service import cache_service

client = TestClient(app)


def test_concurrency_load_and_stress():
    print("\n--- 1. Testing Sub-5ms Cache Lookup Benchmark ---")
    cache_service.set("benchmark:key", "value_123", ttl_seconds=300)

    start_t = time.time()
    for _ in range(1000):
        val = cache_service.get("benchmark:key")
        assert val == "value_123"
    total_time = time.time() - start_t
    avg_per_op = (total_time / 1000.0) * 1000.0  # ms
    print(f"1,000 Cache lookups completed in {total_time:.4f}s ({avg_per_op:.4f} ms per op)")

    assert avg_per_op < 5.0, "Cache lookup speed must be sub-5ms"

    print("\n--- 2. Testing 50 Concurrent HTTP Requests ---")
    def _make_req(idx):
        res = client.get("/api/v1/health")
        return res.status_code

    start_http = time.time()
    with ThreadPoolExecutor(max_workers=10) as pool:
        results = list(pool.map(_make_req, range(50)))

    elapsed_http = time.time() - start_http
    success_count = sum(1 for status_code in results if status_code in (200, 429))
    print(f"50 Concurrent HTTP requests completed in {elapsed_http:.3f}s. Handled cleanly: {success_count}/50")

    assert success_count == 50

    print("\n[SUCCESS] Concurrency Load & Stress Benchmarks PASSED!")


if __name__ == "__main__":
    test_concurrency_load_and_stress()
