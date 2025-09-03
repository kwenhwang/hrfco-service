import subprocess
import json
import time
import re
import asyncio
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from pathlib import Path

@dataclass
class GeminiConfig:
    model: str = "gemini-2.5-flash"
    timeout: int = 60
    rate_limit_delay: float = 2.0
    auto_consult: bool = True
    uncertainty_thresholds: Dict[str, bool] = None
    
    def __post_init__(self):
        if self.uncertainty_thresholds is None:
            self.uncertainty_thresholds = {
                "not_sure": True,
                "uncertain": True,
                "might_be": True,
                "possibly": True,
                "unclear": True
            }

class GeminiIntegration:
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
        self.call_count = 0
        self.session_stats = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "last_consult_time": None
        }
        self._initialized = True
    
    def _load_config(self) -> GeminiConfig:
        """Load configuration from gemini-config.json"""
        config_path = Path("gemini-config.json")
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                return GeminiConfig(**config_data)
            except (json.JSONDecodeError, TypeError) as e:
                print(f"Warning: Failed to load config: {e}. Using defaults.")
        
        # Create default config file
        default_config = GeminiConfig()
        self._save_config(default_config)
        return default_config
    
    def _save_config(self, config: GeminiConfig):
        """Save configuration to gemini-config.json"""
        config_data = {
            "model": config.model,
            "timeout": config.timeout,
            "rate_limit_delay": config.rate_limit_delay,
            "auto_consult": config.auto_consult,
            "uncertainty_thresholds": config.uncertainty_thresholds
        }
        
        with open("gemini-config.json", 'w', encoding='utf-8') as f:
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
        """Detect uncertainty patterns in text that might trigger auto-consultation"""
        if not self.config.auto_consult:
            return False
        
        uncertainty_patterns = [
            r"잘\s*모르겠습니다",
            r"확실하지\s*않습니다",
            r"불분명합니다",
            r"애매합니다",
            r"판단하기\s*어렵습니다",
            r"정확하지\s*않을\s*수\s*있습니다",
            r"I'm\s*not\s*sure",
            r"I\s*don't\s*know",
            r"unclear",
            r"uncertain",
            r"might\s*be",
            r"possibly",
            r"perhaps"
        ]
        
        for pattern in uncertainty_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    async def call_gemini(self, query: str, context: str = "") -> Dict[str, Any]:
        """Call Gemini CLI with rate limiting and error handling"""
        await self._enforce_rate_limit()
        
        self.session_stats["total_calls"] += 1
        
        try:
            # Prepare the prompt
            if context:
                full_prompt = f"Context: {context}\n\nQuery: {query}"
            else:
                full_prompt = query
            
            # Build command
            cmd = ["gemini", "-m", self.config.model, "-p", full_prompt]
            
            # Execute command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=Path.cwd()
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=self.config.timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise TimeoutError(f"Gemini call timed out after {self.config.timeout} seconds")
            
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8', errors='ignore')
                raise RuntimeError(f"Gemini CLI failed: {error_msg}")
            
            response = stdout.decode('utf-8', errors='ignore').strip()
            
            self.session_stats["successful_calls"] += 1
            self.session_stats["last_consult_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
            
            return {
                "success": True,
                "response": response,
                "model": self.config.model,
                "timestamp": self.session_stats["last_consult_time"]
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
            "session_stats": self.session_stats.copy(),
            "config_file": "gemini-config.json"
        }
    
    def update_config(self, **kwargs):
        """Update configuration parameters"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        self._save_config(self.config)

# Global instance
gemini = GeminiIntegration() 