#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HRFCO API 날짜 범위 테스트
"""
import asyncio
import httpx
import os

async def test_date_range():
    """날짜 범위가 있는 API 호출 테스트"""
    
    api_key = os.environ.get("HRFCO_API_KEY", "FE18B23B-A81B-4246-9674-E8D641902A42")
    base_url = "https://api.hrfco.go.kr"
    
    # 테스트할 날짜 범위 요청들
    test_requests = [
        # 1. 댐 데이터 - 특정 관측소, 날짜 범위
        {
            "name": "댐 데이터 (3008110, 20250715-20250716)",
            "url": f"{base_url}/{api_key}/dam/list/1H/3008110/2025071500/2025071623.json"
        },
        
        # 2. 수위 데이터 - 특정 관측소, 날짜 범위
        {
            "name": "수위 데이터 (3008110, 20250715-20250716)",
            "url": f"{base_url}/{api_key}/waterlevel/list/1H/3008110/2025071500/2025071623.json"
        },
        
        # 3. 강수량 데이터 - 특정 관측소, 날짜 범위
        {
            "name": "강수량 데이터 (10014010, 20250715-20250716)",
            "url": f"{base_url}/{api_key}/rainfall/list/1D/10014010/2025071500/2025071623.json"
        },
        
        # 4. 댐 데이터 - 모든 관측소, 날짜 범위
        {
            "name": "댐 데이터 (전체, 20250715-20250716)",
            "url": f"{base_url}/{api_key}/dam/list/1H/2025071500/2025071623.json"
        },
        
        # 5. 수위 데이터 - 모든 관측소, 날짜 범위
        {
            "name": "수위 데이터 (전체, 20250715-20250716)",
            "url": f"{base_url}/{api_key}/waterlevel/list/1H/2025071500/2025071623.json"
        }
    ]
    
    async with httpx.AsyncClient(timeout=10) as client:
        for test in test_requests:
            try:
                print(f"\n🔍 {test['name']}")
                print(f"📡 URL: {test['url']}")
                
                response = await client.get(test['url'])
                print(f"📊 상태 코드: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    content_count = len(data.get('content', []))
                    print(f"✅ 성공: {content_count}개 데이터")
                    
                    if content_count > 0:
                        first_item = data['content'][0]
                        print(f"📋 첫 번째 데이터: {first_item}")
                    else:
                        print("⚠️ 데이터가 없습니다 (날짜 범위에 데이터가 없을 수 있음)")
                        
                else:
                    print(f"❌ 실패: {response.text[:200]}")
                    
            except Exception as e:
                print(f"❌ 오류: {str(e)}")

if __name__ == "__main__":
    print("🔬 HRFCO API 날짜 범위 테스트 시작...")
    asyncio.run(test_date_range()) 