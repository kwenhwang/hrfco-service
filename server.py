# -*- coding: utf-8 -*-
from fastmcp import FastMCP
import sys
import httpx
import os
import json
import logging
import re
import time
import asyncio
from datetime import datetime, timedelta, date

# dateutil.relativedelta 임포트 (설치 필요)
try:
    from dateutil.relativedelta import relativedelta
except ImportError:
    print("ERROR: 'python-dateutil' library not found. Please install it using 'pip install python-dateutil'", file=sys.stderr)
    sys.exit(1)

from dotenv import load_dotenv
from typing import Dict, List, Optional, Union, Any, Tuple, Literal
from mcp.types import TextContent

# --- 기본 설정 ---
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"

load_dotenv()

# --- 로깅 설정 (단순화) ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('hrfco_server.log', encoding='utf-8')
    ]
)
logger = logging.getLogger("hrfco-server")
http_logger = logging.getLogger("httpx")
http_logger.setLevel(logging.WARNING)
cache_logger = logging.getLogger("hrfco-cache")
cache_logger.setLevel(logging.INFO)

# --- FastMCP 초기화 ---
mcp = FastMCP("hrfco-server")

# --- API 및 서버 설정 ---
API_KEY = os.getenv("HRFCO_API_KEY")
if not API_KEY:
    logger.critical("CRITICAL: HRFCO_API_KEY environment variable is not set.")
    raise ValueError("HRFCO_API_KEY 환경 변수가 필요합니다")
else:
    logger.info(f"HRFCO_API_KEY loaded (Length: {len(API_KEY)}).")

BASE_URL = "https://api.hrfco.go.kr"
CACHE_TTL_SECONDS = 300
MAX_CONCURRENT_REQUESTS = 5
semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

# --- 데이터 정의 (HYDRO_TYPES 확장) ---
HYDRO_TYPES = {
    # 수위 (Water Level)
    "waterlevel": {
        "code_key": "wlobscd", "name": "수위", "unit": "m", "value_key": "wl",
        "fields": ["ymdhm", "wl", "fw"], # 기본 반환 필드: 시간, 수위, 유량
        "all_fields": ["ymdhm", "wl", "fw", "ec", "etc"], # 조회 가능한 모든 필드
        "alert_keys": {"att": "attwl", "wrn": "wrnwl", "alm": "almwl", "srs": "srswl", "plan": "pfh"}, # 임계값 키
        "description": "하천의 특정 지점에서의 수위(해발고도 또는 기준면부터의 높이)와 유량 정보를 제공합니다."
    },
    # 강수량 (Rainfall)
    "rainfall": {
        "code_key": "rfobscd", "name": "강수량", "unit": "mm", "value_key": "rf",
        "fields": ["ymdhm", "rf"], # 기본 반환 필드: 시간, 강수량
        "all_fields": ["ymdhm", "rf"],
        "alert_keys": {}, # 강수량 자체에는 표준 임계값 없음
        "description": "특정 지점에서의 일정 시간 동안 내린 비의 양을 제공합니다."
    },
    # 댐 (Dam)
    "dam": {
        "code_key": "dmobscd", "name": "댐", "unit": "varies", "value_key": "swl", # 단위가 다양함 (EL.m, m³/s 등)
        "fields": ["ymdhm", "swl", "inf", "tototf"], # 기본: 시간, 저수위, 유입량, 총방류량
        "all_fields": ["ymdhm", "swl", "inf", "esp", "ecpc", "otf", "tototf", "dmst", "dmopsn"], # 가능한 필드들
        "alert_keys": {"ltd": "ltdwl", "inf": "infwl", "fld": "fldwl", "hltd": "hltdwl"}, # 댐별 상이, 대표 예시
        "description": "댐의 저수위, 저수량, 유입량, 방류량 등의 운영 상태 정보를 제공합니다."
    },
    # 보 (Bo - Weir)
    "bo": {
        "code_key": "boobscd", "name": "보", "unit": "varies", "value_key": "swl",
        "fields": ["ymdhm", "swl", "inf", "tototf"], # 기본: 시간, 저수위(상류), 유입량, 총방류량
        "all_fields": ["ymdhm", "swl", "inf", "esp", "ecpc", "otf", "tototf", "bost", "boopsn"],
        "alert_keys": {"mng": "mngwl", "cnt": "cntwl"}, # 보별 상이, 대표 예시
        "description": "보의 상/하류 수위, 유입량, 방류량, 수문 개방 상태 등의 정보를 제공합니다."
    }
}

# --- 캐시 관리 클래스 ---
class CacheManager:
    def __init__(self, ttl_seconds: int):
        self.cache: Dict[str, Tuple[float, Any]] = {} # 값 타입을 Any로 변경 (JSON 문자열 저장 대비)
        self.ttl_seconds = ttl_seconds
        self._last_cleanup = time.time()
        self._cleanup_interval = 600 # 10분마다 정리 시도
        self._cleanup_threshold = 1000

    def get(self, key: str) -> Optional[Any]:
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
        self.cache[key] = (time.time(), data)
        cache_logger.debug(f"Cache SET: {key[:100]}...")
        self._check_cleanup()

    def _check_cleanup(self) -> None:
        now = time.time()
        # 임계값 초과 또는 일정 시간 경과 시 정리
        if len(self.cache) > self._cleanup_threshold or now - self._last_cleanup > self._cleanup_interval:
            self.cleanup()

    def cleanup(self) -> None:
        now = time.time()
        expired_keys = [k for k, (ts, _) in self.cache.items() if now - ts >= self.ttl_seconds]
        removed_count = 0
        for key in expired_keys:
            if key in self.cache: # 삭제 중 다른 스레드/태스크에서 제거될 수 있음
                del self.cache[key]
                removed_count += 1
        self._last_cleanup = now
        if removed_count > 0:
            cache_logger.info(f"Cache cleanup: Removed {removed_count} expired items. Current size: {len(self.cache)}")

    def clear(self) -> None:
        self.cache.clear()
        cache_logger.info("Cache cleared completely.")

    @property
    def size(self) -> int:
        return len(self.cache)

# --- 관측소 정보 관리 클래스 (수정됨) ---
class ObservatoryManager:
    def __init__(self):
        self.info: Dict[str, Dict[str, Dict]] = {}
        self.name_to_code: Dict[str, Dict[str, str]] = {}
        self._last_update = 0
        self._update_interval = 3600 * 6 # 6시간마다 업데이트 시도

    def update(self, hydro_type: str, obs_data: List[Dict]) -> None:
        if hydro_type not in HYDRO_TYPES: return
        config = HYDRO_TYPES[hydro_type]; code_key = config["code_key"]
        current_type_info = {}; current_type_name_map = {}; loaded_count = 0
        for item in obs_data:
            if not isinstance(item, dict) or code_key not in item: continue
            obscd = item[code_key]; obsnm = item.get("obsnm", "")
            # 필요한 정보만 저장
            processed_item = { k: item.get(k) for k in [
                "obsnm", "agcnm", "addr", "etcaddr", "lon", "lat", "gdt", "pfh"
            ] + list(config.get("alert_keys", {}).values()) if item.get(k) is not None}
            current_type_info[obscd] = processed_item
            if obsnm: current_type_name_map[obsnm] = obscd
            loaded_count += 1
        self.info[hydro_type] = current_type_info
        self.name_to_code[hydro_type] = current_type_name_map
        self._last_update = time.time()
        logger.info(f"Updated observatory info for {hydro_type}: {loaded_count} stations")

    def get_observatory_code(self, hydro_type: str, identifier: str) -> Optional[str]:
        if hydro_type not in self.info: return None
        if identifier in self.info[hydro_type]: return identifier
        if hydro_type in self.name_to_code and identifier in self.name_to_code[hydro_type]:
            return self.name_to_code[hydro_type][identifier]
        identifier_lower = identifier.lower()
        for name, code in self.name_to_code.get(hydro_type, {}).items():
            if name.lower() == identifier_lower: return code
        return None

    def needs_update(self) -> bool:
        return not self.info or time.time() - self._last_update > self._update_interval

    @property
    def total_stations(self) -> int:
        return sum(len(stations) for stations in self.info.values())

# --- 전역 변수 및 캐시 ---
observatory_manager = ObservatoryManager()
cache_manager = CacheManager(CACHE_TTL_SECONDS)

async def ensure_info_loaded():
    """관측소 정보가 로드되지 않았으면 로드"""
    if not observatory_manager.info:
        logger.warning("관측소 정보가 로드되지 않았습니다. 지금 로드합니다...")
        print("stderr: 관측소 정보가 로드되지 않았습니다. 지연 로드 시도...", file=sys.stderr)
        await load_observatory_info()
        if not observatory_manager.info:
            logger.error("관측소 정보 지연 로드 실패. 일부 도구가 작동하지 않을 수 있습니다.")
            print("stderr: 오류: 관측소 정보 지연 로드 실패", file=sys.stderr)

# --- 예외 클래스 정의 ---
class HRFCOError(Exception):
    """홍수통제소 API 관련 기본 예외 클래스"""
    pass

class APIError(HRFCOError):
    """API 호출 관련 예외"""
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response

class ValidationError(HRFCOError):
    """입력값 검증 관련 예외"""
    pass

class CacheError(HRFCOError):
    """캐시 관련 예외"""
    pass

class ObservatoryError(HRFCOError):
    """관측소 정보 관련 예외"""
    pass

# --- 에러 처리 헬퍼 함수 ---
def handle_api_error(error: Exception, context: str) -> Dict:
    """API 관련 예외를 처리하고 사용자 친화적인 오류 메시지를 반환합니다.
    
    Args:
        error (Exception): 처리할 예외 객체
        context (str): 오류 발생 컨텍스트
    
    Returns:
        Dict: 오류 정보를 포함한 딕셔너리
    """
    error_type = type(error).__name__
    
    if isinstance(error, ValidationError):
        logger.error(f"Validation Error in {context}: {str(error)}")
        return {
            "error_type": "ValidationError",
            "message": str(error),
            "detail": "입력값이 유효하지 않습니다. 파라미터를 확인하세요."
        }
    elif isinstance(error, APIError):
        logger.error(f"API Error in {context}: {str(error)}")
        return {
            "error_type": "APIError",
            "message": str(error),
            "detail": "API 호출 중 오류가 발생했습니다. 잠시 후 다시 시도하세요."
        }
    elif isinstance(error, ObservatoryError):
        logger.error(f"Observatory Error in {context}: {str(error)}")
        return {
            "error_type": "ObservatoryError",
            "message": str(error),
            "detail": "관측소 정보를 찾을 수 없습니다. 관측소 코드를 확인하세요."
        }
    else:
        logger.exception(f"Unexpected error in {context}: {str(error)}")
        return {
            "error_type": "UnexpectedError",
            "message": "예기치 않은 오류가 발생했습니다.",
            "detail": str(error)
        }

def _parse_relative_date(date_str: str) -> Optional[date]:
    """상대적 날짜 문자열을 파싱합니다."""
    if not date_str: return None
    date_str = date_str.lower().strip()
    today = date.today()
    
    # "today", "yesterday" 처리
    if date_str == "today": return today
    if date_str == "yesterday": return today - timedelta(days=1)
    
    # "n days ago" 처리
    days_match = re.match(r"(\d+)\s*days?\s*ago", date_str)
    if days_match:
        days = int(days_match.group(1))
        return today - timedelta(days=days)
    
    # "n months ago" 처리
    months_match = re.match(r"(\d+)\s*months?\s*ago", date_str)
    if months_match:
        months = int(months_match.group(1))
        return today - relativedelta(months=months)
    
    # "n years ago" 처리
    years_match = re.match(r"(\d+)\s*years?\s*ago", date_str)
    if years_match:
        years = int(years_match.group(1))
        return today - relativedelta(years=years)
    
    return None

def _format_datetime_for_api(date_input: Union[str, date, datetime], time_type: str) -> str:
    """날짜/시간 입력을 TimeType에 맞는 API 형식으로 변환"""
    dt_obj = None
    if isinstance(date_input, datetime): dt_obj = date_input
    elif isinstance(date_input, date): dt_obj = datetime.combine(date_input, datetime.min.time())
    elif isinstance(date_input, str):
        parsed_date = _parse_relative_date(date_input)
        if parsed_date: dt_obj = datetime.combine(parsed_date, datetime.min.time())
        else:
            try: # YYYYMMDD 또는 YYYY-MM-DD 처리 (시간은 00:00)
                clean_date = re.sub(r'[^0-9]', '', date_input)
                if len(clean_date) >= 8:
                    dt_obj = datetime.strptime(clean_date[:8], '%Y%m%d')
                else: raise ValueError("날짜 형식 불충분")
            except ValueError: raise ValueError(f"날짜 형식 인식 불가: '{date_input}'")
    else: raise TypeError("날짜 입력은 str, date, datetime이어야 함")

    if not dt_obj: raise ValueError(f"날짜 파싱 실패: '{date_input}'")

    # TimeType에 따른 포맷 반환
    if time_type == "10M": return dt_obj.strftime("%Y%m%d%H%M")
    elif time_type == "1H": return dt_obj.strftime("%Y%m%d%H")
    elif time_type == "1D": return dt_obj.strftime("%Y%m%d")
    else: raise ValueError(f"잘못된 time_type: {time_type}")

def validate_date_range(start_date: str, end_date: str, time_type: str) -> Tuple[str, str]:
    """날짜 범위를 검증하고 TimeType에 맞는 API 형식 튜플 반환"""
    try:
        start_fmt = _format_datetime_for_api(start_date, time_type)
        end_fmt = _format_datetime_for_api(end_date, time_type)
        date_format = "%Y%m%d%H%M" if time_type == "10M" else ("%Y%m%d%H" if time_type == "1H" else "%Y%m%d")
        start_dt = datetime.strptime(start_fmt, date_format)
        end_dt = datetime.strptime(end_fmt, date_format)
        if start_dt > end_dt: start_fmt, end_fmt = end_fmt, start_fmt; start_dt, end_dt = end_dt, start_dt
        max_days = 31 if time_type == "10M" else 366
        # timedelta는 datetime 객체 간 차이 계산에 더 정확
        if (end_dt - start_dt) > timedelta(days=max_days):
            period_limit = "1개월" if time_type == "10M" else "1년"
            raise ValidationError(f"{time_type} 단위 조회 시 최대 기간({period_limit})을 초과했습니다.")
        return start_fmt, end_fmt
    except ValueError as e: raise ValidationError(f"날짜 형식 또는 범위 오류: {str(e)}")

def validate_hydro_type(hydro_type: str) -> str:
    """하천 유형을 검증하고 정규화합니다.
    
    Args:
        hydro_type (str): 검증할 하천 유형
        
    Returns:
        str: 정규화된 하천 유형
        
    Note:
        - 지원되는 하천 유형:
          - waterlevel: 수위
          - flowrate: 유량
          - rainfall: 강수
          - bo: 보
          - dam: 댐
          - pump: 펌프
          - gate: 수문
          - quality: 수질
          - weather: 기상
          - integrated: 통합
    """
    normalized_type = hydro_type.lower()
    if normalized_type == "weir": normalized_type = "bo" # 'weir'를 'bo'로 변환
    if normalized_type not in HYDRO_TYPES:
        raise ValidationError(f"지원되지 않는 하천 유형입니다: {hydro_type}")
    return normalized_type

def validate_time_type(time_type: str) -> None:
    """시간 유형을 검증합니다.
    
    Args:
        time_type (str): 검증할 시간 유형
    
    Raises:
        ValueError: 시간 유형이 유효하지 않은 경우
    
    Note:
        지원하는 시간 유형:
        - 10M: 10분 단위
        - 1H: 1시간 단위
        - 1D: 1일 단위
    """
    if not time_type:
        raise ValueError("time_type은 필수입니다.")

    valid_types = ["10M", "1H", "1D"]
    if time_type not in valid_types:
        raise ValueError(f"지원하지 않는 time_type입니다: '{time_type}'. 유효한 유형: {', '.join(valid_types)}")

# --- Helper 함수 수정 ---
async def _fetch_with_cache(url: str) -> Dict:
    try:
        cached_data = cache_manager.get(url)
        if cached_data is not None: return cached_data
        async with semaphore:
            logger.info(f"Fetching URL: {url[:100]}...")
            async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
                try:
                    logger.debug(f"Calling API: {url}")
                    response = await client.get(url)
                    response.raise_for_status()
                    data = response.json()
                    # 성공 응답만 캐시
                    if isinstance(data, dict) and "content" in data:
                        cache_manager.set(url, data)
                    elif isinstance(data, list): # 리스트 응답 래핑 및 캐시
                        wrapper_data = {"content": data}
                        cache_manager.set(url, wrapper_data)
                        data = wrapper_data
                    else: # content 없는 성공 응답 등은 캐시 안 함
                        logger.warning(f"API response for {url[:100]}... lacks 'content'. Not caching.")
                    return data
                except httpx.HTTPStatusError as e:
                    error_info = handle_api_error(e, f"fetching {url[:100]}...")
                    raise APIError(error_info["message"], e.response.status_code, detail=error_info) from e
                except (httpx.RequestError, asyncio.TimeoutError, json.JSONDecodeError) as e:
                    error_info = handle_api_error(e, f"fetching {url[:100]}...")
                    raise APIError(error_info["message"], detail=error_info) from e
                except Exception as e:
                    error_info = handle_api_error(e, f"fetching {url[:100]}...")
                    raise APIError(error_info["message"], detail=error_info) from e
    except APIError as e: raise # APIError는 그대로 전달
    except Exception as e:
        logger.exception(f"Unexpected error in _fetch_with_cache for {url[:100]}...: {str(e)}")
        raise APIError(f"Internal error during fetch: {str(e)}") from e

async def fetch_hrfco_data(
    hydro_type: str,
    data_type: str = "data",
    obs_code: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    time_type: str = "1H",
    fields: Optional[List[str]] = None
) -> Dict:
    """HRFCO API를 호출하여 데이터를 가져옵니다.
    
    Args:
        hydro_type (str): 하천 유형 (예: waterlevel, rainfall 등)
        data_type (str): 데이터 유형 (data 또는 info)
        obs_code (Optional[str]): 관측소 코드
        start_date (Optional[str]): 시작 날짜 (YYYYMMDDHHmm 형식)
        end_date (Optional[str]): 종료 날짜 (YYYYMMDDHHmm 형식)
        time_type (str): 시간 단위 (1H, 1D, 1M)
        fields (Optional[List[str]]): 반환할 필드 목록
        
    Returns:
        Dict: API 응답 데이터
    """
    try:
        # 하천 유형 검증
        normalized_type = validate_hydro_type(hydro_type)
        
        # API URL 구성
        url_parts = [BASE_URL, normalized_type, data_type]
        if data_type == "data" and obs_code:
            url_parts.append(obs_code)
            
        # 기본 URL 생성
        url = "/".join(url_parts)
        
        # 파라미터 구성
        params = {
            "API_KEY": API_KEY,
            "hydro_type": normalized_type,
            "time_type": time_type
        }
        
        # 날짜 범위 검증 및 정규화
        if start_date or end_date:
            try:
                start, end = validate_date_range(start_date, end_date, time_type)
                start_date = _format_datetime_for_api(start, time_type)
                end_date = _format_datetime_for_api(end, time_type)
                params["start_date"] = start_date
                params["end_date"] = end_date
            except ValueError as e:
                raise ValidationError(str(e))
        
        # URL에 파라미터 추가
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{url}?{query_string}"
        
        # API 호출
        return await _fetch_with_cache(url)
        
    except Exception as e:
        error_info = handle_api_error(e, f"fetching {hydro_type} data")
        raise APIError(error_info["message"], detail=error_info) from e

async def load_observatory_info() -> None:
    """관측소 정보를 순차 로드 (ObservatoryManager 사용)"""
    if not observatory_manager.needs_update(): return
    logger.info("Starting sequential loading of observatory info...")
    print("stderr: Starting load_observatory_info", file=sys.stderr)
    start_load_time = time.time()
    tasks_results = {}
    has_error = False
    for hydro_type in HYDRO_TYPES.keys():
        logger.info(f"Loading info for {hydro_type}...")
        try:
            result = await fetch_hrfco_data(hydro_type=hydro_type, data_type="info")
            tasks_results[hydro_type] = result
            if isinstance(result, dict) and "error_type" in result:
                logger.error(f"ERROR loading {hydro_type} info: {result.get('message')}")
                has_error = True
        except Exception as e:
            logger.error(f"CRITICAL ERROR during fetch task for {hydro_type} info: {str(e)}", exc_info=True)
            tasks_results[hydro_type] = {"message": f"Fetch exception: {str(e)}", "error_type": "FetchException"}
            has_error = True

    # 모든 fetch 완료 후 업데이트
    for hydro_type, result in tasks_results.items():
        if isinstance(result, dict) and "error_type" not in result: # 성공한 경우만
            content = result.get("content")
            if isinstance(content, list):
                observatory_manager.update(hydro_type, content)
            else:
                logger.warning(f"Invalid content format for {hydro_type} after fetch.")

    logger.info(f"Finished loading observatory info. Total stations: {observatory_manager.total_stations}")
    if has_error: logger.warning("Some observatory types might have failed to load.")
    print(f"stderr: Finished load_observatory_info in {time.time() - start_load_time:.2f}s", file=sys.stderr)

def _find_observatory_code(hydro_type: str, obs_identifier: str) -> Optional[str]:
    """관측소 이름 또는 코드로 실제 관측소 코드를 찾습니다."""
    if hydro_type not in HYDRO_TYPES or hydro_type not in observatory_manager.info or hydro_type not in observatory_manager.name_to_code:
        logger.warning(f"Observatory info/mapping for {hydro_type} not loaded yet or invalid type.")
        return None

    # 1. 코드로 직접 확인
    if obs_identifier in observatory_manager.info[hydro_type]:
        return obs_identifier
    # 2. 이름으로 확인
    # 이름 중복 가능성 고려 -> 여기서는 일단 첫 번째 매칭 코드 반환
    if obs_identifier in observatory_manager.name_to_code[hydro_type]:
        return observatory_manager.name_to_code[hydro_type][obs_identifier]
    # 3. 대소문자 무시하고 이름으로 확인 (추가)
    obs_identifier_lower = obs_identifier.lower()
    for name, code in observatory_manager.name_to_code[hydro_type].items():
         if name.lower() == obs_identifier_lower:
             return code

    logger.warning(f"Could not find observatory code for identifier '{obs_identifier}' of type '{hydro_type}'.")
    return None

def _get_alert_thresholds(obs_info: Dict, hydro_type: str) -> Dict[str, Optional[float]]:
    """관측소 정보에서 수치형 alert 임계값을 추출합니다."""
    thresholds = {"attention": None, "warning": None, "alarm": None, "serious": None, "plan_flood": None} # 영문 키 사용
    if not obs_info or hydro_type not in HYDRO_TYPES:
        return thresholds

    config = HYDRO_TYPES[hydro_type]
    alert_key_map = config.get("alert_keys") # API 필드명 매핑
    if not alert_key_map:
        return thresholds

    # 표준 레벨 키와 API 필드명 매핑
    level_map = {
        "attention": alert_key_map.get("att"), # 주의
        "warning": alert_key_map.get("wrn"),   # 경고
        "alarm": alert_key_map.get("alm"),     # 경계
        "serious": alert_key_map.get("srs"),   # 심각
        "plan_flood": alert_key_map.get("plan") # 계획홍수위
    }
    # 댐/보의 경우 다른 키 매핑 추가 가능 (예: ltd, inf, fld, mng, cnt 등)

    for level_key, obs_info_key in level_map.items():
         if obs_info_key: # 매핑된 API 키가 있을 경우
            raw_value = obs_info.get(obs_info_key)
            if raw_value is not None and str(raw_value).strip() != '':
                try:
                    thresholds[level_key] = float(raw_value)
                except (ValueError, TypeError):
                    logger.warning(f"Could not convert alert level '{obs_info_key}' value '{raw_value}' to float for obs {obs_info.get(config['code_key'])}.")

    return thresholds

def _determine_alert_status(value: Optional[float], thresholds: Dict[str, Optional[float]], hydro_type: str) -> Optional[str]:
    """값과 임계값을 비교하여 상태 문자열 반환 (수위 외 타입 고려)"""
    if value is None:
        return None # 데이터 없음 -> 상태 알 수 없음

    if hydro_type == "waterlevel":
        # 수위: 높은 순서대로 체크
        if thresholds.get("serious") is not None and value >= thresholds["serious"]: return "Serious"
        if thresholds.get("alarm") is not None and value >= thresholds["alarm"]: return "Alarm"
        if thresholds.get("warning") is not None and value >= thresholds["warning"]: return "Warning"
        if thresholds.get("attention") is not None and value >= thresholds["attention"]: return "Attention"
        return "Normal"
    # TODO: 다른 hydro_type (댐, 보 등)에 대한 상태 결정 로직 추가 (필요시)
    # 예: 댐 저수율(%) 계산 후 상태 판정 등
    else:
        return None # 수위 외 타입은 기본적으로 상태 없음

def _prepare_data_for_response(
    data_list: List[Dict],
    hydro_type: str,
    fields: Optional[List[str]] = None,
    thresholds: Optional[Dict[str, Optional[float]]] = None
) -> List[Dict]:
    """데이터 필터링 및 alert_status 추가"""
    processed_list = []
    config = HYDRO_TYPES.get(hydro_type, {})
    value_key = config.get("value_key")
    # 필드가 지정되지 않았으면 기본 필드 사용, 아니면 요청된 필드 사용
    target_fields = fields if fields else config.get("fields", [])
    # alert_status는 필드 요청과 별개로 수위 타입이면 계산 시도
    include_alert_status = (hydro_type == "waterlevel")

    for item in data_list:
        filtered_item = {}
        # 요청된/기본 필드만 포함
        if target_fields:
             for f in target_fields:
                 if f in item:
                     filtered_item[f] = item.get(f)
        else: # 필드 목록 없으면 모든 필드 포함 (all_fields 기준?) -> 일단 원본 item 다 넣기
             filtered_item = dict(item)

        # Alert Status 계산 및 추가
        if include_alert_status and thresholds and value_key:
             current_value_str = item.get(value_key)
             current_value = None
             if current_value_str is not None:
                 try: current_value = float(current_value_str)
                 except: pass
             alert_status = _determine_alert_status(current_value, thresholds, hydro_type)
             # alert_status 필드를 항상 추가 (필드 목록에 없더라도)
             filtered_item["alert_status"] = alert_status
        elif include_alert_status: # 임계값 없어도 필드는 추가 (None으로)
             filtered_item["alert_status"] = None

        if filtered_item: # 빈 dict가 아니면 추가
             processed_list.append(filtered_item)

    return processed_list


def _paginate_and_summarize_data(
    data_list: List[Dict], # 이미 필터링 및 alert_status 추가된 데이터
    page: int = 1,
    per_page: int = 50,
    hydro_type: Optional[str] = None,
) -> Dict:
    """데이터 리스트를 페이지네이션하고 요약 정보 생성"""
    total_items = len(data_list)

    # 페이지네이션
    total_pages = (total_items + per_page - 1) // per_page if per_page > 0 else (1 if total_items > 0 else 0)
    page = max(1, min(page, total_pages)) if total_pages > 0 else 1
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_content = data_list[start_idx:end_idx]

    pagination_info = {
        "total_items": total_items, "total_pages": total_pages,
        "current_page": page, "per_page": per_page,
        "has_next": page < total_pages, "has_prev": page > 1
    }

    # 요약 정보 생성 (현재 페이지 내용 기준)
    summary = None
    config = HYDRO_TYPES.get(hydro_type, {})
    value_key = config.get("value_key")
    if value_key and paginated_content:
        values = []
        for item in paginated_content: # 현재 페이지 데이터 사용
            value_str = item.get(value_key)
            if value_str is not None:
                try: values.append(float(value_str))
                except: pass
        if values:
            summary = {
                "value_field": value_key,
                "unit": config.get("unit", "N/A"),
                "count_on_page": len(values),
                "avg_on_page": round(sum(values) / len(values), 2) if values else None,
                "max_on_page": max(values) if values else None,
                "min_on_page": min(values) if values else None,
            }
            # Alert 발생 횟수 요약 (수위 데이터일 경우)
            if hydro_type == "waterlevel":
                 alert_counts = {"Attention": 0, "Warning": 0, "Alarm": 0, "Serious": 0}
                 for item in paginated_content:
                     status = item.get("alert_status")
                     if status in alert_counts:
                         alert_counts[status] += 1
                 summary["alert_summary_on_page"] = {k: v for k, v in alert_counts.items() if v > 0}

    return {"content": paginated_content, "pagination": pagination_info, "summary": summary}


# --- MCP 도구 정의 ---
@mcp.tool()
async def get_tools() -> List[TextContent]:
    """사용 가능한 도구 목록과 서버 상태를 반환합니다."""
    await ensure_info_loaded()

    # HYDRO_TYPES 정의에서 필드 정보 추출
    field_info = {}
    for ht, cfg in HYDRO_TYPES.items():
        fields = cfg.get('all_fields', cfg.get('fields', []))
        field_info[ht] = ", ".join(fields) if fields else "N/A"

    # 통계 정보 추가
    stats = {
        "total_observatories_registered": sum(len(stations) for stations in observatory_manager.info.values()),
        "observatories_by_type": {
            config["name"]: len(observatory_manager.info.get(hydro_type, {}))
            for hydro_type, config in HYDRO_TYPES.items() if hydro_type in observatory_manager.info
        },
        "api_cache_status": {
            "active_items": cache_manager.size,
            "ttl_seconds": CACHE_TTL_SECONDS
        },
        "server_version": "1.2.0"
    }

    tools_list = [
        {
            "name": "get_tools",
            "description": "사용 가능한 도구 목록과 서버 상태를 반환합니다.",
            "parameters": {}
        },
        {
            "name": "get_server_config",
            "description": "서버 설정 정보를 반환합니다.",
            "parameters": {}
        },
        {
            "name": "search_observatory",
            "description": "관측소를 검색합니다. 이름이나 주소로 검색 가능하며, hydro_type으로 필터링할 수 있습니다.",
            "parameters": {
                "query": "검색어 (필수)",
                "hydro_type": "수문 유형 (선택, waterlevel/rainfall/dam/weir)",
                "page": "페이지 번호 (기본값: 1)",
                "per_page": "페이지당 항목 수 (1-100, 기본값: 20)"
            }
        },
        {
            "name": "get_hydro_data",
            "description": "수문 데이터를 조회합니다. 날짜 범위와 시간 단위를 지정할 수 있습니다.",
            "parameters": {
                "hydro_type": "수문 유형 (필수, waterlevel/rainfall/dam/weir)",
                "obs_code": "관측소 코드 (필수)",
                "time_type": "시간 단위 (선택, 10M/1H/1D, 기본값: 1H)",
                "start_date": "시작일시 (선택, YYYYMMDD 또는 YYYY-MM-DD 형식)",
                "end_date": "종료일시 (선택, YYYYMMDD 또는 YYYY-MM-DD 형식)",
                "fields": "조회할 필드 목록 (선택)",
                "page": "페이지 번호 (기본값: 1)",
                "per_page": "페이지당 항목 수 (1-100, 기본값: 100)"
            },
            "notes": [
                "time_type별 최대 조회 기간:",
                "- 10M: 1개월",
                "- 1H: 1년",
                "- 1D: 1년"
            ]
        },
        {
            "name": "get_historical_comparison",
            "description": "여러 년도의 동일 기간 수문 데이터를 비교 조회합니다.",
            "parameters": {
                "hydro_type": "수문 유형 (필수, waterlevel/rainfall/dam/weir)",
                "obs_code": "관측소 코드 (필수)",
                "start_month_day": "시작 월일 (필수, MMDD 형식)",
                "end_month_day": "종료 월일 (필수, MMDD 형식)",
                "years": "비교할 년도 목록 (필수, 정수 리스트)",
                "time_type": "시간 단위 (선택, 10M/1H/1D, 기본값: 1H)",
                "fields": "조회할 필드 목록 (선택)"
            },
            "notes": [
                "time_type별 최대 조회 기간:",
                "- 10M: 1개월",
                "- 1H: 1년",
                "- 1D: 1년",
                "윤년을 고려하여 2월 29일 등 특수한 날짜 처리"
            ]
        },
        {
            "name": "get_batch_hydro_data",
            "description": "여러 수문 데이터 요청을 병렬로 처리합니다.",
            "parameters": {
                "requests": "요청 목록 (필수, 각 요청은 request_id, hydro_type, obs_code, start_date, end_date, time_type, fields, page, per_page 포함)"
            },
            "notes": [
                "time_type별 최대 조회 기간:",
                "- 10M: 1개월",
                "- 1H: 1년",
                "- 1D: 1년",
                "긴 기간 조회 시 자동으로 기간을 분할하여 처리"
            ]
        },
        {
            "name": "get_recent_data",
            "description": "최근 수문 데이터를 조회합니다.",
            "parameters": {
                "hydro_type": "수문 유형 (필수, waterlevel/rainfall/dam/weir)",
                "obs_code": "관측소 코드 (필수)",
                "count": "조회할 데이터 개수 (기본값: 24)",
                "time_type": "시간 단위 (선택, 10M/1H/1D, 기본값: 1H)",
                "fields": "조회할 필드 목록 (선택)"
            },
            "notes": [
                "time_type별 최대 조회 기간:",
                "- 10M: 1개월",
                "- 1H: 1년",
                "- 1D: 1년",
                "count에 따라 자동으로 적절한 기간을 계산하여 조회"
            ]
        },
        {
            "name": "get_quick_status",
            "description": "서버 상태와 관측소 정보를 빠르게 확인합니다.",
            "parameters": {}
        }
    ]

    # 도구 설명과 통계를 결합하여 텍스트 생성
    response_text = [
        "=== 서버 상태 ===",
        f"총 관측소 수: {stats['total_observatories_registered']}개",
        "관측소 유형별 수:",
        *[f"- {name}: {count}개" for name, count in stats['observatories_by_type'].items()],
        f"API 캐시 상태: {stats['api_cache_status']['active_items']}개 항목 (TTL: {stats['api_cache_status']['ttl_seconds']}초)",
        f"서버 버전: {stats['server_version']}",
        "",
        "=== 사용 가능한 도구 ===",
        *[f"{i+1}. {tool['name']}: {tool['description']}" for i, tool in enumerate(tools_list)],
        "",
        "=== API 기간 제한 ===",
        "모든 데이터 조회 도구는 time_type별로 다음과 같은 기간 제한이 있습니다:",
        "- 10분(10M) 데이터: 최대 1개월",
        "- 1시간(1H) 데이터: 최대 1년",
        "- 1일(1D) 데이터: 최대 1년",
        "",
        "=== 필드 정보 ===",
        "각 수문 유형별 사용 가능한 필드:",
        *[f"- {ht}: {fields}" for ht, fields in field_info.items()]
    ]

    return [TextContent(text="\n".join(response_text))]

@mcp.tool()
async def get_server_config() -> List[TextContent]:
    """서버 설정 정보를 반환합니다."""
    await ensure_info_loaded()

    # HYDRO_TYPES 정의에서 필드 정보 추출
    field_info = {}
    for ht, cfg in HYDRO_TYPES.items():
        fields = cfg.get('all_fields', cfg.get('fields', []))
        field_info[ht] = fields

    # 서버 설정 정보 구성
    config = {
        "server_version": "1.2.0",
        "api_config": {
            "base_url": "http://apis.data.go.kr/B551149/",
            "cache_ttl_seconds": CACHE_TTL_SECONDS,
            "time_type_limits": {
                "10M": {
                    "description": "10분 단위 데이터",
                    "max_duration_days": 30,
                    "max_duration_description": "최대 1개월"
                },
                "1H": {
                    "description": "1시간 단위 데이터",
                    "max_duration_days": 365,
                    "max_duration_description": "최대 1년"
                },
                "1D": {
                    "description": "1일 단위 데이터",
                    "max_duration_days": 365,
                    "max_duration_description": "최대 1년"
                }
            }
        },
        "hydro_types": {
            ht: {
                "name": cfg["name"],
                "description": cfg.get("description", ""),
                "unit": cfg.get("unit", ""),
                "value_key": cfg.get("value_key", ""),
                "fields": fields,
                "alert_thresholds": cfg.get("alert_thresholds", {})
            }
            for ht, cfg in HYDRO_TYPES.items()
        },
        "observatory_stats": {
            "total_count": sum(len(stations) for stations in observatory_manager.info.values()),
            "by_type": {
                config["name"]: len(observatory_manager.info.get(hydro_type, {}))
                for hydro_type, config in HYDRO_TYPES.items() if hydro_type in observatory_manager.info
            }
        }
    }

    # 응답 텍스트 생성
    response_text = [
        "=== 서버 설정 정보 ===",
        f"서버 버전: {config['server_version']}",
        "",
        "=== API 설정 ===",
        f"기본 URL: {config['api_config']['base_url']}",
        f"캐시 유효 시간: {config['api_config']['cache_ttl_seconds']}초",
        "",
        "=== 시간 단위별 제한 ===",
        *[f"- {tt}: {info['description']} ({info['max_duration_description']})" 
          for tt, info in config['api_config']['time_type_limits'].items()],
        "",
        "=== 수문 유형 정보 ===",
        *[f"- {ht}: {info['name']}",
          f"  설명: {info['description']}",
          f"  단위: {info['unit']}",
          f"  값 필드: {info['value_key']}",
          f"  사용 가능 필드: {', '.join(info['fields'])}",
          f"  경보 임계값: {json.dumps(info['alert_thresholds'], ensure_ascii=False)}"
          for ht, info in config['hydro_types'].items()],
        "",
        "=== 관측소 통계 ===",
        f"총 관측소 수: {config['observatory_stats']['total_count']}개",
        "유형별 관측소 수:",
        *[f"- {name}: {count}개" 
          for name, count in config['observatory_stats']['by_type'].items()]
    ]

    return [TextContent(text="\n".join(response_text))]


@mcp.tool()
async def search_observatory(
    query: str,
    hydro_type: Optional[str] = None,
    page: int = 1,
    per_page: int = 20
) -> List[TextContent]:
    """관측소를 검색합니다.
    
    Args:
        query (str): 검색어 (이름이나 주소의 일부)
        hydro_type (str, optional): 수문 유형 (waterlevel/rainfall/dam/weir)
        page (int): 페이지 번호 (1부터 시작)
        per_page (int): 페이지당 항목 수 (1-100)
    
    Returns:
        List[TextContent]: 검색 결과
    
    Note:
        - 검색 결과에는 관측소의 기본 정보(이름, 주소, 관할기관)와 위치 정보(위도, 경도)가 포함됩니다.
        - 특정 사건/위치 분석 시 관련 하천명, 인근 지역명(읍/면/동), 주요 시설물 이름 등으로 검색하여 필요한 관측소 코드를 확보하세요.
    """
    await ensure_info_loaded()

    # 입력값 검증
    if not query or not query.strip():
        return [TextContent(text="오류: 검색어는 필수입니다.")]

    # hydro_type 정규화 및 검증
    if hydro_type:
        normalized_type = validate_hydro_type(hydro_type)
        if not normalized_type:
            return [TextContent(text=f"오류: 지원하지 않는 hydro_type입니다. 지원 유형: {', '.join(HYDRO_TYPES.keys())}")]
        hydro_type = normalized_type

    # 페이지네이션 검증
    if page < 1:
        return [TextContent(text="오류: page는 1 이상이어야 합니다.")]
    if not 1 <= per_page <= 100:
        return [TextContent(text="오류: per_page는 1에서 100 사이여야 합니다.")]

    # 검색어 정규화
    query = query.strip().lower()

    # 검색 결과 수집
    results = []
    added_codes = set()  # 중복 방지

    # hydro_type이 지정된 경우 해당 유형만 검색
    search_types = [hydro_type] if hydro_type else HYDRO_TYPES.keys()
    
    for ht in search_types:
        stations = observatory_manager.info.get(ht, {})
        for code, info in stations.items():
            if code in added_codes:
                continue
                
            # 이름과 주소에서 검색어 매칭
            name_match = query in info.get("obsnm", "").lower()
            addr_match = query in info.get("obsaddr", "").lower()
            
            if name_match or addr_match:
                results.append({
                    "hydro_type": ht,
                    "code": code,
                    "name": info.get("obsnm", ""),
                    "address": info.get("obsaddr", ""),
                    "jurisdiction": info.get("obsjur", ""),
                    "latitude": info.get("lat", ""),
                    "longitude": info.get("lon", ""),
                    "match_type": "name" if name_match else "address"
                })
                added_codes.add(code)

    # 결과 정렬 (이름 매칭 우선)
    results.sort(key=lambda x: (x["match_type"] == "name", x["name"]))

    # 페이지네이션 적용
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_results = results[start_idx:end_idx]

    # 응답 구성
    response = {
        "query": query,
        "hydro_type_filter": hydro_type,
        "total_matches": len(results),
        "current_page": page,
        "per_page": per_page,
        "total_pages": (len(results) + per_page - 1) // per_page,
        "results": paginated_results
    }

    return [TextContent(text=json.dumps(response, ensure_ascii=False, indent=2))]

@mcp.tool()
async def get_batch_hydro_data(requests: List[Dict]) -> List[TextContent]:
    """여러 수문 데이터 요청을 병렬로 처리합니다.
    
    Args:
        requests (List[Dict]): 요청 목록. 각 요청은 다음 필드를 포함:
            - request_id (str): 요청 식별자
            - hydro_type (str): 수문 유형 (waterlevel, rainfall, dam, weir)
            - obs_code (str): 관측소 코드
            - start_date (str): 시작일시 (YYYYMMDD 또는 YYYY-MM-DD 형식)
            - end_date (str): 종료일시 (YYYYMMDD 또는 YYYY-MM-DD 형식)
            - time_type (str): 시간 단위 (10M: 10분, 1H: 1시간, 1D: 1일)
            - fields (List[str], optional): 조회할 필드 목록
            - page (int, optional): 페이지 번호 (1부터 시작)
            - per_page (int, optional): 페이지당 항목 수 (1-100)
    
    Returns:
        List[TextContent]: 각 요청의 처리 결과
    
    Note:
        - time_type별 최대 조회 기간:
          - 10M: 1개월
          - 1H: 1년
          - 1D: 1년
        - 긴 기간 조회 시 자동으로 기간을 분할하여 처리
    """
    await ensure_info_loaded()

    if not isinstance(requests, list) or not requests:
        return [TextContent(text="오류: 요청 목록(requests)은 비어 있지 않은 리스트여야 합니다.")]

    tasks = {}  # {request_id: task}
    request_details = {}  # {request_id: detail_dict}

    for req in requests:
        req_id = req.get("request_id")
        if not req_id:
            req_id = f"missing_id_{len(request_details)}"
            logger.warning(f"Request missing request_id, assigned temporary ID: {req_id}")
            req["request_id"] = req_id

        if req_id in request_details:
            unique_id = f"{req_id}_{len(request_details)}"
            logger.warning(f"Duplicate request_id '{req_id}', changed to '{unique_id}'")
            req_id = unique_id
            req["request_id"] = req_id

        hydro_type = req.get("hydro_type")
        obs_code = req.get("obs_code")
        start_date = req.get("start_date")
        end_date = req.get("end_date")
        time_type = req.get("time_type", "1H")
        fields = req.get("fields")
        page = req.get("page", 1)
        per_page = req.get("per_page", 100)

        detail = {
            "request_id": req_id,
            "hydro_type": hydro_type,
            "obs_code_requested": obs_code,
            "start_date_requested": start_date,
            "end_date_requested": end_date,
            "time_type": time_type,
            "page": page,
            "per_page": per_page,
            "fields": fields,
            "status": "pending",
            "result": None,
            "error": None
        }
        request_details[req_id] = detail

        # 파라미터 유효성 검증
        if not all([hydro_type, obs_code, start_date, end_date]):
            detail["status"] = "error"
            detail["error"] = "필수 파라미터 누락 (hydro_type, obs_code, start_date, end_date)"
            tasks[req_id] = asyncio.sleep(0, result={"error": detail["error"]})
            continue

        # hydro_type 정규화 및 검증
        normalized_type = validate_hydro_type(hydro_type)
        if not normalized_type:
            detail["status"] = "error"
            detail["error"] = f"지원하지 않는 hydro_type입니다: {hydro_type}"
            tasks[req_id] = asyncio.sleep(0, result={"error": detail["error"]})
            continue

        # time_type 검증
        if time_type not in ["10M", "1H", "1D"]:
            detail["status"] = "error"
            detail["error"] = "time_type은 10M, 1H, 1D 중 하나여야 합니다"
            tasks[req_id] = asyncio.sleep(0, result={"error": detail["error"]})
            continue

        # 날짜 범위 검증 및 정규화
        try:
            start, end = validate_date_range(start_date, end_date, time_type)
            start_date = _format_datetime_for_api(start, time_type)
            end_date = _format_datetime_for_api(end, time_type)
        except ValueError as e:
            detail["status"] = "error"
            detail["error"] = str(e)
            tasks[req_id] = asyncio.sleep(0, result={"error": detail["error"]})
            continue

        # API 호출 태스크 생성
        tasks[req_id] = fetch_hrfco_data(
            hydro_type=normalized_type,
            data_type="list",
            obs_code=obs_code,
            time_type=time_type,
            start_date=start_date,
            end_date=end_date,
            fields=fields,
            page=page,
            per_page=per_page
        )

    # 병렬 실행
    logger.info(f"Processing {len(tasks)} batch requests...")
    results = await asyncio.gather(*tasks.values(), return_exceptions=True)

    # 결과 처리
    for req_id, result in zip(tasks.keys(), results):
        detail = request_details[req_id]
        if isinstance(result, Exception):
            detail["status"] = "error"
            detail["error"] = str(result)
        else:
            detail["status"] = "success"
            detail["result"] = result

    # 최종 응답 구성
    response = {
        "batch_info": {
            "total_requests": len(requests),
            "successful_requests": sum(1 for d in request_details.values() if d["status"] == "success"),
            "failed_requests": sum(1 for d in request_details.values() if d["status"] == "error")
        },
        "results": {
            req_id: {
                "status": detail["status"],
                "error": detail["error"],
                "data": detail["result"]
            }
            for req_id, detail in request_details.items()
        }
    }

    return [TextContent(text=json.dumps(response, ensure_ascii=False, indent=2))]

@mcp.tool()
async def get_recent_data(
    hydro_type: str,
    obs_code: str,
    count: int = 24,
    time_type: str = "1H",
    fields: Optional[List[str]] = None
) -> List[TextContent]:
    """최근 수문 데이터 조회
    
    Args:
        hydro_type (str): 수문 유형 (waterlevel, rainfall, dam, weir)
        obs_code (str): 관측소 코드
        count (int): 조회할 데이터 개수
        time_type (str): 시간 단위 (10M: 10분, 1H: 1시간, 1D: 1일)
        fields (List[str], optional): 조회할 필드 목록
    
    Returns:
        List[TextContent]: 최근 데이터 조회 결과
    
    Note:
        - time_type별 최대 조회 기간:
          - 10M: 1개월
          - 1H: 1년
          - 1D: 1년
        - count에 따라 자동으로 적절한 기간을 계산하여 조회
    """
    await ensure_info_loaded()

    # 입력값 검증
    if not hydro_type or not obs_code:
        return [TextContent(text="오류: hydro_type과 obs_code는 필수입니다.")]

    # hydro_type 정규화 및 검증
    normalized_type = validate_hydro_type(hydro_type)
    if not normalized_type:
        return [TextContent(text=f"오류: 지원하지 않는 hydro_type입니다. 지원 유형: {', '.join(HYDRO_TYPES.keys())}")]

    # time_type 검증
    if time_type not in ["10M", "1H", "1D"]:
        return [TextContent(text="오류: time_type은 10M, 1H, 1D 중 하나여야 합니다.")]

    # count 검증
    if not isinstance(count, int) or count <= 0:
        return [TextContent(text="오류: count는 0보다 큰 정수여야 합니다.")]

    # 날짜 범위 계산
    try:
        end_dt = datetime.now()
        if time_type == "10M":
            start_dt = end_dt - timedelta(days=min(30, count // 144))  # 최대 1개월
        elif time_type == "1H":
            start_dt = end_dt - timedelta(days=min(365, count))  # 최대 1년
        else:  # 1D
            start_dt = end_dt - timedelta(days=min(365, count))  # 최대 1년

        start_date = _format_datetime_for_api(start_dt, time_type)
        end_date = _format_datetime_for_api(end_dt, time_type)
    except Exception as e:
        return [TextContent(text=f"오류: 날짜 계산 중 오류 - {str(e)}")]

    # API 호출
    try:
        result = await fetch_hrfco_data(
            hydro_type=normalized_type,
            data_type="list",
            obs_code=obs_code,
            time_type=time_type,
            start_date=start_date,
            end_date=end_date,
            fields=fields
        )
    except Exception as e:
        logger.exception(f"Error fetching recent data: {str(e)}")
        return [TextContent(text=f"오류: 데이터 조회 실패 - {str(e)}")]

    # 결과 처리
    if not isinstance(result, dict):
        return [TextContent(text=f"오류: 알 수 없는 API 응답 형식: {str(result)[:100]}")]

    content = result.get("content", [])
    if not isinstance(content, list):
        content = []

    # 최신순 정렬 및 개수 제한
    content.sort(key=lambda x: x.get("ymdhm", ""), reverse=True)
    limited_content = content[:count]

    # 응답 구성
    response = {
        "query_info": {
            "hydro_type": normalized_type,
            "obs_code": obs_code,
            "time_type": time_type,
            "requested_count": count,
            "returned_count": len(limited_content),
            "start_date": start_date,
            "end_date": end_date,
            "requested_fields": fields
        },
        "recent_data": limited_content
    }

    return [TextContent(text=json.dumps(response, ensure_ascii=False, indent=2))]


@mcp.tool()
async def analyze_regional_hydro_status(
    region_name: str,
    interest: Optional[str] = None # 예: "홍수", "가뭄" 등 (추후 활용)
) -> List[TextContent]:
    """지정된 지역의 수문 상태를 분석하고 요약 정보를 제공합니다.

    Args:
        region_name (str): 분석할 지역 이름 (예: "대전", "공주")
        interest (str, optional): 관심 주제 (예: "홍수"). 현재는 미사용.

    Returns:
        List[TextContent]: 분석 결과 요약 메시지
    """
    await ensure_info_loaded()
    logger.info(f"Analyzing regional hydro status for: {region_name}")

    # --- 1. 지역명 기반 관련 관측소 검색 ---
    relevant_stations = {} # {hydro_type: [station_info]}
    search_results_text = [] # 검색 과정 로그

    # 주요 수문 유형에 대해 관측소 검색 시도
    # TODO: 검색 로직 개선 필요 (단순 이름 매칭 -> 주소, 관할 구역 등 활용)
    for hydro_type in ["waterlevel", "rainfall", "dam", "bo"]:
        try:
            # search_observatory는 JSON 문자열을 반환하므로 파싱 필요
            search_response_content = await search_observatory(query=region_name, hydro_type=hydro_type, per_page=5) # 유형별 최대 5개 검색
            search_response_str = search_response_content[0].text
            search_result = json.loads(search_response_str)

            if search_result and search_result.get("results"):
                found_stations = search_result["results"]
                relevant_stations[hydro_type] = found_stations
                search_results_text.append(f"- {hydro_type}: {len(found_stations)}개 관측소 발견 (예: {found_stations[0]['name'] if found_stations else '없음'})")
            else:
                 search_results_text.append(f"- {hydro_type}: 관련 관측소 없음")

        except Exception as e:
            logger.error(f"Error searching for {hydro_type} stations in {region_name}: {e}")
            search_results_text.append(f"- {hydro_type}: 검색 중 오류 발생")

    if not any(relevant_stations.values()):
        return [TextContent(text=f"오류: '{region_name}' 지역과 관련된 수문 관측소를 찾을 수 없습니다.")]

    # --- 2. 주요 관측소 데이터 조회 ---
    latest_data = {} # {hydro_type: {station_code: data}}
    data_fetch_tasks = []
    station_details = {} # {station_code: station_info}

    # 수위, 강수량 위주로 최근 데이터 조회 (예시)
    for hydro_type in ["waterlevel", "rainfall"]:
        if hydro_type in relevant_stations:
            for station in relevant_stations[hydro_type]:
                station_code = station.get("code")
                if station_code:
                    station_details[station_code] = station # 상세 정보 저장
                    # get_recent_data는 JSON 문자열 반환 가정 -> 실제로는 dict 반환 가능성 있음 확인 필요
                    # 여기서는 get_recent_data가 dict를 반환한다고 가정하고 직접 호출
                    # 실제로는 get_recent_data의 반환 타입을 확인하고 필요시 파싱해야 함
                    task = asyncio.create_task(
                        get_recent_data(hydro_type=hydro_type, obs_code=station_code, count=1, time_type="1H"), # 최근 1개 데이터
                        name=f"fetch_{hydro_type}_{station_code}"
                    )
                    data_fetch_tasks.append((hydro_type, station_code, task))

    # 데이터 병렬 조회
    results = await asyncio.gather(*(task for _, _, task in data_fetch_tasks), return_exceptions=True)

    # 조회 결과 처리
    for i, result in enumerate(results):
        hydro_type, station_code, _ = data_fetch_tasks[i]
        if isinstance(result, Exception):
            logger.error(f"Error fetching recent data for {station_code} ({hydro_type}): {result}")
        elif isinstance(result, list) and result and isinstance(result[0], TextContent):
             # get_recent_data가 TextContent 리스트를 반환하는 경우 JSON 파싱
             try:
                 data_dict = json.loads(result[0].text)
                 recent_data_list = data_dict.get("recent_data", [])
                 if recent_data_list:
                     if hydro_type not in latest_data: latest_data[hydro_type] = {}
                     latest_data[hydro_type][station_code] = recent_data_list[0] # 가장 최근 데이터 저장
                 else:
                     logger.warning(f"No recent data found for {station_code} ({hydro_type})")
             except json.JSONDecodeError as e:
                 logger.error(f"Failed to parse JSON from get_recent_data for {station_code}: {e}")
             except Exception as e: # 예상치 못한 오류 처리
                 logger.error(f"Unexpected error processing result for {station_code}: {e}")
        else:
             # 예상치 못한 반환 타입 처리
             logger.warning(f"Unexpected return type from get_recent_data for {station_code}: {type(result)}")


    # --- 3. 결과 분석 및 요약 ---
    summary_lines = [f"'{region_name}' 지역 수문 상태 분석 결과:"]
    analysis_performed = False

    # 수위 분석
    if "waterlevel" in latest_data and latest_data["waterlevel"]:
        analysis_performed = True
        summary_lines.append("\n[주요 수위 관측소 현황]")
        for station_code, data in latest_data["waterlevel"].items():
            station_name = station_details.get(station_code, {}).get("name", station_code)
            current_wl = data.get("wl")
            obs_time = data.get("ymdhm", "시간 정보 없음")
            # 관측소 정보에서 임계값 가져오기 (ObservatoryManager 활용 필요)
            obs_info = observatory_manager.info.get("waterlevel", {}).get(station_code, {})
            thresholds = _get_alert_thresholds(obs_info, "waterlevel")
            status = _determine_alert_status(float(current_wl) if current_wl else None, thresholds, "waterlevel")

            status_text = f" ({status})" if status else ""
            threshold_info = f"(주의: {thresholds.get('attention', '-')}, 경고: {thresholds.get('warning', '-')})" if thresholds else ""
            summary_lines.append(f"- {station_name}: 현재 수위 {current_wl}m{status_text} ({obs_time}){threshold_info}")

    # 강수량 분석
    if "rainfall" in latest_data and latest_data["rainfall"]:
        analysis_performed = True
        summary_lines.append("\n[주요 강수량 관측소 현황]")
        for station_code, data in latest_data["rainfall"].items():
            station_name = station_details.get(station_code, {}).get("name", station_code)
            current_rf = data.get("rf")
            obs_time = data.get("ymdhm", "시간 정보 없음")
            summary_lines.append(f"- {station_name}: 최근 1시간 강수량 {current_rf}mm ({obs_time})")
            # TODO: 누적 강수량 계산 로직 추가 (get_recent_data count 늘려서)

    # TODO: 댐/보 데이터 분석 추가

    if not analysis_performed:
         summary_lines.append("\n분석할 최신 데이터가 부족합니다.")

    # 최종 요약 메시지 생성
    # TODO: 종합적인 위험도 판단 로직 추가
    flood_risk = "판단 불가" # 임시
    if analysis_performed:
        # 간단한 위험도 판단 로직 (예시)
        high_risk_found = False
        for hydro_type, stations_data in latest_data.items():
            if hydro_type == "waterlevel":
                for station_code, data in stations_data.items():
                    obs_info = observatory_manager.info.get("waterlevel", {}).get(station_code, {})
                    thresholds = _get_alert_thresholds(obs_info, "waterlevel")
                    current_wl = data.get("wl")
                    status = _determine_alert_status(float(current_wl) if current_wl else None, thresholds, "waterlevel")
                    if status in ["Alarm", "Serious"]:
                        high_risk_found = True
                        break
            # TODO: 강수량, 댐 방류량 등 다른 요인 고려
            if high_risk_found: break

        if high_risk_found: flood_risk = "높음"
        else: flood_risk = "낮음 또는 보통" # 더 세분화 필요

    summary_lines.append(f"\n종합 판단: 현재 '{region_name}' 지역의 홍수 위험도는 **{flood_risk}** 수준으로 보입니다.")
    summary_lines.append("(주의: 이 분석은 제한된 데이터 기반의 예비 평가이며, 실제 상황과 다를 수 있습니다.)")


    # 검색 과정 로그 추가 (디버깅용)
    # summary_lines.append("\n--- 검색 과정 ---")
    # summary_lines.extend(search_results_text)

    return [TextContent(text="\n".join(summary_lines))]


# --- 서버 실행 ---
if __name__ == "__main__":
    logger.info("Starting server directly (if applicable)...")
    # import uvicorn
    # uvicorn.run(mcp, host="0.0.0.0", port=8000, log_config=None) # 기본 로깅 사용
