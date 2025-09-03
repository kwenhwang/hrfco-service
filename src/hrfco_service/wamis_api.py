# -*- coding: utf-8 -*-
"""
WAMIS API 클라이언트
"""

import httpx
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class WAMISAPIClient:
    """WAMIS API 클라이언트"""
    
    BASE_URL = "http://www.wamis.go.kr:8080/wamis/openapi/wkw"
    DAM_URL = "http://www.wamis.go.kr:8080/wamis/openapi/wkd"
    
    def __init__(self):
        self.session = httpx.AsyncClient(timeout=30)
    
    async def get_dam_hourly_data(
        self,
        damcd: str,
        startdt: Optional[str] = None,
        enddt: Optional[str] = None,
        output: str = "json"
    ) -> Dict[str, Any]:
        """댐수문정보 시자료 조회
        
        Args:
            damcd: 댐 코드
            startdt: 시작일 (YYYYMMDD)
            enddt: 종료일 (YYYYMMDD)
            output: 출력 포맷 (json/xml)
        """
        url = f"{self.DAM_URL}/mn_hrdata"
        
        params = {
            "damcd": damcd,
            "output": output
        }
        
        if startdt:
            params["startdt"] = startdt
        if enddt:
            params["enddt"] = enddt
        
        try:
            response = await self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            # WAMIS API 응답 구조 변환
            if "list" in data:
                return {"content": data["list"], "result": data.get("result", {}), "count": data.get("count", 0)}
            return data
        except Exception as e:
            logger.error(f"댐 시자료 조회 오류: {str(e)}")
            return {"error": str(e), "content": []}
    
    async def get_dam_daily_data(
        self,
        damcd: str,
        startdt: Optional[str] = None,
        enddt: Optional[str] = None,
        output: str = "json"
    ) -> Dict[str, Any]:
        """댐수문정보 일자료 조회
        
        Args:
            damcd: 댐 코드
            startdt: 시작일 (YYYYMMDD)
            enddt: 종료일 (YYYYMMDD)
            output: 출력 포맷 (json/xml)
        """
        url = f"{self.DAM_URL}/mn_dtdata"
        
        params = {
            "damcd": damcd,
            "output": output
        }
        
        if startdt:
            params["startdt"] = startdt
        if enddt:
            params["enddt"] = enddt
        
        try:
            response = await self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            # WAMIS API 응답 구조 변환
            if "list" in data:
                return {"content": data["list"], "result": data.get("result", {}), "count": data.get("count", 0)}
            return data
        except Exception as e:
            logger.error(f"댐 일자료 조회 오류: {str(e)}")
            return {"error": str(e), "content": []}
    
    async def get_dam_monthly_data(
        self,
        damcd: str,
        startyear: Optional[str] = None,
        endyear: Optional[str] = None,
        output: str = "json"
    ) -> Dict[str, Any]:
        """댐수문정보 월자료 조회
        
        Args:
            damcd: 댐 코드
            startyear: 시작연도 (YYYY)
            endyear: 종료연도 (YYYY)
            output: 출력 포맷 (json/xml)
        """
        url = f"{self.DAM_URL}/mn_mndata"
        
        params = {
            "damcd": damcd,
            "output": output
        }
        
        if startyear:
            params["startyear"] = startyear
        if endyear:
            params["endyear"] = endyear
        
        try:
            response = await self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            # WAMIS API 응답 구조 변환
            if "list" in data:
                return {"content": data["list"], "result": data.get("result", {}), "count": data.get("count", 0)}
            return data
        except Exception as e:
            logger.error(f"댐 월자료 조회 오류: {str(e)}")
            return {"error": str(e), "content": []}
    
    async def analyze_dam_discharge_wamis(
        self,
        dam_name: Optional[str] = None,
        damcd: Optional[str] = None,
        period_months: int = 6
    ) -> Dict[str, Any]:
        """WAMIS API를 사용한 댐 방류량 분석 (이름 또는 코드로 조회)
        
        Args:
            dam_name: 댐 이름 (코드가 없을 경우 사용)
            damcd: 댐 코드 (이름보다 우선)
            period_months: 분석 기간 (개월)
        """
        try:
            if not damcd and dam_name:
                # 댐 이름으로 댐 코드 검색
                dam_search_result = await self.search_dams(keynm=dam_name)
                if "error" in dam_search_result or not dam_search_result.get("content"):
                    return {"type": "error", "message": f"댐 '{dam_name}'을(를) 찾을 수 없습니다."}
                
                content = dam_search_result["content"]
                if len(content) > 1:
                    exact_match = next((d for d in content if d.get("damnm") == dam_name), None)
                    if not exact_match:
                        dam_list = [f'{d.get("damnm")} ({d.get("damcd")})' for d in content]
                        return {"type": "error", "message": f"여러 개의 댐이 검색되었습니다: {', '.join(dam_list)}"}
                    dam_info = exact_match
                else:
                    dam_info = content[0]
                
                damcd = dam_info.get("damcd")

            if not damcd:
                return {"type": "error", "message": "분석할 댐의 이름 또는 코드를 제공해야 합니다."}

            # 날짜 범위 계산
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_months * 30)
            
            startdt = start_date.strftime("%Y%m%d")
            enddt = end_date.strftime("%Y%m%d")
            
            # 일자료 조회
            daily_data = await self.get_dam_daily_data(damcd, startdt, enddt)
            
            if "error" in daily_data:
                return daily_data
            
            # 댐 정보 조회
            dam_info = await self.search_dams(keynm=damcd)
            dam_name = "알 수 없음"
            
            if "content" in dam_info and dam_info["content"]:
                for dam in dam_info["content"]:
                    if dam.get("damcd") == damcd:
                        dam_name = dam.get("damnm", "알 수 없음")
                        break
            
            # 데이터 분석
            if "content" in daily_data and daily_data["content"]:
                content = daily_data["content"]
                
                # 방류량 데이터 추출 및 정리
                discharge_data = []
                for item in content:
                    try:
                        tdqty = item.get("tdqty", "")  # 총방류량
                        if tdqty and tdqty != "" and float(tdqty) >= 0:
                            discharge_data.append({
                                "date": item.get("obsymd", ""),
                                "discharge": float(tdqty),
                                "inflow": float(item.get("iqty", 0)) if item.get("iqty") else 0,
                                "water_level": float(item.get("rwl", 0)) if item.get("rwl") else 0,
                                "power_discharge": float(item.get("edqty", 0)) if item.get("edqty") else 0,
                                "spillway_discharge": float(item.get("spdqty", 0)) if item.get("spdqty") else 0,
                                "other_discharge": float(item.get("otltdqty", 0)) if item.get("otltdqty") else 0,
                                "water_supply": float(item.get("itqty", 0)) if item.get("itqty") else 0,
                                "rainfall": float(item.get("rf", 0)) if item.get("rf") else 0
                            })
                    except (ValueError, TypeError):
                        continue
                
                if discharge_data:
                    # 날짜순 정렬 (최신순)
                    discharge_data.sort(key=lambda x: x["date"], reverse=True)
                    
                    # 통계 계산
                    discharges = [d["discharge"] for d in discharge_data]
                    avg_discharge = sum(discharges) / len(discharges)
                    max_discharge = max(discharges)
                    min_discharge = min(discharges)
                    
                    # 최근 데이터
                    latest = discharge_data[0]
                    
                    # 트렌드 분석
                    trend_analysis = self._analyze_discharge_trend_wamis(discharge_data[:10])
                    
                    # 운영 상태 분석
                    operation_status = self._analyze_dam_operation_wamis(latest)
                    
                    return {
                        "type": "wamis_dam_discharge_analysis",
                        "dam_name": dam_name,
                        "dam_code": damcd,
                        "period": f"{period_months}개월",
                        "data_points": len(discharge_data),
                        "date_range": {
                            "start": startdt,
                            "end": enddt
                        },
                        "latest_data": latest,
                        "statistics": {
                            "average_discharge": round(avg_discharge, 2),
                            "max_discharge": round(max_discharge, 2),
                            "min_discharge": round(min_discharge, 2),
                            "discharge_range": round(max_discharge - min_discharge, 2)
                        },
                        "trend_analysis": trend_analysis,
                        "operation_status": operation_status,
                        "data_source": "WAMIS API",
                        "raw_data": daily_data
                    }
                else:
                    return {
                        "type": "error",
                        "message": f"댐 {damcd}({dam_name})의 방류량 데이터를 찾을 수 없습니다.",
                        "dam_code": damcd,
                        "dam_name": dam_name
                    }
            else:
                return {
                    "type": "error",
                    "message": f"댐 {damcd}의 데이터를 조회할 수 없습니다.",
                    "dam_code": damcd
                }
                
        except Exception as e:
            logger.error(f"WAMIS 댐 방류량 분석 오류: {str(e)}")
            return {
                "type": "error",
                "message": f"댐 방류량 분석 중 오류가 발생했습니다: {str(e)}",
                "dam_code": damcd
            }
    
    def _analyze_discharge_trend_wamis(self, discharge_data: List[Dict]) -> Dict[str, Any]:
        """WAMIS 데이터 기반 방류량 트렌드 분석"""
        if len(discharge_data) < 2:
            return {"trend": "데이터 부족", "description": "트렌드 분석을 위한 충분한 데이터가 없습니다."}
        
        # 최근 데이터로 트렌드 분석
        recent_discharges = [d["discharge"] for d in discharge_data]
        
        # 단순 선형 회귀로 트렌드 계산
        n = len(recent_discharges)
        x_values = list(range(n))
        y_values = recent_discharges
        
        # 평균 계산
        x_mean = sum(x_values) / n
        y_mean = sum(y_values) / n
        
        # 기울기 계산
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator
        
        # 트렌드 해석
        if slope > 0.1:
            trend = "증가"
            description = "방류량이 증가하는 추세입니다."
        elif slope < -0.1:
            trend = "감소"
            description = "방류량이 감소하는 추세입니다."
        else:
            trend = "안정"
            description = "방류량이 안정적인 상태입니다."
        
        return {
            "trend": trend,
            "slope": round(slope, 4),
            "description": description
        }
    
    def _analyze_dam_operation_wamis(self, latest_data: Dict) -> Dict[str, Any]:
        """WAMIS 데이터 기반 댐 운영 상태 분석"""
        discharge = latest_data["discharge"]
        inflow = latest_data["inflow"]
        water_level = latest_data["water_level"]
        power_discharge = latest_data["power_discharge"]
        spillway_discharge = latest_data["spillway_discharge"]
        
        # 방류량 상태 판단
        if discharge < 10:
            discharge_status = "최소 방류"
            discharge_description = "저수량 확보를 위한 최소 방류 중"
        elif discharge < 50:
            discharge_status = "정상 방류"
            discharge_description = "정상적인 방류량"
        elif discharge < 100:
            discharge_status = "증가 방류"
            discharge_description = "방류량이 증가한 상태"
        else:
            discharge_status = "대량 방류"
            discharge_description = "대량 방류 중 - 홍수 대비 또는 여수로 방류"
        
        # 방류 구성 분석
        discharge_composition = {
            "power_ratio": round(power_discharge / discharge * 100, 1) if discharge > 0 else 0,
            "spillway_ratio": round(spillway_discharge / discharge * 100, 1) if discharge > 0 else 0,
            "other_ratio": round((discharge - power_discharge - spillway_discharge) / discharge * 100, 1) if discharge > 0 else 0
        }
        
        # 유입량 대비 방류량 비율
        if inflow > 0:
            ratio = discharge / inflow
            if ratio < 0.5:
                ratio_status = "저수 중"
                ratio_description = "유입량 대비 방류량이 낮아 저수 중"
            elif ratio < 1.0:
                ratio_status = "균형 유지"
                ratio_description = "유입량과 방류량이 균형을 유지"
            else:
                ratio_status = "방류 중"
                ratio_description = "유입량 대비 방류량이 높아 방류 중"
        else:
            ratio_status = "유입량 없음"
            ratio_description = "유입량이 없어 저수된 물을 방류 중"
        
        return {
            "discharge_status": discharge_status,
            "discharge_description": discharge_description,
            "ratio_status": ratio_status,
            "ratio_description": ratio_description,
            "discharge_composition": discharge_composition,
            "current_discharge": discharge,
            "current_inflow": inflow,
            "water_level": water_level,
            "power_discharge": power_discharge,
            "spillway_discharge": spillway_discharge
        }

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
            data = response.json()
            # WAMIS API 응답 구조 변환
            if "list" in data:
                return {"content": data["list"], "result": data.get("result", {}), "count": data.get("count", 0)}
            return data
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