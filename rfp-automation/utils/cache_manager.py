"""
Thread-Safe Prompt & Response Cache Manager for LLM Invocations
Reduces redundant API calls, prevents quota exhaustion, and accelerates response times.
"""

import os
import time
import json
import hashlib
import logging
from typing import Any, Optional, Dict
from threading import Lock

logger = logging.getLogger(__name__)


class CacheManager:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(CacheManager, cls).__new__(cls)
                cls._instance._init_cache(*args, **kwargs)
            return cls._instance

    def _init_cache(self, cache_file: str = "data/llm_cache.json", default_ttl: int = 86400):
        self.cache_file = cache_file
        self.default_ttl = default_ttl
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.hits = 0
        self.misses = 0
        self._load_disk_cache()

    def _load_disk_cache(self):
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    now = time.time()
                    # Filter out expired items
                    self.memory_cache = {
                        k: v for k, v in data.items()
                        if v.get("expires_at", float("inf")) > now
                    }
        except Exception as e:
            logger.warning(f"Could not load cache from {self.cache_file}: {e}")
            self.memory_cache = {}

    def _save_disk_cache(self):
        try:
            os.makedirs(os.path.dirname(self.cache_file) or ".", exist_ok=True)
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.memory_cache, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not persist cache to {self.cache_file}: {e}")

    @staticmethod
    def generate_key(prefix: str, content: str, **kwargs) -> str:
        payload = f"{prefix}:{content}:{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self.memory_cache.get(key)
            if entry:
                if entry.get("expires_at", float("inf")) > time.time():
                    self.hits += 1
                    return entry.get("value")
                else:
                    # Expired
                    del self.memory_cache[key]
            self.misses += 1
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        with self._lock:
            ttl_seconds = ttl if ttl is not None else self.default_ttl
            expires_at = time.time() + ttl_seconds if ttl_seconds > 0 else float("inf")
            self.memory_cache[key] = {
                "value": value,
                "created_at": time.time(),
                "expires_at": expires_at
            }
            # Periodically or on set, save
            if len(self.memory_cache) % 10 == 0:
                self._save_disk_cache()

    def stats(self) -> Dict[str, Any]:
        with self._lock:
            total = self.hits + self.misses
            ratio = (self.hits / total * 100) if total > 0 else 0.0
            return {
                "entries": len(self.memory_cache),
                "hits": self.hits,
                "misses": self.misses,
                "hit_ratio_pct": round(ratio, 2)
            }

    def clear(self):
        with self._lock:
            self.memory_cache.clear()
            self._save_disk_cache()
