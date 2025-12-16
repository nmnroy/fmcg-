import os
import time
import hashlib
import json
from typing import Optional
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Try to import key manager
try:
    from utils.api_key_manager import APIKeyManager
    MULTIPLE_KEYS_AVAILABLE = True
except:
    MULTIPLE_KEYS_AVAILABLE = False

CACHE_FILE = Path("data/llm_cache.json")
CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)


class GeminiLLM:
    def __init__(self, model_name: str = "gemini-2.5-flash", use_multiple_keys: bool = True):
        """Initialize Gemini LLM with multiple API key support"""
        
        self.model_name = model_name
        self.use_multiple_keys = use_multiple_keys and MULTIPLE_KEYS_AVAILABLE
        
        # Load Cache
        self.cache = {}
        if CACHE_FILE.exists():
            try:
                self.cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
            except: 
                self.cache = {}

        if self.use_multiple_keys:
            try:
                self.key_manager = APIKeyManager()
                print(f"✅ Using {len(self.key_manager.api_keys)} API keys")
            except Exception as e:
                print(f"⚠️ Failed to load multiple keys: {e}")
                self.use_multiple_keys = False
        
        if not self.use_multiple_keys:
            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY_1")
            if not api_key:
                raise ValueError("No API key found")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_name)

    def _get_cache_key(self, prompt: str) -> str:
        return hashlib.md5((self.model_name + prompt).encode()).hexdigest()

    def _save_cache(self):
        try:
            CACHE_FILE.write_text(json.dumps(self.cache, indent=2), encoding="utf-8")
        except: pass
    
    def generate(self, prompt: str, system_instruction: str = None, **kwargs) -> str:
        """Generate response with automatic key rotation and caching"""
        # Prepend system instruction
        final_prompt = prompt
        if system_instruction:
            final_prompt = f"{system_instruction}\n\n{prompt}"
            
        # Check Cache
        cache_key = self._get_cache_key(final_prompt)
        if cache_key in self.cache:
            print("⚡ [CACHE HIT] Returning cached response.")
            return self.cache[cache_key]

        response = ""
        if self.use_multiple_keys:
            response = self._generate_with_rotation(final_prompt, **kwargs)
        else:
            response = self._generate_single(final_prompt, **kwargs)
            
        # Save to Cache
        if response:
            self.cache[cache_key] = response
            self._save_cache()
            
        return response
            
    def generate_content(self, prompt: str, system_instruction: str = None, **kwargs) -> str:
        """Alias for generate to support agent calls"""
        return self.generate(prompt, system_instruction=system_instruction, **kwargs)
    
    def _generate_with_rotation(self, prompt: str, max_retries: int = None, **kwargs) -> str:
        """Generate with multiple keys and retry"""
        
        # Default retries to 2x number of keys or at least 10
        if max_retries is None:
            max_retries = max(len(self.key_manager.api_keys) * 3, 12)
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Get next API key
                api_key = self.key_manager.get_next_key()
                
                # Configure with this key
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(self.model_name)
                
                # Generate
                response = model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": kwargs.get("temperature", 0.7),
                        "max_output_tokens": kwargs.get("max_tokens", 4096),
                    }
                )
                
                return response.text
                
            except Exception as e:
                last_error = str(e)
                self.key_manager.mark_error(api_key)
                
                # Check for rate limits
                is_quota_error = "quota" in last_error.lower() or "rate" in last_error.lower() or "429" in last_error
                
                if attempt < max_retries - 1:
                    if is_quota_error:
                        wait_time = 1 # WAS 20. Reduced for Multi-Key Speed
                        # DEBUG: Print exact error for diagnosis
                        print(f"⚠️ Quota hit! Exact Error: {last_error}")
                        print(f"⚠️ Key ...{api_key[-4:]}. Rotating in {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"⚠️ Error: {last_error[:50]}... Retrying...")
                        time.sleep(2)
                        continue
                
        raise Exception(f"Failed after {max_retries} attempts. Last error: {last_error}")
    
    def _generate_single(self, prompt: str, **kwargs) -> str:
        """Generate with single key"""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": kwargs.get("temperature", 0.7),
                    "max_output_tokens": kwargs.get("max_tokens", 4096),
                }
            )
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def get_stats(self):
        """Get API key usage statistics"""
        if self.use_multiple_keys:
            return self.key_manager.get_stats()
        return {}
    
    async def generate_async(self, prompt: str, system_instruction: str = None, **kwargs) -> str:
        """Async version of generate"""
        import asyncio
        
        # Prepend system instruction
        final_prompt = prompt
        if system_instruction:
            final_prompt = f"{system_instruction}\n\n{prompt}"
            
        # Check Cache
        cache_key = self._get_cache_key(final_prompt)
        if cache_key in self.cache:
            print("⚡ [CACHE HIT] Returning cached response.")
            return self.cache[cache_key]

        response = ""
        if self.use_multiple_keys:
            response = await self._generate_with_rotation_async(final_prompt, **kwargs)
        else:
            # Wrap synchronous single-key generation in thread
            response = await asyncio.to_thread(self._generate_single, final_prompt, **kwargs)
            
        # Save to Cache
        if response:
            self.cache[cache_key] = response
            self._save_cache()
            
        return response

    async def generate_content_async(self, prompt: str, system_instruction: str = None, **kwargs) -> str:
        return await self.generate_async(prompt, system_instruction, **kwargs)

    async def _generate_with_rotation_async(self, prompt: str, max_retries: int = None, **kwargs) -> str:
        """Async generation with multiple keys and retry"""
        import asyncio
        
        # Default retries to 2x number of keys or at least 10
        if max_retries is None:
            max_retries = max(len(self.key_manager.api_keys) * 3, 12)
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Get next API key
                api_key = self.key_manager.get_next_key()
                
                # Configure with this key
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(self.model_name)
                
                # Generate in thread to avoid blocking loop
                response = await asyncio.to_thread(
                    model.generate_content,
                    prompt,
                    generation_config={
                        "temperature": kwargs.get("temperature", 0.7),
                        "max_output_tokens": kwargs.get("max_tokens", 4096),
                    }
                )
                
                return response.text
                
            except Exception as e:
                last_error = str(e)
                self.key_manager.mark_error(api_key)
                
                # Check for rate limits
                is_quota_error = "quota" in last_error.lower() or "rate" in last_error.lower() or "429" in last_error
                
                if attempt < max_retries - 1:
                    if is_quota_error:
                        wait_time = 1 
                        print(f"⚠️ Quota hit! Exact Error: {last_error}")
                        print(f"⚠️ Key ...{api_key[-4:]}. Rotating in {wait_time}s...")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        print(f"⚠️ Error: {last_error[:50]}... Retrying...")
                        await asyncio.sleep(2)
                        continue
                
        raise Exception(f"Failed after {max_retries} attempts. Last error: {last_error}")

    def __call__(self, prompt: str, **kwargs) -> str:
        return self.generate(prompt, **kwargs)