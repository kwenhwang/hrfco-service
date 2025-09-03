"""
ChatGPT Function Calling을 위한 홍수통제소(HRFCO) 및 기상관측소 API 구현
"""

import json
import asyncio
import httpx
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import os
from dotenv import load_dotenv
import urllib.parse

load_dotenv()

# API 키 설정 (실제 키 적용)
HRFCO_API_KEY = os.getenv("HRFCO_API_KEY")
KMA_API_KEY = os.getenv("KMA_API_KEY")

# KMA API 키 URL 디코딩 (필요한 경우)
if KMA_API_KEY and "%2F" in KMA_API_KEY:
    KMA_API_KEY = urllib.parse.unquote(KMA_API_KEY)

# ChatGPT Function Definitions
CHATGPT_FUNCTIONS = [
    {
        "name": "get_water_level_data",
        "description": "홍수통제소 수위 관측소 데이터를 조회합니다. 실시간 수위 정보와 위험 수위 기준을 함께 제공합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "obs_code": {
                    "type": "string",
                    "description": "수위 관측소 코드 (예: 4009670)"
                },
                "hours": {
                    "type": "integer",
                    "description": "조회할 시간 범위 (시간 단위, 기본값: 48)",
                    "default": 48
                },
                "time_type": {
                    "type": "string",
                    "enum": ["10M", "1H", "1D"],
                    "description": "시간 단위 (기본값: 1H)",
                    "default": "1H"
                },
                "include_thresholds": {
                    "type": "boolean",
                    "description": "위험 수위 기준 포함 여부 (기본값: true)",
                    "default": True
                }
            },
            "required": ["obs_code"]
        }
    },
    {
        "name": "get_rainfall_data",
        "description": "홍수통제소 강우량 관측소 데이터를 조회합니다. 실시간 강우량 정보와 누적 강우량을 제공합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "obs_code": {
                    "type": "string",
                    "description": "강우량 관측소 코드"
                },
                "hours": {
                    "type": "integer",
                    "description": "조회할 시간 범위 (시간 단위, 기본값: 48)",
                    "default": 48
                },
                "time_type": {
                    "type": "string",
                    "enum": ["10M", "1H", "1D"],
                    "description": "시간 단위 (기본값: 1H)",
                    "default": "1H"
                }
            },
            "required": ["obs_code"]
        }
    },
    {
        "name": "search_nearby_observatories",
        "description": "특정 지역 주변의 수위, 강우량, 댐 관측소를 검색합니다. 위치 기반으로 가까운 관측소들을 찾아줍니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "address": {
                    "type": "string",
                    "description": "검색할 주소 또는 지역명 (예: '하동군 대석교', '서울시 강남구')"
                },
                "radius_km": {
                    "type": "number",
                    "description": "검색 반경 (km, 기본값: 20)",
                    "default": 20
                },
                "hydro_type": {
                    "type": "string",
                    "enum": ["waterlevel", "rainfall", "dam", "all"],
                    "description": "관측소 유형 (기본값: all)",
                    "default": "all"
                }
            },
            "required": ["address"]
        }
    },
    {
        "name": "get_comprehensive_flood_analysis",
        "description": "특정 지역의 종합 홍수 위험 분석을 수행합니다. 수위, 강우량, 댐 데이터를 종합하여 홍수 위험도를 평가합니다.",
        "parameters": {
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
                "hours": {
                    "type": "integer",
                    "description": "분석 기간 (시간 단위, 기본값: 72)",
                    "default": 72
                },
                "include_forecast": {
                    "type": "boolean",
                    "description": "예보 정보 포함 여부 (기본값: false)",
                    "default": False
                }
            },
            "required": ["water_level_obs"]
        }
    },
    {
        "name": "get_weather_data",
        "description": "기상청 관측소의 날씨 데이터를 조회합니다. 온도, 습도, 강수량, 풍속 등의 기상 정보를 제공합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "station_id": {
                    "type": "string",
                    "description": "기상관측소 ID (예: '108' for 서울)"
                },
                "hours": {
                    "type": "integer",
                    "description": "조회할 시간 범위 (시간 단위, 기본값: 24)",
                    "default": 24
                },
                "data_type": {
                    "type": "string",
                    "enum": ["current", "hourly", "daily"],
                    "description": "데이터 유형 (기본값: hourly)",
                    "default": "hourly"
                }
            },
            "required": ["station_id"]
        }
    },
    {
        "name": "search_weather_stations",
        "description": "특정 지역 주변의 기상관측소를 검색합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "address": {
                    "type": "string",
                    "description": "검색할 주소 또는 지역명"
                },
                "radius_km": {
                    "type": "number",
                    "description": "검색 반경 (km, 기본값: 30)",
                    "default": 30
                }
            },
            "required": ["address"]
        }
    }
]


class HRFCOAPIClient:
    """홍수통제소 API 클라이언트"""
    
    def __init__(self):
        self.base_url = "http://api.hrfco.go.kr"
        self.api_key = HRFCO_API_KEY
        if not self.api_key:
            print("⚠️ HRFCO_API_KEY가 설정되지 않았습니다. 데모 데이터를 사용합니다.")
    
    def _calculate_date_range(self, time_type: str, hours: int):
        """날짜 범위 계산"""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        if time_type == "1D":
            date_format = "%Y%m%d"
        else:
            date_format = "%Y%m%d%H"
            
        return start_time.strftime(date_format), end_time.strftime(date_format)
    
    async def fetch_observatory_info(self, hydro_type: str) -> Dict:
        """관측소 정보 조회"""
        if not self.api_key:
            return self._get_demo_observatory_info(hydro_type)
        
        async with httpx.AsyncClient() as client:
            try:
                url = f"{self.base_url}/{self.api_key}/{hydro_type}/info.json"
                response = await client.get(url, timeout=30)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"API 오류: {e}")
                return self._get_demo_observatory_info(hydro_type)
    
    async def fetch_observatory_data(self, hydro_type: str, time_type: str, obs_code: str, hours: int = 48) -> Dict:
        """관측소 데이터 조회"""
        if not self.api_key:
            return self._get_demo_data(hydro_type, obs_code)
        
        start_date, end_date = self._calculate_date_range(time_type, hours)
        
        async with httpx.AsyncClient() as client:
            try:
                # 올바른 API URL 패턴: /API_KEY/hydro_type/list/time_type/obs_code/start/end.json
                url = f"{self.base_url}/{self.api_key}/{hydro_type}/list/{time_type}/{obs_code}/{start_date}/{end_date}.json"
                response = await client.get(url, timeout=30)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"API 오류: {e}")
                return self._get_demo_data(hydro_type, obs_code)
    
    def _get_demo_observatory_info(self, hydro_type: str) -> Dict:
        """데모 관측소 정보"""
        if hydro_type == "waterlevel":
            return {
                "content": [
                    {
                        "wlobscd": "4009670",
                        "obsnm": "하동군(대석교)",
                        "addr": "경상남도 하동군",
                        "lat": "35-03-33",
                        "lon": "127-47-01",
                        "lvlinterest": "2.2",
                        "lvlcaution": "4.0",
                        "lvlwarning": "5.0",
                        "lvlsevere": "5.9"
                    }
                ]
            }
        elif hydro_type == "rainfall":
            return {
                "content": [
                    {
                        "rfobscd": "4009665",
                        "obsnm": "하동군(횡천초교)",
                        "addr": "경상남도 하동군 횡천면",
                        "lat": "35-04-00",
                        "lon": "127-44-01"
                    }
                ]
            }
        return {"content": []}
    
    def _get_demo_data(self, hydro_type: str, obs_code: str) -> Dict:
        """데모 데이터"""
        current_time = datetime.now()
        demo_data = []
        
        for i in range(48):
            time_point = current_time - timedelta(hours=i)
            if hydro_type == "waterlevel":
                demo_data.append({
                    "wlobscd": obs_code,
                    "ymdhm": time_point.strftime("%Y%m%d%H"),
                    "wl": str(round(0.8 + 0.2 * (i % 10), 2)),
                    "fw": str(round(8.0 + 2.0 * (i % 5), 2))
                })
            elif hydro_type == "rainfall":
                demo_data.append({
                    "rfobscd": obs_code,
                    "ymdhm": time_point.strftime("%Y%m%d%H"),
                    "rf": str(round(max(0, 5 - i * 0.1), 1))
                })
        
        return {"content": demo_data[::-1]}


class WeatherAPIClient:
    """기상청 API 클라이언트"""
    
    def __init__(self):
        self.base_url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0"
        self.api_key = KMA_API_KEY
        # URL 디코딩 (필요시)
        if self.api_key and "%2F" in self.api_key:
            import urllib.parse
            self.api_key = urllib.parse.unquote(self.api_key)
        # 기상관측소 좌표 매핑 (격자 변환용)
        self.weather_stations = {
            "108": {"name": "서울", "nx": 60, "ny": 127},
            "159": {"name": "부산", "nx": 98, "ny": 76},
            "143": {"name": "대구", "nx": 89, "ny": 90},
            "112": {"name": "인천", "nx": 55, "ny": 124},
            "156": {"name": "광주", "nx": 58, "ny": 74},
            "133": {"name": "대전", "nx": 67, "ny": 100},
            "152": {"name": "울산", "nx": 102, "ny": 84},
            "162": {"name": "진주", "nx": 90, "ny": 77},
            "168": {"name": "통영", "nx": 87, "ny": 68}
        }
        if not self.api_key:
            print("⚠️ KMA_API_KEY가 설정되지 않았습니다. 데모 데이터를 사용합니다.")
    
    async def get_weather_data(self, station_id: str, hours: int = 24, data_type: str = "hourly") -> Dict:
        """기상 데이터 조회"""
        if not self.api_key or station_id not in self.weather_stations:
            return self._get_demo_weather_data(station_id)
        
        try:
            # 현재 시간 기준으로 날짜/시간 설정
            now = datetime.now()
            base_date = now.strftime("%Y%m%d")
            base_time = "0500"  # 05시 발표 기준
            
            station_info = self.weather_stations[station_id]
            
            async with httpx.AsyncClient() as client:
                # 단기예보 조회
                url = f"{self.base_url}/getVilageFcst"
                params = {
                    "serviceKey": self.api_key,
                    "pageNo": "1",
                    "numOfRows": "1000",
                    "dataType": "JSON",
                    "base_date": base_date,
                    "base_time": base_time,
                    "nx": station_info["nx"],
                    "ny": station_info["ny"]
                }
                
                response = await client.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                if data.get("response", {}).get("header", {}).get("resultCode") == "00":
                    items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
                    return self._process_weather_data(station_id, items, hours)
                else:
                    print(f"기상청 API 오류: {data}")
                    return self._get_demo_weather_data(station_id)
                    
        except Exception as e:
            print(f"기상청 API 호출 오류: {e}")
            return self._get_demo_weather_data(station_id)
    
    def _process_weather_data(self, station_id: str, items: List[Dict], hours: int) -> Dict:
        """기상청 API 응답 데이터 처리"""
        weather_data = []
        current_time = datetime.now()
        
        # 데이터를 시간별로 그룹핑
        time_groups = {}
        for item in items:
            fc_date = item.get("fcstDate", "")
            fc_time = item.get("fcstTime", "")
            category = item.get("category", "")
            value = item.get("fcstValue", "")
            
            if fc_date and fc_time:
                time_key = fc_date + fc_time
                if time_key not in time_groups:
                    time_groups[time_key] = {}
                time_groups[time_key][category] = value
        
        # 시간순 정렬하여 최근 hours만큼 추출
        sorted_times = sorted(time_groups.keys())[:hours]
        
        for time_key in sorted_times:
            data_group = time_groups[time_key]
            
            # 온도(TMP), 습도(REH), 강수량(PCP), 풍속(WSD) 추출
            weather_record = {
                "station_id": station_id,
                "datetime": time_key,
                "temperature": float(data_group.get("TMP", "20.0")),
                "humidity": float(data_group.get("REH", "60.0")),
                "rainfall": 0.0 if data_group.get("PCP", "강수없음") == "강수없음" else float(data_group.get("PCP", "0.0").replace("mm", "")),
                "wind_speed": float(data_group.get("WSD", "2.0"))
            }
            weather_data.append(weather_record)
        
        return {"data": weather_data}
    
    def _get_demo_weather_data(self, station_id: str) -> Dict:
        """데모 기상 데이터"""
        current_time = datetime.now()
        weather_data = []
        
        for i in range(24):
            time_point = current_time - timedelta(hours=i)
            weather_data.append({
                "station_id": station_id,
                "datetime": time_point.strftime("%Y%m%d%H%M"),
                "temperature": round(20 + 5 * (i % 3), 1),
                "humidity": round(60 + 10 * (i % 4), 1),
                "rainfall": round(max(0, 2 - i * 0.1), 1),
                "wind_speed": round(2 + 3 * (i % 2), 1)
            })
        
        return {"data": weather_data[::-1]}


class GeocodingClient:
    """지오코딩 클라이언트"""
    
    async def get_coordinates(self, address: str) -> Dict[str, float]:
        """주소를 좌표로 변환"""
        # 실제 구현에서는 Kakao, Naver, Google 등의 지오코딩 API 사용
        # 여기서는 주요 지역의 좌표 반환
        locations = {
            "하동군": {"lat": 35.067, "lon": 127.751},
            "서울": {"lat": 37.566, "lon": 126.978},
            "부산": {"lat": 35.179, "lon": 129.075},
            "대구": {"lat": 35.871, "lon": 128.601},
            "인천": {"lat": 37.456, "lon": 126.705},
            "광주": {"lat": 35.160, "lon": 126.851},
            "대전": {"lat": 36.351, "lon": 127.385},
            "울산": {"lat": 35.539, "lon": 129.311}
        }
        
        for city in locations:
            if city in address:
                return locations[city]
        
        # 기본값 (서울)
        return {"lat": 37.566, "lon": 126.978}


# ChatGPT Function Implementations
async def get_water_level_data(obs_code: str, hours: int = 48, time_type: str = "1H", include_thresholds: bool = True) -> str:
    """수위 데이터 조회"""
    client = HRFCOAPIClient()
    
    # 관측소 정보 조회
    obs_info = await client.fetch_observatory_info("waterlevel")
    target_obs = None
    
    for obs in obs_info.get("content", []):
        if obs.get("wlobscd") == obs_code:
            target_obs = obs
            break
    
    if not target_obs:
        return f"관측소 코드 {obs_code}를 찾을 수 없습니다."
    
    # 수위 데이터 조회
    data = await client.fetch_observatory_data("waterlevel", time_type, obs_code, hours)
    water_level_data = data.get("content", [])
    
    if not water_level_data:
        return f"관측소 {obs_code}의 데이터를 찾을 수 없습니다."
    
    # 최신 데이터 분석
    latest_data = water_level_data[-1] if water_level_data else {}
    current_wl = float(latest_data.get("wl", 0))
    
    result = {
        "observatory_info": {
            "obs_code": obs_code,
            "name": target_obs.get("obsnm", ""),
            "address": target_obs.get("addr", ""),
            "coordinates": {
                "lat": target_obs.get("lat", ""),
                "lon": target_obs.get("lon", "")
            }
        },
        "current_water_level": current_wl,
        "data_period": {
            "start": water_level_data[0].get("ymdhm", "") if water_level_data else "",
            "end": water_level_data[-1].get("ymdhm", "") if water_level_data else "",
            "total_records": len(water_level_data)
        },
        "recent_data": water_level_data[-10:] if len(water_level_data) > 10 else water_level_data
    }
    
    # 위험 수위 기준 추가
    if include_thresholds:
        thresholds = {
            "interest": float(target_obs.get("lvlinterest", 0)) if target_obs.get("lvlinterest") else None,
            "caution": float(target_obs.get("lvlcaution", 0)) if target_obs.get("lvlcaution") else None,
            "warning": float(target_obs.get("lvlwarning", 0)) if target_obs.get("lvlwarning") else None,
            "severe": float(target_obs.get("lvlsevere", 0)) if target_obs.get("lvlsevere") else None
        }
        
        # 현재 위험도 평가
        alert_status = "안전"
        if thresholds["severe"] and current_wl >= thresholds["severe"]:
            alert_status = "심각"
        elif thresholds["warning"] and current_wl >= thresholds["warning"]:
            alert_status = "경보"
        elif thresholds["caution"] and current_wl >= thresholds["caution"]:
            alert_status = "주의보"
        elif thresholds["interest"] and current_wl >= thresholds["interest"]:
            alert_status = "관심"
        
        result["thresholds"] = thresholds
        result["alert_status"] = alert_status
        
        # 다음 단계까지 여유
        if alert_status == "안전" and thresholds["interest"]:
            result["margin_to_next_level"] = thresholds["interest"] - current_wl
        elif alert_status == "관심" and thresholds["caution"]:
            result["margin_to_next_level"] = thresholds["caution"] - current_wl
        elif alert_status == "주의보" and thresholds["warning"]:
            result["margin_to_next_level"] = thresholds["warning"] - current_wl
        elif alert_status == "경보" and thresholds["severe"]:
            result["margin_to_next_level"] = thresholds["severe"] - current_wl
    
    return json.dumps(result, ensure_ascii=False, indent=2)


async def get_rainfall_data(obs_code: str, hours: int = 48, time_type: str = "1H") -> str:
    """강우량 데이터 조회"""
    client = HRFCOAPIClient()
    
    # 관측소 정보 조회
    obs_info = await client.fetch_observatory_info("rainfall")
    target_obs = None
    
    for obs in obs_info.get("content", []):
        if obs.get("rfobscd") == obs_code:
            target_obs = obs
            break
    
    if not target_obs:
        return f"강우량 관측소 코드 {obs_code}를 찾을 수 없습니다."
    
    # 강우량 데이터 조회
    data = await client.fetch_observatory_data("rainfall", time_type, obs_code, hours)
    rainfall_data = data.get("content", [])
    
    if not rainfall_data:
        return f"관측소 {obs_code}의 강우량 데이터를 찾을 수 없습니다."
    
    # 강우량 통계 계산
    total_rainfall = sum(float(item.get("rf", 0)) for item in rainfall_data)
    max_rainfall = max(float(item.get("rf", 0)) for item in rainfall_data)
    recent_1h = float(rainfall_data[-1].get("rf", 0)) if rainfall_data else 0
    recent_6h = sum(float(item.get("rf", 0)) for item in rainfall_data[-6:]) if len(rainfall_data) >= 6 else 0
    
    result = {
        "observatory_info": {
            "obs_code": obs_code,
            "name": target_obs.get("obsnm", ""),
            "address": target_obs.get("addr", ""),
            "coordinates": {
                "lat": target_obs.get("lat", ""),
                "lon": target_obs.get("lon", "")
            }
        },
        "rainfall_statistics": {
            "total_rainfall": round(total_rainfall, 1),
            "max_hourly_rainfall": round(max_rainfall, 1),
            "recent_1hour": round(recent_1h, 1),
            "recent_6hours": round(recent_6h, 1)
        },
        "data_period": {
            "start": rainfall_data[0].get("ymdhm", "") if rainfall_data else "",
            "end": rainfall_data[-1].get("ymdhm", "") if rainfall_data else "",
            "total_records": len(rainfall_data)
        },
        "recent_data": rainfall_data[-10:] if len(rainfall_data) > 10 else rainfall_data
    }
    
    return json.dumps(result, ensure_ascii=False, indent=2)


async def search_nearby_observatories(address: str, radius_km: float = 20, hydro_type: str = "all") -> str:
    """주변 관측소 검색"""
    geocoding_client = GeocodingClient()
    hrfco_client = HRFCOAPIClient()
    
    # 주소를 좌표로 변환
    coords = await geocoding_client.get_coordinates(address)
    target_lat, target_lon = coords["lat"], coords["lon"]
    
    # 검색할 관측소 유형 결정
    hydro_types = ["waterlevel", "rainfall", "dam"] if hydro_type == "all" else [hydro_type]
    
    nearby_observatories = []
    
    for ht in hydro_types:
        obs_info = await hrfco_client.fetch_observatory_info(ht)
        
        for obs in obs_info.get("content", []):
            # 좌표 파싱
            lat_str = obs.get("lat", "")
            lon_str = obs.get("lon", "")
            
            if lat_str and lon_str:
                try:
                    # DMS 형식을 Decimal로 변환
                    if "-" in lat_str:
                        lat_parts = lat_str.split("-")
                        obs_lat = float(lat_parts[0]) + float(lat_parts[1])/60 + float(lat_parts[2])/3600
                    else:
                        obs_lat = float(lat_str)
                    
                    if "-" in lon_str:
                        lon_parts = lon_str.split("-")
                        obs_lon = float(lon_parts[0]) + float(lon_parts[1])/60 + float(lon_parts[2])/3600
                    else:
                        obs_lon = float(lon_str)
                    
                    # 거리 계산 (Haversine 공식)
                    import math
                    R = 6371  # 지구 반지름 (km)
                    
                    lat1_rad = math.radians(target_lat)
                    lat2_rad = math.radians(obs_lat)
                    delta_lat = math.radians(obs_lat - target_lat)
                    delta_lon = math.radians(obs_lon - target_lon)
                    
                    a = (math.sin(delta_lat/2) * math.sin(delta_lat/2) + 
                         math.cos(lat1_rad) * math.cos(lat2_rad) * 
                         math.sin(delta_lon/2) * math.sin(delta_lon/2))
                    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
                    distance = R * c
                    
                    if distance <= radius_km:
                        obs_code = obs.get("wlobscd") or obs.get("rfobscd") or obs.get("dmobscd")
                        nearby_observatories.append({
                            "obs_code": obs_code,
                            "name": obs.get("obsnm", ""),
                            "address": obs.get("addr", ""),
                            "type": ht,
                            "distance_km": round(distance, 2),
                            "coordinates": {
                                "lat": obs_lat,
                                "lon": obs_lon
                            }
                        })
                        
                except (ValueError, IndexError):
                    continue
    
    # 거리순 정렬
    nearby_observatories.sort(key=lambda x: x["distance_km"])
    
    result = {
        "search_parameters": {
            "address": address,
            "target_coordinates": coords,
            "radius_km": radius_km,
            "hydro_type": hydro_type
        },
        "total_found": len(nearby_observatories),
        "observatories": nearby_observatories[:20]  # 최대 20개
    }
    
    return json.dumps(result, ensure_ascii=False, indent=2)


async def get_comprehensive_flood_analysis(water_level_obs: str, rainfall_obs: str = None, hours: int = 72, include_forecast: bool = False) -> str:
    """종합 홍수 위험 분석"""
    # 수위 데이터 조회
    wl_data = await get_water_level_data(water_level_obs, hours, include_thresholds=True)
    wl_result = json.loads(wl_data)
    
    analysis = {
        "analysis_type": "종합 홍수 위험 분석",
        "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "water_level_analysis": wl_result
    }
    
    # 강우량 데이터 추가 (있는 경우)
    if rainfall_obs:
        rf_data = await get_rainfall_data(rainfall_obs, hours)
        analysis["rainfall_analysis"] = json.loads(rf_data)
        
        # 강우량과 수위 상관관계 분석
        try:
            rf_result = json.loads(rf_data)
            rf_recent = rf_result.get("rainfall_statistics", {}).get("recent_6hours", 0)
            wl_current = wl_result.get("current_water_level", 0)
            
            risk_level = "낮음"
            if rf_recent > 50 and wl_current > 3:
                risk_level = "매우 높음"
            elif rf_recent > 30 and wl_current > 2:
                risk_level = "높음"
            elif rf_recent > 20 or wl_current > 1:
                risk_level = "보통"
            
            analysis["flood_risk_assessment"] = {
                "overall_risk_level": risk_level,
                "factors": {
                    "current_water_level": wl_current,
                    "recent_6h_rainfall": rf_recent,
                    "alert_status": wl_result.get("alert_status", "안전")
                }
            }
        except:
            pass
    
    # 예보 정보 추가 (요청시)
    if include_forecast:
        analysis["forecast_note"] = "예보 기능은 현재 개발 중입니다."
    
    return json.dumps(analysis, ensure_ascii=False, indent=2)


async def get_weather_data(station_id: str, hours: int = 24, data_type: str = "hourly") -> str:
    """기상 데이터 조회"""
    client = WeatherAPIClient()
    weather_data = await client.get_weather_data(station_id, hours, data_type)
    
    if not weather_data.get("data"):
        return f"기상관측소 {station_id}의 데이터를 찾을 수 없습니다."
    
    data_list = weather_data["data"]
    latest = data_list[-1] if data_list else {}
    
    # 통계 계산
    temperatures = [item["temperature"] for item in data_list]
    rainfall_total = sum(item["rainfall"] for item in data_list)
    
    result = {
        "station_info": {
            "station_id": station_id,
            "data_type": data_type
        },
        "current_weather": {
            "temperature": latest.get("temperature", 0),
            "humidity": latest.get("humidity", 0),
            "rainfall": latest.get("rainfall", 0),
            "wind_speed": latest.get("wind_speed", 0)
        },
        "statistics": {
            "max_temperature": max(temperatures) if temperatures else 0,
            "min_temperature": min(temperatures) if temperatures else 0,
            "avg_temperature": round(sum(temperatures) / len(temperatures), 1) if temperatures else 0,
            "total_rainfall": round(rainfall_total, 1)
        },
        "data_period": {
            "hours": hours,
            "total_records": len(data_list)
        },
        "recent_data": data_list[-10:] if len(data_list) > 10 else data_list
    }
    
    return json.dumps(result, ensure_ascii=False, indent=2)


async def search_weather_stations(address: str, radius_km: float = 30) -> str:
    """기상관측소 검색"""
    # 주요 기상관측소 정보 (실제 구현에서는 기상청 API 사용)
    weather_stations = [
        {"id": "108", "name": "서울", "lat": 37.566, "lon": 126.978},
        {"id": "159", "name": "부산", "lat": 35.179, "lon": 129.075},
        {"id": "143", "name": "대구", "lat": 35.871, "lon": 128.601},
        {"id": "112", "name": "인천", "lat": 37.456, "lon": 126.705},
        {"id": "156", "name": "광주", "lat": 35.160, "lon": 126.851},
        {"id": "133", "name": "대전", "lat": 36.351, "lon": 127.385},
        {"id": "152", "name": "울산", "lat": 35.539, "lon": 129.311},
        {"id": "162", "name": "진주", "lat": 35.165, "lon": 128.109},
        {"id": "168", "name": "통영", "lat": 34.836, "lon": 128.433}
    ]
    
    geocoding_client = GeocodingClient()
    coords = await geocoding_client.get_coordinates(address)
    target_lat, target_lon = coords["lat"], coords["lon"]
    
    nearby_stations = []
    
    for station in weather_stations:
        # 거리 계산
        import math
        R = 6371  # 지구 반지름 (km)
        
        lat1_rad = math.radians(target_lat)
        lat2_rad = math.radians(station["lat"])
        delta_lat = math.radians(station["lat"] - target_lat)
        delta_lon = math.radians(station["lon"] - target_lon)
        
        a = (math.sin(delta_lat/2) * math.sin(delta_lat/2) + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(delta_lon/2) * math.sin(delta_lon/2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        if distance <= radius_km:
            nearby_stations.append({
                "station_id": station["id"],
                "name": station["name"],
                "distance_km": round(distance, 2),
                "coordinates": {
                    "lat": station["lat"],
                    "lon": station["lon"]
                }
            })
    
    # 거리순 정렬
    nearby_stations.sort(key=lambda x: x["distance_km"])
    
    result = {
        "search_parameters": {
            "address": address,
            "target_coordinates": coords,
            "radius_km": radius_km
        },
        "total_found": len(nearby_stations),
        "weather_stations": nearby_stations
    }
    
    return json.dumps(result, ensure_ascii=False, indent=2)


# Function Router
FUNCTION_ROUTER = {
    "get_water_level_data": get_water_level_data,
    "get_rainfall_data": get_rainfall_data,
    "search_nearby_observatories": search_nearby_observatories,
    "get_comprehensive_flood_analysis": get_comprehensive_flood_analysis,
    "get_weather_data": get_weather_data,
    "search_weather_stations": search_weather_stations
}


async def execute_function(function_name: str, arguments: Dict[str, Any]) -> str:
    """Function 실행"""
    if function_name not in FUNCTION_ROUTER:
        return f"지원하지 않는 함수입니다: {function_name}"
    
    try:
        function = FUNCTION_ROUTER[function_name]
        result = await function(**arguments)
        return result
    except Exception as e:
        return f"함수 실행 중 오류가 발생했습니다: {str(e)}"


# 사용 예시
if __name__ == "__main__":
    import json
    
    # Function definitions 출력
    print("=== ChatGPT Function Definitions ===")
    print(json.dumps(CHATGPT_FUNCTIONS, ensure_ascii=False, indent=2))
    
    # 테스트 실행
    async def test_functions():
        print("\n=== 함수 테스트 ===")
        
        # 수위 데이터 조회 테스트
        print("\n1. 수위 데이터 조회:")
        result = await execute_function("get_water_level_data", {
            "obs_code": "4009670",
            "hours": 24
        })
        print(result)
        
        # 주변 관측소 검색 테스트
        print("\n2. 주변 관측소 검색:")
        result = await execute_function("search_nearby_observatories", {
            "address": "하동군 대석교",
            "radius_km": 15
        })
        print(result)
    
    # 테스트 실행
    asyncio.run(test_functions()) 