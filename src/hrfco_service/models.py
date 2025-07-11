# -*- coding: utf-8 -*-
"""
HRFCO Service Data Models and Constants
"""
from typing import Dict, List, Literal

# 수문 데이터 타입 정의
HYDRO_TYPES = {
    # 수위 (Water Level)
    "waterlevel": {
        "code_key": "wlobscd", 
        "name": "수위", 
        "unit": "m", 
        "value_key": "wl",
        "fields": ["ymdhm", "wl", "fw"],  # 기본 반환 필드: 시간, 수위, 유량
        "all_fields": ["ymdhm", "wl", "fw", "ec", "etc"],  # 조회 가능한 모든 필드
        "alert_keys": {
            "att": "attwl", "wrn": "wrnwl", "alm": "almwl", 
            "srs": "srswl", "plan": "pfh"
        },  # 임계값 키
        "description": "하천의 특정 지점에서의 수위(해발고도 또는 기준면부터의 높이)와 유량 정보를 제공합니다."
    },
    # 강수량 (Rainfall)
    "rainfall": {
        "code_key": "rfobscd", 
        "name": "강수량", 
        "unit": "mm", 
        "value_key": "rf",
        "fields": ["ymdhm", "rf"],  # 기본 반환 필드: 시간, 강수량
        "all_fields": ["ymdhm", "rf"],
        "alert_keys": {},  # 강수량 자체에는 표준 임계값 없음
        "description": "특정 지점에서의 일정 시간 동안 내린 비의 양을 제공합니다."
    },
    # 댐 (Dam)
    "dam": {
        "code_key": "dmobscd", 
        "name": "댐", 
        "unit": "varies", 
        "value_key": "swl",  # 단위가 다양함 (EL.m, m³/s 등)
        "fields": ["ymdhm", "swl", "inf", "tototf"],  # 기본: 시간, 저수위, 유입량, 총방류량
        "all_fields": ["ymdhm", "swl", "inf", "esp", "ecpc", "otf", "tototf", "dmst", "dmopsn"],  # 가능한 필드들
        "alert_keys": {
            "ltd": "ltdwl", "inf": "infwl", "fld": "fldwl", "hltd": "hltdwl"
        },  # 댐별 상이, 대표 예시
        "description": "댐의 저수위, 저수량, 유입량, 방류량 등의 운영 상태 정보를 제공합니다."
    },
    # 보 (Bo - Weir)
    "bo": {
        "code_key": "boobscd", 
        "name": "보", 
        "unit": "varies", 
        "value_key": "swl",
        "fields": ["ymdhm", "swl", "inf", "tototf"],  # 기본: 시간, 저수위(상류), 유입량, 총방류량
        "all_fields": ["ymdhm", "swl", "inf", "esp", "ecpc", "otf", "tototf", "bost", "boopsn"],
        "alert_keys": {
            "mng": "mngwl", "cnt": "cntwl"
        },  # 보별 상이, 대표 예시
        "description": "보의 상/하류 수위, 유입량, 방류량, 수문 개방 상태 등의 정보를 제공합니다."
    }
}

# 시간 타입 정의
TIME_TYPES = {
    "10M": "10분",
    "1H": "1시간", 
    "6H": "6시간",
    "1D": "1일"
}

# 알림 상태 정의
ALERT_STATUS = Literal["normal", "attention", "warning", "alert", "serious"]

# API 응답 상태
API_STATUS = Literal["success", "error", "partial"]

class HydroData:
    """수문 데이터 모델"""
    
    def __init__(self, data: Dict):
        self.ymdhm = data.get("ymdhm")  # 시간
        self.value = None
        self.alert_status = None
        self.raw_data = data
    
    def set_value(self, value_key: str, value: float):
        """값 설정"""
        self.value = value
        setattr(self, value_key, value)
    
    def set_alert_status(self, status: ALERT_STATUS):
        """알림 상태 설정"""
        self.alert_status = status
    
    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        result = self.raw_data.copy()
        if self.alert_status:
            result["alert_status"] = self.alert_status
        return result

class ObservatoryInfo:
    """관측소 정보 모델"""
    
    def __init__(self, data: Dict):
        self.obsnm = data.get("obsnm", "")  # 관측소명
        self.agcnm = data.get("agcnm", "")  # 관리기관명
        self.addr = data.get("addr", "")     # 주소
        self.etcaddr = data.get("etcaddr", "")  # 상세주소
        self.lon = data.get("lon")           # 경도
        self.lat = data.get("lat")           # 위도
        self.gdt = data.get("gdt")           # 설치일
        self.pfh = data.get("pfh")           # 계획홍수위
        self.raw_data = data
    
    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        return {
            "obsnm": self.obsnm,
            "agcnm": self.agcnm,
            "addr": self.addr,
            "etcaddr": self.etcaddr,
            "lon": self.lon,
            "lat": self.lat,
            "gdt": self.gdt,
            "pfh": self.pfh
        } 