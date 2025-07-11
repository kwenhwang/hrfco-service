#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HRFCO API 테스트 스크립트
"""
import httpx
import asyncio
import json
import os

async def test_hrfco_api():
    """HRFCO API 테스트"""
    api_key = os.getenv("HRFCO_API_KEY", "your-api-key-here")
    base_url = "http://api.hrfco.go.kr"
    
    # 다양한 가능한 엔드포인트들 테스트
    test_endpoints = [
        # 기본 경로들
        "/waterlevel/info",
        "/rainfall/info", 
        "/dam/info",
        "/bo/info",
        
        # 다른 가능한 경로들
        "/api/waterlevel/info",
        "/api/rainfall/info",
        "/api/dam/info", 
        "/api/bo/info",
        
        # 다른 형식들
        "/waterlevel",
        "/rainfall",
        "/dam",
        "/bo",
        
        # API 버전 포함
        "/v1/waterlevel/info",
        "/v1/rainfall/info",
        "/v1/dam/info",
        "/v1/bo/info",
        
        # 루트 경로 테스트
        "/",
        "/api",
        "/info"
    ]
    
    async with httpx.AsyncClient() as client:
        for endpoint in test_endpoints:
            url = f"{base_url}{endpoint}"
            
            # 엔드포인트에 따라 파라미터 조정
            if "/info" in endpoint:
                params = {
                    "API_KEY": api_key,
                    "hydro_type": endpoint.split("/")[1] if len(endpoint.split("/")) > 1 else "waterlevel",
                    "time_type": "1H"
                }
            else:
                params = {"API_KEY": api_key}
            
            print(f"\n=== 테스트: {endpoint} ===")
            try:
                response = await client.get(url, params=params)
                print(f"Status Code: {response.status_code}")
                print(f"URL: {response.url}")
                
                if response.status_code == 200:
                    print("✅ 성공!")
                    try:
                        data = response.json()
                        print(f"응답 데이터: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}...")
                    except:
                        print(f"응답 텍스트: {response.text[:200]}...")
                elif response.status_code == 401:
                    print("❌ 인증 실패 (API 키 문제)")
                elif response.status_code == 404:
                    print("❌ 경로를 찾을 수 없음")
                else:
                    print(f"❌ 기타 오류: {response.status_code}")
                    print(f"응답: {response.text[:200]}...")
                    
            except Exception as e:
                print(f"❌ 오류: {e}")

if __name__ == "__main__":
    asyncio.run(test_hrfco_api()) 