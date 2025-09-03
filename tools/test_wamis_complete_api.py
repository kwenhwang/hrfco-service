#!/usr/bin/env python3
"""
WAMIS API 완전 테스트 스크립트
강수량, 수위, 기상, 댐수문정보 모든 API를 테스트합니다.
"""

import requests
import json
from datetime import datetime, timedelta
import time

class WAMISAPITester:
    def __init__(self):
        self.base_url_wkw = "http://www.wamis.go.kr:8080/wamis/openapi/wkw"
        self.base_url_wkd = "http://www.wamis.go.kr:8080/wamis/openapi/wkd"
        self.session = requests.Session()
        self.session.verify = False  # SSL 인증서 검증 비활성화
        
    def test_api(self, url, description):
        """API 테스트 함수"""
        print(f"\n🔍 테스트: {description}")
        print(f"URL: {url}")
        
        try:
            response = self.session.get(url, timeout=10)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"✅ 성공: {description}")
                    
                    # 결과 요약
                    if 'result' in data:
                        result = data['result']
                        if result.get('code') == 'success':
                            count = data.get('count', 0)
                            print(f"   📊 결과: {count}개 항목")
                            
                            # 샘플 데이터 출력
                            if 'list' in data and data['list']:
                                sample = data['list'][0]
                                print(f"   📋 샘플 데이터:")
                                for key, value in sample.items():
                                    print(f"      {key}: {value}")
                        else:
                            print(f"   ❌ API 오류: {result.get('msg', '알 수 없는 오류')}")
                    else:
                        print(f"   📊 응답 데이터: {len(str(data))} 문자")
                        
                except json.JSONDecodeError:
                    print(f"   ⚠️ JSON 파싱 오류: {response.text[:200]}")
                    
            else:
                print(f"   ❌ HTTP 오류: {response.status_code}")
                print(f"   📄 응답 내용: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ 요청 오류: {str(e)}")
            
        print("-" * 60)
        
    def test_all_apis(self):
        """모든 WAMIS API 테스트"""
        print("🚀 WAMIS API 완전 테스트 시작")
        print("=" * 80)
        
        # 1. 강우/수위/기상 관련 API 테스트
        print("\n🌧️ 강우/수위/기상 관련 API 테스트")
        print("=" * 60)
        
        # 강우관측소 검색 (확인됨)
        self.test_api(
            f"{self.base_url_wkw}/rf_dubrfobs",
            "강우관측소 검색"
        )
        
        # 수위관측소 검색 (확인 필요)
        self.test_api(
            f"{self.base_url_wkw}/wl_dubrfobs",
            "수위관측소 검색"
        )
        
        # 기상관측소 검색 (확인 필요)
        self.test_api(
            f"{self.base_url_wkw}/ws_dubrfobs",
            "기상관측소 검색"
        )
        
        # 강우량 데이터 (확인 필요)
        self.test_api(
            f"{self.base_url_wkw}/rf_data?obscd=10011100&startdt=20240101&enddt=20240131",
            "강우량 데이터 조회"
        )
        
        # 수위 데이터 (확인 필요)
        self.test_api(
            f"{self.base_url_wkw}/wl_data?obscd=10011100&startdt=20240101&enddt=20240131",
            "수위 데이터 조회"
        )
        
        # 기상 데이터 (확인 필요)
        self.test_api(
            f"{self.base_url_wkw}/ws_data?obscd=10011100&startdt=20240101&enddt=20240131",
            "기상 데이터 조회"
        )
        
        # 2. 댐 관련 API 테스트
        print("\n🏞️ 댐 관련 API 테스트")
        print("=" * 60)
        
        # 댐 검색 (확인됨)
        self.test_api(
            f"{self.base_url_wkd}/mn_dammain",
            "댐 검색"
        )
        
        # 댐 일자료 (확인 필요)
        self.test_api(
            f"{self.base_url_wkd}/mn_dtdata?damcd=5002201&startdt=20240101&enddt=20240131",
            "댐 일자료 조회"
        )
        
        # 댐 시자료 (확인 필요)
        self.test_api(
            f"{self.base_url_wkd}/mn_hrdata?damcd=5002201&startdt=20240101&enddt=20240102",
            "댐 시자료 조회"
        )
        
        # 댐 월자료 (확인 필요)
        self.test_api(
            f"{self.base_url_wkd}/mn_mndata?damcd=5002201&startyear=2023&endyear=2024",
            "댐 월자료 조회"
        )
        
        # 3. 추가 가능한 API 패턴들 테스트
        print("\n🔍 추가 API 패턴 테스트")
        print("=" * 60)
        
        # 다른 가능한 엔드포인트들
        additional_endpoints = [
            f"{self.base_url_wkw}/rf_obs",  # 강우관측소 (다른 패턴)
            f"{self.base_url_wkw}/wl_obs",  # 수위관측소 (다른 패턴)
            f"{self.base_url_wkw}/ws_obs",  # 기상관측소 (다른 패턴)
            f"{self.base_url_wkw}/rf_list",  # 강우관측소 목록
            f"{self.base_url_wkw}/wl_list",  # 수위관측소 목록
            f"{self.base_url_wkw}/ws_list",  # 기상관측소 목록
            f"{self.base_url_wkd}/mn_damlist",  # 댐 목록
            f"{self.base_url_wkd}/mn_damobs",  # 댐 관측소
        ]
        
        for endpoint in additional_endpoints:
            self.test_api(endpoint, f"추가 패턴: {endpoint.split('/')[-1]}")
            
        print("\n✅ 모든 API 테스트 완료!")
        
    def generate_api_summary(self):
        """API 요약 보고서 생성"""
        print("\n📋 WAMIS API 요약 보고서")
        print("=" * 60)
        
        summary = {
            "확인된 API": {
                "강우관측소 검색": "http://www.wamis.go.kr:8080/wamis/openapi/wkw/rf_dubrfobs",
                "댐 검색": "http://www.wamis.go.kr:8080/wamis/openapi/wkd/mn_dammain"
            },
            "확인 필요한 API": {
                "수위관측소 검색": "http://www.wamis.go.kr:8080/wamis/openapi/wkw/wl_dubrfobs",
                "기상관측소 검색": "http://www.wamis.go.kr:8080/wamis/openapi/wkw/ws_dubrfobs",
                "강우량 데이터": "http://www.wamis.go.kr:8080/wamis/openapi/wkw/rf_data",
                "수위 데이터": "http://www.wamis.go.kr:8080/wamis/openapi/wkw/wl_data",
                "기상 데이터": "http://www.wamis.go.kr:8080/wamis/openapi/wkw/ws_data",
                "댐 일자료": "http://www.wamis.go.kr:8080/wamis/openapi/wkd/mn_dtdata",
                "댐 시자료": "http://www.wamis.go.kr:8080/wamis/openapi/wkd/mn_hrdata",
                "댐 월자료": "http://www.wamis.go.kr:8080/wamis/openapi/wkd/mn_mndata"
            }
        }
        
        print("✅ 확인된 API:")
        for name, url in summary["확인된 API"].items():
            print(f"   - {name}: {url}")
            
        print("\n❓ 확인이 필요한 API:")
        for name, url in summary["확인 필요한 API"].items():
            print(f"   - {name}: {url}")
            
        print(f"\n📊 총 API 수: {len(summary['확인된 API']) + len(summary['확인 필요한 API'])}개")
        print(f"   ✅ 확인됨: {len(summary['확인된 API'])}개")
        print(f"   ❓ 확인 필요: {len(summary['확인 필요한 API'])}개")

def main():
    """메인 함수"""
    tester = WAMISAPITester()
    
    try:
        # 모든 API 테스트
        tester.test_all_apis()
        
        # 요약 보고서 생성
        tester.generate_api_summary()
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    main() 