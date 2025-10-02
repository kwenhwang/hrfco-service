// 지능형 관측소 검색 매퍼
import { STATION_MAPPING, StationMapping } from './station-mapping';

export interface SearchResult {
  code: string;
  name: string;
  region: string;
  type: 'dam' | 'waterlevel' | 'rainfall';
  keywords: string[];
  agency: string;
  score: number; // 검색 점수 (0-100)
}

export class SmartStationMapper {
  private mappingCache = new Map<string, SearchResult[]>();
  
  /**
   * 관측소명으로 검색
   */
  searchByName(query: string, type?: 'dam' | 'waterlevel' | 'rainfall'): SearchResult[] {
    const cacheKey = `${query}:${type || 'all'}`;
    
    // 캐시 확인
    if (this.mappingCache.has(cacheKey)) {
      return this.mappingCache.get(cacheKey)!;
    }
    
    const normalized = this.normalizeQuery(query);
    const results: SearchResult[] = [];
    
    for (const station of STATION_MAPPING) {
      // 타입 필터링
      if (type && station.type !== type) continue;
      
      const score = this.calculateScore(station, normalized);
      if (score > 0) {
        results.push({
          ...station,
          score
        });
      }
    }
    
    // 점수순 정렬 (높은 점수부터)
    results.sort((a, b) => b.score - a.score);
    
    // 캐시 저장
    this.mappingCache.set(cacheKey, results);
    
    return results.slice(0, 10); // 상위 10개만 반환
  }
  
  /**
   * 자연어 쿼리 정규화
   */
  private normalizeQuery(query: string): string {
    return query
      .replace(/댐|수위|강우량|우량|관측소|교|대교/g, '') // 불필요한 단어 제거
      .replace(/\s+/g, '') // 공백 제거
      .trim();
  }
  
  /**
   * 검색 점수 계산
   */
  private calculateScore(station: StationMapping, query: string): number {
    let score = 0;
    
    // 원본 쿼리와 정규화된 쿼리 모두 사용
    const originalQuery = query;
    const normalizedStationName = station.name.replace(/[()]/g, '').replace(/\s+/g, '');
    const normalizedQuery = originalQuery.replace(/[()]/g, '').replace(/\s+/g, '');
    
    // 1. 정확한 이름 일치 (최고 점수)
    if (station.name === originalQuery) {
      score += 100;
    }
    
    // 2. 정규화된 이름 일치
    if (normalizedStationName === normalizedQuery) {
      score += 95;
    }
    
    // 3. 이름 포함 일치
    if (station.name.includes(originalQuery) || normalizedStationName.includes(normalizedQuery)) {
      score += 80;
    }
    
    // 4. 키워드 일치
    const keywordMatches = station.keywords.filter(keyword => 
      keyword.includes(originalQuery) || originalQuery.includes(keyword) ||
      keyword.includes(normalizedQuery) || normalizedQuery.includes(keyword)
    );
    score += keywordMatches.length * 20;
    
    // 5. 지역명 일치
    if (station.region.includes(originalQuery) || station.region.includes(normalizedQuery)) {
      score += 30;
    }
    
    // 6. 부분 일치 (유사도)
    const similarity = this.calculateSimilarity(station.name, originalQuery);
    score += similarity * 10;
    
    return Math.min(score, 100); // 최대 100점
  }
  
  /**
   * 문자열 유사도 계산 (간단한 버전)
   */
  private calculateSimilarity(str1: string, str2: string): number {
    const longer = str1.length > str2.length ? str1 : str2;
    const shorter = str1.length > str2.length ? str2 : str1;
    
    if (longer.length === 0) return 1.0;
    
    const distance = this.levenshteinDistance(longer, shorter);
    return (longer.length - distance) / longer.length;
  }
  
  /**
   * 레벤슈타인 거리 계산
   */
  private levenshteinDistance(str1: string, str2: string): number {
    const matrix = Array(str2.length + 1).fill(null).map(() => 
      Array(str1.length + 1).fill(null)
    );
    
    for (let i = 0; i <= str1.length; i++) matrix[0][i] = i;
    for (let j = 0; j <= str2.length; j++) matrix[j][0] = j;
    
    for (let j = 1; j <= str2.length; j++) {
      for (let i = 1; i <= str1.length; i++) {
        const indicator = str1[i - 1] === str2[j - 1] ? 0 : 1;
        matrix[j][i] = Math.min(
          matrix[j][i - 1] + 1,     // 삭제
          matrix[j - 1][i] + 1,     // 삽입
          matrix[j - 1][i - 1] + indicator // 교체
        );
      }
    }
    
    return matrix[str2.length][str1.length];
  }
  
  /**
   * 코드로 관측소 정보 조회
   */
  findByCode(code: string): StationMapping | null {
    return STATION_MAPPING.find(station => station.code === code) || null;
  }
  
  /**
   * 지역별 관측소 검색
   */
  searchByRegion(region: string, type?: 'dam' | 'waterlevel' | 'rainfall'): SearchResult[] {
    const results: SearchResult[] = [];
    
    for (const station of STATION_MAPPING) {
      if (type && station.type !== type) continue;
      
      if (station.region.includes(region)) {
        results.push({
          ...station,
          score: 100 // 지역 일치는 높은 점수
        });
      }
    }
    
    return results.sort((a, b) => b.score - a.score);
  }
  
  /**
   * 캐시 초기화
   */
  clearCache(): void {
    this.mappingCache.clear();
  }
  
  /**
   * 매핑 통계
   */
  getStats() {
    const stats = {
      total: STATION_MAPPING.length,
      byType: {
        dam: 0,
        waterlevel: 0,
        rainfall: 0
      },
      cacheSize: this.mappingCache.size
    };
    
    for (const station of STATION_MAPPING) {
      stats.byType[station.type]++;
    }
    
    return stats;
  }
}

// 싱글톤 인스턴스
export const smartStationMapper = new SmartStationMapper();