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
    """관측소 정보를 로드합니다."""
    if not observatory_manager.needs_update():
        return
    
    logger.info("Loading observatory information...")
    
    for hydro_type in HYDRO_TYPES:
        try:
            result = await api_client.fetch_observatory_info(hydro_type)
            if isinstance(result, dict) and "content" in result:
                observatory_manager.update(hydro_type, result["content"])
            elif isinstance(result, list):
                observatory_manager.update(hydro_type, result)
    else:
                logger.warning(f"Unexpected response format for {hydro_type} observatory info")
        except Exception as e:
            logger.error(f"Failed to load observatory info for {hydro_type}: {e}")

def _prepare_data_for_response(
    data_list: List[Dict],
    hydro_type: str,
    fields: Optional[List[str]] = None,
    thresholds: Optional[Dict[str, Optional[float]]] = None
) -> List[Dict]:
    """응답용 데이터를 준비합니다."""
    if not data_list:
        return []
    
    config = HYDRO_TYPES[hydro_type]
    value_key = config["value_key"]
    default_fields = config["fields"]
    
    # 필드 필터링
    if fields is None:
        fields = default_fields
    
    processed_data = []
    for item in data_list:
        processed_item = {}
        
        # 지정된 필드만 포함
        for field in fields:
            if field in item:
                processed_item[field] = item[field]

        # 알림 상태 추가
        if thresholds and value_key in item:
            try:
                value = float(item[value_key])
                alert_status = _determine_alert_status(value, thresholds, hydro_type)
                if alert_status:
                    processed_item["alert_status"] = alert_status
            except (ValueError, TypeError):
                pass
        
        processed_data.append(processed_item)

    return processed_data

def _paginate_and_summarize_data(
    data_list: List[Dict],
    page: int = 1,
    per_page: int = 50,
    hydro_type: Optional[str] = None,
) -> Dict:
    """데이터를 페이지네이션하고 요약합니다."""
    total_count = len(data_list)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    paginated_data = data_list[start_idx:end_idx]

    # 통계 계산
    stats = {
        "total_count": total_count,
        "page": page,
        "per_page": per_page,
        "total_pages": (total_count + per_page - 1) // per_page,
        "has_next": end_idx < total_count,
        "has_prev": page > 1
    }

    if hydro_type and paginated_data:
        config = HYDRO_TYPES[hydro_type]
        value_key = config["value_key"]
        
        # 수치 데이터 통계
        numeric_values = []
        for item in paginated_data:
            if value_key in item:
                try:
                    numeric_values.append(float(item[value_key]))
                except (ValueError, TypeError):
                    pass
        
        if numeric_values:
            stats["value_stats"] = {
                "count": len(numeric_values),
                "min": min(numeric_values),
                "max": max(numeric_values),
                "avg": sum(numeric_values) / len(numeric_values)
            }

    return {
        "data": paginated_data,
        "pagination": stats
    }

# --- MCP 도구들 ---

@mcp.tool()
async def get_tools() -> List[TextContent]:
    """사용 가능한 도구 목록을 반환합니다."""
    tools_info = {
        "available_tools": [
        {
            "name": "get_tools",
                "description": "사용 가능한 도구 목록 조회"
        },
        {
            "name": "get_server_config",
                "description": "서버 설정 정보 조회"
        },
        {
            "name": "search_observatory",
                "description": "관측소 검색"
        },
        {
            "name": "get_batch_hydro_data",
                "description": "배치 수문 데이터 조회"
        },
        {
            "name": "get_recent_data",
                "description": "최근 수문 데이터 조회"
            },
            {
                "name": "analyze_regional_hydro_status",
                "description": "지역 수문 상태 분석"
        }
        ],
        "hydro_types": list(HYDRO_TYPES.keys()),
        "time_types": list(TIME_TYPES.keys()),
        "cache_stats": cache_manager.get_stats(),
        "observatory_stats": observatory_manager.get_stats()
    }

    return [TextContent(text=json.dumps(tools_info, ensure_ascii=False, indent=2))]

@mcp.tool()
async def get_server_config() -> List[TextContent]:
    """서버 설정 정보를 반환합니다."""
    config_info = {
        "api_base_url": Config.BASE_URL,
        "cache_ttl_seconds": Config.CACHE_TTL_SECONDS,
        "max_concurrent_requests": Config.MAX_CONCURRENT_REQUESTS,
        "request_timeout": Config.REQUEST_TIMEOUT,
        "observatory_update_interval": Config.OBSERVATORY_UPDATE_INTERVAL,
        "log_level": Config.LOG_LEVEL,
        "log_file": Config.LOG_FILE,
        "default_page_size": Config.DEFAULT_PAGE_SIZE,
        "max_page_size": Config.MAX_PAGE_SIZE,
        "cache_stats": cache_manager.get_stats(),
        "observatory_stats": observatory_manager.get_stats()
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

        # 검색 수행
        results = observatory_manager.search_observatories(
            query=query,
            hydro_type=hydro_type,
            limit=per_page
        )
        
        # 페이지네이션
        total_count = len(results)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_results = results[start_idx:end_idx]

    response = {
        "query": query,
            "hydro_type": hydro_type,
            "results": paginated_results,
            "pagination": {
                "page": page,
        "per_page": per_page,
                "total_count": total_count,
                "total_pages": (total_count + per_page - 1) // per_page,
                "has_next": end_idx < total_count,
                "has_prev": page > 1
            }
    }

    return [TextContent(text=json.dumps(response, ensure_ascii=False, indent=2))]
        
    except Exception as e:
        error_info = handle_api_error(e, "searching observatory")
        return [TextContent(text=json.dumps(error_info, ensure_ascii=False, indent=2))]

@mcp.tool()
async def get_batch_hydro_data(requests: List[Dict]) -> List[TextContent]:
    """배치로 수문 데이터를 조회합니다.
    
    Args:
        requests: 요청 리스트 (각 요청은 hydro_type, obs_code, start_date, end_date, time_type 포함)
    """
    try:
        results = []
        
        for i, request in enumerate(requests):
            try:
                # 필수 파라미터 검증
                hydro_type = request.get("hydro_type")
                obs_code = request.get("obs_code")
                
                if not hydro_type or not obs_code:
                    results.append({
                        "index": i,
                        "error": "hydro_type과 obs_code는 필수입니다."
                    })
                    continue # Added continue here

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
             except json.JSONDecodeError as e:
                 logger.error(f"Failed to parse JSON from get_recent_data for {station_code}: {e}")

        # 결과 분석 및 요약
    summary_lines = [f"'{region_name}' 지역 수문 상태 분석 결과:"]
    analysis_performed = False

    # 수위 분석
    if "waterlevel" in latest_data and latest_data["waterlevel"]:
        analysis_performed = True
        summary_lines.append("\n[주요 수위 관측소 현황]")
        for station_code, data in latest_data["waterlevel"].items():
                station_name = station_details.get(station_code, {}).get("obsnm", station_code)
            current_wl = data.get("wl")
            obs_time = data.get("ymdhm", "시간 정보 없음")
                alert_status = data.get("alert_status", "")

                status_text = f" ({alert_status})" if alert_status else ""
                summary_lines.append(f"- {station_name}: 현재 수위 {current_wl}m{status_text} ({obs_time})")

    # 강수량 분석
    if "rainfall" in latest_data and latest_data["rainfall"]:
        analysis_performed = True
        summary_lines.append("\n[주요 강수량 관측소 현황]")
        for station_code, data in latest_data["rainfall"].items():
                station_name = station_details.get(station_code, {}).get("obsnm", station_code)
            current_rf = data.get("rf")
            obs_time = data.get("ymdhm", "시간 정보 없음")
            summary_lines.append(f"- {station_name}: 최근 1시간 강수량 {current_rf}mm ({obs_time})")

    if not analysis_performed:
         summary_lines.append("\n분석할 최신 데이터가 부족합니다.")

        # 종합 판단
        flood_risk = "판단 불가"
    if analysis_performed:
        high_risk_found = False
        for hydro_type, stations_data in latest_data.items():
            if hydro_type == "waterlevel":
                for station_code, data in stations_data.items():
                        alert_status = data.get("alert_status", "")
                        if alert_status in ["alert", "serious"]:
                        high_risk_found = True
                        break
                        if high_risk_found:
                            break

            flood_risk = "높음" if high_risk_found else "낮음 또는 보통"

    summary_lines.append(f"\n종합 판단: 현재 '{region_name}' 지역의 홍수 위험도는 **{flood_risk}** 수준으로 보입니다.")
    summary_lines.append("(주의: 이 분석은 제한된 데이터 기반의 예비 평가이며, 실제 상황과 다를 수 있습니다.)")

    return [TextContent(text="\n".join(summary_lines))]

    except Exception as e:
        error_info = handle_api_error(e, "analyzing regional hydro status")
        return [TextContent(text=json.dumps(error_info, ensure_ascii=False, indent=2))]

def create_server():
    """서버 인스턴스를 생성합니다."""
    return mcp
