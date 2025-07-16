#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
직접 API 테스트 스크립트
Claude 없이도 HRFCO API 기능을 테스트할 수 있습니다.
"""
import asyncio
import httpx
import os
import math
from datetime import datetime, timedelta

class DirectAPITester:
    """직접 API 테스트 클래스"""
    
    BASE_URL = "https://api.hrfco.go.kr"
    SERVICE_KEY = os.environ.get("HRFCO_API_KEY")
    
    def __init__(self):
        self.session = httpx.AsyncClient(timeout=10)
    
    async def test_nearby_search(self, address: str, radius_km: int = 20):
        """주변 검색 테스트"""
        print(f"\n🔍 '{address}' 주변 {radius_km}km 내 수위관측소 검색")
        
        # 1. 주소 → 좌표 변환
        from src.hrfco_service.location_mapping import get_location_coordinates
        coordinates = get_location_coordinates(address)
        
        if not coordinates:
            print(f"❌ '{address}'의 좌표를 찾을 수 없습니다.")
            return
        
        lat, lon = coordinates
        print(f"📍 좌표: 위도 {lat}, 경도 {lon}")
        
        # 2. 수위 관측소 정보 조회
        observatory_info = await self._fetch_observatory_info("waterlevel")
        if not observatory_info.get("content"):
            print("❌ 관측소 정보 조회 실패")
            return
        
        # 3. 거리 계산 및 필터링
        nearby_stations = []
        for station in observatory_info["content"]:
            try:
                station_lat = float(station.get("lat", 0))
                station_lon = float(station.get("lon", 0))
                
                if station_lat == 0 or station_lon == 0:
                    continue
                
                distance = self._calculate_distance(lat, lon, station_lat, station_lon)
                
                if distance <= radius_km:
                    nearby_stations.append({
                        "name": station.get("obsnm", "Unknown"),
                        "distance": distance,
                        "lat": station_lat,
                        "lon": station_lon
                    })
            except (ValueError, TypeError):
                continue
        
        # 4. 결과 출력
        print(f"📊 {radius_km}km 내 관측소: {len(nearby_stations)}개")
        
        if nearby_stations:
            # 거리순 정렬
            nearby_stations.sort(key=lambda x: x["distance"])
            
            print(f"\n🎯 가장 가까운 관측소 (상위 10개):")
            for i, station in enumerate(nearby_stations[:10], 1):
                print(f"  {i:2d}. {station['name']} ({station['distance']:.1f}km)")
        
        return nearby_stations
    
    async def test_hydrological_data(self, address: str, data_type: str = "waterlevel"):
        """수문 데이터 테스트"""
        print(f"\n🌊 '{address}' 주변 {data_type} 데이터 조회")
        
        # 주변 관측소 찾기
        nearby_stations = await self.test_nearby_search(address, 20)
        
        if not nearby_stations:
            return
        
        # 가장 가까운 관측소의 데이터 조회
        closest_station = nearby_stations[0]
        print(f"\n📈 가장 가까운 관측소: {closest_station['name']}")
        
        # 오늘 날짜로 데이터 조회
        today = datetime.now().strftime("%Y%m%d")
        data = await self._fetch_hydrological_data(
            data_type, 
            closest_station["lat"], 
            closest_station["lon"], 
            today
        )
        
        if data:
            print(f"✅ {data_type} 데이터 조회 성공")
            print(f"📊 데이터 개수: {len(data)}")
            if data:
                print(f"📅 최신 데이터: {data[0] if isinstance(data[0], dict) else 'N/A'}")
        else:
            print(f"❌ {data_type} 데이터 조회 실패")
    
    async def _fetch_observatory_info(self, hydro_type: str) -> dict:
        """관측소 정보 조회"""
        url = f"{self.BASE_URL}/{self.SERVICE_KEY}/{hydro_type}/info.json"
        try:
            response = await self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ 관측소 정보 조회 오류: {str(e)}")
            return {"error": str(e), "content": []}
    
    async def _fetch_hydrological_data(self, hydro_type: str, lat: float, lon: float, date: str) -> list:
        """수문 데이터 조회"""
        url = f"{self.BASE_URL}/{self.SERVICE_KEY}/{hydro_type}/data.json"
        params = {
            "lat": lat,
            "lon": lon,
            "date": date
        }
        try:
            response = await self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("content", [])
        except Exception as e:
            print(f"❌ 수문 데이터 조회 오류: {str(e)}")
            return []
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Haversine 공식으로 거리 계산 (km)"""
        R = 6371  # 지구 반지름 (km)
        
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    async def close(self):
        """세션 종료"""
        await self.session.aclose()

async def main():
    """메인 함수"""
    print("🚀 직접 API 테스트 시작")
    
    if not os.environ.get("HRFCO_API_KEY"):
        print("❌ HRFCO_API_KEY 환경변수가 설정되지 않았습니다.")
        return
    
    tester = DirectAPITester()
    
    # 테스트할 지역들
    test_cases = [
        ("세종 반곡동", 20),
        ("청양군", 20),
        ("서울 강남구", 10),
        ("부산 해운대구", 15),
        ("대전 유성구", 12)
    ]
    
    for address, radius in test_cases:
        try:
            await tester.test_nearby_search(address, radius)
            await asyncio.sleep(1)  # API 호출 간격
        except Exception as e:
            print(f"❌ {address} 테스트 중 오류: {str(e)}")
    
    # 수문 데이터 테스트
    print(f"\n{'='*50}")
    print("🌊 수문 데이터 테스트")
    
    data_types = ["waterlevel", "rainfall", "dam", "weir"]
    for data_type in data_types:
        try:
            await tester.test_hydrological_data("세종 반곡동", data_type)
            await asyncio.sleep(1)
        except Exception as e:
            print(f"❌ {data_type} 테스트 중 오류: {str(e)}")
    
    await tester.close()
    print(f"\n✅ 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(main()) 