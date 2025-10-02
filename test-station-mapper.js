const { stationMapper } = require('./dist/netlify/functions/station-mapper');

async function testStationMapper() {
  console.log('🧪 StationMapper 테스트 시작...\n');
  
  try {
    // 1. 초기화
    console.log('1️⃣ StationMapper 초기화...');
    await stationMapper.initializeMapping();
    console.log('✅ 초기화 완료\n');
    
    // 2. 매핑 통계
    const stats = stationMapper.getMappingStats();
    console.log('2️⃣ 매핑 통계:');
    console.log(`총 관측소: ${stats.total}개`);
    console.log(`댐: ${stats.byType.dam}개`);
    console.log(`수위관측소: ${stats.byType.waterlevel}개`);
    console.log(`우량관측소: ${stats.byType.rainfall}개\n`);
    
    // 3. 테스트 쿼리들
    const testQueries = [
      '대청댐',
      '한강대교', 
      '서울우량관측소',
      '가평교',
      '부산',
      '서울'
    ];
    
    console.log('3️⃣ 관측소 검색 테스트:');
    testQueries.forEach(query => {
      const result = stationMapper.findStationCode(query);
      if (result) {
        console.log(`✅ "${query}" → ${result.name} (${result.code}, ${result.data_type})`);
      } else {
        console.log(`❌ "${query}" → 찾을 수 없음`);
      }
    });
    
  } catch (error) {
    console.error('❌ 테스트 실패:', error);
  }
}

testStationMapper();