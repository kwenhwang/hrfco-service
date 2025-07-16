#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 명령줄 테스트
Claude 없이도 HRFCO API 기능을 테스트할 수 있습니다.
"""
import os
import sys
import math
from datetime import datetime

def test_location_mapping():
    """지역 매핑 테스트"""
    print("📍 지역 매핑 테스트")
    
    from src.hrfco_service.location_mapping import get_location_coordinates
    
    test_addresses = [
        "세종 반곡동",
        "청양군", 
        "서울 강남구",
        "부산 해운대구",
        "대전 유성구",
        "인천 연수구",
        "광주 서구",
        "대구 수성구",
        "울산 남구"
    ]
    
    success_count = 0
    total_count = len(test_addresses)
    
    for address in test_addresses:
        coordinates = get_location_coordinates(address)
        if coordinates:
            lat, lon = coordinates
            print(f"✅ {address}: 위도 {lat}, 경도 {lon}")
            success_count += 1
        else:
            print(f"❌ {address}: 좌표를 찾을 수 없습니다")
    
    print(f"\n📊 결과: {success_count}/{total_count} 성공 ({success_count/total_count*100:.1f}%)")
    return success_count == total_count

def test_distance_calculation():
    """거리 계산 테스트"""
    print("\n📏 거리 계산 테스트")
    
    # 테스트 케이스들
    test_cases = [
        # (lat1, lon1, lat2, lon2, expected_distance_km)
        (37.5665, 126.9780, 37.5665, 126.9780, 0.0),  # 같은 지점
        (37.5665, 126.9780, 37.5665, 127.9780, 85.0),  # 서울-수원 대략적 거리
        (37.5665, 126.9780, 35.1796, 129.0756, 325.0),  # 서울-부산 대략적 거리
    ]
    
    def calculate_distance(lat1, lon1, lat2, lon2):
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
    
    success_count = 0
    for i, (lat1, lon1, lat2, lon2, expected) in enumerate(test_cases, 1):
        calculated = calculate_distance(lat1, lon1, lat2, lon2)
        error = abs(calculated - expected)
        
        if error < 10:  # 10km 이내 오차 허용
            print(f"✅ 테스트 {i}: 계산값 {calculated:.1f}km (예상: {expected:.1f}km)")
            success_count += 1
        else:
            print(f"❌ 테스트 {i}: 계산값 {calculated:.1f}km (예상: {expected:.1f}km)")
    
    print(f"📊 거리 계산 테스트: {success_count}/{len(test_cases)} 성공")
    return success_count == len(test_cases)

def test_api_key():
    """API 키 테스트"""
    print("\n🔑 API 키 테스트")
    
    api_key = os.environ.get("HRFCO_API_KEY")
    if api_key and api_key != "your-api-key-here":
        print(f"✅ API 키가 설정되어 있습니다: {api_key[:8]}...")
        return True
    else:
        print("❌ API 키가 설정되지 않았습니다.")
        print("환경변수 HRFCO_API_KEY를 설정해주세요.")
        return False

def test_mcp_server_import():
    """MCP 서버 임포트 테스트"""
    print("\n🔧 MCP 서버 임포트 테스트")
    
    try:
        from src.hrfco_service.server import mcp, api_client, observatory_manager
        print("✅ MCP 서버 모듈 임포트 성공")
        
        # FastMCP 인스턴스 확인
        if mcp:
            print("✅ FastMCP 인스턴스 확인 성공")
        
        # API 클라이언트 확인
        if api_client:
            print("✅ API 클라이언트 확인 성공")
        
        # 관측소 매니저 확인
        if observatory_manager:
            print("✅ 관측소 매니저 확인 성공")
        
        return True
    except Exception as e:
        print(f"❌ MCP 서버 임포트 실패: {str(e)}")
        return False

def test_location_mapping_import():
    """지역 매핑 임포트 테스트"""
    print("\n🗺️ 지역 매핑 임포트 테스트")
    
    try:
        from src.hrfco_service.location_mapping import get_location_coordinates
        print("✅ 지역 매핑 함수 임포트 성공")
        
        # 실제 테스트
        coordinates = get_location_coordinates("서울")
        if coordinates:
            print("✅ 지역 매핑 함수 실행 성공")
            return True
        else:
            print("❌ 지역 매핑 함수 실행 실패")
            return False
            
    except Exception as e:
        print(f"❌ 지역 매핑 임포트 실패: {str(e)}")
        return False

def main():
    """메인 함수"""
    print("🚀 HRFCO API 간단 테스트 시작")
    print("=" * 50)
    
    tests = [
        ("API 키 확인", test_api_key),
        ("지역 매핑 임포트", test_location_mapping_import),
        ("MCP 서버 임포트", test_mcp_server_import),
        ("지역 매핑 기능", test_location_mapping),
        ("거리 계산 기능", test_distance_calculation),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 테스트 중 오류: {str(e)}")
            results.append((test_name, False))
    
    # 결과 요약
    print(f"\n{'='*50}")
    print("📊 테스트 결과 요약")
    print("=" * 50)
    
    success_count = 0
    for test_name, result in results:
        status = "✅ 성공" if result else "❌ 실패"
        print(f"{test_name}: {status}")
        if result:
            success_count += 1
    
    print(f"\n총 {len(results)}개 테스트 중 {success_count}개 성공 ({success_count/len(results)*100:.1f}%)")
    
    if success_count == len(results):
        print("\n🎉 모든 테스트가 성공했습니다!")
        print("✅ HRFCO MCP 서버가 정상적으로 작동할 준비가 되었습니다.")
    else:
        print(f"\n⚠️  {len(results) - success_count}개 테스트가 실패했습니다.")
        print("실패한 테스트를 확인하고 수정해주세요.")

if __name__ == "__main__":
    main() 