#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
충남 청양군 테스트
"""
import asyncio
import httpx
import os
import math

class GeocodingAPI:
    """주소 → 좌표 변환 (OpenStreetMap Nominatim + 지역명 매핑)"""
    
    def __init__(self):
        self.session = httpx.AsyncClient(timeout=10)
        
        # 지역명 매핑 테이블 (백업용)
        self.region_mapping = {
            "세종": (36.4877, 127.2827),
            "세종 반곡동": (36.4877, 127.2827),
            "한강": (37.5665, 126.9780),
            "한강대교": (37.5665, 126.9780),
            "서울": (37.5665, 126.9780),
            "서울 강남구": (37.5172, 127.0473),
            "부산": (35.1796, 129.0756),
            "부산 해운대구": (35.1586, 129.1603),
            "대전": (36.3504, 127.3845),
            "대전 유성구": (36.3626, 127.3566),
            "인천": (37.4563, 126.7052),
            "인천 연수구": (37.4106, 126.6498),
            "광주": (35.1595, 126.8526),
            "대구": (35.8714, 128.6014),
            "울산": (35.5384, 129.3114),
            "제주": (33.4996, 126.5312),
            "강원도": (37.8228, 128.1555),
            "충청북도": (36.8, 127.7),
            "충청남도": (36.6, 126.9),
            "충남": (36.6, 126.9),
            "충남 청양군": (36.45, 126.8),
            "청양군": (36.45, 126.8),
            "전라북도": (35.7175, 127.1530),
            "전라남도": (34.8679, 126.9910),
            "경상북도": (36.4919, 128.8889),
            "경상남도": (35.4606, 128.2132),
        }
    
    async def geocode_address(self, address: str):
        """주소를 좌표로 변환 (여러 방법 시도)"""
        
        # 1. 지역명 매핑 테이블에서 먼저 확인
        if address in self.region_mapping:
            print(f"  📍 매핑 테이블에서 찾음")
            return self.region_mapping[address]
        
        # 4. 부분 매칭 시도
        for region, coords in self.region_mapping.items():
            if region in address or address in region:
                print(f"  📍 부분 매칭으로 찾음: {region}")
                return coords
        
        return None

async def test_cheongyang():
    """충남 청양군 테스트"""
    geocoding = GeocodingAPI()
    
    test_addresses = [
        "충남 청양군",
        "청양군",
        "충남",
        "충청남도"
    ]
    
    for address in test_addresses:
        print(f"\n🔍 주소 변환 테스트: {address}")
        coordinates = await geocoding.geocode_address(address)
        if coordinates:
            lat, lon = coordinates
            print(f"✅ 성공: 위도 {lat}, 경도 {lon}")
        else:
            print("❌ 실패: 좌표 변환 불가")

async def test_cheongyang_nearby():
    """충남 청양군 주변 검색 테스트"""
    geocoding = GeocodingAPI()
    
    # 1. 주소를 좌표로 변환
    address = "충남 청양군"
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
            
            # 3. 반경 20km 내 관측소 필터링
            nearby_obs = []
            for obs in observatories:
                lat_str = obs.get("lat", "")
                lon_str = obs.get("lon", "")
                
                # 좌표 파싱 (도-분-초 → 십진도)
                try:
                    if lat_str and lon_str:
                        # 위도 파싱
                        lat_parts = lat_str.strip().split('-')
                        if len(lat_parts) >= 2:
                            lat_deg = float(lat_parts[0])
                            lat_min = float(lat_parts[1])
                            lat_sec = float(lat_parts[2]) if len(lat_parts) > 2 else 0
                            obs_lat = lat_deg + lat_min/60 + lat_sec/3600
                        else:
                            continue
                        
                        # 경도 파싱
                        lon_parts = lon_str.strip().split('-')
                        if len(lon_parts) >= 2:
                            lon_deg = float(lon_parts[0])
                            lon_min = float(lon_parts[1])
                            lon_sec = float(lon_parts[2]) if len(lon_parts) > 2 else 0
                            obs_lon = lon_deg + lon_min/60 + lon_sec/3600
                        else:
                            continue
                        
                        # 거리 계산
                        R = 6371  # 지구 반지름 (km)
                        lat1_rad = math.radians(target_lat)
                        lon1_rad = math.radians(target_lon)
                        lat2_rad = math.radians(obs_lat)
                        lon2_rad = math.radians(obs_lon)
                        
                        dlat = lat2_rad - lat1_rad
                        dlon = lon2_rad - lon1_rad
                        
                        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
                        c = 2 * math.asin(math.sqrt(a))
                        distance = R * c
                        
                        if distance <= 20.0:  # 20km 반경
                            nearby_obs.append({
                                "obs_code": obs.get("wlobscd"),
                                "obs_name": obs.get("obsnm", ""),
                                "address": obs.get("addr", ""),
                                "distance_km": round(distance, 2)
                            })
                except:
                    continue
            
            # 거리순으로 정렬
            nearby_obs.sort(key=lambda x: x["distance_km"])
            
            print(f"🎯 반경 20km 내 관측소: {len(nearby_obs)}개")
            for obs in nearby_obs[:10]:  # 상위 10개만 표시
                print(f"  📍 {obs['obs_name']} ({obs['obs_code']}) - {obs['distance_km']}km")
        else:
            print(f"❌ 관측소 정보 조회 실패: {response.status_code}")

if __name__ == "__main__":
    print("🔬 충남 청양군 테스트 시작...")
    asyncio.run(test_cheongyang())
    asyncio.run(test_cheongyang_nearby()) 