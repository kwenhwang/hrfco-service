#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HRFCO API MCP Server
HTTP API를 MCP 프로토콜로 래핑하여 Claude에서 직접 사용할 수 있도록 함
"""
import asyncio
import json
import sys
import httpx
import math
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import os

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from hrfco_service.location_mapping import get_location_coordinates, LOCATION_MAPPING
from hrfco_service.wamis_api import WAMISAPIClient, BASIN_CODES
from hrfco_service.ontology_manager import IntegratedOntologyManager

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# 직접 API 함수들을 정의하여 의존성 제거
class HRFCOAPI:
    """HRFCO API 클라이언트"""
    
    BASE_URL = "https://api.hrfco.go.kr"
    SERVICE_KEY = os.environ.get("HRFCO_API_KEY", "your-api-key-here")
    
    def __init__(self):
        self.session = httpx.AsyncClient(timeout=10)
    
    def _calculate_date_range(self, time_type: str, hours: int = 48) -> tuple[str, str]:
        """시간 단위에 따른 날짜 범위를 계산합니다."""
        from datetime import datetime, timedelta
        
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
    
    async def fetch_observatory_info(self, hydro_type: str) -> dict:
        # 관측소 제원 정보
        url = f"{self.BASE_URL}/{self.SERVICE_KEY}/{hydro_type}/info.json"
        try:
            response = await self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "content": []}
    
    async def fetch_observatory_data(self, hydro_type: str, time_type: str, obs_code: Optional[str] = None, sdt: Optional[str] = None, edt: Optional[str] = None, hours: int = 48) -> dict:
        # 실시간 자료
        url = f"{self.BASE_URL}/{self.SERVICE_KEY}/{hydro_type}/list/{time_type}"
        if obs_code:
            url += f"/{obs_code}"
        
        # 날짜 범위가 지정되지 않은 경우 자동 계산
        if not sdt or not edt:
            sdt, edt = self._calculate_date_range(time_type, hours)
        
        # 날짜 범위가 있는 경우 시간 정보를 포함하여 처리
        if sdt and edt:
            # 날짜 형식이 YYYYMMDD인 경우 시간 정보 추가
            if len(sdt) == 8 and len(edt) == 8:
                # 시작 시간을 00:00으로, 종료 시간을 23:59로 설정
                sdt_with_time = f"{sdt}00"  # YYYYMMDDHH
                edt_with_time = f"{edt}23"  # YYYYMMDDHH
                url += f"/{sdt_with_time}/{edt_with_time}"
            else:
                # 이미 시간 정보가 포함된 경우 그대로 사용
                url += f"/{sdt}/{edt}"
        
        url += ".json"
        
        try:
            response = await self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "content": []}

class GeocodingAPI:
    """주소 → 좌표 변환 (OpenStreetMap Nominatim + 지역명 매핑)"""
    
    KAKAO_API_KEY = "617541448c319c443c1fdf168c555e48"
    KAKAO_BASE_URL = "https://dapi.kakao.com/v2/local/search/address.json"
    NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org/search"
    
    def __init__(self):
        self.session = httpx.AsyncClient(timeout=10)
    
    async def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """주소를 좌표로 변환 (여러 방법 시도)"""
        
        # 1. 새로운 지역명 매핑 모듈에서 먼저 확인
        coordinates = get_location_coordinates(address)
        if coordinates:
            return coordinates
        
        # 2. 카카오 API 시도
        try:
            headers = {
                "Authorization": f"KakaoAK {self.KAKAO_API_KEY}"
            }
            params = {
                "query": address
            }
            
            response = await self.session.get(self.KAKAO_BASE_URL, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("documents"):
                doc = data["documents"][0]
                return (float(doc["y"]), float(doc["x"]))  # (위도, 경도)
        except Exception as e:
            print(f"카카오 API 오류: {str(e)}", file=sys.stderr)
        
        # 3. OpenStreetMap Nominatim API 시도
        try:
            params = {
                "q": f"{address}, South Korea",
                "format": "json",
                "limit": 1
            }
            
            response = await self.session.get(self.NOMINATIM_BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data:
                result = data[0]
                return (float(result["lat"]), float(result["lon"]))
        except Exception as e:
            print(f"OpenStreetMap API 오류: {str(e)}", file=sys.stderr)
        
        return None

class DistanceCalculator:
    """거리 계산 유틸리티"""
    
    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Haversine 공식을 사용한 두 지점 간 거리 계산 (km)"""
        R = 6371  # 지구 반지름 (km)
        
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    @staticmethod
    def parse_coordinates(coord_str: str) -> Optional[float]:
        """HRFCO API의 좌표 문자열을 파싱"""
        try:
            # 예: "37-20-40" (도-분-초)
            parts = coord_str.strip().split('-')
            if len(parts) >= 2:
                degrees = float(parts[0])
                minutes = float(parts[1])
                seconds = float(parts[2]) if len(parts) > 2 else 0
                
                decimal_degrees = degrees + minutes/60 + seconds/3600
                return decimal_degrees
            return None
        except:
            return None

class HRFCOMCPServer:
    """HRFCO API를 MCP 프로토콜로 래핑하는 서버"""
    
    def __init__(self):
        self.api_client = HRFCOAPI()
        self.geocoding_client = GeocodingAPI()
        self.distance_calculator = DistanceCalculator()
        self.wamis_client = WAMISAPIClient()
        self.ontology_manager = IntegratedOntologyManager()
        self.tools = [
            {
                "name": "get_observatory_info",
                "description": "수문 관측소 정보를 조회합니다. 수위, 강수량, 댐, 보 관측소의 목록과 위치 정보를 제공합니다.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "hydro_type": {
                            "type": "string",
                            "enum": ["waterlevel", "rainfall", "dam", "bo"],
                            "description": "수문 데이터 타입 (waterlevel: 수위, rainfall: 강수량, dam: 댐, bo: 보)"
                        }
                    },
                    "required": ["hydro_type"]
                }
            },
            {
                "name": "get_hydro_data",
                "description": "실시간 수문 데이터를 조회합니다. 관측소의 현재 수위, 강수량, 댐 방류량, 보 수위 등을 확인할 수 있습니다.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "hydro_type": {
                            "type": "string",
                            "enum": ["waterlevel", "rainfall", "dam", "bo"],
                            "description": "수문 데이터 타입 (waterlevel: 수위, rainfall: 강수량, dam: 댐, bo: 보)"
                        },
                        "time_type": {
                            "type": "string",
                            "enum": ["10M", "1H", "1D"],
                            "description": "시간 단위 (10M: 10분, 1H: 1시간, 1D: 1일)"
                        },
                        "obs_code": {
                            "type": "string",
                            "description": "관측소 코드 (get_observatory_info로 조회 가능)"
                        },
                        "sdt": {
                            "type": "string",
                            "description": "시작 날짜 (YYYYMMDD)"
                        },
                        "edt": {
                            "type": "string",
                            "description": "종료 날짜 (YYYYMMDD)"
                        }
                    },
                    "required": ["hydro_type", "time_type"]
                }
            },
            {
                "name": "get_hydro_data_nearby",
                "description": "특정 주소 주변의 수문 데이터를 조회합니다. 주소를 입력하면 반경 내 관측소들의 데이터를 제공합니다.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "address": {
                            "type": "string",
                            "description": "검색할 주소 (예: 세종 반곡동, 한강)"
                        },
                        "radius_km": {
                            "type": "number",
                            "description": "검색 반경 (km, 기본값: 10)"
                        },
                        "hydro_type": {
                            "type": "string",
                            "enum": ["waterlevel", "rainfall", "dam", "bo"],
                            "description": "수문 데이터 타입"
                        },
                        "time_type": {
                            "type": "string",
                            "enum": ["10M", "1H", "1D"],
                            "description": "시간 단위"
                        },
                        "consider_basin_relationship": {
                            "type": "boolean",
                            "description": "수계 관계를 고려하여 관측소를 필터링할지 여부 (기본값: true)"
                        }
                    },
                    "required": ["address", "hydro_type"]
                }
            },
            {
                "name": "get_server_health",
                "description": "HRFCO MCP 서버의 상태를 확인합니다. 서버가 정상적으로 작동하는지 확인할 수 있습니다.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_server_config",
                "description": "서버 설정 정보를 확인합니다. API 키 설정 상태 등을 확인할 수 있습니다.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "analyze_water_level_with_thresholds",
                "description": "수위 관측소의 데이터를 위험 수위 기준과 함께 분석합니다. 관심, 주의보, 경보, 심각 단계별 위험도를 평가합니다.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "obs_code": {
                            "type": "string",
                            "description": "수위 관측소 코드"
                        },
                        "time_type": {
                            "type": "string",
                            "enum": ["10M", "1H", "1D"],
                            "description": "시간 단위 (기본값: 1H)"
                        },
                        "count": {
                            "type": "integer",
                            "description": "조회할 데이터 개수 (기본값: 48)"
                        },
                        "hours": {
                            "type": "integer",
                            "description": "조회할 시간 범위 (시간 단위, 기본값: 72)"
                        }
                    },
                    "required": ["obs_code"]
                }
            },
            {
                "name": "get_comprehensive_hydro_analysis",
                "description": "수위와 강우량 데이터를 종합적으로 분석합니다. 관측소 간 거리, 상관관계, 위험 수위 분석을 포함합니다.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "water_level_obs": {
                            "type": "string",
                            "description": "수위 관측소 코드"
                        },
                        "rainfall_obs": {
                            "type": "string",
                            "description": "강우량 관측소 코드 (선택사항)"
                        },
                        "time_type": {
                            "type": "string",
                            "enum": ["10M", "1H", "1D"],
                            "description": "시간 단위 (기본값: 1H)"
                        },
                        "count": {
                            "type": "integer",
                            "description": "조회할 데이터 개수 (기본값: 48)"
                        },
                        "hours": {
                            "type": "integer",
                            "description": "조회할 시간 범위 (시간 단위, 기본값: 72)"
                        }
                    },
                    "required": ["water_level_obs"]
                }
            },
            {
                "name": "get_alert_status_summary",
                "description": "지역별 또는 전체의 위험 수위 상태를 요약합니다. 관심, 주의보, 경보, 심각 단계별 관측소 현황을 제공합니다.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "region_name": {
                            "type": "string",
                            "description": "지역 이름 (선택사항, 미입력 시 전체)"
                        },
                        "hydro_type": {
                            "type": "string",
                            "enum": ["waterlevel", "rainfall", "dam", "bo"],
                            "description": "수문 데이터 타입 (기본값: waterlevel)"
                        }
                    }
                }
            },
            {
                "name": "get_basin_comprehensive_analysis",
                "description": "같은 수계의 근접 시설들을 종합적으로 분석합니다. 수위, 강우량, 댐, 보 등의 시설을 거리 기반으로 찾아 통합 분석합니다.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "main_obs_code": {
                            "type": "string",
                            "description": "메인 관측소 코드 (기준점)"
                        },
                        "hydro_types": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["waterlevel", "rainfall", "dam", "bo"]
                            },
                            "description": "분석할 수문 데이터 타입들 (기본값: 모든 타입)"
                        },
                        "max_distance_km": {
                            "type": "number",
                            "description": "최대 검색 거리 (km, 기본값: 20.0)"
                        },
                        "time_type": {
                            "type": "string",
                            "enum": ["10M", "1H", "1D"],
                            "description": "시간 단위 (기본값: 1H)"
                        },
                        "count": {
                            "type": "integer",
                            "description": "조회할 데이터 개수 (기본값: 24)"
                        },
                        "hours": {
                            "type": "integer",
                            "description": "조회할 시간 범위 (시간 단위, 기본값: 48)"
                        }
                    },
                    "required": ["main_obs_code"]
                }
            },
            {
                "name": "search_basin_facilities",
                "description": "WAMIS API를 사용하여 특정 수계의 모든 수문 시설을 검색합니다. 수위, 강우량, 기상, 댐 관측소를 찾을 수 있습니다.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "basin": {
                            "type": "string",
                            "enum": ["한강", "낙동강", "금강", "섬진강", "영산강", "제주도"],
                            "description": "검색할 수계 (기본값: 낙동강)"
                        },
                        "facility_types": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["waterlevel", "rainfall", "weather", "dam"]
                            },
                            "description": "검색할 시설 타입들 (기본값: 모든 타입)"
                        },
                        "management_org": {
                            "type": "string",
                            "enum": ["환경부", "한국수자원공사", "한국농어촌공사", "기상청", "한국수력원자력"],
                            "description": "관할기관 필터 (선택사항)"
                        },
                        "operation_status": {
                            "type": "string",
                            "enum": ["y", "n"],
                            "description": "운영상태 필터 (y: 운영중, n: 폐쇄, 기본값: y)"
                        }
                    },
                    "required": ["basin"]
                }
            },
            {
                "name": "analyze_water_system_relationship",
                "description": "WAMIS API를 사용하여 특정 관측소의 수계별 상류/하류 관계를 분석합니다. 표준유역코드를 기준으로 정확한 수계 관계를 파악합니다.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "target_obs_code": {
                            "type": "string",
                            "description": "분석 대상 관측소 코드"
                        },
                        "basin": {
                            "type": "string",
                            "enum": ["한강", "낙동강", "금강", "섬진강", "영산강", "제주도"],
                            "description": "수계 (기본값: 낙동강)"
                        },
                        "hydro_type": {
                            "type": "string",
                            "enum": ["waterlevel", "rainfall"],
                            "description": "수문 데이터 타입 (기본값: waterlevel)"
                        },
                        "include_upstream": {
                            "type": "boolean",
                            "description": "상류 관측소 포함 여부 (기본값: true)"
                        },
                        "include_downstream": {
                            "type": "boolean",
                            "description": "하류 관측소 포함 여부 (기본값: true)"
                        }
                    },
                    "required": ["target_obs_code"]
                }
            },
            {
                "name": "get_integrated_ontology_info",
                "description": "통합 온톨로지를 사용하여 관측소 정보를 조회합니다. 홍수통제소, WAMIS, 기상청 API의 정보를 통합하여 제공합니다.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "obs_code": {
                            "type": "string",
                            "description": "관측소 코드"
                        },
                        "obs_type": {
                            "type": "string",
                            "enum": ["waterlevel", "rainfall", "dam", "weather"],
                            "description": "관측소 타입 (선택사항)"
                        },
                        "basin": {
                            "type": "string",
                            "enum": ["한강", "낙동강", "금강", "섬진강", "영산강", "제주도"],
                            "description": "수계 (선택사항)"
                        },
                        "source": {
                            "type": "string",
                            "enum": ["hrfco", "wamis", "weather"],
                            "description": "데이터 소스 (선택사항)"
                        }
                    }
                }
            },
            {
                "name": "search_integrated_observatories",
                "description": "통합 온톨로지를 사용하여 관측소를 검색합니다. 여러 API의 정보를 통합하여 검색 결과를 제공합니다.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "obs_type": {
                            "type": "string",
                            "enum": ["waterlevel", "rainfall", "dam", "weather"],
                            "description": "관측소 타입 (선택사항)"
                        },
                        "basin": {
                            "type": "string",
                            "enum": ["한강", "낙동강", "금강", "섬진강", "영산강", "제주도"],
                            "description": "수계 (선택사항)"
                        },
                        "source": {
                            "type": "string",
                            "enum": ["hrfco", "wamis", "weather"],
                            "description": "데이터 소스 (선택사항)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "검색 결과 제한 개수 (기본값: 50)"
                        }
                    }
                }
            },
            {
                "name": "get_water_system_analysis",
                "description": "통합 온톨로지를 사용하여 특정 관측소의 수계 관계를 분석합니다. 상류/하류 관계와 같은 수계 내 관측소들을 파악합니다.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "target_obs_code": {
                            "type": "string",
                            "description": "분석 대상 관측소 코드"
                        },
                        "include_upstream": {
                            "type": "boolean",
                            "description": "상류 관측소 포함 여부 (기본값: true)"
                        },
                        "include_downstream": {
                            "type": "boolean",
                            "description": "하류 관측소 포함 여부 (기본값: true)"
                        },
                        "include_same_basin": {
                            "type": "boolean",
                            "description": "같은 수계 관측소 포함 여부 (기본값: true)"
                        }
                    },
                    "required": ["target_obs_code"]
                }
            },
            {
                "name": "get_basin_comprehensive_summary",
                "description": "통합 온톨로지를 사용하여 특정 수계의 종합 요약 정보를 제공합니다. 수계 내 모든 관측소의 분포와 통계를 제공합니다.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "basin": {
                            "type": "string",
                            "enum": ["한강", "낙동강", "금강", "섬진강", "영산강", "제주도"],
                            "description": "수계 (기본값: 낙동강)"
                        },
                        "include_statistics": {
                            "type": "boolean",
                            "description": "통계 정보 포함 여부 (기본값: true)"
                        },
                        "include_stations": {
                            "type": "boolean",
                            "description": "관측소 목록 포함 여부 (기본값: false)"
                        }
                    },
                    "required": ["basin"]
                }
            }
        ]
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """MCP 요청을 처리합니다"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id", 0)
        
        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "hrfco-mcp-server",
                            "version": "1.0.0"
                        }
                    }
                }
            
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": self.tools
                    }
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name == "get_observatory_info":
                    result = await self._get_observatory_info(arguments)
                elif tool_name == "get_hydro_data":
                    result = await self._get_hydro_data(arguments)
                elif tool_name == "get_hydro_data_nearby":
                    result = await self._get_hydro_data_nearby(arguments)
                elif tool_name == "get_server_health":
                    result = await self._get_server_health()
                elif tool_name == "get_server_config":
                    result = await self._get_server_config()
                elif tool_name == "analyze_water_level_with_thresholds":
                    result = await self._analyze_water_level_with_thresholds(arguments)
                elif tool_name == "get_comprehensive_hydro_analysis":
                    result = await self._get_comprehensive_hydro_analysis(arguments)
                elif tool_name == "get_alert_status_summary":
                    result = await self._get_alert_status_summary(arguments)
                elif tool_name == "get_basin_comprehensive_analysis":
                    result = await self._get_basin_comprehensive_analysis(arguments)
                elif tool_name == "search_basin_facilities":
                    result = await self._search_basin_facilities(arguments)
                elif tool_name == "analyze_water_system_relationship":
                    result = await self._analyze_water_system_relationship(arguments)
                elif tool_name == "get_integrated_ontology_info":
                    result = await self._get_integrated_ontology_info(arguments)
                elif tool_name == "search_integrated_observatories":
                    result = await self._search_integrated_observatories(arguments)
                elif tool_name == "get_water_system_analysis":
                    result = await self._get_water_system_analysis(arguments)
                elif tool_name == "get_basin_comprehensive_summary":
                    result = await self._get_basin_comprehensive_summary(arguments)
                else:
                    raise ValueError(f"Unknown tool: {tool_name}")
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, ensure_ascii=False, indent=2)
                            }
                        ]
                    }
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
                
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
    
    async def _get_observatory_info(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """관측소 정보 조회"""
        hydro_type = arguments.get("hydro_type")
        if not hydro_type:
            raise ValueError("hydro_type is required")
        
        result = await self.api_client.fetch_observatory_info(hydro_type)
        return {
            "type": "observatory_info",
            "hydro_type": hydro_type,
            "data": result
        }
    
    async def _get_hydro_data(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """수문 데이터 조회"""
        hydro_type = arguments.get("hydro_type")
        time_type = arguments.get("time_type")
        obs_code = arguments.get("obs_code")
        sdt = arguments.get("sdt")
        edt = arguments.get("edt")
        if not all([hydro_type, time_type]):
            raise ValueError("hydro_type, time_type는 필수입니다")
        result = await self.api_client.fetch_observatory_data(str(hydro_type), str(time_type), str(obs_code) if obs_code else None, str(sdt) if sdt else None, str(edt) if edt else None)
        return {
            "type": "hydro_data",
            "hydro_type": hydro_type,
            "time_type": time_type,
            "obs_code": obs_code,
            "sdt": sdt,
            "edt": edt,
            "data": result
        }
    
    async def _get_hydro_data_nearby(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """주변 수문 데이터 조회 (수계 관계 고려)"""
        address = arguments.get("address")
        radius_km = arguments.get("radius_km", 10.0)
        hydro_type = arguments.get("hydro_type")
        time_type = arguments.get("time_type", "1H")
        consider_basin_relationship = arguments.get("consider_basin_relationship", True)
        
        if not address or not hydro_type:
            raise ValueError("address와 hydro_type은 필수입니다")
        
        # 1. 주소를 좌표로 변환
        coordinates = await self.geocoding_client.geocode_address(address)
        if not coordinates:
            return {
                "type": "error",
                "message": f"주소 '{address}'를 좌표로 변환할 수 없습니다."
            }
        
        target_lat, target_lon = coordinates
        
        # 2. 모든 수문 관측소 정보 조회 (수위, 강우량, 댐, 보)
        all_observatories = []
        
        # 수위 관측소
        waterlevel_info = await self.api_client.fetch_observatory_info("waterlevel")
        if waterlevel_info.get("content"):
            for obs in waterlevel_info["content"]:
                obs["hydro_type"] = "waterlevel"
                all_observatories.append(obs)
        
        # 강우량 관측소
        rainfall_info = await self.api_client.fetch_observatory_info("rainfall")
        if rainfall_info.get("content"):
            for obs in rainfall_info["content"]:
                obs["hydro_type"] = "rainfall"
                all_observatories.append(obs)
        
        # 댐 관측소
        dam_info = await self.api_client.fetch_observatory_info("dam")
        if dam_info.get("content"):
            for obs in dam_info["content"]:
                obs["hydro_type"] = "dam"
                all_observatories.append(obs)
        
        # 3. 반경 내 관측소 필터링
        nearby_observatories = []
        for obs in all_observatories:
            # 좌표 파싱
            lat_str = obs.get("lat", "")
            lon_str = obs.get("lon", "")
            
            obs_lat = self.distance_calculator.parse_coordinates(lat_str)
            obs_lon = self.distance_calculator.parse_coordinates(lon_str)
            
            if obs_lat and obs_lon:
                distance = self.distance_calculator.haversine_distance(
                    target_lat, target_lon, obs_lat, obs_lon
                )
                
                if distance <= radius_km:
                    obs_code = obs.get("dmobscd") or obs.get("wlobscd") or obs.get("rfobscd")
                    obs_type = obs.get("hydro_type", hydro_type)
                    nearby_observatories.append({
                        "obs_code": obs_code,
                        "obs_name": obs.get("obsnm", ""),
                        "address": obs.get("addr", ""),
                        "distance_km": round(distance, 2),
                        "coordinates": {"lat": obs_lat, "lon": obs_lon},
                        "hydro_type": obs_type
                    })
        
        # 거리순으로 정렬
        nearby_observatories.sort(key=lambda x: x["distance_km"])
        
        # 4. 통합 온톨로지를 사용한 수계 관계 분석
        basin_analysis = None
        if consider_basin_relationship and nearby_observatories:
            try:
                # 온톨로지 업데이트 확인
                await self.ontology_manager.update_ontology()
                
                # 가장 가까운 관측소를 기준으로 수계 분석
                closest_obs = nearby_observatories[0]
                water_system_analysis = self.ontology_manager.get_water_system_analysis(closest_obs["obs_code"])
                
                if water_system_analysis:
                    basin_analysis = {
                        "closest_station": closest_obs["obs_code"],
                        "water_system_analysis": water_system_analysis,
                        "ontology_summary": self.ontology_manager.get_integrated_ontology_summary()
                    }
            except Exception as e:
                # 수계 분석 실패 시 기존 방식으로 진행
                pass
        
        # 5. 각 관측소의 최신 데이터 조회 (최대 5개로 제한)
        results = []
        for obs in nearby_observatories[:5]:  # 최대 5개로 제한
            obs_hydro_type = obs.get("hydro_type", hydro_type)
            obs_data = await self.api_client.fetch_observatory_data(
                obs_hydro_type, time_type, obs["obs_code"]
            )
            
            if obs_data.get("content"):
                # 최신 데이터만 포함 (최대 3개)
                recent_data = obs_data["content"][:3] if isinstance(obs_data["content"], list) else []
                
                results.append({
                    "station_info": obs,
                    "recent_data": recent_data,
                    "total_available": len(obs_data["content"]) if isinstance(obs_data["content"], list) else 0
                })
        
        return {
            "type": "hydro_data_nearby",
            "search_parameters": {
                "address": address,
                "radius_km": radius_km,
                "hydro_type": hydro_type,
                "time_type": time_type,
                "consider_basin_relationship": consider_basin_relationship
            },
            "target_location": {
                "lat": target_lat,
                "lon": target_lon
            },
            "nearby_stations": nearby_observatories,
            "data_results": results,
            "basin_analysis": basin_analysis,
            "summary": {
                "total_nearby_stations": len(nearby_observatories),
                "stations_with_data": len(results),
                "search_radius_km": radius_km
            }
        }
    
    async def _get_server_health(self) -> Dict[str, Any]:
        """서버 상태 확인"""
        return {
            "type": "server_health",
            "status": "ok",
            "message": "HRFCO MCP Server is running normally"
        }
    
    async def _get_server_config(self) -> Dict[str, Any]:
        """서버 설정 확인"""
        return {
            "type": "server_config",
            "api_base_url": self.api_client.BASE_URL,
            "available_hydro_types": ["waterlevel", "rainfall", "dam", "bo"],
            "available_time_types": ["10M", "1H", "1D"]
        }

    async def _analyze_water_level_with_thresholds(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """수위 관측소의 데이터를 위험 수위 기준과 함께 분석합니다"""
        obs_code = arguments.get("obs_code")
        time_type = arguments.get("time_type", "1H")
        count = arguments.get("count", 48)
        hours = arguments.get("hours", 72)
        
        if not obs_code:
            return {"error": "관측소 코드가 필요합니다."}
        
        try:
            # 관측소 정보 조회
            obs_info_data = await self.api_client.fetch_observatory_info("waterlevel")
            obs_info = None
            for obs in obs_info_data.get("content", []):
                if obs.get("wlobscd") == obs_code:
                    obs_info = obs
                    break
            
            if not obs_info:
                return {"error": f"관측소를 찾을 수 없습니다: {obs_code}"}
            
            # 위험 수위 기준 추출
            thresholds = {}
            threshold_keys = {
                "attention": "attwl",
                "warning": "wrnwl", 
                "alert": "almwl",
                "serious": "srswl"
            }
            
            for alert_type, key in threshold_keys.items():
                value = obs_info.get(key)
                if value is not None:
                    try:
                        thresholds[alert_type] = float(value)
                    except (ValueError, TypeError):
                        thresholds[alert_type] = None
            
            # 수위 데이터 조회 (더 많은 시간 범위로)
            data = await self.api_client.fetch_observatory_data(
                hydro_type="waterlevel",
                time_type=time_type,
                obs_code=obs_code,
                hours=hours
            )
            
            if not data.get("content"):
                return {"error": "수위 데이터를 조회할 수 없습니다."}
            
            # 데이터 분석
            content = data["content"][:count]
            content.sort(key=lambda x: x.get("ymdhm", ""), reverse=True)
            
            # 현재 수위
            current_wl = float(content[0].get("wl", 0)) if content else 0
            
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
            
            # 변화 추세 분석
            if len(content) >= 2:
                recent_data = content[:6]  # 최근 6개 데이터
                wl_values = [float(d.get("wl", 0)) for d in recent_data if d.get("wl")]
                
                if len(wl_values) >= 2:
                    trend = "increasing" if wl_values[0] > wl_values[-1] else "decreasing"
                    change_rate = (wl_values[0] - wl_values[-1]) / len(wl_values) if len(wl_values) > 1 else 0
                    
                    alert_analysis["trend"] = {
                        "direction": trend,
                        "change_rate": change_rate,
                        "recent_values": wl_values
                    }
            
            return {
                "observatory_info": {
                    "obs_code": obs_code,
                    "obs_name": obs_info.get("obsnm", "Unknown"),
                    "location": {
                        "lat": obs_info.get("lat"),
                        "lon": obs_info.get("lon")
                    }
                },
                "thresholds": thresholds,
                "alert_analysis": alert_analysis,
                "recent_data": content[:10],
                            "summary": {
                "total_records": len(content),
                "total_available": len(content),
                "time_range": {
                    "start": content[-1].get("ymdhm") if content else None,
                    "end": content[0].get("ymdhm") if content else None
                },
                "hours_requested": hours,
                "data_count_requested": count
            }
            }
            
        except Exception as e:
            return {"error": f"분석 중 오류가 발생했습니다: {str(e)}"}

    async def _get_comprehensive_hydro_analysis(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """수위와 강우량 데이터를 종합적으로 분석합니다"""
        water_level_obs = arguments.get("water_level_obs")
        rainfall_obs = arguments.get("rainfall_obs")
        time_type = arguments.get("time_type", "1H")
        count = arguments.get("count", 48)
        hours = arguments.get("hours", 72)
        
        if not water_level_obs:
            return {"error": "수위 관측소 코드가 필요합니다."}
        
        try:
            # 수위 관측소 정보 조회
            wl_obs_info_data = await self.api_client.fetch_observatory_info("waterlevel")
            wl_obs_info = None
            for obs in wl_obs_info_data.get("content", []):
                if obs.get("wlobscd") == water_level_obs:
                    wl_obs_info = obs
                    break
            
            if not wl_obs_info:
                return {"error": f"수위 관측소를 찾을 수 없습니다: {water_level_obs}"}
            
            # 수위 위험 수위 기준 추출
            wl_thresholds = {}
            threshold_keys = {
                "attention": "attwl",
                "warning": "wrnwl", 
                "alert": "almwl",
                "serious": "srswl"
            }
            
            for alert_type, key in threshold_keys.items():
                value = wl_obs_info.get(key)
                if value is not None:
                    try:
                        wl_thresholds[alert_type] = float(value)
                    except (ValueError, TypeError):
                        wl_thresholds[alert_type] = None
            
            # 수위 데이터 조회 (더 많은 시간 범위로)
            wl_data = await self.api_client.fetch_observatory_data(
                hydro_type="waterlevel",
                time_type=time_type,
                obs_code=water_level_obs,
                hours=hours
            )
            
            if not wl_data.get("content"):
                return {"error": "수위 데이터를 조회할 수 없습니다."}
            
            wl_content = wl_data["content"][:count]
            wl_content.sort(key=lambda x: x.get("ymdhm", ""), reverse=True)
            
            # 강우량 데이터 처리
            rf_content = []
            rf_obs_info = None
            distance_info = None
            
            if rainfall_obs:
                # 강우량 관측소 정보 조회
                rf_obs_info_data = await self.api_client.fetch_observatory_info("rainfall")
                for obs in rf_obs_info_data.get("content", []):
                    if obs.get("rfobscd") == rainfall_obs:
                        rf_obs_info = obs
                        break
                
                # 거리 계산
                if wl_obs_info and rf_obs_info:
                    try:
                        lat1 = float(wl_obs_info.get("lat", 0))
                        lon1 = float(wl_obs_info.get("lon", 0))
                        lat2 = float(rf_obs_info.get("lat", 0))
                        lon2 = float(rf_obs_info.get("lon", 0))
                        
                        if lat1 != 0 and lon1 != 0 and lat2 != 0 and lon2 != 0:
                            distance = self.distance_calculator.haversine_distance(lat1, lon1, lat2, lon2)
                            distance_info = {
                                "distance_km": round(distance, 2),
                                "proximity": "매우 근접" if distance < 1 else "근접" if distance < 5 else "보통" if distance < 10 else "원거리"
                            }
                    except (ValueError, TypeError):
                        pass
                
                # 강우량 데이터 조회 (더 많은 시간 범위로)
                rf_data = await self.api_client.fetch_observatory_data(
                    hydro_type="rainfall",
                    time_type=time_type,
                    obs_code=rainfall_obs,
                    hours=hours
                )
                
                if rf_data.get("content"):
                    rf_content = rf_data["content"][:count]
                    rf_content.sort(key=lambda x: x.get("ymdhm", ""), reverse=True)
            
            # 위험 수위 분석
            current_wl = float(wl_content[0].get("wl", 0)) if wl_content else 0
            alert_analysis = {}
            
            for alert_type, threshold in wl_thresholds.items():
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
            
            # 강우량-수위 상관관계 분석
            correlation_analysis = {}
            if rf_content and wl_content:
                # 시간별 매칭
                wl_dict = {item.get("ymdhm"): float(item.get("wl", 0)) for item in wl_content}
                rf_dict = {item.get("ymdhm"): float(item.get("rf", 0)) for item in rf_content}
                
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
                        recent_data = matched_data[:6]  # 최근 6개
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
            
            return {
                "analysis_period": {
                    "time_type": time_type,
                    "data_count": len(wl_content),
                    "time_range": {
                        "start": wl_content[-1].get("ymdhm") if wl_content else None,
                        "end": wl_content[0].get("ymdhm") if wl_content else None
                    }
                },
                "water_level_station": {
                    "obs_code": water_level_obs,
                    "obs_name": wl_obs_info.get("obsnm", "Unknown"),
                    "thresholds": wl_thresholds,
                    "alert_analysis": alert_analysis
                },
                "rainfall_station": {
                    "obs_code": rainfall_obs if rainfall_obs else None,
                    "obs_name": rf_obs_info.get("obsnm") if rf_obs_info else None,
                    "data_available": len(rf_content) > 0,
                    "total_available": len(rf_content) if rf_content else 0
                },
                "station_distance": distance_info,
                "correlation_analysis": correlation_analysis,
                "recent_data": {
                    "water_level": wl_content[:10],
                    "rainfall": rf_content[:10] if rf_content else []
                }
            }
            
        except Exception as e:
            return {"error": f"종합 분석 중 오류가 발생했습니다: {str(e)}"}

    async def _get_alert_status_summary(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """지역별 또는 전체의 위험 수위 상태를 요약합니다"""
        region_name = arguments.get("region_name")
        hydro_type = arguments.get("hydro_type", "waterlevel")
        
        try:
            # 관측소 정보 조회
            obs_info_data = await self.api_client.fetch_observatory_info(hydro_type)
            stations = obs_info_data.get("content", [])
            
            if not stations:
                return {"error": f"{hydro_type} 관측소 정보를 조회할 수 없습니다."}
            
            # 지역 필터링
            if region_name:
                filtered_stations = []
                for station in stations:
                    obs_name = station.get("obsnm", "").lower()
                    if region_name.lower() in obs_name:
                        filtered_stations.append(station)
                stations = filtered_stations
            
            if not stations:
                return {"error": f"'{region_name or '전체'}' 지역의 {hydro_type} 관측소를 찾을 수 없습니다."}
            
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
                obs_code = station.get(f"{hydro_type[:2]}obscd")
                if not obs_code:
                    continue
                
                try:
                    # 최신 데이터 조회
                    data = await self.api_client.fetch_observatory_data(
                        hydro_type=hydro_type,
                        time_type="1H",
                        obs_code=obs_code
                    )
                    
                    if data.get("content"):
                        latest_data = data["content"][0]  # 최신 데이터
                        
                        # 위험 수위 기준 추출
                        thresholds = {}
                        if hydro_type == "waterlevel":
                            threshold_keys = {
                                "attention": "attwl",
                                "warning": "wrnwl", 
                                "alert": "almwl",
                                "serious": "srswl"
                            }
                            
                            for alert_type, key in threshold_keys.items():
                                value = station.get(key)
                                if value is not None:
                                    try:
                                        thresholds[alert_type] = float(value)
                                    except (ValueError, TypeError):
                                        thresholds[alert_type] = None
                        
                        # 현재 값
                        if hydro_type == "waterlevel":
                            current_value = float(latest_data.get("wl", 0))
                        elif hydro_type == "rainfall":
                            current_value = float(latest_data.get("rf", 0))
                        else:
                            current_value = None
                        
                        if current_value is not None:
                            # 알림 상태 결정
                            alert_status = "normal"
                            for alert_type in ["serious", "alert", "warning", "attention"]:
                                threshold = thresholds.get(alert_type)
                                if threshold is not None and current_value >= threshold:
                                    alert_status = alert_type
                                    break
                            
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
                    continue
            
            # 요약 통계
            total_stations = len(station_details)
            alert_stats = {status: len(stations) for status, stations in alert_summary.items()}
            
            return {
                "region": region_name or "전체",
                "hydro_type": hydro_type,
                "total_stations_checked": total_stations,
                "alert_statistics": alert_stats,
                "alert_details": alert_summary,
                "station_details": station_details
            }
            
        except Exception as e:
            return {"error": f"알림 상태 요약 중 오류가 발생했습니다: {str(e)}"}

    async def _get_basin_comprehensive_analysis(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """같은 수계의 근접 시설들을 종합적으로 분석합니다"""
        main_obs_code = arguments.get("main_obs_code")
        hydro_types = arguments.get("hydro_types", ["waterlevel", "rainfall", "dam", "bo"])
        max_distance_km = arguments.get("max_distance_km", 20.0)
        time_type = arguments.get("time_type", "1H")
        count = arguments.get("count", 48)
        hours = arguments.get("hours", 72)
        
        if not main_obs_code:
            return {"error": "메인 관측소 코드가 필요합니다."}
        
        try:
            # 메인 관측소 정보 확인
            main_obs_info = None
            main_hydro_type = None
            
            # 메인 관측소의 타입과 정보 찾기
            for hydro_type in hydro_types:
                obs_info_data = await self.api_client.fetch_observatory_info(hydro_type)
                for obs in obs_info_data.get("content", []):
                    obs_code = obs.get(f"{hydro_type[:2]}obscd")
                    if obs_code == main_obs_code:
                        main_obs_info = obs
                        main_hydro_type = hydro_type
                        break
                if main_obs_info:
                    break
            
            if not main_obs_info:
                return {"error": f"메인 관측소를 찾을 수 없습니다: {main_obs_code}"}
            
            # 메인 관측소 좌표
            main_lat = float(main_obs_info.get("lat", 0))
            main_lon = float(main_obs_info.get("lon", 0))
            
            if main_lat == 0 or main_lon == 0:
                return {"error": "메인 관측소의 좌표 정보가 없습니다."}
            
            # 근접 시설들 찾기
            nearby_facilities = []
            
            for hydro_type in hydro_types:
                obs_info_data = await self.api_client.fetch_observatory_info(hydro_type)
                facilities = obs_info_data.get("content", [])
                
                for facility in facilities:
                    try:
                        lat = float(facility.get("lat", 0))
                        lon = float(facility.get("lon", 0))
                        
                        if lat != 0 and lon != 0:
                            distance = self.distance_calculator.haversine_distance(
                                main_lat, main_lon, lat, lon
                            )
                            
                            if distance <= max_distance_km:
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
                    data = await self.api_client.fetch_observatory_data(
                        hydro_type=facility["hydro_type"],
                        time_type=time_type,
                        obs_code=facility["obs_code"]
                    )
                    
                    if data.get("content"):
                        content = data["content"][:count]
                        content.sort(key=lambda x: x.get("ymdhm", ""), reverse=True)
                        
                        facility_data[facility["obs_code"]] = {
                            "facility_info": facility,
                            "data": content,
                            "total_available": len(data["content"])
                        }
                except Exception as e:
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
                                thresholds = {}
                                threshold_keys = {
                                    "attention": "attwl",
                                    "warning": "wrnwl", 
                                    "alert": "almwl",
                                    "serious": "srswl"
                                }
                                
                                for alert_type, key in threshold_keys.items():
                                    value = facility["info"].get(key)
                                    if value is not None:
                                        try:
                                            thresholds[alert_type] = float(value)
                                        except (ValueError, TypeError):
                                            thresholds[alert_type] = None
                                
                                if thresholds:
                                    current_wl = values[0] if values else None
                                    alert_analysis = {}
                                    
                                    for alert_type, threshold in thresholds.items():
                                        if threshold is not None and current_wl is not None:
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
            
            return analysis_results
            
        except Exception as e:
            return {"error": f"수계 종합 분석 중 오류가 발생했습니다: {str(e)}"}

    async def _search_basin_facilities(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """WAMIS API를 사용하여 수계별 시설 검색"""
        try:
            basin = arguments.get("basin", "낙동강")
            facility_types = arguments.get("facility_types", ["waterlevel", "rainfall", "weather", "dam"])
            management_org = arguments.get("management_org")
            operation_status = arguments.get("operation_status", "y")
            
            # 수계 코드 변환
            basin_code = BASIN_CODES.get(basin, "2")  # 기본값: 낙동강
            
            # 관할기관 코드 변환
            mngorg_code = None
            if management_org:
                from hrfco_service.wamis_api import MANAGEMENT_ORG_CODES
                mngorg_code = MANAGEMENT_ORG_CODES.get(management_org)
            
            # 시설 검색
            results = {}
            
            if "waterlevel" in facility_types:
                wl_result = await self.wamis_client.search_waterlevel_stations(
                    basin=basin_code,
                    oper=operation_status,
                    mngorg=mngorg_code
                )
                results["waterlevel"] = wl_result
            
            if "rainfall" in facility_types:
                rf_result = await self.wamis_client.search_rainfall_stations(
                    basin=basin_code,
                    oper=operation_status,
                    mngorg=mngorg_code
                )
                results["rainfall"] = rf_result
            
            if "weather" in facility_types:
                we_result = await self.wamis_client.search_weather_stations(
                    basin=basin_code,
                    oper=operation_status
                )
                results["weather"] = we_result
            
            if "dam" in facility_types:
                dam_result = await self.wamis_client.search_dams(
                    basin=basin_code,
                    mngorg=mngorg_code
                )
                results["dam"] = dam_result
            
            # 통계 정보 추가
            total_facilities = 0
            facility_counts = {}
            
            for facility_type, result in results.items():
                if isinstance(result, dict) and "content" in result:
                    content = result.get("content", [])
                    if isinstance(content, list):
                        facility_counts[facility_type] = len(content)
                        total_facilities += len(content)
                    else:
                        facility_counts[facility_type] = 0
                else:
                    facility_counts[facility_type] = 0
            
            response = {
                "search_parameters": {
                    "basin": basin,
                    "basin_code": basin_code,
                    "facility_types": facility_types,
                    "management_org": management_org,
                    "operation_status": operation_status
                },
                "facility_counts": facility_counts,
                "total_facilities": total_facilities,
                "results": results
            }
            
            return response
            
        except Exception as e:
            return {
                "error": f"수계 시설 검색 중 오류가 발생했습니다: {str(e)}",
                "search_parameters": arguments
            }

    async def _analyze_water_system_relationship(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """WAMIS API를 사용하여 수계별 상류/하류 관계 분석"""
        try:
            target_obs_code = arguments.get("target_obs_code")
            basin = arguments.get("basin", "낙동강")
            hydro_type = arguments.get("hydro_type", "waterlevel")
            include_upstream = arguments.get("include_upstream", True)
            include_downstream = arguments.get("include_downstream", True)
            
            if not target_obs_code:
                raise ValueError("target_obs_code는 필수입니다")
            
            # WAMIS API를 사용하여 수계별 상류/하류 관계 분석
            result = await self.wamis_client.get_basin_water_system_analysis(
                target_obs_code=target_obs_code,
                basin=basin,
                hydro_type=hydro_type,
                include_upstream=include_upstream,
                include_downstream=include_downstream
            )
            
            return result
            
        except Exception as e:
            return {
                "error": f"수계 관계 분석 중 오류가 발생했습니다: {str(e)}",
                "analysis_parameters": arguments
            }

    async def _get_integrated_ontology_info(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """통합 온톨로지를 사용하여 관측소 정보 조회"""
        try:
            # 온톨로지 업데이트 확인
            await self.ontology_manager.update_ontology()
            
            obs_code = arguments.get("obs_code")
            obs_type = arguments.get("obs_type")
            basin = arguments.get("basin")
            source = arguments.get("source")
            
            if obs_code:
                # 특정 관측소 정보 조회
                obs_info = self.ontology_manager.get_observatory_info(obs_code)
                if obs_info:
                    return {
                        "type": "observatory_info",
                        "obs_code": obs_code,
                        "data": obs_info
                    }
                else:
                    return {
                        "error": f"관측소를 찾을 수 없습니다: {obs_code}"
                    }
            else:
                # 검색 조건으로 관측소 검색
                results = self.ontology_manager.search_observatories(
                    obs_type=obs_type,
                    basin=basin,
                    source=source
                )
                
                return {
                    "type": "observatory_search",
                    "search_criteria": {
                        "obs_type": obs_type,
                        "basin": basin,
                        "source": source
                    },
                    "total_count": len(results),
                    "results": results[:50]  # 최대 50개
                }
                
        except Exception as e:
            return {
                "error": f"통합 온톨로지 정보 조회 중 오류가 발생했습니다: {str(e)}",
                "search_parameters": arguments
            }

    async def _search_integrated_observatories(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """통합 온톨로지를 사용하여 관측소 검색"""
        try:
            # 온톨로지 업데이트 확인
            await self.ontology_manager.update_ontology()
            
            obs_type = arguments.get("obs_type")
            basin = arguments.get("basin")
            source = arguments.get("source")
            limit = arguments.get("limit", 50)
            
            results = self.ontology_manager.search_observatories(
                obs_type=obs_type,
                basin=basin,
                source=source
            )
            
            return {
                "type": "integrated_search",
                "search_criteria": {
                    "obs_type": obs_type,
                    "basin": basin,
                    "source": source,
                    "limit": limit
                },
                "total_count": len(results),
                "limited_count": min(len(results), limit),
                "results": results[:limit]
            }
            
        except Exception as e:
            return {
                "error": f"통합 관측소 검색 중 오류가 발생했습니다: {str(e)}",
                "search_parameters": arguments
            }

    async def _get_water_system_analysis(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """통합 온톨로지를 사용하여 수계 관계 분석"""
        try:
            # 온톨로지 업데이트 확인
            await self.ontology_manager.update_ontology()
            
            target_obs_code = arguments.get("target_obs_code")
            include_upstream = arguments.get("include_upstream", True)
            include_downstream = arguments.get("include_downstream", True)
            include_same_basin = arguments.get("include_same_basin", True)
            
            if not target_obs_code:
                raise ValueError("target_obs_code는 필수입니다")
            
            # 수계 관계 분석
            analysis = self.ontology_manager.get_water_system_analysis(target_obs_code)
            if not analysis:
                return {
                    "error": f"관측소의 수계 관계를 분석할 수 없습니다: {target_obs_code}"
                }
            
            # 필터링된 관계 정보
            filtered_relationships = {}
            if include_upstream:
                filtered_relationships["upstream"] = analysis["relationships"]["upstream"]
            if include_downstream:
                filtered_relationships["downstream"] = analysis["relationships"]["downstream"]
            if include_same_basin:
                filtered_relationships["same_basin"] = analysis["relationships"]["same_basin"]
            
            return {
                "type": "water_system_analysis",
                "target_station": analysis["target_station"],
                "relationships": filtered_relationships,
                "summary": analysis["summary"],
                "analysis_criteria": {
                    "include_upstream": include_upstream,
                    "include_downstream": include_downstream,
                    "include_same_basin": include_same_basin
                }
            }
            
        except Exception as e:
            return {
                "error": f"수계 관계 분석 중 오류가 발생했습니다: {str(e)}",
                "analysis_parameters": arguments
            }

    async def _get_basin_comprehensive_summary(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """통합 온톨로지를 사용하여 수계 종합 요약"""
        try:
            # 온톨로지 업데이트 확인
            await self.ontology_manager.update_ontology()
            
            basin = arguments.get("basin", "낙동강")
            include_statistics = arguments.get("include_statistics", True)
            include_stations = arguments.get("include_stations", False)
            
            # 수계 요약 정보
            basin_summary = self.ontology_manager.get_basin_summary(basin)
            if not basin_summary:
                return {
                    "error": f"수계 정보를 찾을 수 없습니다: {basin}"
                }
            
            # 온톨로지 전체 요약
            ontology_summary = self.ontology_manager.get_integrated_ontology_summary()
            
            result = {
                "type": "basin_comprehensive_summary",
                "basin": basin,
                "basin_summary": basin_summary,
                "ontology_summary": ontology_summary if include_statistics else None
            }
            
            # 관측소 목록 포함 여부
            if not include_stations:
                result["basin_summary"].pop("stations", None)
            
            return result
            
        except Exception as e:
            return {
                "error": f"수계 종합 요약 중 오류가 발생했습니다: {str(e)}",
                "summary_parameters": arguments
            }

    async def run(self):
        """MCP 서버를 실행합니다"""
        print("🚀 HRFCO MCP Server 시작 중...", file=sys.stderr)
        print(f"📡 API URL: {self.api_client.BASE_URL}", file=sys.stderr)
        print("✅ MCP 프로토콜 준비 완료", file=sys.stderr)
        
        while True:
            try:
                # STDIN에서 JSON-RPC 요청 읽기
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                
                request = json.loads(line.strip())
                response = await self.handle_request(request)
                
                # STDOUT으로 JSON-RPC 응답 출력
                print(json.dumps(response, ensure_ascii=False), flush=True)
                
            except json.JSONDecodeError as e:
                print(json.dumps({
                    "jsonrpc": "2.0",
                    "id": 0,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }, ensure_ascii=False), flush=True)
            except Exception as e:
                print(json.dumps({
                    "jsonrpc": "2.0",
                    "id": 0,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }, ensure_ascii=False), flush=True)

async def main():
    """메인 함수"""
    server = HRFCOMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main()) 