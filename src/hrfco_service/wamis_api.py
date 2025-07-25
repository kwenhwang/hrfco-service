# -*- coding: utf-8 -*-
"""
WAMIS API 클라이언트
"""

import httpx
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class WAMISAPIClient:
    """WAMIS API 클라이언트"""
    
    BASE_URL = "http://www.wamis.go.kr:8080/wamis/openapi/wkw"
    DAM_URL = "http://www.wamis.go.kr:8080/wamis/openapi/wkd"
    
    def __init__(self):
        self.session = httpx.AsyncClient(timeout=30)
    
    async def search_rainfall_stations(
        self,
        basin: Optional[str] = None,
        oper: Optional[str] = None,
        mngorg: Optional[str] = None,
        obsknd: Optional[str] = None,
        keynm: Optional[str] = None,
        sort: str = "1",
        output: str = "json"
    ) -> Dict[str, Any]:
        """강수량 관측소 검색"""
        url = f"{self.BASE_URL}/rf_dubrfobs"
        
        params = {
            "sort": sort,
            "output": output
        }
        
        if basin:
            params["basin"] = basin
        if oper:
            params["oper"] = oper
        if mngorg:
            params["mngorg"] = mngorg
        if obsknd:
            params["obsknd"] = obsknd
        if keynm:
            params["keynm"] = keynm
        
        try:
            response = await self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"강수량 관측소 검색 오류: {str(e)}")
            return {"error": str(e), "content": []}
    
    async def search_waterlevel_stations(
        self,
        basin: Optional[str] = None,
        oper: Optional[str] = None,
        mngorg: Optional[str] = None,
        obsknd: Optional[str] = None,
        keynm: Optional[str] = None,
        sort: str = "1",
        output: str = "json"
    ) -> Dict[str, Any]:
        """수위 관측소 검색"""
        url = f"{self.BASE_URL}/wl_dubwlobs"
        
        params = {
            "sort": sort,
            "output": output
        }
        
        if basin:
            params["basin"] = basin
        if oper:
            params["oper"] = oper
        if mngorg:
            params["mngorg"] = mngorg
        if obsknd:
            params["obsknd"] = obsknd
        if keynm:
            params["keynm"] = keynm
        
        try:
            response = await self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"수위 관측소 검색 오류: {str(e)}")
            return {"error": str(e), "content": []}
    
    async def search_weather_stations(
        self,
        basin: Optional[str] = None,
        oper: Optional[str] = None,
        keynm: Optional[str] = None,
        sort: str = "1",
        output: str = "json"
    ) -> Dict[str, Any]:
        """기상 관측소 검색"""
        url = f"{self.BASE_URL}/we_dwtwtobs"
        
        params = {
            "sort": sort,
            "output": output
        }
        
        if basin:
            params["basin"] = basin
        if oper:
            params["oper"] = oper
        if keynm:
            params["keynm"] = keynm
        
        try:
            response = await self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"기상 관측소 검색 오류: {str(e)}")
            return {"error": str(e), "content": []}
    
    async def search_dams(
        self,
        basin: Optional[str] = None,
        mngorg: Optional[str] = None,
        damdvcd: Optional[str] = None,
        keynm: Optional[str] = None,
        sort: str = "1"
    ) -> Dict[str, Any]:
        """댐 검색"""
        url = f"{self.DAM_URL}/mn_dammain"
        
        params = {
            "sort": sort
        }
        
        if basin:
            params["basin"] = basin
        if mngorg:
            params["mngorg"] = mngorg
        if damdvcd:
            params["damdvcd"] = damdvcd
        if keynm:
            params["keynm"] = keynm
        
        try:
            response = await self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"댐 검색 오류: {str(e)}")
            return {"error": str(e), "content": []}
    
    async def get_basin_facilities(
        self,
        basin: str,
        facility_types: List[str] = ["waterlevel", "rainfall", "weather", "dam"]
    ) -> Dict[str, Any]:
        """특정 수계의 모든 시설 검색"""
        results = {}
        
        try:
            if "waterlevel" in facility_types:
                wl_result = await self.search_waterlevel_stations(basin=basin, oper="y")
                results["waterlevel"] = wl_result
            
            if "rainfall" in facility_types:
                rf_result = await self.search_rainfall_stations(basin=basin, oper="y")
                results["rainfall"] = rf_result
            
            if "weather" in facility_types:
                we_result = await self.search_weather_stations(basin=basin, oper="y")
                results["weather"] = we_result
            
            if "dam" in facility_types:
                dam_result = await self.search_dams(basin=basin)
                results["dam"] = dam_result
            
            return results
            
        except Exception as e:
            logger.error(f"수계 시설 검색 오류: {str(e)}")
            return {"error": str(e)}

    async def get_basin_water_system_analysis(
        self,
        target_obs_code: str,
        basin: str,
        hydro_type: str = "waterlevel",
        include_upstream: bool = True,
        include_downstream: bool = True,
        max_distance_km: float = 50.0
    ) -> Dict[str, Any]:
        """특정 관측소의 수계별 상류/하류 관계 분석"""
        
        try:
            # 1. 대상 관측소 정보 조회
            target_info = None
            basin_code = BASIN_CODES.get(basin, "2")
            
            # 수계별 관측소 검색
            if hydro_type == "waterlevel":
                stations_result = await self.search_waterlevel_stations(
                    basin=basin_code, oper="y"
                )
            elif hydro_type == "rainfall":
                stations_result = await self.search_rainfall_stations(
                    basin=basin_code, oper="y"
                )
            else:
                return {"error": f"지원하지 않는 수문 타입: {hydro_type}"}
            
            if not isinstance(stations_result, dict) or "content" not in stations_result:
                return {"error": "관측소 정보를 조회할 수 없습니다."}
            
            # 대상 관측소 찾기
            for station in stations_result["content"]:
                if station.get("obscd") == target_obs_code:
                    target_info = station
                    break
            
            if not target_info:
                return {"error": f"관측소를 찾을 수 없습니다: {target_obs_code}"}
            
            # 2. 수계 내 모든 관측소의 위치 정보 수집
            all_stations = []
            for station in stations_result["content"]:
                # 표준유역코드(sbsncd)를 기준으로 상류/하류 관계 파악
                sbsncd = station.get("sbsncd", "")
                obsnm = station.get("obsnm", "")
                obscd = station.get("obscd", "")
                
                if sbsncd and obsnm and obscd:
                    all_stations.append({
                        "obscd": obscd,
                        "obsnm": obsnm,
                        "sbsncd": sbsncd,
                        "bbsnnm": station.get("bbsnnm", ""),
                        "mngorg": station.get("mngorg", "")
                    })
            
            # 3. 표준유역코드를 기준으로 상류/하류 분류
            target_sbsncd = target_info.get("sbsncd", "")
            
            upstream_stations = []
            downstream_stations = []
            same_basin_stations = []
            
            for station in all_stations:
                station_sbsncd = station["sbsncd"]
                
                # 같은 표준유역에 있는 관측소들
                if station_sbsncd == target_sbsncd:
                    same_basin_stations.append(station)
                # 상류 유역 (표준유역코드가 더 작은 경우)
                elif station_sbsncd < target_sbsncd:
                    upstream_stations.append(station)
                # 하류 유역 (표준유역코드가 더 큰 경우)
                elif station_sbsncd > target_sbsncd:
                    downstream_stations.append(station)
            
            # 4. 결과 구성
            result = {
                "target_station": {
                    "obscd": target_obs_code,
                    "obsnm": target_info.get("obsnm", ""),
                    "sbsncd": target_sbsncd,
                    "bbsnnm": target_info.get("bbsnnm", ""),
                    "mngorg": target_info.get("mngorg", "")
                },
                "basin_analysis": {
                    "basin": basin,
                    "basin_code": basin_code,
                    "hydro_type": hydro_type,
                    "total_stations_in_basin": len(all_stations),
                    "same_basin_stations": len(same_basin_stations),
                    "upstream_stations": len(upstream_stations) if include_upstream else 0,
                    "downstream_stations": len(downstream_stations) if include_downstream else 0
                },
                "water_system": {
                    "same_basin": same_basin_stations[:5],  # 최대 5개
                    "upstream": upstream_stations[:3] if include_upstream else [],  # 최대 3개
                    "downstream": downstream_stations[:3] if include_downstream else []  # 최대 3개
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"수계 분석 오류: {str(e)}")
            return {"error": f"수계 분석 중 오류가 발생했습니다: {str(e)}"}

    async def get_water_system_hierarchy(
        self,
        basin: str,
        hydro_type: str = "waterlevel"
    ) -> Dict[str, Any]:
        """수계별 관측소 계층 구조 분석"""
        
        try:
            basin_code = BASIN_CODES.get(basin, "2")
            
            # 수계별 관측소 검색
            if hydro_type == "waterlevel":
                stations_result = await self.search_waterlevel_stations(
                    basin=basin_code, oper="y"
                )
            elif hydro_type == "rainfall":
                stations_result = await self.search_rainfall_stations(
                    basin=basin_code, oper="y"
                )
            else:
                return {"error": f"지원하지 않는 수문 타입: {hydro_type}"}
            
            if not isinstance(stations_result, dict) or "content" not in stations_result:
                return {"error": "관측소 정보를 조회할 수 없습니다."}
            
            # 표준유역코드별로 그룹화
            basin_hierarchy = {}
            for station in stations_result["content"]:
                sbsncd = station.get("sbsncd", "")
                if sbsncd:
                    if sbsncd not in basin_hierarchy:
                        basin_hierarchy[sbsncd] = {
                            "sbsncd": sbsncd,
                            "bbsnnm": station.get("bbsnnm", ""),
                            "stations": []
                        }
                    
                    basin_hierarchy[sbsncd]["stations"].append({
                        "obscd": station.get("obscd", ""),
                        "obsnm": station.get("obsnm", ""),
                        "mngorg": station.get("mngorg", "")
                    })
            
            # 표준유역코드 순으로 정렬
            sorted_hierarchy = sorted(basin_hierarchy.values(), key=lambda x: x["sbsncd"])
            
            return {
                "basin": basin,
                "basin_code": basin_code,
                "hydro_type": hydro_type,
                "total_sub_basins": len(sorted_hierarchy),
                "hierarchy": sorted_hierarchy
            }
            
        except Exception as e:
            logger.error(f"수계 계층 구조 분석 오류: {str(e)}")
            return {"error": f"수계 계층 구조 분석 중 오류가 발생했습니다: {str(e)}"}

# 수계 코드 매핑
BASIN_CODES = {
    "한강": "1",
    "낙동강": "2", 
    "금강": "3",
    "섬진강": "4",
    "영산강": "5",
    "제주도": "6"
}

# 관할기관 코드 매핑
MANAGEMENT_ORG_CODES = {
    "환경부": "1",
    "한국수자원공사": "2", 
    "한국농어촌공사": "3",
    "기상청": "4",
    "한국수력원자력": "9"
}

# 관측방법 코드 매핑
OBSERVATION_METHOD_CODES = {
    "보통": "1",
    "T/M": "2",
    "자기": "3"
}

# 댐 용도 코드 매핑
DAM_PURPOSE_CODES = {
    "다목적": "1",
    "생공전용": "2",
    "발전지용": "3", 
    "조정지댐": "4",
    "기타": "5"
} 