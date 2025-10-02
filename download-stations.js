#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// HRFCO API 키
const API_KEY = 'FE18B23B-A81B-4246-9674-E8D641902A42';

// 데이터 저장 디렉토리 생성
const dataDir = path.join(__dirname, 'netlify', 'functions', 'data');
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true });
}

// API 호출 함수
async function fetchStationData(dataType) {
  try {
    const endpoint = `${dataType}/info.json`;
    const url = `http://api.hrfco.go.kr/${API_KEY}/${endpoint}`;
    
    console.log(`🔍 ${dataType} API 호출: ${url}`);
    
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`${dataType} API 호출 실패: ${response.status}`);
    }
    
    const data = await response.json();
    console.log(`📊 ${dataType} API 응답 코드: ${data.code || 'N/A'}`);
    
    // API 응답에 code 필드가 없는 경우도 있으므로 content 존재 여부로 판단
    if (!data.content) {
      throw new Error(`${dataType} API 오류: content가 없습니다`);
    }
    
    // 데이터 타입별로 다른 응답 형식 처리
    let stations = [];
    if (data.content) {
      stations = data.content.map((station) => ({
        obs_code: station.damcd || station.wlobscd || station.rfobscd || '',
        obs_name: station.damnm || station.obsnm || '',
        river_name: station.rivnm || station.river_name,
        location: station.addr || station.location,
        address: station.addr,
        agency: station.agcnm || station.agency,
        latitude: station.lat ? parseFloat(station.lat) : undefined,
        longitude: station.lon ? parseFloat(station.lon) : undefined,
        data_type: dataType
      }));
    }
    
    console.log(`✅ ${dataType} 관측소 ${stations.length}개 다운로드 완료`);
    return stations;
    
  } catch (error) {
    console.error(`❌ ${dataType} 다운로드 실패:`, error.message);
    return [];
  }
}

// 메인 실행 함수
async function main() {
  console.log('🚀 HRFCO 관측소 데이터 다운로드 시작...');
  
  const dataTypes = ['dam', 'waterlevel', 'rainfall'];
  
  for (const dataType of dataTypes) {
    const stations = await fetchStationData(dataType);
    
    if (stations.length > 0) {
      const fileName = `${dataType}-stations.json`;
      const filePath = path.join(dataDir, fileName);
      
      fs.writeFileSync(filePath, JSON.stringify(stations, null, 2), 'utf8');
      console.log(`💾 ${dataType} 데이터 저장 완료: ${filePath}`);
      
      // 문경시 관련 관측소 찾기
      const mungyeongStations = stations.filter(station => 
        station.obs_name && station.obs_name.includes('문경')
      );
      
      if (mungyeongStations.length > 0) {
        console.log(`📍 문경시 관련 ${dataType} 관측소:`);
        mungyeongStations.forEach(station => {
          console.log(`  - ${station.obs_name}: ${station.obs_code}`);
        });
      }
    }
  }
  
  console.log('🎉 모든 관측소 데이터 다운로드 완료!');
}

// 실행
main().catch(console.error);