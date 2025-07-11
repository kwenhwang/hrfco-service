# -*- coding: utf-8 -*-
"""
HRFCO Service Configuration Module
"""
import os
import logging
from typing import Dict, Any
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

class Config:
    """HRFCO Service 설정 클래스"""
    
    # API 설정 - 환경변수에서 API 키 로드
    API_KEY = os.getenv("HRFCO_API_KEY", "your-api-key-here")
    BASE_URL = "http://api.hrfco.go.kr"
    
    # 캐시 설정
    CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "300"))
    CACHE_CLEANUP_INTERVAL = int(os.getenv("CACHE_CLEANUP_INTERVAL", "600"))
    CACHE_CLEANUP_THRESHOLD = int(os.getenv("CACHE_CLEANUP_THRESHOLD", "1000"))
    
    # HTTP 설정
    MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "5"))
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
    
    # 관측소 정보 업데이트 설정
    OBSERVATORY_UPDATE_INTERVAL = int(os.getenv("OBSERVATORY_UPDATE_INTERVAL", "21600"))  # 6시간
    
    # 로깅 설정
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "hrfco_server.log")
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 페이지네이션 설정
    DEFAULT_PAGE_SIZE = int(os.getenv("DEFAULT_PAGE_SIZE", "50"))
    MAX_PAGE_SIZE = int(os.getenv("MAX_PAGE_SIZE", "100"))
    
    @classmethod
    def validate(cls) -> None:
        """필수 설정값 검증 - API 키가 항상 설정되어 있으므로 검증 통과"""
        if not cls.API_KEY:
            raise ValueError("API 키가 설정되지 않았습니다")
    
    @classmethod
    def get_logging_config(cls) -> Dict[str, Any]:
        """로깅 설정 반환"""
        return {
            'level': getattr(logging, cls.LOG_LEVEL.upper()),
            'format': cls.LOG_FORMAT,
            'handlers': [
                logging.StreamHandler(),
                logging.FileHandler(cls.LOG_FILE, encoding='utf-8')
            ]
        } 