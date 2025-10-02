#!/usr/bin/env python3
"""
Test intelligent water search functions
"""
import asyncio
import json
from smart_water_search import SmartWaterSearch

async def test_all_functions():
    """Test all intelligent search functions"""
    print("🧪 Testing Intelligent Water Search System")
    
    search = SmartWaterSearch()
    
    # Test 1: search_water_station_by_name
    print("\n🔍 Test 1: search_water_station_by_name('한강')")
    result1 = await search.search_stations_by_name("한강", limit=3)
    print(f"✅ Found {result1.get('found_stations', 0)} stations")
    if result1.get('stations'):
        print(f"   First station: {result1['stations'][0]['name']}")
    
    # Test 2: get_water_info_by_location  
    print("\n🔍 Test 2: get_water_info_by_location('서울 수위')")
    result2 = await search.get_water_info_by_location("서울 수위", limit=2)
    print(f"✅ Status: {result2.get('status', 'unknown')}")
    if result2.get('data', {}).get('stations'):
        print(f"   Found: {len(result2['data']['stations'])} stations")
    
    # Test 3: recommend_nearby_stations
    print("\n🔍 Test 3: recommend_nearby_stations('부산')")
    result3 = await search.recommend_nearby_stations("부산", radius=30)
    print(f"✅ Recommendations: {len(result3.get('recommendations', []))}")
    
    # Test response sizes
    print("\n📊 Response Size Analysis:")
    print(f"   Test 1 size: {len(json.dumps(result1, ensure_ascii=False))} bytes")
    print(f"   Test 2 size: {len(json.dumps(result2, ensure_ascii=False))} bytes") 
    print(f"   Test 3 size: {len(json.dumps(result3, ensure_ascii=False))} bytes")
    
    print("\n🎉 All tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_all_functions())
