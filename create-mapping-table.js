#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// 다운로드한 데이터 파일들 읽기
const dataDir = path.join(__dirname, 'netlify', 'functions', 'data');

function loadStationData(fileName) {
  try {
    const filePath = path.join(dataDir, fileName);
    if (fs.existsSync(filePath)) {
      const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
      console.log(`✅ ${fileName}: ${data.length}개 로드`);
      return data;
    }
  } catch (error) {
    console.warn(`⚠️ ${fileName} 로드 실패:`, error.message);
  }
  return [];
}

// 모든 관측소 데이터 로드
const dams = loadStationData('dam-stations.json');
const waterlevels = loadStationData('waterlevel-stations.json');
const rainfalls = loadStationData('rainfall-stations.json');

// 경량 매핑 테이블 생성
function createLightweightMapping(stations, type) {
  return stations.map(station => {
    // 키워드 추출 (이름에서 지역명, 관측소명 분리)
    const keywords = extractKeywords(station.obs_name, station.location);
    
    return {
      code: station.obs_code,
      name: station.obs_name,
      region: station.location || '',
      type: type,
      keywords: keywords,
      agency: station.agency || ''
    };
  });
}

// 키워드 추출 함수
function extractKeywords(name, location) {
  const keywords = [];
  
  // 기본 이름 추가
  keywords.push(name);
  
  // 지역명 추출
  if (location) {
    const regionParts = location.split(/[시도군구읍면동리]/);
    regionParts.forEach(part => {
      if (part.trim() && part.trim().length > 1) {
        keywords.push(part.trim());
      }
    });
  }
  
  // 관측소명에서 키워드 추출
  const nameParts = name.split(/[()]/);
  nameParts.forEach(part => {
    if (part.trim() && part.trim().length > 1) {
      keywords.push(part.trim());
    }
  });
  
  // 중복 제거 및 정리
  return [...new Set(keywords)].filter(k => k.length > 1);
}

// 매핑 테이블 생성
const damMappings = createLightweightMapping(dams, 'dam');
const waterlevelMappings = createLightweightMapping(waterlevels, 'waterlevel');
const rainfallMappings = createLightweightMapping(rainfalls, 'rainfall');

// 전체 매핑 테이블
const STATION_MAPPING = [...damMappings, ...waterlevelMappings, ...rainfallMappings];

console.log(`\n📊 매핑 테이블 생성 완료:`);
console.log(`- 댐: ${damMappings.length}개`);
console.log(`- 수위관측소: ${waterlevelMappings.length}개`);
console.log(`- 우량관측소: ${rainfallMappings.length}개`);
console.log(`- 총계: ${STATION_MAPPING.length}개`);

// 평림댐 관련 매핑 확인
const pyeongrimStations = STATION_MAPPING.filter(station => 
  station.name.includes('평림') || station.keywords.some(k => k.includes('평림'))
);

console.log(`\n📍 평림 관련 관측소:`);
pyeongrimStations.forEach(station => {
  console.log(`- ${station.name}: ${station.code} (${station.type})`);
});

// TypeScript 파일로 출력
const tsContent = `// HRFCO 관측소 경량 매핑 테이블 (자동 생성)
// 생성일: ${new Date().toISOString()}
// 총 ${STATION_MAPPING.length}개 관측소

export interface StationMapping {
  code: string;
  name: string;
  region: string;
  type: 'dam' | 'waterlevel' | 'rainfall';
  keywords: string[];
  agency: string;
}

export const STATION_MAPPING: StationMapping[] = ${JSON.stringify(STATION_MAPPING, null, 2)};

// 매핑 통계
export const MAPPING_STATS = {
  total: ${STATION_MAPPING.length},
  byType: {
    dam: ${damMappings.length},
    waterlevel: ${waterlevelMappings.length},
    rainfall: ${rainfallMappings.length}
  }
};
`;

// 파일 저장
const outputPath = path.join(__dirname, 'netlify', 'functions', 'station-mapping.ts');
fs.writeFileSync(outputPath, tsContent, 'utf8');

console.log(`\n💾 매핑 테이블 저장 완료: ${outputPath}`);
console.log(`📏 파일 크기: ${(fs.statSync(outputPath).size / 1024).toFixed(1)}KB`);

// 평림댐 테스트
console.log(`\n🔍 평림댐 검색 테스트:`);
const testQuery = '평림댐';
const matches = STATION_MAPPING.filter(station => 
  station.name.includes(testQuery) || 
  station.keywords.some(k => k.includes('평림'))
);

matches.forEach(match => {
  console.log(`✅ ${match.name}: ${match.code} (${match.type})`);
});