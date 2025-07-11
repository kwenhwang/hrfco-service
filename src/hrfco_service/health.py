# -*- coding: utf-8 -*-
"""
HRFCO Service Health Check and Monitoring
"""
import time
import logging
from typing import Dict, Any
from datetime import datetime

from .config import Config
from .cache import CacheManager
from .observatory import ObservatoryManager

logger = logging.getLogger(__name__)

class HealthChecker:
    """서비스 헬스체크 관리자"""
    
    def __init__(self, cache_manager: CacheManager, observatory_manager: ObservatoryManager):
        self.cache_manager = cache_manager
        self.observatory_manager = observatory_manager
        self.start_time = time.time()
        self.last_check = time.time()
    
    def get_health_status(self) -> Dict[str, Any]:
        """전체 헬스 상태를 반환합니다."""
        current_time = time.time()
        uptime = current_time - self.start_time
        
        # 기본 상태
        status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": int(uptime),
            "version": "1.0.0"
        }
        
        # 캐시 상태 확인
        cache_stats = self.cache_manager.get_stats()
        status["cache"] = {
            "size": cache_stats["size"],
            "ttl_seconds": cache_stats["ttl_seconds"],
            "status": "healthy" if cache_stats["size"] < 10000 else "warning"
        }
        
        # 관측소 정보 상태 확인
        obs_stats = self.observatory_manager.get_stats()
        status["observatory"] = {
            "total_stations": obs_stats["total_stations"],
            "last_update": obs_stats["last_update"],
            "needs_update": obs_stats["needs_update"],
            "status": "healthy" if obs_stats["total_stations"] > 0 else "unhealthy"
        }
        
        # API 키 상태 확인
        api_key_status = "healthy" if Config.API_KEY else "unhealthy"
        status["api_key"] = {
            "status": api_key_status,
            "configured": bool(Config.API_KEY)
        }
        
        # 전체 상태 결정
        if (status["cache"]["status"] == "unhealthy" or 
            status["observatory"]["status"] == "unhealthy" or
            status["api_key"]["status"] == "unhealthy"):
            status["status"] = "unhealthy"
        elif (status["cache"]["status"] == "warning" or 
              status["observatory"]["status"] == "warning"):
            status["status"] = "degraded"
        
        self.last_check = current_time
        return status
    
    def is_healthy(self) -> bool:
        """서비스가 정상인지 확인합니다."""
        health_status = self.get_health_status()
        return health_status["status"] == "healthy"
    
    def get_metrics(self) -> Dict[str, Any]:
        """메트릭 정보를 반환합니다."""
        cache_stats = self.cache_manager.get_stats()
        obs_stats = self.observatory_manager.get_stats()
        
        return {
            "cache_size": cache_stats["size"],
            "cache_ttl": cache_stats["ttl_seconds"],
            "total_observatories": obs_stats["total_stations"],
            "uptime_seconds": int(time.time() - self.start_time),
            "last_health_check": self.last_check
        } 