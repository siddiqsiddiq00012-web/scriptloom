import logging
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Dict, Any

logger = logging.getLogger("scriptloom.worker")

# Define Task Queue Retry Limits
RETRY_POLICIES = {
    "FFmpegQueue": 2,
    "STTQueue": 3,
    "EmbeddingQueue": 3,
    "VoiceDNAQueue": 1,
}


class CategorizedTaskPool:
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.active_tasks = 0

    def submit_task(
        self,
        queue_category: str,
        func: Callable[..., Any],
        *args,
        **kwargs,
    ):
        retry_limit = RETRY_POLICIES.get(queue_category, 1)

        def _wrapper():
            self.active_tasks += 1
            attempts = 0
            success = False
            last_err = None

            while attempts <= retry_limit and not success:
                attempts += 1
                try:
                    start_t = time.time()
                    func(*args, **kwargs)
                    elapsed = time.time() - start_t
                    logger.info(f"[{queue_category}] Task succeeded on attempt {attempts}/{retry_limit + 1} in {elapsed:.2f}s")
                    success = True
                except Exception as exc:
                    last_err = exc
                    logger.warning(f"[{queue_category}] Task attempt {attempts} failed: {exc}")
                    time.sleep(0.5)

            self.active_tasks -= 1
            if not success:
                logger.error(f"[{queue_category}] Task permanently failed after {retry_limit + 1} attempts: {last_err}")

        self.executor.submit(_wrapper)


# Global Task Pool Instance
async_worker_pool = CategorizedTaskPool(max_workers=4)
