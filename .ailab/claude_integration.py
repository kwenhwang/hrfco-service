import os
import json
import time
import re
import asyncio
import httpx
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ClaudeConfig:
    model: str = "claude-3-5-sonnet-20241022"
    api_key: str = ""
    timeout: int = 60
    rate_limit_delay: float = 1.0
    auto_consult: bool = True
    max_tokens: int = 4000
    temperature: float = 0.7
    
    def __post_init__(self):
        if not self.api_key:
            self.api_key = os.getenv("ANTHROPIC_API_KEY", "")

class ClaudeIntegration:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.config = self._load_config()
        self.last_call_time = 0
        self.session_stats = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "last_consult_time": None
        }
        self._initialized = True
    
    def _load_config(self) -> ClaudeConfig:
        """Load configuration from claude-config.json"""
        config_path = Path("claude-config.json")
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                return ClaudeConfig(**config_data)
            except (json.JSONDecodeError, TypeError) as e:
                print(f"Warning: Failed to load Claude config: {e}. Using defaults.")
        
        # Create default config file
        default_config = ClaudeConfig()
        self._save_config(default_config)
        return default_config
    
    def _save_config(self, config: ClaudeConfig):
        """Save configuration to claude-config.json"""
        config_data = {
            "model": config.model,
            "api_key": config.api_key,
            "timeout": config.timeout,
            "rate_limit_delay": config.rate_limit_delay,
            "auto_consult": config.auto_consult,
            "max_tokens": config.max_tokens,
            "temperature": config.temperature
        }
        
        with open("claude-config.json", 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
    
    async def _enforce_rate_limit(self):
        """Enforce rate limiting between calls"""
        current_time = time.time()
        time_since_last_call = current_time - self.last_call_time
        
        if time_since_last_call < self.config.rate_limit_delay:
            sleep_time = self.config.rate_limit_delay - time_since_last_call
            await asyncio.sleep(sleep_time)
        
        self.last_call_time = time.time()
    
    def detect_uncertainty_patterns(self, text: str) -> bool:
        """Detect uncertainty patterns in Gemini's responses"""
        if not self.config.auto_consult:
            return False
        
        uncertainty_patterns = [
            r"I'm\s*not\s*sure",
            r"I\s*don't\s*know",
            r"unclear",
            r"uncertain",
            r"might\s*be",
            r"possibly",
            r"perhaps",
            r"it\s*depends",
            r"could\s*be",
            r"may\s*be",
            r"not\s*certain",
            r"I\s*think",
            r"probably"
        ]
        
        for pattern in uncertainty_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    async def call_claude(self, prompt: str, context: str = "") -> Dict[str, Any]:
        """Call Claude API with rate limiting and error handling"""
        if not self.config.api_key:
            return {
                "success": False,
                "error": "Claude API key not set. Please set ANTHROPIC_API_KEY environment variable.",
                "model": self.config.model,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        
        await self._enforce_rate_limit()
        self.session_stats["total_calls"] += 1
        
        try:
            # Prepare the message
            if context:
                full_prompt = f"Context: {context}\n\nPrompt: {prompt}"
            else:
                full_prompt = prompt
            
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.config.api_key,
                "anthropic-version": "2023-06-01"
            }
            
            data = {
                "model": self.config.model,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "messages": [
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ]
            }
            
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=data
                )
                
                if response.status_code != 200:
                    error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"error": response.text}
                    raise RuntimeError(f"Claude API error ({response.status_code}): {error_data}")
                
                result = response.json()
                response_text = result["content"][0]["text"]
                
                self.session_stats["successful_calls"] += 1
                self.session_stats["last_consult_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
                
                return {
                    "success": True,
                    "response": response_text,
                    "model": self.config.model,
                    "timestamp": self.session_stats["last_consult_time"],
                    "usage": result.get("usage", {})
                }
                
        except Exception as e:
            self.session_stats["failed_calls"] += 1
            return {
                "success": False,
                "error": str(e),
                "model": self.config.model,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status and statistics"""
        return {
            "model": self.config.model,
            "auto_consult": self.config.auto_consult,
            "rate_limit_delay": self.config.rate_limit_delay,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "api_key_set": bool(self.config.api_key),
            "session_stats": self.session_stats.copy(),
            "config_file": "claude-config.json"
        }
    
    def update_config(self, **kwargs):
        """Update configuration parameters"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        self._save_config(self.config)

# Global instance
claude = ClaudeIntegration() 