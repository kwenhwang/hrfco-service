#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
향상된 MCP 서버 기능 테스트
"""

import asyncio
import json
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_server import HRFCOMCPServer

async def test_enhanced_mcp_features():
    """향상된 MCP 기능들을 테스트합니다"""
    
    print("🧪 향상된 MCP 서버 기능 테스트 시작")
    print("=" * 50)
    
    # MCP 서버 인스턴스 생성
    server = HRFCOMCPServer()
    
    # 테스트 케이스들
    test_cases = [
        {
            "name": "수위 관측소 위험 수위 분석 (기본)",
            "tool": "analyze_water_level_with_thresholds",
            "arguments": {
                "obs_code": "4009670",  # 하동군 대석교
                "time_type": "1H",
                "count": 24,
                "hours": 48
            }
        },
        {
            "name": "수위 관측소 위험 수위 분석 (확장)",
            "tool": "analyze_water_level_with_thresholds",
            "arguments": {
                "obs_code": "4009670",  # 하동군 대석교
                "time_type": "1H",
                "count": 72,
                "hours": 168  # 7일
            }
        },
        {
            "name": "종합 수문 분석 (기본)",
            "tool": "get_comprehensive_hydro_analysis",
            "arguments": {
                "water_level_obs": "4009670",  # 하동군 대석교
                "rainfall_obs": "40094090",    # 하동군(읍내리)
                "time_type": "1H",
                "count": 48,
                "hours": 72
            }
        },
        {
            "name": "종합 수문 분석 (확장)",
            "tool": "get_comprehensive_hydro_analysis",
            "arguments": {
                "water_level_obs": "4009670",  # 하동군 대석교
                "rainfall_obs": "40094090",    # 하동군(읍내리)
                "time_type": "1H",
                "count": 168,
                "hours": 168  # 7일
            }
        },
        {
            "name": "지역별 위험 수위 상태 요약",
            "tool": "get_alert_status_summary",
            "arguments": {
                "region_name": "하동",
                "hydro_type": "waterlevel"
            }
        },
        {
            "name": "전체 수위 관측소 상태 요약",
            "tool": "get_alert_status_summary",
            "arguments": {
                "hydro_type": "waterlevel"
            }
        },
        {
            "name": "수계 종합 분석 (기본)",
            "tool": "get_basin_comprehensive_analysis",
            "arguments": {
                "main_obs_code": "4009670",  # 하동군 대석교
                "hydro_types": ["waterlevel", "rainfall"],
                "max_distance_km": 10.0,
                "time_type": "1H",
                "count": 48,
                "hours": 72
            }
        },
        {
            "name": "수계 종합 분석 (확장)",
            "tool": "get_basin_comprehensive_analysis",
            "arguments": {
                "main_obs_code": "4009670",  # 하동군 대석교
                "hydro_types": ["waterlevel", "rainfall", "dam", "bo"],
                "max_distance_km": 20.0,
                "time_type": "1H",
                "count": 168,
                "hours": 168  # 7일
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 테스트 {i}: {test_case['name']}")
        print("-" * 40)
        
        try:
            # 도구 호출
            if test_case['tool'] == "analyze_water_level_with_thresholds":
                result = await server._analyze_water_level_with_thresholds(test_case['arguments'])
            elif test_case['tool'] == "get_comprehensive_hydro_analysis":
                result = await server._get_comprehensive_hydro_analysis(test_case['arguments'])
            elif test_case['tool'] == "get_alert_status_summary":
                result = await server._get_alert_status_summary(test_case['arguments'])
            elif test_case['tool'] == "get_basin_comprehensive_analysis":
                result = await server._get_basin_comprehensive_analysis(test_case['arguments'])
            else:
                print(f"❌ 알 수 없는 도구: {test_case['tool']}")
                continue
            
            # 결과 출력
            if "error" in result:
                print(f"❌ 오류: {result['error']}")
            else:
                print("✅ 성공!")
                
                # 주요 정보 추출 및 출력
                if test_case['tool'] == "analyze_water_level_with_thresholds":
                    print(f"   관측소: {result.get('observatory_info', {}).get('obs_name', 'Unknown')}")
                    print(f"   현재 수위: {result.get('alert_analysis', {}).get('attention', {}).get('current', 'N/A')}m")
                    
                    # 데이터 개수 정보
                    summary = result.get('summary', {})
                    print(f"   요청된 데이터: {summary.get('data_count_requested', 'N/A')}개")
                    print(f"   실제 사용 가능: {summary.get('total_available', 'N/A')}개")
                    print(f"   요청된 시간 범위: {summary.get('hours_requested', 'N/A')}시간")
                    
                    # 통계 정보 (새로운 기능)
                    statistics = result.get('statistics', {})
                    if statistics:
                        analysis_period = statistics.get('analysis_period', {})
                        print(f"   분석 기간: {analysis_period.get('days', 'N/A')}일 ({analysis_period.get('hours', 'N/A')}시간)")
                        print(f"   최고 수위: {statistics.get('max_water_level', 'N/A')}m")
                        print(f"   최저 수위: {statistics.get('min_water_level', 'N/A')}m")
                        print(f"   평균 수위: {statistics.get('avg_water_level', 'N/A')}m")
                    
                    # 위험 수위 상태 출력
                    for alert_type in ['attention', 'warning', 'alert', 'serious']:
                        if alert_type in result.get('alert_analysis', {}):
                            status = result['alert_analysis'][alert_type]
                            if status['status'] == 'exceeded':
                                print(f"   ⚠️ {alert_type.upper()}: {status['margin']:.2f}m 초과")
                            else:
                                print(f"   ✅ {alert_type.upper()}: {status['margin']:.2f}m 여유")
                
                elif test_case['tool'] == "get_comprehensive_hydro_analysis":
                    print(f"   수위 관측소: {result.get('water_level_station', {}).get('obs_name', 'Unknown')}")
                    print(f"   강우량 관측소: {result.get('rainfall_station', {}).get('obs_name', 'N/A')}")
                    
                    # 거리 정보
                    distance_info = result.get('station_distance')
                    if distance_info:
                        print(f"   관측소 간 거리: {distance_info['distance_km']}km ({distance_info['proximity']})")
                    
                    # 데이터 개수 정보
                    analysis_period = result.get('analysis_period', {})
                    print(f"   요청된 데이터: {analysis_period.get('data_count_requested', 'N/A')}개")
                    print(f"   실제 사용 가능: {analysis_period.get('total_available', 'N/A')}개")
                    print(f"   요청된 시간 범위: {analysis_period.get('hours_requested', 'N/A')}시간")
                    
                    # 위험 수위 상태
                    alert_analysis = result.get('water_level_station', {}).get('alert_analysis', {})
                    for alert_type in ['attention', 'warning', 'alert', 'serious']:
                        if alert_type in alert_analysis:
                            status = alert_analysis[alert_type]
                            if status['status'] == 'exceeded':
                                print(f"   ⚠️ {alert_type.upper()}: {status['margin']:.2f}m 초과")
                            else:
                                print(f"   ✅ {alert_type.upper()}: {status['margin']:.2f}m 여유")
                
                elif test_case['tool'] == "get_alert_status_summary":
                    region = result.get('region', '전체')
                    total_stations = result.get('total_stations_checked', 0)
                    alert_stats = result.get('alert_statistics', {})
                    
                    print(f"   지역: {region}")
                    print(f"   총 관측소: {total_stations}개")
                    print(f"   정상: {alert_stats.get('normal', 0)}개")
                    print(f"   관심: {alert_stats.get('attention', 0)}개")
                    print(f"   주의보: {alert_stats.get('warning', 0)}개")
                    print(f"   경보: {alert_stats.get('alert', 0)}개")
                    print(f"   심각: {alert_stats.get('serious', 0)}개")
                
                elif test_case['tool'] == "get_basin_comprehensive_analysis":
                    main_facility = result.get('main_facility', {})
                    print(f"   메인 시설: {main_facility.get('obs_name', 'Unknown')} ({main_facility.get('hydro_type', 'Unknown')})")
                    
                    # 검색 파라미터
                    search_params = result.get('search_parameters', {})
                    print(f"   검색 거리: {search_params.get('max_distance_km', 'N/A')}km")
                    print(f"   분석 타입: {', '.join(search_params.get('hydro_types', []))}")
                    
                    # 수계 통계
                    basin_stats = result.get('basin_statistics', {})
                    print(f"   발견된 시설: {basin_stats.get('total_facilities_found', 0)}개")
                    print(f"   데이터 있는 시설: {basin_stats.get('facilities_with_data', 0)}개")
                    
                    # 거리 분포
                    distance_dist = basin_stats.get('distance_distribution', {})
                    if distance_dist.get('closest'):
                        print(f"   가장 가까운 시설: {distance_dist['closest']:.2f}km")
                        print(f"   가장 먼 시설: {distance_dist['farthest']:.2f}km")
                        print(f"   평균 거리: {distance_dist['average']:.2f}km")
                    
                    # 타입별 분포
                    type_dist = basin_stats.get('hydro_type_distribution', {})
                    for hydro_type, count in type_dist.items():
                        print(f"   {hydro_type}: {count}개")
                
                # 상세 결과는 JSON으로 저장
                output_file = f"test_result_{test_case['tool']}_{i}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"   📄 상세 결과: {output_file}")
        
        except Exception as e:
            print(f"❌ 테스트 실패: {str(e)}")
    
    print("\n🎉 모든 테스트 완료!")
    print("=" * 50)

async def test_data_availability():
    """데이터 가용성 테스트"""
    
    print("\n🔍 데이터 가용성 테스트")
    print("=" * 50)
    
    server = HRFCOMCPServer()
    
    # 다양한 시간 범위로 테스트
    test_ranges = [
        {"hours": 24, "name": "24시간"},
        {"hours": 48, "name": "48시간"},
        {"hours": 72, "name": "72시간"},
        {"hours": 168, "name": "7일"},
        {"hours": 720, "name": "30일"}
    ]
    
    for test_range in test_ranges:
        print(f"\n📊 {test_range['name']} 데이터 테스트")
        print("-" * 30)
        
        try:
            result = await server._analyze_water_level_with_thresholds({
                "obs_code": "4009670",  # 하동군 대석교
                "time_type": "1H",
                "count": 100,
                "hours": test_range["hours"]
            })
            
            if "error" in result:
                print(f"❌ 오류: {result['error']}")
            else:
                summary = result.get('summary', {})
                total_available = summary.get('total_available', 0)
                hours_requested = summary.get('hours_requested', 0)
                
                print(f"   요청 시간 범위: {hours_requested}시간")
                print(f"   사용 가능한 데이터: {total_available}개")
                print(f"   데이터 밀도: {total_available/hours_requested:.2f}개/시간" if hours_requested > 0 else "   데이터 밀도: N/A")
                
                if total_available > 0:
                    print("   ✅ 데이터 사용 가능")
                else:
                    print("   ❌ 데이터 없음")
        
        except Exception as e:
            print(f"❌ 테스트 실패: {str(e)}")

async def test_analysis_period_info():
    """분석 기준 기간 정보 테스트"""
    
    print("\n📊 분석 기준 기간 정보 테스트")
    print("=" * 50)
    
    server = HRFCOMCPServer()
    
    try:
        result = await server._analyze_water_level_with_thresholds({
            "obs_code": "4009670",  # 하동군 대석교
            "time_type": "1H",
            "count": 72,
            "hours": 168  # 7일
        })
        
        if "error" in result:
            print(f"❌ 오류: {result['error']}")
            return
        
        print("✅ 분석 기준 기간 정보 테스트 완료!")
        
        # 통계 정보 확인
        statistics = result.get('statistics', {})
        if statistics:
            analysis_period = statistics.get('analysis_period', {})
            
            print(f"\n📈 분석 기준 기간 정보:")
            print(f"   시작 시간: {analysis_period.get('start_time', 'N/A')}")
            print(f"   종료 시간: {analysis_period.get('end_time', 'N/A')}")
            print(f"   분석 기간: {analysis_period.get('days', 'N/A')}일 ({analysis_period.get('hours', 'N/A')}시간)")
            print(f"   데이터 개수: {analysis_period.get('data_count', 'N/A')}개")
            
            print(f"\n📊 통계 정보:")
            print(f"   최고 수위: {statistics.get('max_water_level', 'N/A')}m")
            print(f"   최저 수위: {statistics.get('min_water_level', 'N/A')}m")
            print(f"   평균 수위: {statistics.get('avg_water_level', 'N/A')}m")
            print(f"   현재 수위: {statistics.get('current_water_level', 'N/A')}m")
            print(f"   데이터 포인트: {statistics.get('data_points', 'N/A')}개")
        
        # 상세 결과 저장
        with open("analysis_period_test_result.json", 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n📄 상세 결과: analysis_period_test_result.json")
        
    except Exception as e:
        print(f"❌ 분석 기준 기간 정보 테스트 실패: {str(e)}")

async def test_basin_comprehensive_analysis():
    """수계 종합 분석 테스트"""
    
    print("\n🏞️ 수계 종합 분석 테스트")
    print("=" * 50)
    
    server = HRFCOMCPServer()
    
    try:
        result = await server._get_basin_comprehensive_analysis({
            "main_obs_code": "4009670",  # 하동군 대석교
            "hydro_types": ["waterlevel", "rainfall", "dam", "bo"],
            "max_distance_km": 15.0,
            "time_type": "1H",
            "count": 72,
            "hours": 168  # 7일
        })
        
        if "error" in result:
            print(f"❌ 오류: {result['error']}")
            return
        
        print("✅ 수계 종합 분석 완료!")
        
        # 주요 정보 출력
        main_facility = result.get('main_facility', {})
        search_params = result.get('search_parameters', {})
        basin_stats = result.get('basin_statistics', {})
        
        print(f"\n📍 메인 시설:")
        print(f"   이름: {main_facility.get('obs_name', 'Unknown')}")
        print(f"   타입: {main_facility.get('hydro_type', 'Unknown')}")
        print(f"   코드: {main_facility.get('obs_code', 'Unknown')}")
        
        print(f"\n🔍 검색 파라미터:")
        print(f"   최대 거리: {search_params.get('max_distance_km', 'N/A')}km")
        print(f"   분석 타입: {', '.join(search_params.get('hydro_types', []))}")
        print(f"   시간 범위: {search_params.get('hours', 'N/A')}시간")
        
        print(f"\n📊 수계 통계:")
        print(f"   발견된 시설: {basin_stats.get('total_facilities_found', 0)}개")
        print(f"   데이터 있는 시설: {basin_stats.get('facilities_with_data', 0)}개")
        
        # 거리 분포
        distance_dist = basin_stats.get('distance_distribution', {})
        if distance_dist.get('closest'):
            print(f"   가장 가까운 시설: {distance_dist['closest']:.2f}km")
            print(f"   가장 먼 시설: {distance_dist['farthest']:.2f}km")
            print(f"   평균 거리: {distance_dist['average']:.2f}km")
        
        # 타입별 분포
        type_dist = basin_stats.get('hydro_type_distribution', {})
        print(f"\n🏗️ 시설 타입별 분포:")
        for hydro_type, count in type_dist.items():
            print(f"   {hydro_type}: {count}개")
        
        # 근접 시설 정보
        nearby_facilities = result.get('nearby_facilities', [])
        print(f"\n🏘️ 근접 시설 정보 (상위 5개):")
        for i, facility in enumerate(nearby_facilities[:5], 1):
            print(f"   {i}. {facility.get('obs_name', 'Unknown')} ({facility.get('hydro_type', 'Unknown')})")
            print(f"      거리: {facility.get('distance_km', 'N/A')}km")
            print(f"      데이터: {'있음' if facility.get('data_available') else '없음'}")
            
            # 통계 정보
            stats = facility.get('statistics', {})
            if stats:
                print(f"      현재값: {stats.get('current_value', 'N/A')}")
                print(f"      최고값: {stats.get('max_value', 'N/A')}")
                print(f"      최저값: {stats.get('min_value', 'N/A')}")
                print(f"      평균값: {stats.get('avg_value', 'N/A')}")
        
        # 상세 결과 저장
        with open("basin_comprehensive_analysis_result.json", 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n📄 상세 결과: basin_comprehensive_analysis_result.json")
        
    except Exception as e:
        print(f"❌ 수계 종합 분석 테스트 실패: {str(e)}")

async def test_specific_scenario():
    """특정 시나리오 테스트 (하동군 대석교 분석)"""
    
    print("\n🔍 특정 시나리오 테스트: 하동군 대석교 종합 분석")
    print("=" * 50)
    
    server = HRFCOMCPServer()
    
    try:
        # 종합 분석 실행 (확장된 시간 범위)
        result = await server._get_comprehensive_hydro_analysis({
            "water_level_obs": "4009670",  # 하동군 대석교
            "rainfall_obs": "40094090",    # 하동군(읍내리)
            "time_type": "1H",
            "count": 168,  # 7일치 데이터
            "hours": 168   # 7일
        })
        
        if "error" in result:
            print(f"❌ 오류: {result['error']}")
            return
        
        print("✅ 종합 분석 완료!")
        
        # 주요 정보 출력
        wl_station = result.get('water_level_station', {})
        rf_station = result.get('rainfall_station', {})
        distance_info = result.get('station_distance', {})
        alert_analysis = wl_station.get('alert_analysis', {})
        analysis_period = result.get('analysis_period', {})
        
        print(f"\n📊 분석 결과:")
        print(f"   수위 관측소: {wl_station.get('obs_name', 'Unknown')} ({wl_station.get('obs_code', 'Unknown')})")
        print(f"   강우량 관측소: {rf_station.get('obs_name', 'N/A')} ({rf_station.get('obs_code', 'N/A')})")
        
        if distance_info:
            print(f"   관측소 간 거리: {distance_info.get('distance_km', 'N/A')}km ({distance_info.get('proximity', 'N/A')})")
        
        print(f"\n📈 데이터 가용성:")
        print(f"   요청된 시간 범위: {analysis_period.get('hours_requested', 'N/A')}시간")
        print(f"   수위 데이터: {analysis_period.get('total_available', 'N/A')}개")
        print(f"   강우량 데이터: {rf_station.get('total_available', 'N/A')}개")
        
        print(f"\n⚠️ 위험 수위 상태:")
        for alert_type in ['attention', 'warning', 'alert', 'serious']:
            if alert_type in alert_analysis:
                status = alert_analysis[alert_type]
                if status['status'] == 'exceeded':
                    print(f"   {alert_type.upper()}: {status['margin']:.2f}m 초과 (현재: {status['current']:.2f}m)")
                else:
                    print(f"   {alert_type.upper()}: {status['margin']:.2f}m 여유 (현재: {status['current']:.2f}m)")
        
        # 상관관계 분석
        correlation = result.get('correlation_analysis', {})
        if correlation:
            recent_analysis = correlation.get('recent_analysis', {})
            print(f"\n📈 상관관계 분석:")
            print(f"   매칭된 데이터: {correlation.get('matched_records', 0)}개")
            print(f"   최대 강우량: {recent_analysis.get('max_rainfall', 0):.1f}mm")
            print(f"   최대 수위 변화: {recent_analysis.get('max_wl_change', 0):.2f}m")
        
        # 상세 결과 저장
        with open("comprehensive_analysis_result.json", 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n📄 상세 결과: comprehensive_analysis_result.json")
        
    except Exception as e:
        print(f"❌ 시나리오 테스트 실패: {str(e)}")

async def main():
    """메인 함수"""
    print("🚀 향상된 MCP 서버 기능 테스트")
    print("=" * 50)
    
    # 기본 기능 테스트
    await test_enhanced_mcp_features()
    
    # 데이터 가용성 테스트
    await test_data_availability()
    
    # 분석 기준 기간 정보 테스트
    await test_analysis_period_info()
    
    # 수계 종합 분석 테스트
    await test_basin_comprehensive_analysis()
    
    # 특정 시나리오 테스트
    await test_specific_scenario()
    
    print("\n✨ 모든 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(main()) 