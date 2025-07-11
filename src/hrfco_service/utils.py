# -*- coding: utf-8 -*-
"""
HRFCO Service Utility Functions
"""
import re
import sys
import logging
from datetime import datetime, date, timedelta
from typing import Optional, Union, Tuple, Dict, Any
from dateutil.relativedelta import relativedelta

from .models import HYDRO_TYPES, TIME_TYPES

logger = logging.getLogger(__name__)

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

# --- 날짜/시간 처리 함수들 ---
def _parse_relative_date(date_str: str) -> Optional[date]:
    """상대 날짜 문자열을 파싱합니다.
    
    Args:
        date_str: 상대 날짜 문자열 (예: "today", "yesterday", "3days_ago")
    
    Returns:
        파싱된 날짜 또는 None
    """
    today = date.today()
    
    if date_str == "today":
        return today
    elif date_str == "yesterday":
        return today - timedelta(days=1)
    elif date_str == "tomorrow":
        return today + timedelta(days=1)
    elif date_str.endswith("_days_ago"):
        try:
            days = int(date_str.split("_")[0])
            return today - timedelta(days=days)
        except ValueError:
            return None
    elif date_str.endswith("_days_later"):
        try:
            days = int(date_str.split("_")[0])
            return today + timedelta(days=days)
        except ValueError:
            return None
    elif date_str.endswith("_months_ago"):
        try:
            months = int(date_str.split("_")[0])
            return today - relativedelta(months=months)
        except ValueError:
            return None
    elif date_str.endswith("_months_later"):
        try:
            months = int(date_str.split("_")[0])
            return today + relativedelta(months=months)
        except ValueError:
            return None
    
    return None

def _format_datetime_for_api(date_input: Union[str, date, datetime], time_type: str) -> str:
    """API 요청용 날짜/시간 형식으로 변환합니다.
    
    Args:
        date_input: 날짜 입력 (문자열, date, datetime)
        time_type: 시간 타입 (10M, 1H, 6H, 1D)
    
    Returns:
        API 형식의 날짜/시간 문자열
    """
    if isinstance(date_input, str):
        # 상대 날짜 처리
        parsed_date = _parse_relative_date(date_input)
        if parsed_date:
            date_input = parsed_date
        else:
            # 이미 형식화된 문자열인지 확인
            if re.match(r'^\d{8}$', date_input):  # YYYYMMDD
                return date_input
            elif re.match(r'^\d{12}$', date_input):  # YYYYMMDDHHMM
                return date_input
            elif re.match(r'^\d{14}$', date_input):  # YYYYMMDDHHMMSS
                return date_input[:12]  # HHMMSS 제거
    
    if isinstance(date_input, (date, datetime)):
        if time_type in ["10M", "1H"]:
            # 시간 단위: YYYYMMDDHHMM
            return date_input.strftime("%Y%m%d%H%M")
        else:
            # 일 단위: YYYYMMDD
            return date_input.strftime("%Y%m%d")
    
    raise ValidationError(f"지원하지 않는 날짜 형식: {date_input}")

def validate_date_range(start_date: str, end_date: str, time_type: str) -> Tuple[str, str]:
    """날짜 범위를 검증하고 정규화합니다.
    
    Args:
        start_date: 시작 날짜
        end_date: 종료 날짜
        time_type: 시간 타입
    
    Returns:
        정규화된 (시작날짜, 종료날짜) 튜플
    
    Raises:
        ValidationError: 날짜 범위가 유효하지 않은 경우
    """
    try:
        start = _format_datetime_for_api(start_date, time_type)
        end = _format_datetime_for_api(end_date, time_type)
        
        if start > end:
            raise ValidationError("시작 날짜가 종료 날짜보다 늦을 수 없습니다.")
        
        return start, end
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ValidationError(f"날짜 형식 오류: {e}")

def validate_hydro_type(hydro_type: str) -> str:
    """수문 데이터 타입을 검증합니다.
    
    Args:
        hydro_type: 수문 데이터 타입
    
    Returns:
        정규화된 수문 데이터 타입
    
    Raises:
        ValidationError: 지원하지 않는 타입인 경우
    """
    if not hydro_type:
        raise ValidationError("수문 데이터 타입이 필요합니다.")
    
    hydro_type = hydro_type.lower().strip()
    
    if hydro_type not in HYDRO_TYPES:
        valid_types = ", ".join(HYDRO_TYPES.keys())
        raise ValidationError(f"지원하지 않는 수문 데이터 타입: {hydro_type}. 지원 타입: {valid_types}")
    
    return hydro_type

def validate_time_type(time_type: str) -> None:
    """시간 타입을 검증합니다.
    
    Args:
        time_type: 시간 타입
    
    Raises:
        ValidationError: 지원하지 않는 타입인 경우
    """
    if not time_type:
        raise ValidationError("시간 타입이 필요합니다.")
    
    if time_type not in TIME_TYPES:
        valid_types = ", ".join(TIME_TYPES.keys())
        raise ValidationError(f"지원하지 않는 시간 타입: {time_type}. 지원 타입: {valid_types}")

# --- 에러 처리 헬퍼 함수 ---
def handle_api_error(error: Exception, context: str) -> Dict:
    """API 관련 예외를 처리하고 사용자 친화적인 오류 메시지를 반환합니다.
    
    Args:
        error: 처리할 예외 객체
        context: 오류 발생 컨텍스트
    
    Returns:
        오류 정보를 포함한 딕셔너리
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
        logger.error(f"API Error in {context}: {str(error)} (Status: {error.status_code})")
        return {
            "error_type": "APIError",
            "message": str(error),
            "status_code": error.status_code,
            "detail": "API 호출 중 오류가 발생했습니다."
        }
    elif isinstance(error, CacheError):
        logger.error(f"Cache Error in {context}: {str(error)}")
        return {
            "error_type": "CacheError",
            "message": str(error),
            "detail": "캐시 처리 중 오류가 발생했습니다."
        }
    else:
        logger.error(f"Unexpected Error in {context}: {str(error)}")
        return {
            "error_type": "UnexpectedError",
            "message": str(error),
            "detail": "예상치 못한 오류가 발생했습니다."
        }

# --- 데이터 처리 헬퍼 함수들 ---
def _find_observatory_code(hydro_type: str, obs_identifier: str, observatory_manager) -> Optional[str]:
    """관측소 코드를 찾습니다.
    
    Args:
        hydro_type: 수문 데이터 타입
        obs_identifier: 관측소 식별자 (코드 또는 이름)
        observatory_manager: 관측소 관리자
    
    Returns:
        관측소 코드 또는 None
    """
    if not obs_identifier:
        return None
    
    return observatory_manager.get_observatory_code(hydro_type, obs_identifier)

def _get_alert_thresholds(obs_info: Dict, hydro_type: str) -> Dict[str, Optional[float]]:
    """알림 임계값을 추출합니다.
    
    Args:
        obs_info: 관측소 정보
        hydro_type: 수문 데이터 타입
    
    Returns:
        임계값 딕셔너리
    """
    if hydro_type not in HYDRO_TYPES:
        return {}
    
    config = HYDRO_TYPES[hydro_type]
    alert_keys = config.get("alert_keys", {})
    thresholds = {}
    
    for alert_type, key in alert_keys.items():
        value = obs_info.get(key)
        if value is not None:
            try:
                thresholds[alert_type] = float(value)
            except (ValueError, TypeError):
                thresholds[alert_type] = None
    
    return thresholds

def _determine_alert_status(value: Optional[float], thresholds: Dict[str, Optional[float]], hydro_type: str) -> Optional[str]:
    """알림 상태를 결정합니다.
    
    Args:
        value: 측정값
        thresholds: 임계값 딕셔너리
        hydro_type: 수문 데이터 타입
    
    Returns:
        알림 상태 또는 None
    """
    if value is None or not thresholds:
        return None
    
    # 임계값 순서: serious > alert > warning > attention
    if "serious" in thresholds and thresholds["serious"] is not None and value >= thresholds["serious"]:
        return "serious"
    elif "alert" in thresholds and thresholds["alert"] is not None and value >= thresholds["alert"]:
        return "alert"
    elif "warning" in thresholds and thresholds["warning"] is not None and value >= thresholds["warning"]:
        return "warning"
    elif "attention" in thresholds and thresholds["attention"] is not None and value >= thresholds["attention"]:
        return "attention"
    
    return "normal" 