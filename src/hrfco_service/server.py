from fastmcp import FastMCP
import sys
import httpx
import os
import json
import logging
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import Dict, List, Optional, Union, Any
from mcp.types import TextContent

if sys.platform == "win32":
    import os
    os.environ["PYTHONIOENCODING"] = "utf-8"

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hrfco-server")

# API 설정
API_KEY = os.getenv("HRFCO_API_KEY")
if not API_KEY:
    raise ValueError("HRFCO_API_KEY 환경 변수가 필요합니다")

BASE_URL = "https://api.hrfco.go.kr"
HYDRO_TYPES = {
    "waterlevel": {"code_key": "wlobscd", "name": "수위", "unit": "m"},
    "rainfall": {"code_key": "rfobscd", "name": "강수량", "unit": "mm"},
    "dam": {"code_key": "dmobscd", "name": "댐", "unit": "El.m"},
    "bo": {"code_key": "boobscd", "name": "보", "unit": "El.m"}
}

# MCP 서버 인스턴스 생성
mcp = FastMCP("hrfco-server")

# 관측소 정보 캐시
OBSERVATORY_INFO: Dict[str, Dict[str, Dict]] = {}
NAME_TO_CODE: Dict[str, Dict[str, str]] = {}
LOCATION_CACHE: Dict[str, List[Dict[str, Any]]] = {}
INTEGRATED_DATA: List[Dict[str, Any]] = []

async def fetch_hrfco_data(
    hydro_type: str,
    data_type: str,
    time_type: Optional[str] = None,
    obs_code: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict:
    """HRFCO API 데이터를 가져옵니다."""
    url = f"{BASE_URL}/{API_KEY}/{hydro_type}/{data_type}"
    if data_type == "list":
        if time_type not in ["10M", "1H", "1D", None]:
            raise ValueError("time_type은 10M, 1H, 1D 중 하나여야 합니다")
        if time_type:
            url += f"/{time_type}"
            if obs_code:
                url += f"/{obs_code}"
                if (start_date and not end_date) or (end_date and not start_date):
                    raise ValueError("start_date와 end_date는 함께 제공되어야 합니다")
                if start_date and end_date:
                    # 날짜 형식 변환 (YYYY-MM-DD -> YYYYMMDD)
                    if re.match(r'\d{4}-\d{2}-\d{2}', start_date):
                        start_date = start_date.replace('-', '')
                    if re.match(r'\d{4}-\d{2}-\d{2}', end_date):
                        end_date = end_date.replace('-', '')
                    url += f"/{start_date}/{end_date}"
    url += ".json"

    logger.info(f"요청 URL: {url}")
    async with httpx.AsyncClient(timeout=15.0, verify=False) as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        logger.debug(f"{hydro_type}/{data_type} 응답: {json.dumps(data, ensure_ascii=False)[:200]}...")
        return data

async def load_observatory_info():
    """관측소 제원 정보를 로드합니다."""
    global INTEGRATED_DATA
    INTEGRATED_DATA = []
    
    for hydro_type in HYDRO_TYPES.keys():
        try:
            data = await fetch_hrfco_data(hydro_type=hydro_type, data_type="info")
            content = data.get("content", [])
            # null 값 필터링
            valid_content = [item for item in content if item is not None]
            OBSERVATORY_INFO[hydro_type] = {
                item[HYDRO_TYPES[hydro_type]["code_key"]]: item 
                for item in valid_content 
                if isinstance(item, dict) and HYDRO_TYPES[hydro_type]["code_key"] in item
            }
            NAME_TO_CODE[hydro_type] = {
                item.get("obsnm"): item[HYDRO_TYPES[hydro_type]["code_key"]]
                for item in valid_content 
                if isinstance(item, dict) and "obsnm" in item and HYDRO_TYPES[hydro_type]["code_key"] in item
            }
            
            # 통합 데이터 생성
            for item in valid_content:
                if isinstance(item, dict) and "obsnm" in item and HYDRO_TYPES[hydro_type]["code_key"] in item:
                    integrated_item = {
                        "type": hydro_type,
                        "obscd": item[HYDRO_TYPES[hydro_type]["code_key"]],
                        "obsnm": item.get("obsnm", ""),
                        "agcnm": item.get("agcnm", ""),
                        "addr": item.get("addr", ""),
                        "etcaddr": item.get("etcaddr", ""),
                        "lon": item.get("lon", ""),
                        "lat": item.get("lat", ""),
                        "additional_info": {}
                    }
                    
                    # 추가 정보 저장
                    for key, value in item.items():
                        if key not in ["obsnm", "agcnm", "addr", "etcaddr", "lon", "lat", "links", HYDRO_TYPES[hydro_type]["code_key"]]:
                            integrated_item["additional_info"][key] = value
                    
                    INTEGRATED_DATA.append(integrated_item)
                    
                    # 위치 기반 캐싱
                    location_key = f"{item.get('addr', '')} {item.get('etcaddr', '')}"
                    if location_key.strip():
                        if location_key not in LOCATION_CACHE:
                            LOCATION_CACHE[location_key] = []
                        LOCATION_CACHE[location_key].append(integrated_item)
            
            logger.info(f"{hydro_type} 관측소 정보 로드 완료: {len(OBSERVATORY_INFO[hydro_type])}개")
        except httpx.HTTPError as e:
            logger.error(f"{hydro_type} 관측소 정보 로드 실패: {str(e)}")
            OBSERVATORY_INFO[hydro_type] = {}
            NAME_TO_CODE[hydro_type] = {}

def format_date(date_str: str, time_type: str) -> str:
    """날짜 문자열을 API 요청에 맞게 포맷팅합니다."""
    if not date_str:
        return ""
    
    # 하이픈 제거
    date_str = date_str.replace('-', '')
    
    # YYYYMMDD 형식 확인
    if re.match(r'^\d{8}$', date_str):
        if time_type == "10M":
            return f"{date_str}0000"  # 10분 단위는 시분 필요
        elif time_type == "1H":
            return f"{date_str}00"    # 1시간 단위는 시간 필요
        else:
            return date_str           # 1일 단위는 그대로
    
    # 이미 올바른 형식이면 그대로 반환
    return date_str

def find_observatory_by_location(location_query: str) -> List[Dict[str, Any]]:
    """위치 정보로 관측소를 찾습니다."""
    if not LOCATION_CACHE:
        return []
    
    results = []
    for location, observatories in LOCATION_CACHE.items():
        if location_query.lower() in location.lower():
            results.extend(observatories)
    
    # 관측소 이름에서도 검색
    for item in INTEGRATED_DATA:
        if location_query.lower() in item["obsnm"].lower():
            if item not in results:
                results.append(item)
    
    return results

@mcp.tool()
async def get_tools() -> List[TextContent]:
    """사용 가능한 도구와 기능을 보여줍니다."""
    if not OBSERVATORY_INFO:
        await load_observatory_info()
    
    tools_info = {
    "get_hydro_data": {
        "description": "다양한 수문 데이터(수위, 강수량, 댐, 보)를 조회합니다.",
        "parameters": {
            "hydro_type": {
                "description": "수문 유형 선택",
                "options": [
                    "waterlevel (수위)",
                    "rainfall (강수량)",
                    "dam (댐)",
                    "bo (보)"
                ],
                "example": "rainfall"
            },
            "obs_code": {
                "description": "관측소 코드 또는 이름",
                "example": "강릉시(대기리) 또는 10014080"
            },
            "time_type": {
                "description": "시간 단위",
                "options": ["10M (10분)", "1H (1시간)", "1D (1일)"],
                "default": "10M"
            },
            "start_date": {
                "description": "조회 시작일 (YYYYMMDD 또는 YYYY-MM-DD)",
                "example": "2025-03-20"
            },
            "end_date": {
                "description": "조회 종료일 (YYYYMMDD 또는 YYYY-MM-DD)",
                "example": "2025-03-26"
            }
        },
        "usage_example": "강수량 데이터 조회: get_hydro_data(hydro_type='rainfall', obs_code='강릉시(대기리)', start_date='2025-03-20', end_date='2025-03-26')"
    },
    "search_observatory": {
        "description": "지역명 또는 관측소명으로 관측소를 검색합니다. 모든 수문 유형(수위, 강수량, 댐, 보)에서 검색 가능합니다.",
        "parameters": {
            "query": {
                "description": "검색어 (지역명, 관측소명 등)",
                "example": "대전"
            },
            "hydro_type": {
                "description": "특정 수문 유형으로 검색 범위 제한 (선택사항)",
                "options": ["waterlevel", "rainfall", "dam", "bo"],
                "example": "rainfall"
            }
        },
        "usage_example": "대전 지역의 모든 관측소 검색: search_observatory(query='대전')"
    },
    "get_recent_data": {
        "description": "최근 수문 데이터를 조회합니다. 수위, 강수량, 댐, 보 등 모든 유형의 최신 데이터를 확인할 수 있습니다.",
        "parameters": {
            "hydro_type": {
                "description": "수문 유형 선택",
                "options": ["waterlevel", "rainfall", "dam", "bo"],
                "example": "dam"
            },
            "obs_code": {
                "description": "관측소 코드 또는 이름",
                "example": "소양강댐 또는 1012110"
            },
            "days": {
                "description": "조회할 일수",
                "default": 1,
                "example": 7
            },
            "time_type": {
                "description": "시간 단위",
                "options": ["10M", "1H", "1D"],
                "default": "1D"
            }
        },
        "usage_example": "소양강댐의 최근 7일 데이터 조회: get_recent_data(hydro_type='dam', obs_code='소양강댐', days=7)"
    }
}

    
    stats = {
        "총 관측소 수": len(INTEGRATED_DATA),
        "유형별 관측소 수": {
            HYDRO_TYPES[hydro_type]["name"]: len(OBSERVATORY_INFO.get(hydro_type, {}))
            for hydro_type in HYDRO_TYPES
        }
    }
    
    return [TextContent(
        type="text", 
        text=f"# 홍수통제소 API 도구\n\n"
             f"## 사용 가능한 도구\n\n"
             f"{json.dumps(tools_info, ensure_ascii=False, indent=2)}\n\n"
             f"## 데이터 통계\n\n"
             f"{json.dumps(stats, ensure_ascii=False, indent=2)}"
    )]

@mcp.tool()
async def initialize_server() -> List[TextContent]:
    """서버를 초기화합니다."""
    try:
        logger.info("서버 초기화 중: 관측소 정보 로드...")
        await load_observatory_info()
        logger.info(f"관측소 정보 로드 완료: 총 {len(INTEGRATED_DATA)}개")
        return [TextContent(type="text", text="서버가 성공적으로 초기화되었습니다.")]
    except Exception as e:
        logger.error(f"서버 초기화 실패: {str(e)}")
        return [TextContent(type="text", text=f"오류: 서버 초기화 실패 - {str(e)}")]

@mcp.tool()
async def get_hydro_data(
    hydro_type: str,
    obs_code: str,
    time_type: str = "10M",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[TextContent]:
    """수문 데이터를 조회합니다."""
    if not OBSERVATORY_INFO:
        await load_observatory_info()

    if hydro_type not in HYDRO_TYPES:
        return [TextContent(type="text", text=f"오류: 알 수 없는 수문 유형 '{hydro_type}'. 유효 유형: {', '.join(HYDRO_TYPES.keys())}")]

    # 이름으로 코드 변환
    if hydro_type in NAME_TO_CODE and obs_code in NAME_TO_CODE[hydro_type]:
        obs_code_original = obs_code
        obs_code = NAME_TO_CODE[hydro_type][obs_code]
        logger.info(f"이름 '{obs_code_original}' → 코드 '{obs_code}'로 변환")
    else:
        logger.debug(f"입력 '{obs_code}'를 코드로 직접 사용")

    # 코드 유효성 검사
    if hydro_type not in OBSERVATORY_INFO or not OBSERVATORY_INFO[hydro_type]:
        return [TextContent(type="text", text=f"오류: {hydro_type} 제원 정보가 로드되지 않았습니다. 서버를 재시작해 보세요.")]
    if obs_code not in OBSERVATORY_INFO[hydro_type]:
        valid_codes = ", ".join(list(OBSERVATORY_INFO[hydro_type].keys())[:5])
        valid_names = ", ".join(list(NAME_TO_CODE[hydro_type].keys())[:5])
        return [
            TextContent(
                type="text",
                text=f"오류: '{obs_code}'는 유효하지 않은 {HYDRO_TYPES[hydro_type]['name']} 코드 또는 이름입니다.\n유효 코드 예: {valid_codes}\n유효 이름 예: {valid_names}"
            )
        ]

    try:
        # 날짜 형식 변환
        formatted_start_date = format_date(start_date, time_type) if start_date else None
        formatted_end_date = format_date(end_date, time_type) if end_date else None
        
        data = await fetch_hrfco_data(
            hydro_type=hydro_type,
            data_type="list",
            time_type=time_type,
            obs_code=obs_code,
            start_date=formatted_start_date,
            end_date=formatted_end_date
        )
        
        # 관측소 정보 추가
        obs_info = OBSERVATORY_INFO[hydro_type].get(obs_code, {})
        if obs_info:
            data["observatory_info"] = obs_info
        
        return [TextContent(type="text", text=json.dumps(data, ensure_ascii=False, indent=2))]
    except httpx.HTTPStatusError as e:
        error_data = {}
        try:
            error_data = e.response.json()
        except:
            error_data = {"message": str(e)}
            
        if error_data.get("code") == "920":
            return [TextContent(type="text", text=f"오류: '{obs_code}'는 HRFCO에서 유효하지 않은 코드입니다.")]
        if error_data.get("code") == "930":
            return [TextContent(type="text", text=f"오류: 잘못된 날짜 형식입니다. YYYYMMDD 또는 YYYY-MM-DD 형식으로 입력해주세요.")]
        return [TextContent(type="text", text=f"오류: {HYDRO_TYPES[hydro_type]['name']} API 요청 실패 - {json.dumps(error_data, ensure_ascii=False)}")]
    except Exception as e:
        logger.error(f"예상치 못한 오류: {str(e)}")
        return [TextContent(type="text", text=f"오류: 처리 중 문제가 발생했습니다 - {str(e)}")]

@mcp.tool()
async def search_observatory(
    query: str,
    hydro_type: Optional[str] = None
) -> List[TextContent]:
    """관측소를 검색합니다."""
    if not OBSERVATORY_INFO:
        await load_observatory_info()
    
    results = find_observatory_by_location(query)
    
    # 수문 유형으로 필터링
    if hydro_type:
        if hydro_type not in HYDRO_TYPES:
            return [TextContent(type="text", text=f"오류: 알 수 없는 수문 유형 '{hydro_type}'. 유효 유형: {', '.join(HYDRO_TYPES.keys())}")]
        results = [item for item in results if item["type"] == hydro_type]
    
    if not results:
        return [TextContent(type="text", text=f"'{query}'에 해당하는 관측소를 찾을 수 없습니다.")]
    
    # 결과 포맷팅
    formatted_results = []
    for item in results:
        formatted_item = {
            "유형": HYDRO_TYPES[item["type"]]["name"],
            "코드": item["obscd"],
            "이름": item["obsnm"],
            "주소": f"{item['addr']} {item['etcaddr']}".strip(),
            "관할기관": item["agcnm"]
        }
        formatted_results.append(formatted_item)
    
    return [TextContent(
        type="text", 
        text=f"# '{query}' 검색 결과 ({len(results)}개)\n\n{json.dumps(formatted_results, ensure_ascii=False, indent=2)}"
    )]

@mcp.tool()
async def get_integrated_data() -> List[TextContent]:
    """통합된 관측소 제원 정보를 조회합니다."""
    if not INTEGRATED_DATA:
        await load_observatory_info()
    if not INTEGRATED_DATA:
        return [TextContent(type="text", text="오류: 통합 데이터를 로드할 수 없습니다.")]

    # 요약 정보 생성
    summary = {
        "총 관측소 수": len(INTEGRATED_DATA),
        "유형별 관측소 수": {
            HYDRO_TYPES[hydro_type]["name"]: len(OBSERVATORY_INFO.get(hydro_type, {}))
            for hydro_type in HYDRO_TYPES
        }
    }

    result = {
        "summary": summary,
        "data": INTEGRATED_DATA[:10]  # 처음 10개만 표시
    }

    return [TextContent(
        type="text",
        text=f"# 통합 관측소 정보 (처음 10개)\n\n{json.dumps(result, ensure_ascii=False, indent=2)}\n\n전체 {len(INTEGRATED_DATA)}개 중 10개만 표시됩니다."
    )]

@mcp.tool()
async def filter_by_time(
    hydro_type: str,
    obs_code: str,
    time_type: str = "10M",
    start_date: str = None,
    end_date: str = None,
    hour: Optional[str] = None,
    minute: Optional[str] = None,
    page: int = 1,
    per_page: int = 100
) -> List[TextContent]:
    """특정 시간대의 수문 데이터만 필터링하여 조회합니다."""
    if not OBSERVATORY_INFO:
        await load_observatory_info()
    if hydro_type not in HYDRO_TYPES:
        return [TextContent(type="text", text=f"오류: 알 수 없는 수문 유형 '{hydro_type}'. 유효 유형: {', '.join(HYDRO_TYPES.keys())}")]

    # 이름으로 코드 변환
    if hydro_type in NAME_TO_CODE and obs_code in NAME_TO_CODE[hydro_type]:
        obs_code_original = obs_code
        obs_code = NAME_TO_CODE[hydro_type][obs_code]
        logger.info(f"이름 '{obs_code_original}' → 코드 '{obs_code}'로 변환")

    # 코드 유효성 검사
    if obs_code not in OBSERVATORY_INFO.get(hydro_type, {}):
        valid_codes = ", ".join(list(OBSERVATORY_INFO[hydro_type].keys())[:5])
        valid_names = ", ".join(list(NAME_TO_CODE[hydro_type].keys())[:5])
        return [
            TextContent(
                type="text",
                text=f"오류: '{obs_code}'는 유효하지 않은 {HYDRO_TYPES[hydro_type]['name']} 코드 또는 이름입니다.\n유효 코드 예: {valid_codes}\n유효 이름 예: {valid_names}"
            )
        ]

    try:
        # 날짜 형식 변환 및 데이터 조회
        formatted_start_date = format_date(start_date, time_type) if start_date else None
        formatted_end_date = format_date(end_date, time_type) if end_date else None
        
        data = await fetch_hrfco_data(
            hydro_type=hydro_type,
            data_type="list",
            time_type=time_type,
            obs_code=obs_code,
            start_date=formatted_start_date,
            end_date=formatted_end_date
        )
        
        content = data.get("content", [])
        
        # 시간 필터링
        if hour is not None or minute is not None:
            filtered_content = []
            for item in content:
                ymdhm = item.get("ymdhm", "")
                if len(ymdhm) >= 12:  # yyyyMMddHHmm 형식 확인
                    item_hour = ymdhm[8:10]
                    item_minute = ymdhm[10:12]
                    
                    if hour is not None and minute is not None:
                        if item_hour == hour.zfill(2) and item_minute == minute.zfill(2):
                            filtered_content.append(item)
                    elif hour is not None:
                        if item_hour == hour.zfill(2):
                            filtered_content.append(item)
                    elif minute is not None:
                        if item_minute == minute.zfill(2):
                            filtered_content.append(item)
            data["content"] = filtered_content
        else:
            filtered_content = content

        # 페이지네이션 적용
        total_items = len(filtered_content)
        total_pages = (total_items + per_page - 1) // per_page
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        data["content"] = filtered_content[start_idx:end_idx]
        data["pagination"] = {
            "total_items": total_items,
            "total_pages": total_pages,
            "current_page": page,
            "per_page": per_page,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
        
        # 관측소 정보 추가
        obs_info = OBSERVATORY_INFO[hydro_type].get(obs_code, {})
        if obs_info:
            data["observatory_info"] = obs_info
        
        return [TextContent(type="text", text=json.dumps(data, ensure_ascii=False, indent=2))]
    except Exception as e:
        logger.error(f"예상치 못한 오류: {str(e)}")
        return [TextContent(type="text", text=f"오류: 처리 중 문제가 발생했습니다 - {str(e)}")]

# 캐시 설정
CACHE = {}
CACHE_TTL = 300  # 5분

@mcp.tool()
async def get_recent_data(
    hydro_type: str,
    obs_code: str,
    count: int = 10,
    time_type: str = "10M",
    fields: Optional[str] = None  # 필요한 필드만 선택적으로 반환
) -> List[TextContent]:
    """
    최근 수문 데이터를 조회합니다. 기본적으로 최근 10개 항목을 제공합니다.
    
    Args:
        hydro_type: 수문 유형 (waterlevel, rainfall, dam, bo)
        obs_code: 관측소 코드 또는 이름
        count: 조회할 항목 수 (기본값: 10)
        time_type: 시간 단위 (10M, 1H, 1D)
        fields: 반환할 필드 (쉼표로 구분, 예: "ymdhm,wl,swl")
    """
    # 캐시 키 생성
    cache_key = f"{hydro_type}_{obs_code}_{count}_{time_type}_{fields}"
    
    # 캐시된 데이터 확인
    now = time.time()
    if cache_key in CACHE and CACHE[cache_key]["expires_at"] > now:
        logger.info(f"캐시에서 데이터 조회: {cache_key}")
        return [TextContent(type="text", text=CACHE[cache_key]["data"])]
    
    if not OBSERVATORY_INFO:
        await load_observatory_info()

    if hydro_type not in HYDRO_TYPES:
        return [TextContent(type="text", text=f"오류: 알 수 없는 수문 유형 '{hydro_type}'. 유효 유형: {', '.join(HYDRO_TYPES.keys())}")]

    # 이름으로 코드 변환
    if hydro_type in NAME_TO_CODE and obs_code in NAME_TO_CODE[hydro_type]:
        obs_code_original = obs_code
        obs_code = NAME_TO_CODE[hydro_type][obs_code]
        logger.info(f"이름 '{obs_code_original}' → 코드 '{obs_code}'로 변환")

    # 코드 유효성 검사
    if hydro_type not in OBSERVATORY_INFO or not OBSERVATORY_INFO[hydro_type]:
        return [TextContent(type="text", text=f"오류: {hydro_type} 제원 정보가 로드되지 않았습니다. 서버를 재시작해 보세요.")]
    if obs_code not in OBSERVATORY_INFO[hydro_type]:
        # 더 간결한 오류 메시지
        return [
            TextContent(
                type="text",
                text=f"오류: '{obs_code}'는 유효하지 않은 {HYDRO_TYPES[hydro_type]['name']} 코드 또는 이름입니다."
            )
        ]

    try:
        # 날짜 계산 최적화 (시간 단위에 따라 적절한 기간 설정)
        days_to_fetch = {"10M": 1, "1H": 3, "1D": 30}.get(time_type, 1)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_to_fetch)

        # 날짜 형식 변환
        formatted_start_date = format_date(start_date.strftime("%Y%m%d"), time_type)
        formatted_end_date = format_date(end_date.strftime("%Y%m%d"), time_type)

        data = await fetch_hrfco_data(
            hydro_type=hydro_type,
            data_type="list",
            time_type=time_type,
            obs_code=obs_code,
            start_date=formatted_start_date,
            end_date=formatted_end_date
        )

        # 데이터 가공 및 최적화
        content = data.get("content", [])
        
        # 데이터가 없는 경우 빠른 반환
        if not content:
            result = {"message": "데이터가 없습니다.", "observatory_info": OBSERVATORY_INFO[hydro_type].get(obs_code, {})}
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        # 최근 데이터 순으로 정렬 (ymdhm 기준 내림차순)
        content.sort(key=lambda x: x.get("ymdhm", ""), reverse=True)
        
        # 최근 count개 항목만 유지
        limited_content = content[:min(count, len(content))]
        
        # 필드 필터링 (필요한 필드만 포함)
        if fields:
            field_list = [f.strip() for f in fields.split(",")]
            filtered_content = []
            for item in limited_content:
                filtered_item = {}
                for field in field_list:
                    if field in item:
                        filtered_item[field] = item[field]
                filtered_content.append(filtered_item)
            limited_content = filtered_content
        
        # 데이터 필드 결정 (매핑 사용)
        data_field_map = {
            "waterlevel": "wl",
            "rainfall": "rf",
            "dam": "swl",
            "bo": "swl"
        }
        data_field = data_field_map.get(hydro_type)
        
        # 간결한 결과 구성
        result = {
            "observatory_info": {
                "code": obs_code,
                "name": OBSERVATORY_INFO[hydro_type].get(obs_code, {}).get("obsnm", obs_code),
                "type": HYDRO_TYPES[hydro_type]["name"]
            },
            "content": limited_content,
            "content_info": {
                "requested": count,
                "returned": len(limited_content),
                "total_available": len(content)
            }
        }
        
        # 요약 정보 생성 (최근 count개 항목만 대상으로)
        if data_field and any(data_field in item for item in limited_content):
            values = [float(item.get(data_field, 0)) for item in limited_content if data_field in item and item.get(data_field)]
            if values:
                result["summary"] = {
                    "count": len(values),
                    "avg": round(sum(values) / len(values), 2),
                    "max": max(values),
                    "min": min(values),
                    "unit": HYDRO_TYPES[hydro_type]["unit"]
                }
        
        # 결과를 JSON으로 변환
        json_result = json.dumps(result, ensure_ascii=False, indent=2)
        
        # 캐시에 저장
        CACHE[cache_key] = {
            "data": json_result,
            "expires_at": now + CACHE_TTL
        }
        
        return [TextContent(type="text", text=json_result)]
    except httpx.HTTPStatusError as e:
        # 간결한 오류 메시지
        error_message = f"API 요청 실패: {str(e)}"
        return [TextContent(type="text", text=error_message)]
    except Exception as e:
        logger.error(f"예상치 못한 오류: {str(e)}")
        return [TextContent(type="text", text=f"오류: {str(e)}")]
