#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
여러 지역 테스트 스크립트
"""
import asyncio
import httpx
import os
import math

class GeocodingAPI:
    """주소 → 좌표 변환 (OpenStreetMap Nominatim + 지역명 매핑)"""
    
    KAKAO_API_KEY = "617541448c319c443c1fdf168c555e48"
    KAKAO_BASE_URL = "https://dapi.kakao.com/v2/local/search/address.json"
    NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org/search"
    
    def __init__(self):
        self.session = httpx.AsyncClient(timeout=10)
    
    async def geocode_address(self, address: str):
        """주소를 좌표로 변환 (여러 방법 시도)"""
        
        # 1. 새로운 지역명 매핑 모듈에서 먼저 확인
        from src.hrfco_service.location_mapping import get_location_coordinates
        coordinates = get_location_coordinates(address)
        if coordinates:
            print(f"  📍 매핑 테이블에서 찾음")
            return coordinates
        
        # 2. 카카오 API 시도
        try:
            headers = {
                "Authorization": f"KakaoAK {self.KAKAO_API_KEY}"
            }
            params = {
                "query": address
            }
            
            response = await self.session.get(self.KAKAO_BASE_URL, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("documents"):
                doc = data["documents"][0]
                print(f"  📍 카카오 API에서 찾음")
                return (float(doc["y"]), float(doc["x"]))  # (위도, 경도)
        except Exception as e:
            print(f"  ❌ 카카오 API 오류: {str(e)}")
        
        # 3. OpenStreetMap Nominatim API 시도
        try:
            params = {
                "q": f"{address}, South Korea",
                "format": "json",
                "limit": 1
            }
            
            response = await self.session.get(self.NOMINATIM_BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data:
                result = data[0]
                print(f"  📍 OpenStreetMap API에서 찾음")
                return (float(result["lat"]), float(result["lon"]))
        except Exception as e:
            print(f"  ❌ OpenStreetMap API 오류: {str(e)}")
        
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

class HRFCOAPI:
    """HRFCO API 클라이언트"""
    
    BASE_URL = "https://api.hrfco.go.kr"
    SERVICE_KEY = os.environ.get("HRFCO_API_KEY", "your-api-key-here")
    
    def __init__(self):
        self.session = httpx.AsyncClient(timeout=10)
    
    async def fetch_observatory_info(self, hydro_type: str) -> dict:
        url = f"{self.BASE_URL}/{self.SERVICE_KEY}/{hydro_type}/info.json"
        try:
            response = await self.session.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "content": []}

async def test_region(geocoding_client, api_client, distance_calculator, region_name):
    """지역 테스트"""
    print(f"\n🔬 {region_name} 테스트 시작...")
    
    # 1. 주소 변환 테스트
    print(f"\n🔍 주소 변환 테스트: {region_name}")
    coordinates = await geocoding_client.geocode_address(region_name)
    
    if coordinates:
        lat, lon = coordinates
        print(f"✅ 성공: 위도 {lat}, 경도 {lon}")
        
        # 2. 주변 검색 테스트
        print(f"\n🎯 주변 검색 테스트: {region_name}")
        print(f"  📍 대상 좌표: 위도 {lat}, 경도 {lon}")
        
        # 수위 관측소 정보 조회
        observatory_info = await api_client.fetch_observatory_info("waterlevel")
        if not observatory_info.get("content"):
            print("❌ 관측소 정보 조회 실패")
            return
        
        print(f"📊 총 {len(observatory_info['content'])}개 수위 관측소 발견")
        
        # 반경 내 관측소 필터링 (20km)
        radius_km = 20.0
        nearby_observatories = []
        
        for obs in observatory_info["content"]:
            lat_str = obs.get("lat", "")
            lon_str = obs.get("lon", "")
            
            if lat_str and lon_str:
                # 좌표 파싱
                try:
                    parts_lat = lat_str.strip().split('-')
                    parts_lon = lon_str.strip().split('-')
                    
                    if len(parts_lat) >= 2 and len(parts_lon) >= 2:
                        obs_lat = float(parts_lat[0]) + float(parts_lat[1])/60 + (float(parts_lat[2])/3600 if len(parts_lat) > 2 else 0)
                        obs_lon = float(parts_lon[0]) + float(parts_lon[1])/60 + (float(parts_lon[2])/3600 if len(parts_lon) > 2 else 0)
                        
                        distance = distance_calculator.haversine_distance(lat, lon, obs_lat, obs_lon)
                        
                        if distance <= radius_km:
                            nearby_observatories.append({
                                "obs_code": obs.get("wlobscd", ""),
                                "obs_name": obs.get("obsnm", ""),
                                "address": obs.get("addr", ""),
                                "distance_km": round(distance, 2)
                            })
                except:
                    continue
        
        # 거리순으로 정렬
        nearby_observatories.sort(key=lambda x: x["distance_km"])
        
        print(f"🎯 반경 {radius_km}km 내 관측소: {len(nearby_observatories)}개")
        
        # 상위 10개 출력
        for i, obs in enumerate(nearby_observatories[:10], 1):
            print(f"  📍 {obs['obs_name']} ({obs['obs_code']}) - {obs['distance_km']}km")
            if obs['address']:
                print(f"     📍 주소: {obs['address']}")
        
        if len(nearby_observatories) > 10:
            print(f"  ... 외 {len(nearby_observatories) - 10}개")
        
        return len(nearby_observatories)
    else:
        print(f"❌ 실패: 주소를 좌표로 변환할 수 없습니다")
        return 0

async def main():
    """메인 함수"""
    print("🚀 여러 지역 테스트 시작")
    
    # API 키 설정
    api_key = os.environ.get("HRFCO_API_KEY")
    if not api_key or api_key == "your-api-key-here":
        print("❌ HRFCO_API_KEY 환경변수가 설정되지 않았습니다.")
        return
    
    # 클라이언트 초기화
    geocoding_client = GeocodingAPI()
    api_client = HRFCOAPI()
    distance_calculator = DistanceCalculator()
    
    # 테스트할 지역들
    test_regions = [
        "서울 강남구",
        "부산 해운대구", 
        "대전 유성구",
        "인천 연수구",
        "광주 서구",
        "대구 수성구",
        "울산 남구",
        "수원",
        "성남",
        "의정부",
        "안양",
        "부천",
        "광명",
        "평택",
        "과천",
        "오산",
        "시흥",
        "군포",
        "의왕",
        "하남",
        "용인",
        "파주",
        "이천",
        "안성",
        "김포",
        "화성",
        "광주",
        "여주",
        "양평",
        "고양",
        "남양주",
        "구리",
        "포천",
        "연천",
        "가평",
        "춘천",
        "원주",
        "강릉",
        "동해",
        "태백",
        "속초",
        "삼척",
        "청주",
        "충주",
        "제천",
        "보은",
        "옥천",
        "영동",
        "증평",
        "진천",
        "괴산",
        "음성",
        "단양",
        "천안",
        "공주",
        "보령",
        "아산",
        "서산",
        "논산",
        "계룡",
        "당진",
        "금산",
        "부여",
        "서천",
        "청양",
        "홍성",
        "예산",
        "태안",
        "전주",
        "군산",
        "익산",
        "정읍",
        "남원",
        "김제",
        "완주",
        "진안",
        "무주",
        "장수",
        "임실",
        "순창",
        "고창",
        "부안",
        "목포",
        "여수",
        "순천",
        "나주",
        "광양",
        "담양",
        "곡성",
        "구례",
        "고흥",
        "보성",
        "화순",
        "장흥",
        "강진",
        "해남",
        "영암",
        "무안",
        "함평",
        "영광",
        "장성",
        "완도",
        "진도",
        "신안",
        "포항",
        "경산",
        "김천",
        "안동",
        "구미",
        "영주",
        "영천",
        "상주",
        "문경",
        "경주",
        "의성",
        "청송",
        "영양",
        "영덕",
        "청도",
        "고령",
        "성주",
        "칠곡",
        "예천",
        "봉화",
        "울진",
        "울릉",
        "창원",
        "진주",
        "통영",
        "사천",
        "김해",
        "밀양",
        "거제",
        "양산",
        "의령",
        "함안",
        "창녕",
        "고성",
        "남해",
        "하동",
        "산청",
        "함양",
        "거창",
        "합천",
        "제주"
    ]
    
    results = {}
    total_regions = len(test_regions)
    successful_regions = 0
    
    for i, region in enumerate(test_regions, 1):
        print(f"\n{'='*60}")
        print(f"진행률: {i}/{total_regions} ({i/total_regions*100:.1f}%)")
        
        try:
            count = await test_region(geocoding_client, api_client, distance_calculator, region)
            if count > 0:
                successful_regions += 1
                results[region] = count
        except Exception as e:
            print(f"❌ {region} 테스트 중 오류: {str(e)}")
    
    # 결과 요약
    print(f"\n{'='*60}")
    print("📊 테스트 결과 요약")
    print(f"총 테스트 지역: {total_regions}개")
    print(f"성공한 지역: {successful_regions}개")
    print(f"성공률: {successful_regions/total_regions*100:.1f}%")
    
    if results:
        print(f"\n🎯 관측소가 가장 많은 지역 (상위 10개):")
        sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
        for i, (region, count) in enumerate(sorted_results[:10], 1):
            print(f"  {i:2d}. {region}: {count}개 관측소")
    
    await geocoding_client.session.aclose()
    await api_client.session.aclose()

if __name__ == "__main__":
    asyncio.run(main()) 