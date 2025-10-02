// Korean text processing and similarity utilities
export interface Station {
  wlobscd?: string;
  rfobscd?: string;
  damcd?: string;
  obsnm: string;
  addr: string;
  agcnm?: string;
  etcaddr?: string;
  lon?: string;
  lat?: string;
}

export interface SearchResult {
  query: string;
  data_type: string;
  found_stations: number;
  total_available: number;
  stations: Array<{
    code: string;
    name: string;
    address: string;
    agency?: string;
    real_code?: string;
  }>;
  error?: string;
  note?: string;
}

// Korean region mapping
export const REGION_MAPPING: Record<string, string[]> = {
  '서울': ['서울', '한강', '청계천'],
  '부산': ['부산', '낙동강', '수영강'],
  '대구': ['대구', '낙동강', '금호강'],
  '인천': ['인천', '한강', '굴포천'],
  '광주': ['광주', '영산강', '황룡강'],
  '대전': ['대전', '금강', '갑천'],
  '울산': ['울산', '태화강', '회야강'],
  '경기': ['경기', '한강', '임진강'],
  '강원': ['강원', '한강', '낙동강'],
  '충북': ['충북', '한강', '금강'],
  '충남': ['충남', '금강', '한강'],
  '전북': ['전북', '금강', '만경강'],
  '전남': ['전남', '영산강', '섬진강'],
  '경북': ['경북', '낙동강', '형산강'],
  '경남': ['경남', '낙동강', '남강'],
  '제주': ['제주', '한천', '천미천']
};

export const RIVER_KEYWORDS = ['한강', '낙동강', '금강', '영산강', '섬진강', '임진강'];

// Normalize Korean query
export function normalizeQuery(query: string) {
  const cleanQuery = query.trim().replace(/\s+/g, '');
  
  let dataType = 'waterlevel';
  if (['강우', '비', '강수'].some(k => cleanQuery.includes(k))) {
    dataType = 'rainfall';
  } else if (cleanQuery.includes('댐')) {
    dataType = 'dam';
  }
  
  const locationHints: string[] = [];
  
  // Region matching
  for (const [region, keywords] of Object.entries(REGION_MAPPING)) {
    if (keywords.some(k => cleanQuery.includes(k))) {
      locationHints.push(...keywords);
    }
  }
  
  // River matching
  RIVER_KEYWORDS.forEach(river => {
    if (cleanQuery.includes(river)) {
      locationHints.push(river);
    }
  });
  
  return {
    original: query,
    dataType,
    locationHints: [...new Set(locationHints)],
    cleanQuery: cleanQuery.replace(/(수위|강우|비|강수|댐)/g, '')
  };
}

// Simple similarity calculation
export function calculateSimilarity(station: Station, queryInfo: ReturnType<typeof normalizeQuery>): number {
  let score = 0;
  const stationName = station.obsnm || '';
  const stationAddr = station.addr || '';
  
  // Direct keyword matching
  queryInfo.locationHints.forEach(hint => {
    if (stationName.includes(hint)) score += 0.5;
    if (stationAddr.includes(hint)) score += 0.3;
  });
  
  // Simple string similarity
  const nameMatch = stringMatch(queryInfo.cleanQuery, stationName);
  const addrMatch = stringMatch(queryInfo.cleanQuery, stationAddr);
  score += Math.max(nameMatch, addrMatch) * 0.4;
  
  return Math.min(score, 1.0);
}

// Basic string matching
function stringMatch(a: string, b: string): number {
  if (!a || !b) return 0;
  const longer = a.length > b.length ? a : b;
  const shorter = a.length > b.length ? b : a;
  if (longer.length === 0) return 1.0;
  
  let matches = 0;
  for (let i = 0; i < shorter.length; i++) {
    if (longer.includes(shorter[i])) matches++;
  }
  return matches / longer.length;
}

// API call helper
export async function fetchHRFCOData(endpoint: string): Promise<any> {
  const apiKey = process.env.HRFCO_API_KEY;
  if (!apiKey) throw new Error('API key required');
  
  const response = await fetch(`http://api.hrfco.go.kr/${apiKey}/${endpoint}`);
  if (!response.ok) throw new Error(`API error: ${response.status}`);
  
  return response.json();
}
