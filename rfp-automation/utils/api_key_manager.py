import os
import random
import time
from typing import List
from collections import deque
from dotenv import load_dotenv

load_dotenv()

class APIKeyManager:
    def __init__(self):
        """Initialize with multiple API keys"""
        self.api_keys = []
        
        # Load individual keys
        for i in range(1, 10):
            key = os.getenv(f"GOOGLE_API_KEY_{i}")
            if key:
                self.api_keys.append(key)
        
        # Fallback to comma-separated
        if not self.api_keys:
            keys_str = os.getenv("GOOGLE_API_KEYS", "")
            if keys_str:
                self.api_keys = [k.strip() for k in keys_str.split(",") if k.strip()]
        
        # Fallback to single key
        if not self.api_keys:
            key = os.getenv("GOOGLE_API_KEY")
            if key:
                self.api_keys = [key]
        
        if not self.api_keys:
            raise ValueError("No API keys found in environment variables")
        
        # Round-robin queue
        self.key_queue = deque(self.api_keys)
        
        # Track usage
        self.key_stats = {key: {"calls": 0, "errors": 0} for key in self.api_keys}
        
        print(f"✅ Loaded {len(self.api_keys)} API key(s)")
    
    def get_next_key(self):
        """Get next API key using round-robin"""
        key = self.key_queue[0]
        self.key_queue.rotate(-1)
        self.key_stats[key]["calls"] += 1
        return key
    
    def mark_error(self, key):
        """Mark an error for a key"""
        if key in self.key_stats:
            self.key_stats[key]["errors"] += 1
    
    def get_stats(self):
        """Get usage statistics"""
        return self.key_stats