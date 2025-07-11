# -*- coding: utf-8 -*-
"""
HRFCO Service Observatory Management Module
"""
import time
import logging
from typing import Dict, List, Optional

from .config import Config
from .models import HYDRO_TYPES

logger = logging.getLogger(__name__)

class ObservatoryManager:
    """관측소 정보 관리 클래스"""
    
    def __init__(self):
        self.info: Dict[str, Dict[str, Dict]] = {}
        self.name_to_code: Dict[str, Dict[str, str]] = {}
        self._last_update = 0
        self._update_interval = Config.OBSERVATORY_UPDATE_INTERVAL

    def update(self, hydro_type: str, obs_data: List[Dict]) -> None:
        """관측소 정보를 업데이트합니다.
        
        Args:
            hydro_type: 수문 데이터 타입
            obs_data: 관측소 데이터 리스트
        """
        if hydro_type not in HYDRO_TYPES:
            return
        
        config = HYDRO_TYPES[hydro_type]
        code_key = config["code_key"]
        current_type_info = {}
        current_type_name_map = {}
        loaded_count = 0
        
        for item in obs_data:
            if not isinstance(item, dict) or code_key not in item:
                continue
            
            obscd = item[code_key]
            obsnm = item.get("obsnm", "")
            
            # 필요한 정보만 저장
            processed_item = {
                k: item.get(k) for k in [
                    "obsnm", "agcnm", "addr", "etcaddr", "lon", "lat", "gdt", "pfh"
                ] + list(config.get("alert_keys", {}).values()) 
                if item.get(k) is not None
            }
            
            current_type_info[obscd] = processed_item
            if obsnm:
                current_type_name_map[obsnm] = obscd
            loaded_count += 1
        
        self.info[hydro_type] = current_type_info
        self.name_to_code[hydro_type] = current_type_name_map
        self._last_update = time.time()
        logger.info(f"Updated observatory info for {hydro_type}: {loaded_count} stations")

    def get_observatory_code(self, hydro_type: str, identifier: str) -> Optional[str]:
        """관측소 코드를 찾습니다.
        
        Args:
            hydro_type: 수문 데이터 타입
            identifier: 관측소 식별자 (코드 또는 이름)
            
        Returns:
            관측소 코드 또는 None
        """
        if hydro_type not in self.info:
            return None
        
        # 직접 코드인지 확인
        if identifier in self.info[hydro_type]:
            return identifier
        
        # 이름으로 검색
        if hydro_type in self.name_to_code and identifier in self.name_to_code[hydro_type]:
            return self.name_to_code[hydro_type][identifier]
        
        # 대소문자 무시 검색
        identifier_lower = identifier.lower()
        for name, code in self.name_to_code.get(hydro_type, {}).items():
            if name.lower() == identifier_lower:
                return code
        
        return None

    def get_observatory_info(self, hydro_type: str, obs_code: str) -> Optional[Dict]:
        """관측소 정보를 가져옵니다.
        
        Args:
            hydro_type: 수문 데이터 타입
            obs_code: 관측소 코드
            
        Returns:
            관측소 정보 또는 None
        """
        if hydro_type not in self.info:
            return None
        
        return self.info[hydro_type].get(obs_code)

    def search_observatories(
        self, 
        query: str, 
        hydro_type: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict]:
        """관측소를 검색합니다.
        
        Args:
            query: 검색 쿼리
            hydro_type: 수문 데이터 타입 (None이면 모든 타입)
            limit: 최대 결과 수
            
        Returns:
            검색 결과 리스트
        """
        results = []
        query_lower = query.lower()
        
        # 검색할 타입들 결정
        search_types = [hydro_type] if hydro_type else HYDRO_TYPES.keys()
        
        for htype in search_types:
            if htype not in self.info:
                continue
            
            for obs_code, obs_info in self.info[htype].items():
                obsnm = obs_info.get("obsnm", "")
                addr = obs_info.get("addr", "")
                
                # 이름이나 주소에 검색어가 포함되어 있는지 확인
                if (query_lower in obsnm.lower() or 
                    query_lower in addr.lower() or
                    query_lower in obs_code.lower()):
                    
                    result = {
                        "hydro_type": htype,
                        "obs_code": obs_code,
                        "obsnm": obsnm,
                        "addr": addr,
                        "agcnm": obs_info.get("agcnm", ""),
                        "lon": obs_info.get("lon"),
                        "lat": obs_info.get("lat")
                    }
                    results.append(result)
                    
                    if len(results) >= limit:
                        return results
        
        return results

    def needs_update(self) -> bool:
        """업데이트가 필요한지 확인합니다."""
        return not self.info or time.time() - self._last_update > self._update_interval

    @property
    def total_stations(self) -> int:
        """총 관측소 수를 반환합니다."""
        return sum(len(stations) for stations in self.info.values())

    def get_stats(self) -> Dict:
        """관측소 통계 정보를 반환합니다."""
        stats = {
            "total_stations": self.total_stations,
            "last_update": self._last_update,
            "needs_update": self.needs_update(),
            "by_type": {}
        }
        
        for hydro_type in HYDRO_TYPES:
            count = len(self.info.get(hydro_type, {}))
            stats["by_type"][hydro_type] = count
        
        return stats 