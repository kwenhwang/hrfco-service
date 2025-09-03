# -*- coding: utf-8 -*-
"""
HRFCO Service Configuration Module
"""
import os
import logging
import json
import base64
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# 로거 설정
logger = logging.getLogger(__name__)

# 환경 변수 로드
load_dotenv()

class Config:
    """HRFCO Service 설정 클래스"""
    
    # 기본 제공 API 키 (사용자가 입력하지 않아도 사용 가능)
    DEFAULT_HRFCO_API_KEY = "FE18B23B-A81B-4246-9674-E8D641902A42"  # 실제 API 키
    DEFAULT_WEATHER_API_KEY = "bI7VVvskaOdKJGMej%2F2zJzaxEyiCeGn8kLEidNAxHV7%2FRLiWMCAIlqMY08bwU1MqnakQ4ulEirojxHU800l%2BMA%3D%3D"  # 기상청 API 키
    DEFAULT_WAMIS_API_KEY = None  # WAMIS는 API 키가 필요없음
    
    # API 설정 - 환경변수 또는 기본값 사용
    API_KEY = None
    WEATHER_API_KEY = None
    WAMIS_API_KEY = None
    
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
    
    # API 키 파일 경로
    API_KEYS_FILE = os.getenv("API_KEYS_FILE", ".api_keys.json")
    
    @classmethod
    def load_api_keys(cls) -> None:
        """API 키를 여러 소스에서 로드 (우선순위: 환경변수 > 파일 > 기본값)"""
        # 1. 환경변수에서 로드
        cls.API_KEY = os.getenv("HRFCO_API_KEY")
        cls.WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
        cls.WAMIS_API_KEY = os.getenv("WAMIS_API_KEY")
        
        # 2. API 키 파일에서 로드 (환경변수가 없을 경우)
        if not cls.API_KEY or cls.API_KEY == "your-api-key-here":
            cls._load_from_file()
        
        # 3. 기본 제공 API 키 사용 (환경변수나 파일에 없을 경우)
        if not cls.API_KEY or cls.API_KEY == "your-api-key-here":
            cls.API_KEY = cls.DEFAULT_HRFCO_API_KEY
            logger.info("기본 제공 HRFCO API 키를 사용합니다.")
        
        if not cls.WEATHER_API_KEY or cls.WEATHER_API_KEY == "your-weather-api-key-here":
            cls.WEATHER_API_KEY = cls.DEFAULT_WEATHER_API_KEY
            logger.info("기본 제공 기상청 API 키를 사용합니다.")
        
        if not cls.WAMIS_API_KEY or cls.WAMIS_API_KEY == "your-wamis-api-key-here":
            cls.WAMIS_API_KEY = cls.DEFAULT_WAMIS_API_KEY
            logger.info("기본 제공 WAMIS API 키를 사용합니다.")
    
    @classmethod
    def _load_from_file(cls) -> None:
        """API 키 파일에서 로드 (암호화된 키 지원)"""
        try:
            keys_file = Path(cls.API_KEYS_FILE)
            key_file = Path(".encryption_key")
            
            if keys_file.exists():
                with open(keys_file, 'r', encoding='utf-8') as f:
                    keys_data = json.load(f)
                
                # 암호화된 키 복호화 시도
                if key_file.exists():
                    try:
                        from cryptography.fernet import Fernet
                        import base64
                        
                        with open(key_file, 'rb') as f:
                            encryption_key = f.read()
                        
                        f = Fernet(encryption_key)
                        
                        # HRFCO API 키
                        if not cls.API_KEY and "hrfco_api_key" in keys_data:
                            encrypted_key = keys_data["hrfco_api_key"]
                            decrypted = f.decrypt(base64.b64decode(encrypted_key.encode()))
                            cls.API_KEY = decrypted.decode()
                        
                        # 기상청 API 키
                        if not cls.WEATHER_API_KEY and "weather_api_key" in keys_data:
                            encrypted_key = keys_data["weather_api_key"]
                            decrypted = f.decrypt(base64.b64decode(encrypted_key.encode()))
                            cls.WEATHER_API_KEY = decrypted.decode()
                        
                        # WAMIS API 키
                        if not cls.WAMIS_API_KEY and "wamis_api_key" in keys_data:
                            encrypted_key = keys_data["wamis_api_key"]
                            decrypted = f.decrypt(base64.b64decode(encrypted_key.encode()))
                            cls.WAMIS_API_KEY = decrypted.decode()
                        
                        logger.info(f"암호화된 API 키를 파일에서 로드했습니다: {keys_file}")
                        return
                    except Exception as e:
                        logger.debug(f"암호화된 키 복호화 실패: {e}")
                
                # 일반 텍스트 키 로드 (기존 방식)
                if not cls.API_KEY:
                    cls.API_KEY = keys_data.get("hrfco_api_key")
                if not cls.WEATHER_API_KEY:
                    cls.WEATHER_API_KEY = keys_data.get("weather_api_key")
                if not cls.WAMIS_API_KEY:
                    cls.WAMIS_API_KEY = keys_data.get("wamis_api_key")
                
                logger.info(f"API 키를 파일에서 로드했습니다: {keys_file}")
        except Exception as e:
            logger.debug(f"API 키 파일 로드 실패: {e}")
    
    @classmethod
    def save_api_keys(cls, hrfco_key: str = None, weather_key: str = None, wamis_key: str = None) -> bool:
        """API 키를 파일에 저장 (선택사항)"""
        try:
            keys_data = {}
            
            if hrfco_key:
                keys_data["hrfco_api_key"] = hrfco_key
            if weather_key:
                keys_data["weather_api_key"] = weather_key
            if wamis_key:
                keys_data["wamis_api_key"] = wamis_key
            
            if keys_data:
                keys_file = Path(cls.API_KEYS_FILE)
                with open(keys_file, 'w', encoding='utf-8') as f:
                    json.dump(keys_data, f, indent=2, ensure_ascii=False)
                
                # 파일 권한 설정 (소유자만 읽기/쓰기)
                keys_file.chmod(0o600)
                logger.info(f"API 키를 파일에 저장했습니다: {keys_file}")
                return True
        except Exception as e:
            logger.error(f"API 키 저장 실패: {e}")
            return False
    
    @classmethod
    def get_api_key(cls, api_type: str = "hrfco") -> Optional[str]:
        """API 타입별 키 반환"""
        if api_type == "hrfco":
            return cls.API_KEY
        elif api_type == "weather":
            return cls.WEATHER_API_KEY
        elif api_type == "wamis":
            return cls.WAMIS_API_KEY
        else:
            return None
    
    @classmethod
    def is_api_key_valid(cls, api_type: str = "hrfco") -> bool:
        """API 키가 유효한지 확인"""
        if api_type == "wamis":
            # WAMIS는 API 키가 필요없음
            return True
        
        key = cls.get_api_key(api_type)
        return key and key not in ["your-api-key-here", "your-weather-api-key-here", "your-wamis-api-key-here"]
    
    @classmethod
    def validate(cls) -> None:
        """필수 설정값 검증 - 기본 제공 API 키 사용"""
        cls.load_api_keys()
        
        if cls.is_api_key_valid("hrfco"):
            logger.info("HRFCO API 키가 설정되어 있습니다.")
        else:
            logger.warning("HRFCO API 키가 설정되지 않았습니다. 기본 제공 키를 사용합니다.")
        
        if cls.is_api_key_valid("weather"):
            logger.info("기상청 API 키가 설정되어 있습니다.")
        else:
            logger.warning("기상청 API 키가 설정되지 않았습니다. 기본 제공 키를 사용합니다.")
        
        if cls.is_api_key_valid("wamis"):
            logger.info("WAMIS API 키가 설정되어 있습니다.")
        else:
            logger.info("WAMIS는 API 키가 필요없습니다. 공개 API를 사용합니다.")
    
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