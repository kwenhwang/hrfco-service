# -*- coding: utf-8 -*-
"""
HRFCO Service API Client Module
"""
import asyncio
import httpx
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from .config import Config
from .cache import CacheManager
from .utils import APIError, ValidationError, handle_api_error
from .models import HYDRO_TYPES

logger = logging.getLogger(__name__)

async def fetch_observatory_info(hydro_type: str, document_type: str = "json"):
    """
    관측소 제원 정보 조회 (수위/댐/강수량)
    hydro_type: waterlevel, dam, rainfall 등
    document_type: json 또는 xml
    """
    # API 키가 없으면 데모 데이터 반환
    if not Config.API_KEY or Config.API_KEY == "your-api-key-here":
        return {
            "message": "API 키가 설정되지 않았습니다. 실제 데이터를 조회하려면 API 키를 설정해주세요.",
            "hydro_type": hydro_type,
            "demo_mode": True,
            "note": "이것은 데모 모드입니다. 실제 데이터를 보려면 HRFCO_API_KEY 환경변수를 설정하세요."
        }
    
    url = f"{Config.BASE_URL}/{Config.API_KEY}/{hydro_type}/info.{document_type}"
    logger.info(f"Fetching observatory info: {url}")
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json() if document_type == "json" else resp.text

async def fetch_observatory_data(
    hydro_type: str,
    time_type: str = "10M",
    obs_code: Optional[str] = None,
    sdt: Optional[str] = None,
    edt: Optional[str] = None,
    document_type: str = "json"
):
    """
    수위/댐/강수량 실시간 자료 조회 (레퍼런스 기반)
    hydro_type: waterlevel, dam, rainfall 등
    time_type: 10M, 1H, 1D
    obs_code: 관측소 코드 (없으면 전체)
    sdt, edt: 시작/종료 시간 (옵션)
    document_type: json 또는 xml
    """
    # API 키가 없으면 안내 메시지 반환
    if not Config.API_KEY or Config.API_KEY == "your-api-key-here":
        return {
            "message": "API 키가 설정되지 않았습니다. 실제 데이터를 조회하려면 API 키를 설정해주세요.",
            "hydro_type": hydro_type,
            "time_type": time_type,
            "obs_code": obs_code,
            "demo_mode": True,
            "note": "이것은 데모 모드입니다. 실제 데이터를 보려면 HRFCO_API_KEY 환경변수를 설정하세요."
        }
    
    # 기본 URL 구성
    url = f"{Config.BASE_URL}/{Config.API_KEY}/{hydro_type}/list/{time_type}"
    
    # 관측소 코드 추가
    if obs_code:
        url += f"/{obs_code}"
    
    # 날짜 범위 추가
    if sdt and edt:
        url += f"/{sdt}/{edt}"
    
    url += f".{document_type}"
    logger.info(f"Fetching observatory data: {url}")
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json() if document_type == "json" else resp.text

class HRFCOAPIClient:
    """HRFCO API 클라이언트"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.semaphore = asyncio.Semaphore(Config.MAX_CONCURRENT_REQUESTS)
        self.timeout = Config.REQUEST_TIMEOUT
        
        # 설정 검증 (API 키가 없어도 기본 동작)
        try:
            Config.validate()
        except Exception as e:
            logger.warning(f"설정 검증 경고: {e}")
    
    async def _fetch_with_cache(self, url: str) -> Dict:
        """캐시를 사용하여 API 요청을 수행합니다."""
        try:
            # 캐시에서 먼저 확인
            cached_data = await self.cache_manager.get(url)
            if cached_data:
                logger.debug(f"Cache hit for URL: {url}")
                return cached_data
            
            # API 요청 수행
            async with self.semaphore:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    logger.info(f"Making API request: {url}")
                    response = await client.get(url)
                    response.raise_for_status()
                    data = response.json()
                    
                    # 캐시에 저장
                    await self.cache_manager.set(url, data)
                    return data
                    
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error for URL {url}: {e.response.status_code}")
            raise APIError(f"HTTP {e.response.status_code}: {e.response.text}", status_code=e.response.status_code)
        except httpx.RequestError as e:
            logger.error(f"Request error for URL {url}: {e}")
            raise APIError(f"Request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error for URL {url}: {e}")
            raise APIError(f"Unexpected error: {str(e)}")

    def _calculate_date_range(self, time_type: str, hours: int = 48) -> tuple[str, str]:
        """시간 단위에 따른 날짜 범위를 계산합니다."""
        now = datetime.now()
        
        # 시간 단위에 따른 시작 시간 계산
        if time_type == "10M":
            # 10분 단위: 최근 N시간
            start_time = now - timedelta(hours=hours)
        elif time_type == "1H":
            # 1시간 단위: 최근 N시간
            start_time = now - timedelta(hours=hours)
        elif time_type == "1D":
            # 1일 단위: 최근 N일
            start_time = now - timedelta(days=hours//24)
        else:
            # 기본값: 최근 48시간
            start_time = now - timedelta(hours=48)
        
        # 날짜 형식 변환 (YYYYMMDDHHmm)
        start_str = start_time.strftime("%Y%m%d%H%M")
        end_str = now.strftime("%Y%m%d%H%M")
        
        return start_str, end_str

    async def fetch_data(
        self,
        hydro_type: str,
        data_type: str = "data",
        obs_code: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        time_type: str = "1H",
        fields: Optional[List[str]] = None,
        hours: int = 48
    ) -> Dict:
        """HRFCO API를 호출하여 데이터를 가져옵니다.
        
        Args:
            hydro_type: 하천 유형 (예: waterlevel, rainfall 등)
            data_type: 데이터 유형 (data 또는 info)
            obs_code: 관측소 코드
            start_date: 시작 날짜 (YYYYMMDDHHmm 형식)
            end_date: 종료 날짜 (YYYYMMDDHHmm 형식)
            time_type: 시간 단위 (1H, 1D, 10M)
            fields: 반환할 필드 목록
            hours: 조회할 시간 범위 (시간 단위)
            
        Returns:
            API 응답 데이터
        """
        try:
            # 하천 유형 검증
            if hydro_type not in HYDRO_TYPES:
                raise ValidationError(f"지원되지 않는 하천 유형입니다: {hydro_type}")
            
            # API 키가 없으면 데모 데이터 반환
            if not Config.API_KEY or Config.API_KEY == "your-api-key-here":
                return {
                    "message": "API 키가 설정되지 않았습니다. 실제 데이터를 조회하려면 API 키를 설정해주세요.",
                    "hydro_type": hydro_type,
                    "time_type": time_type,
                    "obs_code": obs_code,
                    "demo_mode": True,
                    "note": "이것은 데모 모드입니다. 실제 데이터를 보려면 HRFCO_API_KEY 환경변수를 설정하세요."
                }
            
            # 날짜 범위가 지정되지 않은 경우 자동 계산
            if not start_date or not end_date:
                start_date, end_date = self._calculate_date_range(time_type, hours)
                logger.info(f"Auto-calculated date range: {start_date} to {end_date}")
            
            # API URL 구성
            url_parts = [Config.BASE_URL, hydro_type, data_type]
            if data_type == "data" and obs_code:
                url_parts.append(obs_code)
            
            # 기본 URL 생성
            url = "/".join(url_parts)
            
            # 파라미터 구성
            params = {
                "API_KEY": Config.API_KEY,
                "hydro_type": hydro_type,
                "time_type": time_type,
                "start_date": start_date,
                "end_date": end_date
            }
            
            # URL에 파라미터 추가
            query_string = "&".join(f"{k}={v}" for k, v in params.items())
            url = f"{url}?{query_string}"
            
            # API 호출
            return await self._fetch_with_cache(url)
            
        except Exception as e:
            error_info = handle_api_error(e, f"fetching {hydro_type} data")
            raise APIError(error_info["message"], response=error_info) from e
    
    async def fetch_observatory_info(self, hydro_type: str) -> Dict:
        """관측소 정보를 가져옵니다.
        
        Args:
            hydro_type: 하천 유형
            
        Returns:
            관측소 정보 데이터
        """
        return await self.fetch_data(hydro_type, "info")
    
    async def fetch_observatory_data(
        self,
        hydro_type: str,
        obs_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        time_type: str = "1H",
        hours: int = 48
    ) -> Dict:
        """특정 관측소의 데이터를 가져옵니다.
        
        Args:
            hydro_type: 하천 유형
            obs_code: 관측소 코드
            start_date: 시작 날짜
            end_date: 종료 날짜
            time_type: 시간 단위
            hours: 조회할 시간 범위 (시간 단위)
            
        Returns:
            관측소 데이터
        """
        return await self.fetch_data(
            hydro_type=hydro_type,
            data_type="data",
            obs_code=obs_code,
            start_date=start_date,
            end_date=end_date,
            time_type=time_type,
            hours=hours
        ) 