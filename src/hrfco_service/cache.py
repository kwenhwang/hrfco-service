# -*- coding: utf-8 -*-
"""
HRFCO Service Cache Management Module
"""
import time
import logging
from typing import Dict, Any, Optional, Tuple

from .config import Config

cache_logger = logging.getLogger("hrfco-cache")
cache_logger.setLevel(logging.INFO)

class CacheManager:
    """캐시 관리 클래스"""
    
    def __init__(self, ttl_seconds: int = None):
        self.cache: Dict[str, Tuple[float, Any]] = {}
        self.ttl_seconds = ttl_seconds or Config.CACHE_TTL_SECONDS
        self._last_cleanup = time.time()
        self._cleanup_interval = Config.CACHE_CLEANUP_INTERVAL
        self._cleanup_threshold = Config.CACHE_CLEANUP_THRESHOLD

    def get(self, key: str) -> Optional[Any]:
        """캐시에서 데이터 조회"""
        now = time.time()
        if key in self.cache:
            timestamp, data = self.cache[key]
            if now - timestamp < self.ttl_seconds:
                cache_logger.debug(f"Cache HIT: {key[:100]}...")
                return data
            else:
                cache_logger.debug(f"Cache EXPIRED: {key[:100]}...")
                del self.cache[key]
        return None

    def set(self, key: str, data: Any) -> None:
        """캐시에 데이터 저장"""
        self.cache[key] = (time.time(), data)
        cache_logger.debug(f"Cache SET: {key[:100]}...")
        self._check_cleanup()

    def _check_cleanup(self) -> None:
        """캐시 정리 필요 여부 확인"""
        now = time.time()
        if (len(self.cache) > self._cleanup_threshold or 
            now - self._last_cleanup > self._cleanup_interval):
            self.cleanup()

    def cleanup(self) -> None:
        """만료된 캐시 항목 정리"""
        now = time.time()
        expired_keys = [
            k for k, (ts, _) in self.cache.items() 
            if now - ts >= self.ttl_seconds
        ]
        removed_count = 0
        for key in expired_keys:
            if key in self.cache:
                del self.cache[key]
                removed_count += 1
        self._last_cleanup = now
        if removed_count > 0:
            cache_logger.info(
                f"Cache cleanup: Removed {removed_count} expired items. "
                f"Current size: {len(self.cache)}"
            )

    def clear(self) -> None:
        """캐시 전체 삭제"""
        self.cache.clear()
        cache_logger.info("Cache cleared completely.")

    @property
    def size(self) -> int:
        """캐시 크기 반환"""
        return len(self.cache)

    def get_stats(self) -> Dict[str, Any]:
        """캐시 통계 정보 반환"""
        return {
            'size': self.size,
            'ttl_seconds': self.ttl_seconds,
            'cleanup_interval': self._cleanup_interval,
            'cleanup_threshold': self._cleanup_threshold
        } 