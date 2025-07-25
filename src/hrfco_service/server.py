# -*- coding: utf-8 -*-
"""
HRFCO Service Main Server Module
"""
import sys
import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from fastmcp import FastMCP
from mcp.types import TextContent

from .config import Config
from .cache import CacheManager
from .api import HRFCOAPIClient
from .observatory import ObservatoryManager
from .utils import (
    validate_hydro_type, validate_time_type, validate_date_range,
    _format_datetime_for_api, _get_alert_thresholds, _determine_alert_status,
    handle_api_error, APIError, ValidationError
)
from .models import HYDRO_TYPES, TIME_TYPES

# --- 기본 설정 ---
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"

# --- 로깅 설정 ---
logging.basicConfig(**Config.get_logging_config())
logger = logging.getLogger("hrfco-server")
http_logger = logging.getLogger("httpx")
http_logger.setLevel(logging.WARNING)

# --- FastMCP 초기화 ---
mcp = FastMCP("hrfco-server")

# --- 전역 변수 및 매니저 초기화 ---
cache_manager = CacheManager()
api_client = HRFCOAPIClient(cache_manager)
observatory_manager = ObservatoryManager()

async def ensure_info_loaded():
    """관측소 정보가 로드되지 않았으면 로드"""
    if not observatory_manager.info:
        logger.warning("관측소 정보가 로드되지 않았습니다. 지금 로드합니다...")
        await load_observatory_info()
        if not observatory_manager.info:
            logger.error("관측소 정보 지연 로드 실패. 일부 도구가 작동하지 않을 수 있습니다.")

async def load_observatory_info() -> None:
    """모든 수문 데이터 타입의 관측소 정보를 로드합니다."""
    try:
        for hydro_type in HYDRO_TYPES.keys():
            logger.info(f"Loading observatory info for {hydro_type}...")
            data = await api_client.fetch_observatory_info(hydro_type)
            
            if data.get("content"):
                observatory_manager.update(hydro_type, data["content"])
                logger.info(f"Loaded {len(data['content'])} stations for {hydro_type}")
            else:
                logger.warning(f"No content found for {hydro_type}")
                
    except Exception as e:
        logger.error(f"Error loading observatory info: {e}")

def _prepare_data_for_response(
    data_list: List[Dict],
    hydro_type: str,
    fields: Optional[List[str]] = None,
    thresholds: Optional[Dict[str, Optional[float]]] = None
) -> List[Dict]:
    """응답용 데이터를 준비합니다."""
    if not data_list:
        return []
    
    # 기본 필드 설정
    if fields is None:
        config = HYDRO_TYPES.get(hydro_type, {})
        fields = config.get("fields", ["ymdhm", "value"])
    
    processed_data = []
    for item in data_list:
        processed_item = {}
        
        # 요청된 필드들 처리
        for field in fields:
            if field in item:
                processed_item[field] = item[field]
        
        # 임계값 및 경고 상태 추가
        if thresholds and "value" in processed_item:
            value = processed_item["value"]
            if value is not None:
                alert_status = _determine_alert_status(value, thresholds, hydro_type)
                if alert_status:
                    processed_item["alert_status"] = alert_status
        
        processed_data.append(processed_item)
    
    return processed_data

def _paginate_and_summarize_data(
    data_list: List[Dict],
    page: int = 1,
    per_page: int = 50,
    hydro_type: Optional[str] = None,
) -> Dict:
    """데이터를 페이지네이션하고 요약합니다."""
    if not data_list:
        return {
            "total_count": 0,
            "page": page,
            "per_page": per_page,
            "total_pages": 0,
            "data": [],
            "summary": {}
        }
    
    total_count = len(data_list)
    total_pages = (total_count + per_page - 1) // per_page
    
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    page_data = data_list[start_idx:end_idx]
    
    # 요약 정보 계산
    summary = {}
    if hydro_type == "waterlevel":
        values = [item.get("wl", 0) for item in data_list if item.get("wl") is not None]
        if values:
            summary = {
                "max_water_level": max(values),
                "min_water_level": min(values),
                "avg_water_level": sum(values) / len(values),
                "current_water_level": data_list[0].get("wl") if data_list else None
            }
    elif hydro_type == "rainfall":
        values = [item.get("rf", 0) for item in data_list if item.get("rf") is not None]
        if values:
            summary = {
                "total_rainfall": sum(values),
                "max_hourly_rainfall": max(values),
                "avg_hourly_rainfall": sum(values) / len(values),
                "rainfall_hours": len([v for v in values if v > 0])
            }
    
    return {
        "total_count": total_count,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "data": page_data,
        "summary": summary
    }

def _analyze_water_level_trends(data: List[Dict], thresholds: Dict) -> Dict:
    """수위 데이터의 추세와 위험 수위 분석을 수행합니다."""
    if not data:
        return {}
    
    # 데이터 정렬 (시간순)
    sorted_data = sorted(data, key=lambda x: x.get("ymdhm", ""))
    
    # 현재 수위 (최신 데이터)
    current_wl = float(sorted_data[-1].get("wl", 0)) if sorted_data else 0
    
    # 통계 계산
    wl_values = [float(item.get("wl", 0)) for item in sorted_data if item.get("wl")]
    
    if not wl_values:
        return {}
    
    # 시간 범위 계산
    if len(sorted_data) >= 2:
        start_time = sorted_data[0].get("ymdhm", "")
        end_time = sorted_data[-1].get("ymdhm", "")
        
        # YYYYMMDDHHmm 형식에서 시간 차이 계산
        try:
            start_dt = datetime.strptime(start_time, "%Y%m%d%H%M")
            end_dt = datetime.strptime(end_time, "%Y%m%d%H%M")
            time_span_hours = (end_dt - start_dt).total_seconds() / 3600
            time_span_days = time_span_hours / 24
        except:
            time_span_hours = len(sorted_data)  # 시간 단위로 추정
            time_span_days = time_span_hours / 24
    else:
        time_span_hours = 1
        time_span_days = 1/24
    
    # 통계 정보
    stats = {
        "max_water_level": max(wl_values),
        "min_water_level": min(wl_values),
        "avg_water_level": sum(wl_values) / len(wl_values),
        "current_water_level": current_wl,
        "data_points": len(wl_values),
        "analysis_period": {
            "start_time": sorted_data[0].get("ymdhm", "") if sorted_data else "",
            "end_time": sorted_data[-1].get("ymdhm", "") if sorted_data else "",
            "hours": round(time_span_hours, 1),
            "days": round(time_span_days, 2),
            "data_count": len(sorted_data)
        }
    }
    
    # 위험 수위 분석
    alert_analysis = {}
    for alert_type, threshold in thresholds.items():
        if threshold is not None:
            if current_wl >= threshold:
                alert_analysis[alert_type] = {
                    "status": "exceeded",
                    "threshold": threshold,
                    "current": current_wl,
                    "margin": current_wl - threshold
                }
            else:
                alert_analysis[alert_type] = {
                    "status": "safe",
                    "threshold": threshold,
                    "current": current_wl,
                    "margin": threshold - current_wl
                }
    
    # 추세 분석 (최근 6개 데이터 기준)
    trend_analysis = {}
    if len(sorted_data) >= 6:
        recent_data = sorted_data[-6:]
        recent_wl_values = [float(item.get("wl", 0)) for item in recent_data if item.get("wl")]
        
        if len(recent_wl_values) >= 2:
            # 변화율 계산
            wl_changes = []
            for i in range(1, len(recent_wl_values)):
                change = recent_wl_values[i] - recent_wl_values[i-1]
                wl_changes.append(change)
            
            avg_change = sum(wl_changes) / len(wl_changes) if wl_changes else 0
            max_change = max(wl_changes) if wl_changes else 0
            min_change = min(wl_changes) if wl_changes else 0
            
            # 추세 방향 결정
            if avg_change > 0.1:
                trend_direction = "상승"
            elif avg_change < -0.1:
                trend_direction = "하락"
            else:
                trend_direction = "안정"
            
            trend_analysis = {
                "direction": trend_direction,
                "avg_change_rate": round(avg_change, 3),
                "max_change_rate": round(max_change, 3),
                "min_change_rate": round(min_change, 3),
                "trend_period_hours": len(recent_data) - 1
            }
    
    return {
        "statistics": stats,
        "alert_analysis": alert_analysis,
        "trend_analysis": trend_analysis
    }

def _calculate_distance_between_stations(station1_info: Dict, station2_info: Dict) -> Optional[float]:
    """두 관측소 간의 거리를 계산합니다."""
    try:
        lat1 = float(station1_info.get("lat", 0))
        lon1 = float(station1_info.get("lon", 0))
        lat2 = float(station2_info.get("lat", 0))
        lon2 = float(station2_info.get("lon", 0))
        
        if lat1 == 0 or lon1 == 0 or lat2 == 0 or lon2 == 0:
            return None
        
        # 간단한 거리 계산 (Haversine 공식)
        from math import radians, cos, sin, asin, sqrt
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        distance = 6371 * c  # 지구 반지름 (km)
        
        return round(distance, 2)
    except (ValueError, TypeError):
        return None

@mcp.tool()
async def get_tools() -> List[TextContent]:
    """사용 가능한 도구 목록을 반환합니다."""
    tools_info = {
        "available_tools": [
            {
                "name": "get_observatory_info",
                "description": "수문 관측소 정보를 조회합니다",
                "parameters": ["hydro_type"]
            },
            {
                "name": "get_hydro_data",
                "description": "수문 데이터를 조회합니다",
                "parameters": ["hydro_type", "time_type", "obs_code", "start_date", "end_date"]
            },
            {
                "name": "search_observatory",
                "description": "관측소를 검색합니다",
                "parameters": ["query", "hydro_type", "page", "per_page"]
            },
            {
                "name": "get_recent_data",
                "description": "최근 수문 데이터를 조회합니다",
                "parameters": ["hydro_type", "obs_code", "count", "time_type", "fields"]
            },
            {
                "name": "analyze_regional_hydro_status",
                "description": "지역 수문 상태를 분석합니다",
                "parameters": ["region_name", "interest"]
            }
        ],
        "hydro_types": list(HYDRO_TYPES.keys()),
        "time_types": list(TIME_TYPES.keys())
    }
    
    return [TextContent(text=json.dumps(tools_info, ensure_ascii=False, indent=2))]

@mcp.tool()
async def get_server_config() -> List[TextContent]:
    """서버 설정 정보를 반환합니다."""
    config_info = {
        "server_info": {
            "name": "HRFCO Service",
            "version": "1.0.0",
            "status": "running"
        },
        "api_config": {
            "base_url": api_client.BASE_URL,
            "cache_enabled": cache_manager.enabled,
            "cache_ttl": Config.CACHE_TTL_SECONDS
        },
        "available_data_types": {
            "hydro_types": list(HYDRO_TYPES.keys()),
            "time_types": list(TIME_TYPES.keys())
        }
    }
    
    return [TextContent(text=json.dumps(config_info, ensure_ascii=False, indent=2))]

@mcp.tool()
async def search_observatory(
    query: str,
    hydro_type: Optional[str] = None,
    page: int = 1,
    per_page: int = 20
) -> List[TextContent]:
    """관측소를 검색합니다.
    
    Args:
        query: 검색 쿼리
        hydro_type: 수문 데이터 타입 (선택사항)
        page: 페이지 번호
        per_page: 페이지당 결과 수
    """
    try:
        await ensure_info_loaded()
        
        # 검색 실행
        results = observatory_manager.search_observatories(
            query=query,
            hydro_type=hydro_type,
            limit=per_page * 2  # 더 많은 결과를 가져와서 필터링
        )
        
        # 페이지네이션
        summary = _paginate_and_summarize_data(
            results, page, per_page, hydro_type
        )
        
        return [TextContent(text=json.dumps(summary, ensure_ascii=False, indent=2))]
        
    except Exception as e:
        error_info = handle_api_error(e, "searching observatories")
        return [TextContent(text=json.dumps(error_info, ensure_ascii=False, indent=2))]

@mcp.tool()
async def get_batch_hydro_data(requests: List[Dict]) -> List[TextContent]:
    """여러 수문 데이터를 일괄 조회합니다.
    
    Args:
        requests: 요청 목록 (각 요청은 hydro_type, obs_code, time_type, start_date, end_date 포함)
    """
    try:
        await ensure_info_loaded()
        
        results = []
        for i, request in enumerate(requests):
            try:
                hydro_type = request.get("hydro_type")
                obs_code = request.get("obs_code")
                
                if not hydro_type or not obs_code:
                    results.append({
                        "index": i,
                        "success": False,
                        "error": "hydro_type과 obs_code는 필수입니다."
                    })
                    continue

                # 파라미터 검증
                normalized_type = validate_hydro_type(hydro_type)
                validate_time_type(request.get("time_type", "1H"))
                
                # 날짜 범위 검증
                start_date = request.get("start_date")
                end_date = request.get("end_date")
                time_type = request.get("time_type", "1H")
                
                if start_date and end_date:
                    start_date, end_date = validate_date_range(start_date, end_date, time_type)
                
                # API 호출
                data = await api_client.fetch_observatory_data(
                    hydro_type=normalized_type,
                    obs_code=obs_code,
                    start_date=start_date,
                    end_date=end_date,
                    time_type=time_type
                )
                
                results.append({
                    "index": i,
                    "success": True,
                    "data": data
                })
                
            except Exception as e:
                error_info = handle_api_error(e, f"batch request {i}")
                results.append({
                    "index": i,
                    "success": False,
                    "error": error_info
                })
        
        return [TextContent(text=json.dumps(results, ensure_ascii=False, indent=2))]
        
    except Exception as e:
        error_info = handle_api_error(e, "batch hydro data request")
        return [TextContent(text=json.dumps(error_info, ensure_ascii=False, indent=2))]

@mcp.tool()
async def get_recent_data(
    hydro_type: str,
    obs_code: str,
    count: int = 24,
    time_type: str = "1H",
    fields: Optional[List[str]] = None
) -> List[TextContent]:
    """최근 수문 데이터를 조회합니다.
    
    Args:
        hydro_type: 수문 데이터 타입
        obs_code: 관측소 코드
        count: 조회할 데이터 개수
        time_type: 시간 단위
        fields: 반환할 필드 목록
    """
    try:
        await ensure_info_loaded()

        # 파라미터 검증
        normalized_type = validate_hydro_type(hydro_type)
        validate_time_type(time_type)
        
        # 관측소 코드 확인
        actual_obs_code = observatory_manager.get_observatory_code(normalized_type, obs_code)
        if not actual_obs_code:
            return [TextContent(text=f"오류: 관측소를 찾을 수 없습니다: {obs_code}")]

        # 관측소 정보 가져오기
        obs_info = observatory_manager.get_observatory_info(normalized_type, actual_obs_code)
        thresholds = _get_alert_thresholds(obs_info or {}, normalized_type) if obs_info else {}
        
        # 최근 데이터 조회
        data = await api_client.fetch_observatory_data(
            hydro_type=normalized_type,
            obs_code=actual_obs_code,
            time_type=time_type
        )
        
        if not isinstance(data, dict) or "content" not in data:
            return [TextContent(text="오류: API 응답 형식이 올바르지 않습니다.")]

        content = data.get("content", [])
        if not isinstance(content, list):
            content = []

        # 최신순 정렬 및 개수 제한
        content.sort(key=lambda x: x.get("ymdhm", ""), reverse=True)
        limited_content = content[:count]

        # 데이터 처리
        processed_data = _prepare_data_for_response(
            limited_content, normalized_type, fields, thresholds
        )
        
        response = {
            "query_info": {
                "hydro_type": normalized_type,
                "obs_code": actual_obs_code,
                "time_type": time_type,
                "requested_count": count,
                "returned_count": len(processed_data),
                "requested_fields": fields
            },
            "recent_data": processed_data
        }

        return [TextContent(text=json.dumps(response, ensure_ascii=False, indent=2))]

    except Exception as e:
        error_info = handle_api_error(e, "fetching recent data")
        return [TextContent(text=json.dumps(error_info, ensure_ascii=False, indent=2))]

@mcp.tool()
async def analyze_regional_hydro_status(
    region_name: str,
    interest: Optional[str] = None
) -> List[TextContent]:
    """지정된 지역의 수문 상태를 분석합니다.

    Args:
        region_name: 분석할 지역 이름
        interest: 관심 주제 (선택사항)
    """
    try:
        await ensure_info_loaded()
        
        # 지역 관련 관측소 검색
        relevant_stations = {}
        search_results_text = []
        
        for hydro_type in ["waterlevel", "rainfall", "dam", "bo"]:
            try:
                search_response = await search_observatory(
                    query=region_name, 
                    hydro_type=hydro_type, 
                    per_page=5
                )
                search_result = json.loads(search_response[0].text)

                if search_result and search_result.get("results"):
                    found_stations = search_result["results"]
                    relevant_stations[hydro_type] = found_stations
                    search_results_text.append(
                        f"- {hydro_type}: {len(found_stations)}개 관측소 발견"
                    )
                else:
                    search_results_text.append(f"- {hydro_type}: 관련 관측소 없음")

            except Exception as e:
                logger.error(f"Error searching for {hydro_type} stations in {region_name}: {e}")
                search_results_text.append(f"- {hydro_type}: 검색 중 오류 발생")

        if not any(relevant_stations.values()):
            return [TextContent(text=f"오류: '{region_name}' 지역과 관련된 수문 관측소를 찾을 수 없습니다.")]

        # 주요 관측소 데이터 조회
        latest_data = {}
        data_fetch_tasks = []
        station_details = {}

        for hydro_type in ["waterlevel", "rainfall"]:
            if hydro_type in relevant_stations:
                for station in relevant_stations[hydro_type]:
                    station_code = station.get("obs_code")
                    if station_code:
                        station_details[station_code] = station
                        task = asyncio.create_task(
                            get_recent_data(
                                hydro_type=hydro_type, 
                                obs_code=station_code, 
                                count=1, 
                                time_type="1H"
                            ),
                            name=f"fetch_{hydro_type}_{station_code}"
                        )
                        data_fetch_tasks.append((hydro_type, station_code, task))

        # 데이터 병렬 조회
        results = await asyncio.gather(*[task for _, _, task in data_fetch_tasks], return_exceptions=True)

        # 조회 결과 처리
        for i, result in enumerate(results):
            hydro_type, station_code, _ = data_fetch_tasks[i]
            if isinstance(result, Exception):
                logger.error(f"Error fetching recent data for {station_code} ({hydro_type}): {result}")
            elif isinstance(result, list) and result and isinstance(result[0], TextContent):
                try:
                    data_dict = json.loads(result[0].text)
                    recent_data_list = data_dict.get("recent_data", [])
                    if recent_data_list:
                        if hydro_type not in latest_data:
                            latest_data[hydro_type] = {}
                        latest_data[hydro_type][station_code] = recent_data_list[0]
                except Exception as e:
                    logger.error(f"Error parsing data for {station_code}: {e}")

        # 분석 결과 구성
        analysis_result = {
            "region_name": region_name,
            "interest": interest,
            "search_summary": search_results_text,
            "station_count": {k: len(v) for k, v in relevant_stations.items()},
            "latest_data": latest_data,
            "station_details": station_details
        }

        return [TextContent(text=json.dumps(analysis_result, ensure_ascii=False, indent=2))]

    except Exception as e:
        error_info = handle_api_error(e, "analyzing regional hydro status")
        return [TextContent(text=json.dumps(error_info, ensure_ascii=False, indent=2))]

@mcp.tool()
async def analyze_water_level_with_thresholds(
    obs_code: str,
    time_type: str = "1H",
    count: int = 24,  # 기본값을 24로 줄임
    hours: int = 48,  # 기본값을 48로 줄임
    detailed: bool = False  # 상세 분석 여부
) -> List[TextContent]:
    """수위 관측소의 데이터를 위험 수위 기준과 함께 분석합니다.
    
    Args:
        obs_code: 수위 관측소 코드
        time_type: 시간 단위
        count: 조회할 데이터 개수 (기본값: 24)
        hours: 조회할 시간 범위 (시간 단위, 기본값: 48)
        detailed: 상세 분석 여부 (기본값: False)
    """
    try:
        await ensure_info_loaded()

        # 파라미터 검증
        validate_time_type(time_type)
        
        # 상세 분석 요청 시 더 많은 데이터 조회
        if detailed:
            count = max(count, 72)  # 최소 72개
            hours = max(hours, 168)  # 최소 7일
        
        # 관측소 코드 확인
        actual_obs_code = observatory_manager.get_observatory_code("waterlevel", obs_code)
        if not actual_obs_code:
            return [TextContent(text=f"오류: 수위 관측소를 찾을 수 없습니다: {obs_code}")]

        # 관측소 정보 가져오기
        obs_info = observatory_manager.get_observatory_info("waterlevel", actual_obs_code)
        thresholds = _get_alert_thresholds(obs_info or {}, "waterlevel") if obs_info else {}
        
        # 수위 데이터 조회
        data = await api_client.fetch_observatory_data(
            hydro_type="waterlevel",
            obs_code=actual_obs_code,
            time_type=time_type,
            hours=hours
        )
        
        if not isinstance(data, dict) or "content" not in data:
            return [TextContent(text="오류: API 응답 형식이 올바르지 않습니다.")]

        content = data.get("content", [])
        if not isinstance(content, list):
            content = []

        # 최신순 정렬 및 개수 제한
        content.sort(key=lambda x: x.get("ymdhm", ""), reverse=True)
        limited_content = content[:count]

        # 위험 수위 분석
        alert_analysis = _analyze_water_level_trends(limited_content, thresholds)
        
        # 응답 구성 (상세 분석 여부에 따라 다르게)
        response = {
            "observatory_info": {
                "obs_code": actual_obs_code,
                "obs_name": obs_info.get("obsnm") if obs_info else "Unknown",
                "location": {
                    "lat": obs_info.get("lat") if obs_info else None,
                    "lon": obs_info.get("lon") if obs_info else None
                } if obs_info else None
            },
            "thresholds": thresholds,
            "alert_analysis": alert_analysis,
            "summary": {
                "total_records": len(limited_content),
                "total_available": len(content),
                "time_range": {
                    "start": limited_content[-1].get("ymdhm") if limited_content else None,
                    "end": limited_content[0].get("ymdhm") if limited_content else None
                },
                "hours_requested": hours,
                "data_count_requested": count,
                "detailed_analysis": detailed
            }
        }
        
        # 상세 분석이 아닌 경우 최근 데이터만 포함
        if not detailed:
            response["recent_data"] = limited_content[:5]  # 최근 5개만
        else:
            response["recent_data"] = limited_content[:10]  # 최근 10개
            # 통계 정보 추가
            if "statistics" in alert_analysis:
                response["statistics"] = alert_analysis["statistics"]

        return [TextContent(text=json.dumps(response, ensure_ascii=False, indent=2))]

    except Exception as e:
        error_info = handle_api_error(e, "analyzing water level with thresholds")
        return [TextContent(text=json.dumps(error_info, ensure_ascii=False, indent=2))]

@mcp.tool()
async def get_comprehensive_hydro_analysis(
    water_level_obs: str,
    rainfall_obs: Optional[str] = None,
    time_type: str = "1H",
    count: int = 24,  # 기본값을 24로 줄임
    hours: int = 48,  # 기본값을 48로 줄임
    detailed: bool = False  # 상세 분석 여부
) -> List[TextContent]:
    """수위와 강우량 데이터를 종합적으로 분석합니다.
    
    Args:
        water_level_obs: 수위 관측소 코드
        rainfall_obs: 강우량 관측소 코드 (선택사항)
        time_type: 시간 단위
        count: 조회할 데이터 개수 (기본값: 24)
        hours: 조회할 시간 범위 (시간 단위, 기본값: 48)
        detailed: 상세 분석 여부 (기본값: False)
    """
    try:
        await ensure_info_loaded()

        # 파라미터 검증
        validate_time_type(time_type)
        
        # 상세 분석 요청 시 더 많은 데이터 조회
        if detailed:
            count = max(count, 72)  # 최소 72개
            hours = max(hours, 168)  # 최소 7일
        
        # 수위 관측소 확인
        wl_obs_code = observatory_manager.get_observatory_code("waterlevel", water_level_obs)
        if not wl_obs_code:
            return [TextContent(text=f"오류: 수위 관측소를 찾을 수 없습니다: {water_level_obs}")]

        # 수위 관측소 정보
        wl_obs_info = observatory_manager.get_observatory_info("waterlevel", wl_obs_code)
        wl_thresholds = _get_alert_thresholds(wl_obs_info or {}, "waterlevel") if wl_obs_info else {}
        
        # 수위 데이터 조회
        wl_data = await api_client.fetch_observatory_data(
            hydro_type="waterlevel",
            obs_code=wl_obs_code,
            time_type=time_type,
            hours=hours
        )
        
        if not isinstance(wl_data, dict) or "content" not in wl_data:
            return [TextContent(text="오류: 수위 데이터 API 응답 형식이 올바르지 않습니다.")]

        wl_content = wl_data.get("content", [])
        if not isinstance(wl_content, list):
            wl_content = []

        # 강우량 데이터 처리
        rf_content = []
        rf_obs_info = None
        distance_info = None
        
        if rainfall_obs:
            rf_obs_code = observatory_manager.get_observatory_code("rainfall", rainfall_obs)
            if rf_obs_code:
                rf_obs_info = observatory_manager.get_observatory_info("rainfall", rf_obs_code)
                
                # 거리 계산
                if wl_obs_info and rf_obs_info:
                    distance = _calculate_distance_between_stations(wl_obs_info, rf_obs_info)
                    if distance:
                        distance_info = {
                            "distance_km": distance,
                            "proximity": "매우 근접" if distance < 1 else "근접" if distance < 5 else "보통" if distance < 10 else "원거리"
                        }
                
                # 강우량 데이터 조회
                rf_data = await api_client.fetch_observatory_data(
                    hydro_type="rainfall",
                    obs_code=rf_obs_code,
                    time_type=time_type,
                    hours=hours
                )
                
                if isinstance(rf_data, dict) and "content" in rf_data:
                    rf_content = rf_data.get("content", [])
                    if not isinstance(rf_content, list):
                        rf_content = []

        # 데이터 정렬 및 제한
        wl_content.sort(key=lambda x: x.get("ymdhm", ""), reverse=True)
        rf_content.sort(key=lambda x: x.get("ymdhm", ""), reverse=True)
        
        limited_wl = wl_content[:count]
        limited_rf = rf_content[:count] if rf_content else []

        # 위험 수위 분석
        alert_analysis = _analyze_water_level_trends(limited_wl, wl_thresholds)
        
        # 강우량-수위 상관관계 분석 (상세 분석 시에만)
        correlation_analysis = {}
        if detailed and limited_rf and limited_wl:
            # 시간별 매칭
            wl_dict = {item.get("ymdhm"): float(item.get("wl", 0)) for item in limited_wl}
            rf_dict = {item.get("ymdhm"): float(item.get("rf", 0)) for item in limited_rf}
            
            matched_data = []
            for time_key in wl_dict.keys():
                if time_key in rf_dict:
                    matched_data.append({
                        "time": time_key,
                        "water_level": wl_dict[time_key],
                        "rainfall": rf_dict[time_key]
                    })
            
            if matched_data:
                # 변화율 분석
                if len(matched_data) >= 2:
                    recent_data = matched_data[-6:]  # 최근 6개
                    wl_changes = []
                    rf_totals = []
                    
                    for i in range(1, len(recent_data)):
                        wl_change = recent_data[i-1]["water_level"] - recent_data[i]["water_level"]
                        rf_total = recent_data[i-1]["rainfall"]
                        wl_changes.append(wl_change)
                        rf_totals.append(rf_total)
                    
                    correlation_analysis = {
                        "matched_records": len(matched_data),
                        "recent_analysis": {
                            "water_level_changes": wl_changes,
                            "rainfall_totals": rf_totals,
                            "max_rainfall": max(rf_totals) if rf_totals else 0,
                            "max_wl_change": max(wl_changes) if wl_changes else 0
                        }
                    }

        # 응답 구성
        response = {
            "analysis_period": {
                "time_type": time_type,
                "data_count": len(limited_wl),
                "total_available": len(wl_content),
                "time_range": {
                    "start": limited_wl[-1].get("ymdhm") if limited_wl else None,
                    "end": limited_wl[0].get("ymdhm") if limited_wl else None
                },
                "hours_requested": hours,
                "data_count_requested": count,
                "detailed_analysis": detailed
            },
            "water_level_station": {
                "obs_code": wl_obs_code,
                "obs_name": wl_obs_info.get("obsnm") if wl_obs_info else "Unknown",
                "thresholds": wl_thresholds,
                "alert_analysis": alert_analysis
            },
            "rainfall_station": {
                "obs_code": rainfall_obs if rainfall_obs else None,
                "obs_name": rf_obs_info.get("obsnm") if rf_obs_info else None,
                "data_available": len(limited_rf) > 0,
                "total_available": len(rf_content) if rf_content else 0
            },
            "station_distance": distance_info,
            "recent_data": {
                "water_level": limited_wl[:5] if not detailed else limited_wl[:10],
                "rainfall": limited_rf[:5] if not detailed else limited_rf[:10] if limited_rf else []
            }
        }
        
        # 상세 분석 시에만 상관관계 분석 포함
        if detailed:
            response["correlation_analysis"] = correlation_analysis

        return [TextContent(text=json.dumps(response, ensure_ascii=False, indent=2))]

    except Exception as e:
        error_info = handle_api_error(e, "comprehensive hydro analysis")
        return [TextContent(text=json.dumps(error_info, ensure_ascii=False, indent=2))]

@mcp.tool()
async def get_alert_status_summary(
    region_name: Optional[str] = None,
    hydro_type: str = "waterlevel"
) -> List[TextContent]:
    """지역별 또는 전체의 위험 수위 상태를 요약합니다.
    
    Args:
        region_name: 지역 이름 (선택사항)
        hydro_type: 수문 데이터 타입
    """
    try:
        await ensure_info_loaded()

        # 파라미터 검증
        normalized_type = validate_hydro_type(hydro_type)
        
        # 관측소 검색
        search_query = region_name if region_name else ""
        search_response = await search_observatory(
            query=search_query,
            hydro_type=normalized_type,
            per_page=20
        )
        
        search_result = json.loads(search_response[0].text)
        stations = search_result.get("results", [])
        
        if not stations:
            return [TextContent(text=f"오류: '{region_name or '전체'}' 지역의 {hydro_type} 관측소를 찾을 수 없습니다.")]

        # 각 관측소의 최신 데이터 조회
        alert_summary = {
            "normal": [],
            "attention": [],
            "warning": [],
            "alert": [],
            "serious": []
        }
        
        station_details = []
        
        for station in stations[:10]:  # 최대 10개 관측소만 처리
            obs_code = station.get("obs_code")
            if not obs_code:
                continue
                
            try:
                # 최신 데이터 조회
                data = await api_client.fetch_observatory_data(
                    hydro_type=normalized_type,
                    obs_code=obs_code,
                    time_type="1H"
                )
                
                if isinstance(data, dict) and "content" in data:
                    content = data.get("content", [])
                    if content:
                        latest_data = content[0]  # 최신 데이터
                        
                        # 관측소 정보
                        obs_info = observatory_manager.get_observatory_info(normalized_type, obs_code)
                        thresholds = _get_alert_thresholds(obs_info or {}, normalized_type) if obs_info else {}
                        
                        # 알림 상태 결정
                        if normalized_type == "waterlevel":
                            current_value = latest_data.get("wl")
                        elif normalized_type == "rainfall":
                            current_value = latest_data.get("rf")
                        else:
                            current_value = None
                        
                        if current_value is not None:
                            alert_status = _determine_alert_status(current_value, thresholds, normalized_type)
                            
                            station_info = {
                                "obs_code": obs_code,
                                "obs_name": station.get("obsnm", "Unknown"),
                                "current_value": current_value,
                                "alert_status": alert_status,
                                "thresholds": thresholds,
                                "last_update": latest_data.get("ymdhm")
                            }
                            
                            if alert_status in alert_summary:
                                alert_summary[alert_status].append(station_info)
                            
                            station_details.append(station_info)
                            
            except Exception as e:
                logger.error(f"Error fetching data for station {obs_code}: {e}")
                continue

        # 요약 통계
        total_stations = len(station_details)
        alert_stats = {status: len(stations) for status, stations in alert_summary.items()}
        
        response = {
            "region": region_name or "전체",
            "hydro_type": normalized_type,
            "total_stations_checked": total_stations,
            "alert_statistics": alert_stats,
            "alert_details": alert_summary,
            "station_details": station_details
        }

        return [TextContent(text=json.dumps(response, ensure_ascii=False, indent=2))]

    except Exception as e:
        error_info = handle_api_error(e, "alert status summary")
        return [TextContent(text=json.dumps(error_info, ensure_ascii=False, indent=2))]

@mcp.tool()
async def get_basin_comprehensive_analysis(
    main_obs_code: str,
    hydro_types: List[str] = ["waterlevel", "rainfall", "dam", "bo"],
    max_distance_km: float = 20.0,
    time_type: str = "1H",
    count: int = 48,
    hours: int = 72
) -> List[TextContent]:
    """같은 수계의 근접 시설들을 종합적으로 분석합니다.
    
    Args:
        main_obs_code: 메인 관측소 코드 (기준점)
        hydro_types: 분석할 수문 데이터 타입들
        max_distance_km: 최대 검색 거리 (km)
        time_type: 시간 단위
        count: 조회할 데이터 개수
        hours: 조회할 시간 범위 (시간 단위)
    """
    try:
        await ensure_info_loaded()

        # 파라미터 검증
        validate_time_type(time_type)
        
        # 메인 관측소 정보 확인
        main_obs_info = None
        main_hydro_type = None
        
        # 메인 관측소의 타입과 정보 찾기
        for hydro_type in hydro_types:
            obs_code = observatory_manager.get_observatory_code(hydro_type, main_obs_code)
            if obs_code:
                obs_info = observatory_manager.get_observatory_info(hydro_type, obs_code)
                if obs_info:
                    main_obs_info = obs_info
                    main_hydro_type = hydro_type
                    break
        
        if not main_obs_info:
            return [TextContent(text=f"오류: 메인 관측소를 찾을 수 없습니다: {main_obs_code}")]
        
        # 메인 관측소 좌표
        main_lat = float(main_obs_info.get("lat", 0))
        main_lon = float(main_obs_info.get("lon", 0))
        
        if main_lat == 0 or main_lon == 0:
            return [TextContent(text="오류: 메인 관측소의 좌표 정보가 없습니다.")]
        
        # 근접 시설들 찾기
        nearby_facilities = []
        
        for hydro_type in hydro_types:
            obs_info_data = await api_client.fetch_observatory_info(hydro_type)
            facilities = obs_info_data.get("content", [])
            
            for facility in facilities:
                try:
                    lat = float(facility.get("lat", 0))
                    lon = float(facility.get("lon", 0))
                    
                    if lat != 0 and lon != 0:
                        distance = _calculate_distance_between_stations(
                            {"lat": main_lat, "lon": main_lon},
                            {"lat": lat, "lon": lon}
                        )
                        
                        if distance and distance <= max_distance_km:
                            facility_code = facility.get(f"{hydro_type[:2]}obscd")
                            if facility_code:
                                nearby_facilities.append({
                                    "hydro_type": hydro_type,
                                    "obs_code": facility_code,
                                    "obs_name": facility.get("obsnm", "Unknown"),
                                    "distance_km": distance,
                                    "info": facility
                                })
                except (ValueError, TypeError):
                    continue
        
        # 거리순 정렬
        nearby_facilities.sort(key=lambda x: x["distance_km"])
        
        # 각 시설의 데이터 수집
        facility_data = {}
        
        for facility in nearby_facilities[:10]:  # 최대 10개만 처리
            try:
                data = await api_client.fetch_observatory_data(
                    hydro_type=facility["hydro_type"],
                    obs_code=facility["obs_code"],
                    time_type=time_type,
                    hours=hours
                )
                
                if isinstance(data, dict) and "content" in data:
                    content = data.get("content", [])
                    if isinstance(content, list):
                        # 시간순 정렬 및 개수 제한
                        content.sort(key=lambda x: x.get("ymdhm", ""), reverse=True)
                        limited_content = content[:count]
                        
                        facility_data[facility["obs_code"]] = {
                            "facility_info": facility,
                            "data": limited_content,
                            "total_available": len(content)
                        }
            except Exception as e:
                logger.warning(f"시설 데이터 조회 실패: {facility['obs_code']} - {str(e)}")
                continue
        
        # 통합 분석
        analysis_results = {
            "main_facility": {
                "hydro_type": main_hydro_type,
                "obs_code": main_obs_code,
                "obs_name": main_obs_info.get("obsnm", "Unknown"),
                "location": {"lat": main_lat, "lon": main_lon}
            },
            "search_parameters": {
                "max_distance_km": max_distance_km,
                "hydro_types": hydro_types,
                "time_type": time_type,
                "hours": hours,
                "count": count
            },
            "nearby_facilities": [],
            "basin_statistics": {
                "total_facilities_found": len(nearby_facilities),
                "facilities_with_data": len(facility_data),
                "hydro_type_distribution": {},
                "distance_distribution": {
                    "closest": min([f["distance_km"] for f in nearby_facilities]) if nearby_facilities else None,
                    "farthest": max([f["distance_km"] for f in nearby_facilities]) if nearby_facilities else None,
                    "average": sum([f["distance_km"] for f in nearby_facilities]) / len(nearby_facilities) if nearby_facilities else None
                }
            }
        }
        
        # 각 시설별 분석
        for facility in nearby_facilities[:10]:
            facility_result = {
                "hydro_type": facility["hydro_type"],
                "obs_code": facility["obs_code"],
                "obs_name": facility["obs_name"],
                "distance_km": facility["distance_km"],
                "data_available": facility["obs_code"] in facility_data
            }
            
            if facility["obs_code"] in facility_data:
                data_info = facility_data[facility["obs_code"]]
                
                # 데이터 통계 계산
                if data_info["data"]:
                    if facility["hydro_type"] == "waterlevel":
                        values = [float(item.get("wl", 0)) for item in data_info["data"] if item.get("wl")]
                    elif facility["hydro_type"] == "rainfall":
                        values = [float(item.get("rf", 0)) for item in data_info["data"] if item.get("rf")]
                    elif facility["hydro_type"] == "dam":
                        values = [float(item.get("damwl", 0)) for item in data_info["data"] if item.get("damwl")]
                    elif facility["hydro_type"] == "bo":
                        values = [float(item.get("bowl", 0)) for item in data_info["data"] if item.get("bowl")]
                    else:
                        values = []
                    
                    if values:
                        facility_result["statistics"] = {
                            "max_value": max(values),
                            "min_value": min(values),
                            "avg_value": sum(values) / len(values),
                            "current_value": values[0] if values else None,
                            "data_points": len(values),
                            "total_available": data_info["total_available"]
                        }
                        
                        # 위험 수위 분석 (수위 관측소인 경우)
                        if facility["hydro_type"] == "waterlevel":
                            thresholds = _get_alert_thresholds(facility["info"], "waterlevel")
                            if thresholds:
                                current_wl = values[0] if values else 0
                                alert_analysis = {}
                                
                                for alert_type, threshold in thresholds.items():
                                    if threshold is not None:
                                        if current_wl >= threshold:
                                            alert_analysis[alert_type] = {
                                                "status": "exceeded",
                                                "threshold": threshold,
                                                "current": current_wl,
                                                "margin": current_wl - threshold
                                            }
                                        else:
                                            alert_analysis[alert_type] = {
                                                "status": "safe",
                                                "threshold": threshold,
                                                "current": current_wl,
                                                "margin": threshold - current_wl
                                            }
                                
                                facility_result["alert_analysis"] = alert_analysis
            
            analysis_results["nearby_facilities"].append(facility_result)
        
        # 수계별 분포 통계
        hydro_type_counts = {}
        for facility in nearby_facilities:
            hydro_type = facility["hydro_type"]
            hydro_type_counts[hydro_type] = hydro_type_counts.get(hydro_type, 0) + 1
        
        analysis_results["basin_statistics"]["hydro_type_distribution"] = hydro_type_counts
        
        return [TextContent(text=json.dumps(analysis_results, ensure_ascii=False, indent=2))]

    except Exception as e:
        error_info = handle_api_error(e, "basin comprehensive analysis")
        return [TextContent(text=json.dumps(error_info, ensure_ascii=False, indent=2))]

# --- 서버 실행 ---
if __name__ == "__main__":
    mcp.run()
