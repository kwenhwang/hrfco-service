# -*- coding: utf-8 -*-
"""
통합 온톨로지 매니저
기상청, 홍수통제소, WAMIS API의 정보를 통합하여 관리
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class IntegratedOntologyManager:
    """통합 온톨로지 매니저"""
    
    def __init__(self):
        self.observatories = {}  # 통합 관측소 정보
        self.basins = {}        # 수계 정보
        self.relationships = {}  # 관측소 간 관계
        self.last_update = None
        self.update_interval = timedelta(hours=6)  # 6시간마다 업데이트
        
    async def initialize_ontology(self):
        """온톨로지 초기화"""
        logger.info("통합 온톨로지 초기화 시작")
        
        # 1. 홍수통제소 API에서 관측소 정보 수집
        await self._collect_hrfco_data()
        
        # 2. WAMIS API에서 수계 정보 수집
        await self._collect_wamis_data()
        
        # 3. 기상청 API에서 기상 관측소 정보 수집
        await self._collect_weather_data()
        
        # 4. 관측소 간 관계 분석
        await self._analyze_relationships()
        
        self.last_update = datetime.now()
        logger.info("통합 온톨로지 초기화 완료")
    
    async def _collect_hrfco_data(self):
        """홍수통제소 API 데이터 수집"""
        try:
            from .api import HRFCOAPIClient
            from .cache import CacheManager
            cache_manager = CacheManager()
            api_client = HRFCOAPIClient(cache_manager)
            
            # 수위 관측소 정보
            waterlevel_info = await api_client.fetch_observatory_info("waterlevel")
            if waterlevel_info and waterlevel_info.get("content"):
                for obs in waterlevel_info["content"]:
                    if not isinstance(obs, dict):
                        continue
                        
                    obs_code = obs.get("wlobscd")
                    if obs_code:
                        self.observatories[obs_code] = {
                            "obs_code": obs_code,
                            "obs_name": obs.get("obsnm", ""),
                            "obs_type": "waterlevel",
                            "source": "hrfco",
                            "lat": obs.get("lat", ""),
                            "lon": obs.get("lon", ""),
                            "addr": obs.get("addr", ""),
                            "thresholds": self._extract_thresholds(obs),
                            "hrfco_data": obs
                        }
            
            # 강우량 관측소 정보
            rainfall_info = await api_client.fetch_observatory_info("rainfall")
            if rainfall_info and rainfall_info.get("content"):
                for obs in rainfall_info["content"]:
                    if not isinstance(obs, dict):
                        continue
                        
                    obs_code = obs.get("rfobscd")
                    if obs_code:
                        self.observatories[obs_code] = {
                            "obs_code": obs_code,
                            "obs_name": obs.get("obsnm", ""),
                            "obs_type": "rainfall",
                            "source": "hrfco",
                            "lat": obs.get("lat", ""),
                            "lon": obs.get("lon", ""),
                            "addr": obs.get("addr", ""),
                            "hrfco_data": obs
                        }
            
            # 댐 정보
            dam_info = await api_client.fetch_observatory_info("dam")
            if dam_info and dam_info.get("content"):
                for obs in dam_info["content"]:
                    if not isinstance(obs, dict):
                        continue
                        
                    obs_code = obs.get("dmobscd")
                    if obs_code:
                        self.observatories[obs_code] = {
                            "obs_code": obs_code,
                            "obs_name": obs.get("obsnm", ""),
                            "obs_type": "dam",
                            "source": "hrfco",
                            "lat": obs.get("lat", ""),
                            "lon": obs.get("lon", ""),
                            "addr": obs.get("addr", ""),
                            "hrfco_data": obs
                        }
            
            logger.info(f"홍수통제소 API에서 {len(self.observatories)}개 관측소 정보 수집")
            
        except Exception as e:
            logger.error(f"홍수통제소 API 데이터 수집 오류: {str(e)}")
    
    async def _collect_wamis_data(self):
        """WAMIS API 데이터 수집"""
        try:
            from .wamis_api import WAMISAPIClient, BASIN_CODES
            wamis_client = WAMISAPIClient()
            
            # 각 수계별로 관측소 정보 수집
            for basin_name, basin_code in BASIN_CODES.items():
                basin_data = {
                    "basin_code": basin_code,
                    "basin_name": basin_name,
                    "stations": {}
                }
                
                # 수위 관측소
                wl_result = await wamis_client.search_waterlevel_stations(
                    basin=basin_code, oper="y"
                )
                if wl_result.get("content"):
                    for obs in wl_result["content"]:
                        obs_code = obs.get("obscd")
                        if obs_code:
                            basin_data["stations"][obs_code] = {
                                "obs_code": obs_code,
                                "obs_name": obs.get("obsnm", ""),
                                "obs_type": "waterlevel",
                                "source": "wamis",
                                "sbsncd": obs.get("sbsncd", ""),
                                "bbsnnm": obs.get("bbsnnm", ""),
                                "mngorg": obs.get("mngorg", ""),
                                "wamis_data": obs
                            }
                
                # 강우량 관측소
                rf_result = await wamis_client.search_rainfall_stations(
                    basin=basin_code, oper="y"
                )
                if rf_result.get("content"):
                    for obs in rf_result["content"]:
                        obs_code = obs.get("obscd")
                        if obs_code:
                            basin_data["stations"][obs_code] = {
                                "obs_code": obs_code,
                                "obs_name": obs.get("obsnm", ""),
                                "obs_type": "rainfall",
                                "source": "wamis",
                                "sbsncd": obs.get("sbsncd", ""),
                                "bbsnnm": obs.get("bbsnnm", ""),
                                "mngorg": obs.get("mngorg", ""),
                                "wamis_data": obs
                            }
                
                # 댐 정보
                dam_result = await wamis_client.search_dams(basin=basin_code)
                if dam_result.get("content"):
                    for obs in dam_result["content"]:
                        obs_code = obs.get("damcd")
                        if obs_code:
                            basin_data["stations"][obs_code] = {
                                "obs_code": obs_code,
                                "obs_name": obs.get("damnm", ""),
                                "obs_type": "dam",
                                "source": "wamis",
                                "sbsncd": obs.get("sbsncd", ""),
                                "bbsnnm": obs.get("bbsnnm", ""),
                                "mngorg": obs.get("mggvnm", ""),
                                "wamis_data": obs
                            }
                
                self.basins[basin_name] = basin_data
                
                # 기존 관측소 정보와 통합
                for obs_code, obs_info in basin_data["stations"].items():
                    if obs_code in self.observatories:
                        # 기존 정보에 WAMIS 정보 추가
                        self.observatories[obs_code].update({
                            "wamis_data": obs_info.get("wamis_data"),
                            "sbsncd": obs_info.get("sbsncd"),
                            "bbsnnm": obs_info.get("bbsnnm"),
                            "mngorg": obs_info.get("mngorg")
                        })
                    else:
                        # 새로운 관측소 추가
                        self.observatories[obs_code] = obs_info
            
            logger.info(f"WAMIS API에서 {len(self.basins)}개 수계 정보 수집")
            
        except Exception as e:
            logger.error(f"WAMIS API 데이터 수집 오류: {str(e)}")
    
    async def _collect_weather_data(self):
        """기상청 API 데이터 수집 (향후 확장)"""
        # 기상청 API는 향후 구현 예정
        logger.info("기상청 API 데이터 수집 (향후 구현)")
    
    async def _analyze_relationships(self):
        """관측소 간 관계 분석"""
        try:
            # 1. 수계별 그룹화
            basin_groups = {}
            for obs_code, obs_info in self.observatories.items():
                basin = obs_info.get("bbsnnm", "unknown")
                if basin not in basin_groups:
                    basin_groups[basin] = []
                basin_groups[basin].append(obs_info)
            
            # 2. 표준유역코드별 상류/하류 관계 분석
            for basin_name, stations in basin_groups.items():
                # 표준유역코드별로 정렬
                sorted_stations = sorted(stations, key=lambda x: x.get("sbsncd", ""))
                
                for i, station in enumerate(sorted_stations):
                    obs_code = station.get("obs_code")
                    if not obs_code:  # obs_code가 None이면 건너뛰기
                        continue
                        
                    sbsncd = station.get("sbsncd", "")
                    
                    if obs_code not in self.relationships:
                        self.relationships[obs_code] = {
                            "upstream": [],
                            "downstream": [],
                            "same_basin": [],
                            "nearby": []
                        }
                    
                    # 같은 표준유역의 다른 관측소들
                    for other_station in sorted_stations:
                        other_obs_code = other_station.get("obs_code")
                        if not other_obs_code or other_obs_code == obs_code:
                            continue
                            
                        other_sbsncd = other_station.get("sbsncd", "")
                        
                        # 안전한 접근을 위한 기본값 설정
                        if obs_code not in self.relationships:
                            self.relationships[obs_code] = {
                                "upstream": [],
                                "downstream": [],
                                "same_basin": [],
                                "nearby": []
                            }
                        
                        if other_sbsncd == sbsncd:
                            if "same_basin" not in self.relationships[obs_code]:
                                self.relationships[obs_code]["same_basin"] = []
                            self.relationships[obs_code]["same_basin"].append({
                                "obs_code": other_obs_code,
                                "obs_name": other_station.get("obs_name", ""),
                                "obs_type": other_station.get("obs_type", "")
                            })
                        elif other_sbsncd < sbsncd:  # 상류
                            if "upstream" not in self.relationships[obs_code]:
                                self.relationships[obs_code]["upstream"] = []
                            self.relationships[obs_code]["upstream"].append({
                                "obs_code": other_obs_code,
                                "obs_name": other_station.get("obs_name", ""),
                                "obs_type": other_station.get("obs_type", ""),
                                "sbsncd": other_sbsncd
                            })
                        elif other_sbsncd > sbsncd:  # 하류
                            if "downstream" not in self.relationships[obs_code]:
                                self.relationships[obs_code]["downstream"] = []
                            self.relationships[obs_code]["downstream"].append({
                                "obs_code": other_obs_code,
                                "obs_name": other_station.get("obs_name", ""),
                                "obs_type": other_station.get("obs_type", ""),
                                "sbsncd": other_sbsncd
                            })
            
            logger.info(f"관측소 간 관계 분석 완료: {len(self.relationships)}개 관측소")
            
        except Exception as e:
            logger.error(f"관측소 간 관계 분석 오류: {str(e)}")
    
    def _extract_thresholds(self, obs_data: Dict) -> Dict:
        """위험 수위 기준 추출"""
        thresholds = {}
        
        # 홍수통제소 API의 위험 수위 기준
        if "wl" in obs_data:
            wl_thresholds = obs_data.get("wl", {})
            if isinstance(wl_thresholds, dict):
                thresholds.update({
                    "attention": wl_thresholds.get("attention"),
                    "warning": wl_thresholds.get("warning"),
                    "alert": wl_thresholds.get("alert"),
                    "serious": wl_thresholds.get("serious")
                })
        
        return thresholds
    
    def get_observatory_info(self, obs_code: str) -> Optional[Dict]:
        """관측소 정보 조회"""
        return self.observatories.get(obs_code)
    
    def search_observatories(self, 
                           obs_type: Optional[str] = None,
                           basin: Optional[str] = None,
                           source: Optional[str] = None) -> List[Dict]:
        """관측소 검색"""
        results = []
        
        for obs_code, obs_info in self.observatories.items():
            # 타입 필터
            if obs_type and obs_info.get("obs_type") != obs_type:
                continue
            
            # 수계 필터
            if basin and obs_info.get("bbsnnm") != basin:
                continue
            
            # 소스 필터
            if source and obs_info.get("source") != source:
                continue
            
            results.append(obs_info)
        
        return results
    
    def get_water_system_analysis(self, target_obs_code: str) -> Optional[Dict]:
        """수계 관계 분석"""
        if target_obs_code not in self.relationships:
            return None
        
        target_info = self.get_observatory_info(target_obs_code)
        if not target_info:
            return None
        
        relationships = self.relationships[target_obs_code]
        
        # 안전한 접근을 위한 기본값 설정
        upstream = relationships.get("upstream", [])
        downstream = relationships.get("downstream", [])
        same_basin = relationships.get("same_basin", [])
        nearby = relationships.get("nearby", [])
        
        return {
            "target_station": target_info,
            "relationships": {
                "upstream": upstream,
                "downstream": downstream,
                "same_basin": same_basin,
                "nearby": nearby
            },
            "summary": {
                "upstream_count": len(upstream),
                "downstream_count": len(downstream),
                "same_basin_count": len(same_basin),
                "nearby_count": len(nearby)
            }
        }
    
    def get_basin_summary(self, basin_name: str) -> Optional[Dict]:
        """수계 요약 정보"""
        if basin_name not in self.basins:
            return None
        
        basin_data = self.basins[basin_name]
        stations = basin_data["stations"]
        
        # 타입별 통계
        type_counts = {}
        for obs_info in stations.values():
            obs_type = obs_info.get("obs_type", "unknown")
            type_counts[obs_type] = type_counts.get(obs_type, 0) + 1
        
        return {
            "basin_name": basin_name,
            "basin_code": basin_data["basin_code"],
            "total_stations": len(stations),
            "type_distribution": type_counts,
            "stations": list(stations.values())
        }
    
    def get_integrated_ontology_summary(self) -> Dict:
        """통합 온톨로지 요약"""
        total_observatories = len(self.observatories)
        total_basins = len(self.basins)
        total_relationships = len(self.relationships)
        
        # 소스별 통계
        source_counts = {}
        type_counts = {}
        
        for obs_info in self.observatories.values():
            source = obs_info.get("source", "unknown")
            obs_type = obs_info.get("obs_type", "unknown")
            
            source_counts[source] = source_counts.get(source, 0) + 1
            type_counts[obs_type] = type_counts.get(obs_type, 0) + 1
        
        return {
            "total_observatories": total_observatories,
            "total_basins": total_basins,
            "total_relationships": total_relationships,
            "source_distribution": source_counts,
            "type_distribution": type_counts,
            "last_update": self.last_update.isoformat() if self.last_update else None
        }
    
    async def update_ontology(self):
        """온톨로지 업데이트"""
        if (self.last_update is None or 
            datetime.now() - self.last_update > self.update_interval):
            await self.initialize_ontology() 