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
    
    async def fetch_observatory_info(self, hydro_type: str) -> dict:
        # 관측소 제원 정보
        url = f"{self.BASE_URL}/{self.SERVICE_KEY}/{hydro_type}/info.json"
        try:
            response = await self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "content": []}
    
    async def fetch_observatory_data(self, hydro_type: str, time_type: str, obs_code: Optional[str] = None, sdt: Optional[str] = None, edt: Optional[str] = None) -> dict:
        # 실시간 자료
        url = f"{self.BASE_URL}/{self.SERVICE_KEY}/{hydro_type}/list/{time_type}"
        if obs_code:
            url += f"/{obs_code}"
        
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
        """주변 수문 데이터 조회"""
        address = arguments.get("address")
        radius_km = arguments.get("radius_km", 10.0)
        hydro_type = arguments.get("hydro_type")
        time_type = arguments.get("time_type", "1H")
        
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
        
        # 2. 관측소 정보 조회
        observatory_info = await self.api_client.fetch_observatory_info(hydro_type)
        if not observatory_info.get("content"):
            return {
                "type": "error",
                "message": "관측소 정보를 조회할 수 없습니다."
            }
        
        # 3. 반경 내 관측소 필터링
        nearby_observatories = []
        for obs in observatory_info["content"]:
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
                    nearby_observatories.append({
                        "obs_code": obs.get("dmobscd") or obs.get("wlobscd") or obs.get("rfobscd"),
                        "obs_name": obs.get("obsnm", ""),
                        "address": obs.get("addr", ""),
                        "distance_km": round(distance, 2),
                        "coordinates": {"lat": obs_lat, "lon": obs_lon}
                    })
        
        # 거리순으로 정렬
        nearby_observatories.sort(key=lambda x: x["distance_km"])
        
        # 4. 각 관측소의 최신 데이터 조회 (최대 10개)
        results = []
        for obs in nearby_observatories[:10]:
            obs_data = await self.api_client.fetch_observatory_data(
                hydro_type, time_type, obs["obs_code"]
            )
            
            if obs_data.get("content"):
                results.append({
                    "observatory": obs,
                    "data": obs_data["content"][0] if obs_data["content"] else None
                })
        
        return {
            "type": "hydro_data_nearby",
            "address": address,
            "target_coordinates": {"lat": target_lat, "lon": target_lon},
            "radius_km": radius_km,
            "hydro_type": hydro_type,
            "time_type": time_type,
            "total_observatories": len(nearby_observatories),
            "results": results
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