#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HRFCO API 주변 검색 테스트
"""
import asyncio
import httpx
import os
import math

class GeocodingAPI:
    """카카오 지도 API를 사용한 주소 → 좌표 변환"""
    
    KAKAO_API_KEY = "617541448c319c443c1fdf168c555e48"
    BASE_URL = "https://dapi.kakao.com/v2/local/search/address.json"
    
    def __init__(self):
        self.session = httpx.AsyncClient(timeout=10)
    
    async def geocode_address(self, address: str):
        """주소를 좌표로 변환"""
        try:
            headers = {
                "Authorization": f"KakaoAK {self.KAKAO_API_KEY}"
            }
            params = {
                "query": address
            }
            
            response = await self.session.get(self.BASE_URL, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("documents"):
                doc = data["documents"][0]
                return (float(doc["y"]), float(doc["x"]))  # (위도, 경도)
            
            return None
        except Exception as e:
            print(f"지오코딩 오류: {str(e)}")
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
    def parse_coordinates(coord_str: str):
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

async def test_geocoding():
    """지오코딩 테스트"""
    geocoding = GeocodingAPI()
    
    test_addresses = [
        "세종 반곡동",
        "한강",
        "서울 강남구",
        "부산 해운대구"
    ]
    
    for address in test_addresses:
        print(f"\n🔍 주소 변환 테스트: {address}")
        coordinates = await geocoding.geocode_address(address)
        if coordinates:
            lat, lon = coordinates
            print(f"✅ 성공: 위도 {lat}, 경도 {lon}")
        else:
            print("❌ 실패: 좌표 변환 불가")

async def test_distance_calculation():
    """거리 계산 테스트"""
    calculator = DistanceCalculator()
    
    # 세종 반곡동 좌표 (예시)
    sejong_lat, sejong_lon = 36.4877, 127.2827
    
    # 테스트 좌표들
    test_coords = [
        ("서울 강남구", 37.5172, 127.0473),
        ("부산 해운대구", 35.1586, 129.1603),
        ("대전 유성구", 36.3626, 127.3566),
        ("인천 연수구", 37.4106, 126.6498)
    ]
    
    print(f"\n📏 거리 계산 테스트 (기준: 세종 반곡동)")
    for name, lat, lon in test_coords:
        distance = calculator.haversine_distance(sejong_lat, sejong_lon, lat, lon)
        print(f"📍 {name}: {distance:.1f}km")

async def test_coordinate_parsing():
    """좌표 파싱 테스트"""
    calculator = DistanceCalculator()
    
    test_coords = [
        "37-20-40",
        "127-16-48",
        "36-29-12",
        "128-56-48"
    ]
    
    print(f"\n🔢 좌표 파싱 테스트")
    for coord_str in test_coords:
        parsed = calculator.parse_coordinates(coord_str)
        if parsed:
            print(f"✅ {coord_str} → {parsed:.6f}°")
        else:
            print(f"❌ {coord_str} → 파싱 실패")

async def test_nearby_search():
    """주변 검색 통합 테스트"""
    geocoding = GeocodingAPI()
    calculator = DistanceCalculator()
    
    # 1. 주소를 좌표로 변환
    address = "세종 반곡동"
    print(f"\n🎯 주변 검색 테스트: {address}")
    
    coordinates = await geocoding.geocode_address(address)
    if not coordinates:
        print("❌ 주소 변환 실패")
        return
    
    target_lat, target_lon = coordinates
    print(f"📍 대상 좌표: 위도 {target_lat}, 경도 {target_lon}")
    
    # 2. HRFCO API에서 관측소 정보 조회
    api_key = os.environ.get("HRFCO_API_KEY", "FE18B23B-A81B-4246-9674-E8D641902A42")
    base_url = "https://api.hrfco.go.kr"
    
    async with httpx.AsyncClient(timeout=10) as client:
        # 수위 관측소 정보 조회
        url = f"{base_url}/{api_key}/waterlevel/info.json"
        response = await client.get(url)
        
        if response.status_code == 200:
            data = response.json()
            observatories = data.get("content", [])
            
            print(f"📊 총 {len(observatories)}개 수위 관측소 발견")
            
            # 3. 반경 10km 내 관측소 필터링
            nearby_obs = []
            for obs in observatories:
                lat_str = obs.get("lat", "")
                lon_str = obs.get("lon", "")
                
                obs_lat = calculator.parse_coordinates(lat_str)
                obs_lon = calculator.parse_coordinates(lon_str)
                
                if obs_lat and obs_lon:
                    distance = calculator.haversine_distance(
                        target_lat, target_lon, obs_lat, obs_lon
                    )
                    
                    if distance <= 10.0:  # 10km 반경
                        nearby_obs.append({
                            "obs_code": obs.get("wlobscd"),
                            "obs_name": obs.get("obsnm", ""),
                            "address": obs.get("addr", ""),
                            "distance_km": round(distance, 2)
                        })
            
            # 거리순으로 정렬
            nearby_obs.sort(key=lambda x: x["distance_km"])
            
            print(f"🎯 반경 10km 내 관측소: {len(nearby_obs)}개")
            for obs in nearby_obs[:5]:  # 상위 5개만 표시
                print(f"  📍 {obs['obs_name']} ({obs['obs_code']}) - {obs['distance_km']}km")
        else:
            print(f"❌ 관측소 정보 조회 실패: {response.status_code}")

if __name__ == "__main__":
    print("🔬 HRFCO API 주변 검색 테스트 시작...")
    asyncio.run(test_geocoding())
    asyncio.run(test_distance_calculation())
    asyncio.run(test_coordinate_parsing())
    asyncio.run(test_nearby_search()) 