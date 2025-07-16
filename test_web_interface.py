#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
웹 인터페이스 테스트
브라우저에서 HRFCO API 기능을 테스트할 수 있습니다.
"""
import os
import math
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# HTML 템플릿
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HRFCO API 테스트</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; color: #34495e; }
        input, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; }
        button { background: #3498db; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #2980b9; }
        .result { margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 5px; border-left: 4px solid #3498db; }
        .error { border-left-color: #e74c3c; }
        .success { border-left-color: #27ae60; }
        .station-item { padding: 10px; margin: 5px 0; background: white; border-radius: 3px; border: 1px solid #ddd; }
        .loading { text-align: center; color: #7f8c8d; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌊 HRFCO API 테스트</h1>
        
        <form id="testForm">
            <div class="form-group">
                <label for="address">주소:</label>
                <input type="text" id="address" name="address" value="세종 반곡동" placeholder="예: 세종 반곡동, 청양군">
            </div>
            
            <div class="form-group">
                <label for="radius">검색 반경 (km):</label>
                <input type="number" id="radius" name="radius" value="20" min="1" max="100">
            </div>
            
            <div class="form-group">
                <label for="data_type">데이터 유형:</label>
                <select id="data_type" name="data_type">
                    <option value="waterlevel">수위</option>
                    <option value="rainfall">강우</option>
                    <option value="dam">댐</option>
                    <option value="weir">보</option>
                </select>
            </div>
            
            <button type="submit">🔍 검색</button>
        </form>
        
        <div id="result"></div>
    </div>

    <script>
        document.getElementById('testForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = '<div class="loading">🔍 검색 중...</div>';
            
            const formData = new FormData(this);
            const data = {
                address: formData.get('address'),
                radius: formData.get('radius'),
                data_type: formData.get('data_type')
            };
            
            try {
                const response = await fetch('/api/test', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    resultDiv.innerHTML = `
                        <div class="result success">
                            <h3>✅ 검색 결과</h3>
                            <p><strong>주소:</strong> ${result.address}</p>
                            <p><strong>좌표:</strong> 위도 ${result.coordinates.lat}, 경도 ${result.coordinates.lon}</p>
                            <p><strong>${result.radius}km 내 관측소:</strong> ${result.stations.length}개</p>
                            
                            ${result.stations.length > 0 ? `
                                <h4>🎯 가장 가까운 관측소:</h4>
                                ${result.stations.slice(0, 10).map((station, index) => `
                                    <div class="station-item">
                                        <strong>${index + 1}. ${station.name}</strong><br>
                                        거리: ${station.distance.toFixed(1)}km<br>
                                        좌표: 위도 ${station.lat}, 경도 ${station.lon}
                                    </div>
                                `).join('')}
                            ` : '<p>❌ 해당 반경 내 관측소가 없습니다.</p>'}
                        </div>
                    `;
                } else {
                    resultDiv.innerHTML = `
                        <div class="result error">
                            <h3>❌ 오류</h3>
                            <p>${result.error}</p>
                        </div>
                    `;
                }
            } catch (error) {
                resultDiv.innerHTML = `
                    <div class="result error">
                        <h3>❌ 네트워크 오류</h3>
                        <p>${error.message}</p>
                    </div>
                `;
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/test', methods=['POST'])
def api_test():
    try:
        data = request.get_json()
        address = data.get('address', '')
        radius = int(data.get('radius', 20))
        data_type = data.get('data_type', 'waterlevel')
        
        if not address:
            return jsonify({'success': False, 'error': '주소를 입력해주세요.'})
        
        # 주소 → 좌표 변환
        from src.hrfco_service.location_mapping import get_location_coordinates
        coordinates = get_location_coordinates(address)
        
        if not coordinates:
            return jsonify({'success': False, 'error': f"'{address}'의 좌표를 찾을 수 없습니다."})
        
        lat, lon = coordinates
        
        # 관측소 정보 조회 (실제로는 API 호출이 필요하지만 여기서는 시뮬레이션)
        stations = simulate_nearby_stations(lat, lon, radius, data_type)
        
        return jsonify({
            'success': True,
            'address': address,
            'coordinates': {'lat': lat, 'lon': lon},
            'radius': radius,
            'data_type': data_type,
            'stations': stations
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def simulate_nearby_stations(lat: float, lon: float, radius_km: int, data_type: str):
    """시뮬레이션된 주변 관측소 데이터"""
    import random
    
    stations = []
    num_stations = random.randint(5, 15)
    
    for i in range(num_stations):
        # 랜덤 거리 (0 ~ radius_km)
        distance = random.uniform(0.5, radius_km)
        
        # 랜덤 방향으로 좌표 계산
        angle = random.uniform(0, 2 * math.pi)
        dlat = distance / 111.32  # 대략적인 위도 차이
        dlon = distance / (111.32 * math.cos(math.radians(lat)))  # 경도 차이
        
        station_lat = lat + (random.choice([-1, 1]) * dlat * random.uniform(0.1, 1.0))
        station_lon = lon + (random.choice([-1, 1]) * dlon * random.uniform(0.1, 1.0))
        
        stations.append({
            'name': f"{data_type.capitalize()} 관측소 {i+1}",
            'distance': distance,
            'lat': round(station_lat, 6),
            'lon': round(station_lon, 6)
        })
    
    # 거리순 정렬
    stations.sort(key=lambda x: x['distance'])
    return stations

if __name__ == '__main__':
    print("🌐 웹 인터페이스 테스트 서버 시작")
    print("📱 브라우저에서 http://localhost:5000 접속")
    print("🔑 HRFCO_API_KEY 환경변수가 설정되어 있는지 확인하세요.")
    
    if not os.environ.get("HRFCO_API_KEY"):
        print("⚠️  HRFCO_API_KEY 환경변수가 설정되지 않았습니다. 시뮬레이션 모드로 실행됩니다.")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 