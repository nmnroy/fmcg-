"""
Unit tests for CacheManager
"""
import unittest
import time
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rfp-automation")))

from utils.cache_manager import CacheManager


class TestCacheManager(unittest.TestCase):
    def setUp(self):
        self.cache = CacheManager(cache_file="data/test_llm_cache.json", default_ttl=2)
        self.cache.clear()

    def test_cache_set_and_get(self):
        key = self.cache.generate_key("test", "query_text")
        self.cache.set(key, {"answer": 42})
        val = self.cache.get(key)
        self.assertEqual(val, {"answer": 42})

    def test_cache_expiry(self):
        key = self.cache.generate_key("test", "expire_soon")
        self.cache.set(key, "data", ttl=1)
        self.assertEqual(self.cache.get(key), "data")
        time.sleep(1.1)
        self.assertIsNone(self.cache.get(key))


if __name__ == "__main__":
    unittest.main()
