// 한국어 수문 용어 자연어 처리기
export interface TermMapping {
  rainfall: string[];
  waterlevel: string[];
  dam: string[];
}

// 한국 기상청/수자원공사 공식 용어집 기반 매핑
export const TERM_MAPPING: TermMapping = {
  rainfall: [
    "우량", "강우량", "비", "강우", "강수량", "비오는량", 
    "강수", "비량", "우량관측소", "강우관측소", "비관측소",
    "mm", "밀리미터", "강수강도", "시간당강수량", "일강수량"
  ],
  waterlevel: [
    "수위", "물높이", "강물높이", "하천수위", "수위관측소",
    "물의높이", "강수위", "하천높이", "수심", "물깊이",
    "m", "미터", "EL", "표고", "수위표"
  ],
  dam: [
    "댐", "저수지", "호수", "댐수위", "저수지수위", "댐저수율",
    "저수량", "댐용량", "저수지용량", "댐관측소", "저수지관측소",
    "%", "퍼센트", "저수율", "댐저수율", "저수지저수율"
  ]
};

// 지역별 방언 및 일반적 표현 매핑
export const REGIONAL_TERMS = {
  rainfall: {
    "경상도": ["비", "비오는량", "우량"],
    "전라도": ["비", "강우", "우량"],
    "충청도": ["비", "강수량", "우량"],
    "강원도": ["비", "강우량", "우량"],
    "경기도": ["비", "강수량", "우량"]
  },
  waterlevel: {
    "경상도": ["수위", "물높이", "강물높이"],
    "전라도": ["수위", "물높이", "하천높이"],
    "충청도": ["수위", "물높이", "강수위"],
    "강원도": ["수위", "물높이", "하천수위"],
    "경기도": ["수위", "물높이", "강물높이"]
  }
};

/**
 * 쿼리에서 데이터 타입 감지
 */
export function detectDataType(query: string): 'dam' | 'waterlevel' | 'rainfall' {
  const normalizedQuery = query.toLowerCase();
  
  // 각 타입별 용어 확인
  for (const [type, terms] of Object.entries(TERM_MAPPING)) {
    if (terms.some((term: string) => normalizedQuery.includes(term.toLowerCase()))) {
      return type as 'dam' | 'waterlevel' | 'rainfall';
    }
  }
  
  // 기본값: 수위관측소
  return 'waterlevel';
}

/**
 * 쿼리에서 관측소명 추출
 */
export function extractStationName(query: string): string {
  // 불필요한 용어 제거
  const cleanedQuery = query
    .replace(/우량|강우량|비|강우|강수량|수위|물높이|댐|저수지|호수|관측소|알려줘|어때|현재|지금/g, '')
    .replace(/[()]/g, '')
    .replace(/\s+/g, ' ')
    .trim();
  
  return cleanedQuery;
}

/**
 * 쿼리 의도 분석
 */
export function analyzeQueryIntent(query: string): {
  dataType: 'dam' | 'waterlevel' | 'rainfall';
  stationName: string;
  intent: 'current_value' | 'status' | 'trend' | 'general';
  confidence: number;
} {
  const dataType = detectDataType(query);
  const stationName = extractStationName(query);
  
  let intent: 'current_value' | 'status' | 'trend' | 'general' = 'general';
  let confidence = 0.5;
  
  // 의도 분석
  if (query.includes('현재') || query.includes('지금') || query.includes('어때')) {
    intent = 'current_value';
    confidence = 0.9;
  } else if (query.includes('상태') || query.includes('정상') || query.includes('이상')) {
    intent = 'status';
    confidence = 0.8;
  } else if (query.includes('추세') || query.includes('변화') || query.includes('증가') || query.includes('감소')) {
    intent = 'trend';
    confidence = 0.8;
  }
  
  // 관측소명이 명확한 경우 신뢰도 증가
  if (stationName.length > 2 && !stationName.includes('관측소')) {
    confidence += 0.2;
  }
  
  return {
    dataType,
    stationName,
    intent,
    confidence: Math.min(confidence, 1.0)
  };
}

/**
 * 완전한 답변 생성
 */
export function generateDirectAnswer(
  query: string, 
  stationData: any, 
  dataType: 'dam' | 'waterlevel' | 'rainfall'
): string {
  console.log('🔍 generateDirectAnswer called:', {
    query,
    stationName: stationData.name,
    dataType,
    currentData: stationData.current_data
  });
  
  const station = stationData;
  const currentData = station.current_data;
  
  if (dataType === 'rainfall') {
    const rainfall = currentData?.rainfall || '0.0mm';
    const status = currentData?.status || '정상';
    const answer = `${station.name}의 현재 강수량은 ${rainfall}이며, 상태는 ${status}입니다.`;
    console.log('✅ Generated rainfall answer:', answer);
    return answer;
  } else if (dataType === 'waterlevel') {
    const waterLevel = currentData?.water_level || 'N/A';
    const status = currentData?.status || '정상';
    const answer = `${station.name}의 현재 수위는 ${waterLevel}이며, 상태는 ${status}입니다.`;
    console.log('✅ Generated waterlevel answer:', answer);
    return answer;
  } else if (dataType === 'dam') {
    const waterLevel = currentData?.water_level || 'N/A';
    const storageRate = currentData?.storage_rate || 'N/A';
    const answer = `${station.name}의 현재 수위는 ${waterLevel}이며, 저수율은 ${storageRate}입니다.`;
    console.log('✅ Generated dam answer:', answer);
    return answer;
  }
  
  const answer = `${station.name}의 현재 측정값을 조회했습니다.`;
  console.log('✅ Generated default answer:', answer);
  return answer;
}

/**
 * 요약 정보 생성
 */
export function generateSummary(
  stationData: any, 
  dataType: 'dam' | 'waterlevel' | 'rainfall'
): string {
  const station = stationData;
  const currentValue = station.current_data?.rainfall || 
                      station.current_data?.water_level || 
                      station.current_data?.storage_rate || 'N/A';
  
  if (dataType === 'rainfall') {
    return `${station.name} 현재 강수량 ${currentValue}`;
  } else if (dataType === 'waterlevel') {
    return `${station.name} 현재 수위 ${currentValue}`;
  } else if (dataType === 'dam') {
    return `${station.name} 현재 수위 ${currentValue}`;
  }
  
  return `${station.name} 현재 측정값 ${currentValue}`;
}