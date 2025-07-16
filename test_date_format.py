#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HRFCO API 날짜 형식 테스트
"""
import asyncio
import httpx
import os

async def test_date_formats():
    """다양한 날짜 형식으로 API 호출 테스트"""
    
    api_key = os.environ.get("HRFCO_API_KEY", "FE18B23B-A81B-4246-9674-E8D641902A42")
    base_url = "https://api.hrfco.go.kr"
    
    # 테스트할 URL 패턴들
    test_patterns = [
        # 패턴 1: 기본 형식 (날짜 없음)
        f"{base_url}/{api_key}/dam/list/1H.json",
        
        # 패턴 2: 관측소 코드만
        f"{base_url}/{api_key}/dam/list/1H/3008110.json",
        
        # 패턴 3: 날짜 형식 1 (YYYYMMDD)
        f"{base_url}/{api_key}/dam/list/1H/3008110/20250715/20250716.json",
        
        # 패턴 4: 날짜 형식 2 (YYYY-MM-DD)
        f"{base_url}/{api_key}/dam/list/1H/3008110/2025-07-15/2025-07-16.json",
        
        # 패턴 5: 날짜 형식 3 (YYYY/MM/DD)
        f"{base_url}/{api_key}/dam/list/1H/3008110/2025/07/15/2025/07/16.json",
        
        # 패턴 6: 날짜 형식 4 (YYYYMMDDHH)
        f"{base_url}/{api_key}/dam/list/1H/3008110/2025071514/2025071614.json",
        
        # 패턴 7: 날짜 형식 5 (YYYYMMDDHHMM)
        f"{base_url}/{api_key}/dam/list/1H/3008110/202507151400/202507161400.json",
    ]
    
    async with httpx.AsyncClient(timeout=10) as client:
        for i, url in enumerate(test_patterns, 1):
            try:
                print(f"\n🔍 테스트 패턴 {i}: {url}")
                response = await client.get(url)
                print(f"📊 상태 코드: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ 성공: {len(data.get('content', []))}개 데이터")
                    if data.get('content'):
                        print(f"📋 첫 번째 데이터: {data['content'][0]}")
                else:
                    print(f"❌ 실패: {response.text[:200]}")
                    
            except Exception as e:
                print(f"❌ 오류: {str(e)}")

async def test_correct_format():
    """올바른 형식으로 API 호출 테스트"""
    
    api_key = os.environ.get("HRFCO_API_KEY", "FE18B23B-A81B-4246-9674-E8D641902A42")
    base_url = "https://api.hrfco.go.kr"
    
    # HRFCO API 공식 문서에 따른 올바른 형식
    correct_urls = [
        # 1. 관측소 정보 조회
        f"{base_url}/{api_key}/dam/info.json",
        
        # 2. 실시간 데이터 (날짜 범위 없음)
        f"{base_url}/{api_key}/dam/list/1H.json",
        
        # 3. 특정 관측소 실시간 데이터
        f"{base_url}/{api_key}/dam/list/1H/3008110.json",
        
        # 4. 날짜 범위가 있는 경우 (YYYYMMDD 형식)
        f"{base_url}/{api_key}/dam/list/1H/3008110/20250715/20250716.json",
    ]
    
    async with httpx.AsyncClient(timeout=10) as client:
        for i, url in enumerate(correct_urls, 1):
            try:
                print(f"\n🎯 올바른 형식 테스트 {i}: {url}")
                response = await client.get(url)
                print(f"📊 상태 코드: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ 성공: {len(data.get('content', []))}개 데이터")
                    if data.get('content'):
                        print(f"📋 첫 번째 데이터: {data['content'][0]}")
                else:
                    print(f"❌ 실패: {response.text[:200]}")
                    
            except Exception as e:
                print(f"❌ 오류: {str(e)}")

if __name__ == "__main__":
    print("🔬 HRFCO API 날짜 형식 테스트 시작...")
    asyncio.run(test_date_formats())
    print("\n" + "="*50)
    asyncio.run(test_correct_format()) 