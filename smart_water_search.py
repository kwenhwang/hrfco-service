#!/usr/bin/env python3
"""
AI-Friendly Water Data Search System
자연어 질의를 통한 지능형 수문 데이터 검색
"""
import asyncio
import json
import re
from typing import Dict, List, Any, Optional
from difflib import SequenceMatcher
import httpx
from dotenv import load_dotenv
import os

load_dotenv()

class SmartWaterSearch:
    def __init__(self):
        self.api_key = os.getenv('HRFCO_API_KEY', '')
        self.base_url = "http://api.hrfco.go.kr"
        self.stations_cache = {}
        
        # 한국 주요 지역/강 매핑
        self.location_mapping = {
            "서울": ["서울", "한강", "청계천"],
            "부산": ["부산", "낙동강", "수영강"],
            "대구": ["대구", "낙동강", "금호강"],
            "인천": ["인천", "한강", "굴포천"],
            "광주": ["광주", "영산강", "황룡강"],
            "대전": ["대전", "금강", "갑천"],
            "울산": ["울산", "태화강", "회야강"],
            "경기": ["경기", "한강", "임진강"],
            "강원": ["강원", "한강", "낙동강"],
            "충북": ["충북", "한강", "금강"],
            "충남": ["충남", "금강", "한강"],
            "전북": ["전북", "금강", "만경강"],
            "전남": ["전남", "영산강", "섬진강"],
            "경북": ["경북", "낙동강", "형산강"],
            "경남": ["경남", "낙동강", "남강"],
            "제주": ["제주", "한천", "천미천"]
        }
        
        self.river_keywords = ["한강", "낙동강", "금강", "영산강", "섬진강", "임진강"]
    
    async def get_all_stations(self, hydro_type: str = "waterlevel") -> List[Dict]:
        """모든 관측소 데이터 캐싱"""
        if hydro_type in self.stations_cache:
            return self.stations_cache[hydro_type]
        
        try:
            url = f"{self.base_url}/{self.api_key}/{hydro_type}/info.json"
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                stations = data.get("content", [])
                self.stations_cache[hydro_type] = stations
                return stations
        except Exception as e:
            return []
    
    def normalize_query(self, query: str) -> Dict[str, Any]:
        """자연어 질의 정규화"""
        query = query.strip().replace(" ", "")
        
        # 데이터 타입 추출
        data_type = "waterlevel"
        if any(keyword in query for keyword in ["강우", "비", "강수"]):
            data_type = "rainfall"
        elif "댐" in query:
            data_type = "dam"
        
        # 지역/강 이름 추출
        location_hints = []
        for region, keywords in self.location_mapping.items():
            if any(keyword in query for keyword in keywords):
                location_hints.extend(keywords)
        
        # 강 이름 직접 매칭
        for river in self.river_keywords:
            if river in query:
                location_hints.append(river)
        
        return {
            "original": query,
            "data_type": data_type,
            "location_hints": list(set(location_hints)),
            "clean_query": re.sub(r'(수위|강우|비|강수|댐)', '', query)
        }
    
    def calculate_similarity(self, station: Dict, query_info: Dict) -> float:
        """관측소와 질의 간 유사도 계산"""
        score = 0.0
        station_name = station.get("obsnm", "")
        station_addr = station.get("addr", "")
        
        # 관측소명 직접 매칭
        for hint in query_info["location_hints"]:
            if hint in station_name:
                score += 0.5
            if hint in station_addr:
                score += 0.3
        
        # 문자열 유사도
        name_similarity = SequenceMatcher(None, query_info["clean_query"], station_name).ratio()
        addr_similarity = SequenceMatcher(None, query_info["clean_query"], station_addr).ratio()
        
        score += max(name_similarity, addr_similarity) * 0.4
        
        return min(score, 1.0)
    
    async def search_stations_by_name(self, location_name: str, data_type: str = "waterlevel", 
                                    auto_fetch_data: bool = False, limit: int = 5) -> Dict[str, Any]:
        """지역명으로 관측소 검색"""
        query_info = self.normalize_query(location_name)
        stations = await self.get_all_stations(query_info["data_type"])
        
        if not stations:
            return {"error": "관측소 데이터를 가져올 수 없습니다"}
        
        # 유사도 계산 및 정렬
        scored_stations = []
        for station in stations:
            similarity = self.calculate_similarity(station, query_info)
            if similarity > 0.1:  # 최소 임계값
                scored_stations.append((station, similarity))
        
        # 점수순 정렬
        scored_stations.sort(key=lambda x: x[1], reverse=True)
        top_stations = [station for station, score in scored_stations[:limit]]
        
        result = {
            "query": location_name,
            "data_type": query_info["data_type"],
            "found_stations": len(top_stations),
            "total_available": len(stations),
            "stations": []
        }
        
        for station in top_stations:
            station_info = {
                "code": station.get("wlobscd") or station.get("rfobscd") or station.get("damcd"),
                "name": station.get("obsnm"),
                "address": station.get("addr"),
                "agency": station.get("agcnm")
            }
            
            # 자동 데이터 조회
            if auto_fetch_data and station_info["code"]:
                try:
                    data = await self.get_station_data(station_info["code"], query_info["data_type"])
                    station_info["current_data"] = data
                except:
                    station_info["current_data"] = "데이터 조회 실패"
            
            result["stations"].append(station_info)
        
        return result
    
    async def get_station_data(self, obs_code: str, data_type: str = "waterlevel") -> Dict:
        """관측소 실시간 데이터 조회"""
        try:
            url = f"{self.base_url}/{self.api_key}/{data_type}/data.json"
            params = {"obs_code": obs_code, "time_type": "1H"}
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(url, params=params)
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"error": "데이터 없음"}
        except:
            return {"error": "조회 실패"}
    
    async def get_water_info_by_location(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """원스톱 수문 정보 조회"""
        search_result = await self.search_stations_by_name(query, auto_fetch_data=True, limit=limit)
        
        if "error" in search_result:
            # 검색 실패 시 대안 제시
            alternatives = await self.suggest_alternatives(query)
            return {
                "status": "no_match",
                "message": f"'{query}'에 대한 관측소를 찾을 수 없습니다",
                "suggestions": alternatives
            }
        
        return {
            "status": "success",
            "summary": f"{query} 관련 {search_result['found_stations']}개 관측소 발견",
            "data": search_result
        }
    
    async def suggest_alternatives(self, query: str) -> List[str]:
        """검색 실패 시 대안 제시"""
        stations = await self.get_all_stations("waterlevel")
        suggestions = []
        
        # 유사한 지역명 찾기
        for station in stations[:50]:  # 성능을 위해 제한
            name = station.get("obsnm", "")
            addr = station.get("addr", "")
            if any(char in name + addr for char in query):
                suggestions.append(f"{name} ({addr})")
        
        return suggestions[:5]
    
    async def recommend_nearby_stations(self, location: str, radius: int = 20, 
                                      priority: str = "distance") -> Dict[str, Any]:
        """주변 관측소 추천"""
        # 간단한 구현 - 실제로는 좌표 기반 거리 계산 필요
        search_result = await self.search_stations_by_name(location, limit=10)
        
        if "error" in search_result:
            return search_result
        
        return {
            "location": location,
            "radius_km": radius,
            "priority": priority,
            "recommendations": search_result["stations"][:5]
        }

# FastAPI 통합
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Smart Water Search API", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

search_engine = SmartWaterSearch()

@app.get("/search/station")
async def search_station_endpoint(location_name: str, data_type: str = "waterlevel", 
                                auto_fetch_data: bool = False, limit: int = 5):
    return await search_engine.search_stations_by_name(location_name, data_type, auto_fetch_data, limit)

@app.get("/search/water-info")
async def water_info_endpoint(query: str, limit: int = 5):
    return await search_engine.get_water_info_by_location(query, limit)

@app.get("/search/nearby")
async def nearby_stations_endpoint(location: str, radius: int = 20, priority: str = "distance"):
    return await search_engine.recommend_nearby_stations(location, radius, priority)

if __name__ == "__main__":
    import uvicorn
    print("🔍 Smart Water Search System Starting...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
