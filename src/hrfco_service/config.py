# HRFCO Service Configuration

import os
from typing import Optional

# API 설정
HRFCO_BASE_URL = "http://api.hrfco.go.kr"
WAMIS_BASE_URL = "https://api.wamis.go.kr"
KMA_BASE_URL = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0"

# 환경변수에서 API 키 로드 (보안상 하드코딩 금지)
def get_hrfco_api_key() -> Optional[str]:
    """HRFCO API 키를 환경변수에서 안전하게 가져옵니다."""
    return os.getenv("HRFCO_API_KEY")

def get_weather_api_key() -> Optional[str]:
    """기상청 API 키를 환경변수에서 안전하게 가져옵니다."""
    return os.getenv("KMA_API_KEY")

def get_wamis_api_key() -> Optional[str]:
    """WAMIS API 키를 환경변수에서 안전하게 가져옵니다."""
    return os.getenv("WAMIS_API_KEY")

# 캐시 설정
CACHE_TTL = 300  # 5분
CACHE_MAX_SIZE = 1000

# 로깅 설정  
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# 요청 설정
REQUEST_TIMEOUT = 30
MAX_RETRIES = 3

# 개발/테스트용 설정
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# API 키 검증
def validate_api_keys() -> dict:
    """API 키 설정 상태를 확인합니다."""
    return {
        "hrfco": bool(get_hrfco_api_key()),
        "weather": bool(get_weather_api_key()),
        "wamis": bool(get_wamis_api_key())
    } 