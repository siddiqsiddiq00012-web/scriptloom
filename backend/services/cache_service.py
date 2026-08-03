import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from backend.core.config import settings


class BaseCacheProvider(ABC):
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        pass

    @abstractmethod
    def clear_namespace(self, prefix: str) -> None:
        pass

    @abstractmethod
    def increment(self, key: str, amount: int = 1) -> int:
        pass

    @abstractmethod
    def decrement(self, key: str, amount: int = 1) -> int:
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, int]:
        pass


class MemoryCacheProvider(BaseCacheProvider):
    def __init__(self):
        # key -> (value, expire_timestamp)
        self._store: Dict[str, tuple] = {}
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[Any]:
        now = time.time()
        if key in self._store:
            val, expire = self._store[key]
            if expire == 0 or now < expire:
                self.hits += 1
                return val
            else:
                del self._store[key]
        self.misses += 1
        return None

    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        expire = time.time() + ttl_seconds if ttl_seconds > 0 else 0
        self._store[key] = (value, expire)

    def delete(self, key: str) -> None:
        if key in self._store:
            del self._store[key]

    def exists(self, key: str) -> bool:
        return self.get(key) is not None

    def clear_namespace(self, prefix: str) -> None:
        keys_to_del = [k for k in self._store.keys() if k.startswith(prefix)]
        for k in keys_to_del:
            del self._store[k]

    def increment(self, key: str, amount: int = 1) -> int:
        curr = self.get(key) or 0
        new_val = int(curr) + amount
        self.set(key, new_val, ttl_seconds=0)
        return new_val

    def decrement(self, key: str, amount: int = 1) -> int:
        return self.increment(key, amount=-amount)

    def get_stats(self) -> Dict[str, int]:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "total_keys": len(self._store),
        }


# Global Cache Instance
cache_service = MemoryCacheProvider()


class CacheInvalidator:
    @staticmethod
    def invalidate_voice_dna(user_id: int):
        cache_service.delete(f"voice_dna:{user_id}")

    @staticmethod
    def invalidate_creator_memory(user_id: int):
        cache_service.clear_namespace(f"creator_memory:{user_id}")

    @staticmethod
    def invalidate_subscription(user_id: int):
        cache_service.delete(f"subscription:{user_id}")
        cache_service.delete(f"usage:{user_id}")
