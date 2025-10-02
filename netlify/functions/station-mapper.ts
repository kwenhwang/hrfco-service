// HRFCO 관측소 제원정보를 다운받아 매핑 규칙을 생성하는 모듈

interface StationInfo {
  obs_code: string;
  obs_name: string;
  river_name?: string;
  location?: string;
  address?: string;
  agency?: string;
  latitude?: number;
  longitude?: number;
  data_type: 'dam' | 'waterlevel' | 'rainfall';
}

interface StationMapping {
  [key: string]: {
    code: string;
    data_type: 'dam' | 'waterlevel' | 'rainfall';
    name: string;
    river?: string;
    location?: string;
  };
}

export class StationMapper {
  private stationMapping: StationMapping = {};
  private isInitialized = false;

  // HRFCO API에서 관측소 제원정보를 다운받아 매핑 생성
  async initializeMapping(): Promise<void> {
    try {
      console.log('🔄 HRFCO 관측소 제원정보 다운로드 시작...');
      
      // 1. 댐 정보 다운로드
      const damStations = await this.fetchStationInfo('dam');
      console.log(`📊 댐 관측소 ${damStations.length}개 다운로드 완료`);
      
      // 2. 수위관측소 정보 다운로드
      const waterlevelStations = await this.fetchStationInfo('waterlevel');
      console.log(`📊 수위관측소 ${waterlevelStations.length}개 다운로드 완료`);
      
      // 3. 우량관측소 정보 다운로드
      const rainfallStations = await this.fetchStationInfo('rainfall');
      console.log(`📊 우량관측소 ${rainfallStations.length}개 다운로드 완료`);
      
      // 4. 매핑 규칙 생성
      this.createMappingRules(damStations, 'dam');
      this.createMappingRules(waterlevelStations, 'waterlevel');
      this.createMappingRules(rainfallStations, 'rainfall');
      
      this.isInitialized = true;
      console.log(`✅ 총 ${Object.keys(this.stationMapping).length}개 관측소 매핑 완료`);
      
    } catch (error) {
      console.error('❌ 관측소 매핑 초기화 실패:', error);
      // 실패 시 데모 데이터로 폴백
      this.createDemoMapping();
    }
  }

  // 저장된 관측소 정보 파일에서 데이터 로드
  private async fetchStationInfo(dataType: string): Promise<StationInfo[]> {
    try {
      // 저장된 파일에서 데이터 로드 시도
      const fs = require('fs');
      const path = require('path');
      
      const fileName = `${dataType}-stations.json`;
      const filePath = path.join(__dirname, '..', 'data', fileName);
      
      if (fs.existsSync(filePath)) {
        console.log(`📁 ${dataType} 저장된 파일에서 로드: ${filePath}`);
        const fileData = fs.readFileSync(filePath, 'utf8');
        const stations = JSON.parse(fileData);
        console.log(`✅ ${dataType} 관측소 ${stations.length}개 파일에서 로드 완료`);
        return stations;
      } else {
        console.log(`⚠️ ${dataType} 저장된 파일이 없음: ${filePath}`);
        throw new Error(`저장된 ${dataType} 파일이 없습니다`);
      }
      
    } catch (error) {
      console.warn(`⚠️ ${dataType} 파일 로드 실패, 데모 데이터 사용:`, error);
      return this.getDemoStationInfo(dataType);
    }
  }

  // 매핑 규칙 생성
  private createMappingRules(stations: StationInfo[], dataType: 'dam' | 'waterlevel' | 'rainfall'): void {
    stations.forEach(station => {
      if (!station.obs_code || !station.obs_name) return;
      
      // 1. 정확한 이름으로 매핑
      this.stationMapping[station.obs_name] = {
        code: station.obs_code,
        data_type: dataType,
        name: station.obs_name,
        river: station.river_name,
        location: station.location || station.address
      };
      
      // 2. 지역명 + 관측소명 조합으로 매핑
      if (station.location) {
        const locationKey = `${station.location}${station.obs_name}`;
        this.stationMapping[locationKey] = {
          code: station.obs_code,
          data_type: dataType,
          name: station.obs_name,
          river: station.river_name,
          location: station.location
        };
      }
      
      // 3. 하천명 + 관측소명 조합으로 매핑
      if (station.river_name) {
        const riverKey = `${station.river_name}${station.obs_name}`;
        this.stationMapping[riverKey] = {
          code: station.obs_code,
          data_type: dataType,
          name: station.obs_name,
          river: station.river_name,
          location: station.location
        };
      }
      
      // 4. 관측소명에서 키워드 추출하여 매핑
      const keywords = this.extractKeywords(station.obs_name);
      keywords.forEach(keyword => {
        if (keyword.length > 1) { // 1글자 키워드는 제외
          this.stationMapping[keyword] = {
            code: station.obs_code,
            data_type: dataType,
            name: station.obs_name,
            river: station.river_name,
            location: station.location
          };
        }
      });
    });
  }

  // 관측소명에서 키워드 추출
  private extractKeywords(name: string): string[] {
    const keywords: string[] = [];
    
    // 댐, 대교, 관측소 등 접미사 제거
    const cleanName = name.replace(/[댐대교관측소]/g, '');
    
    // 2글자 이상의 연속된 문자 추출
    for (let i = 0; i < cleanName.length - 1; i++) {
      for (let j = i + 2; j <= cleanName.length; j++) {
        const keyword = cleanName.substring(i, j);
        if (keyword.length >= 2) {
          keywords.push(keyword);
        }
      }
    }
    
    return keywords;
  }

  // 관측소 코드 찾기
  findStationCode(query: string): { code: string; data_type: string; name: string } | null {
    if (!this.isInitialized) {
      console.warn('⚠️ StationMapper가 초기화되지 않았습니다');
      return null;
    }

    // 1. 정확한 매칭
    if (this.stationMapping[query]) {
      const mapping = this.stationMapping[query];
      return {
        code: mapping.code,
        data_type: mapping.data_type,
        name: mapping.name
      };
    }

    // 2. 부분 매칭 (포함 관계)
    for (const [key, mapping] of Object.entries(this.stationMapping)) {
      if (key.includes(query) || query.includes(key)) {
        return {
          code: mapping.code,
          data_type: mapping.data_type,
          name: mapping.name
        };
      }
    }

    // 3. 키워드 매칭
    const queryKeywords = this.extractKeywords(query);
    for (const keyword of queryKeywords) {
      if (this.stationMapping[keyword]) {
        const mapping = this.stationMapping[keyword];
        return {
          code: mapping.code,
          data_type: mapping.data_type,
          name: mapping.name
        };
      }
    }

    return null;
  }

  // 데모 데이터 생성 (API 실패 시 사용)
  private createDemoMapping(): void {
    console.log('📝 데모 매핑 데이터 생성 중...');
    
    // 주요 댐들
    const demoDams = [
      { name: '대청댐', code: '1018680', river: '금강', location: '대전' },
      { name: '소양댐', code: '1018681', river: '한강', location: '춘천' },
      { name: '충주댐', code: '1018682', river: '한강', location: '충주' },
      { name: '안동댐', code: '1018683', river: '낙동강', location: '안동' },
      { name: '임하댐', code: '1018684', river: '낙동강', location: '안동' },
      { name: '합천댐', code: '1018685', river: '낙동강', location: '합천' },
    ];

    // 주요 수위관측소들
    const demoWaterlevels = [
      { name: '한강대교', code: '1018700', river: '한강', location: '서울' },
      { name: '잠실대교', code: '1018701', river: '한강', location: '서울' },
      { name: '성산대교', code: '1018702', river: '한강', location: '서울' },
      { name: '반포대교', code: '1018703', river: '한강', location: '서울' },
      { name: '동작대교', code: '1018704', river: '한강', location: '서울' },
      { name: '한남대교', code: '1018705', river: '한강', location: '서울' },
    ];

    // 주요 우량관측소들
    const demoRainfalls = [
      { name: '서울우량관측소', code: '1018825', river: '한강', location: '서울' },
      { name: '부산우량관측소', code: '1018826', river: '낙동강', location: '부산' },
      { name: '대구우량관측소', code: '1018827', river: '낙동강', location: '대구' },
      { name: '인천우량관측소', code: '1018828', river: '한강', location: '인천' },
      { name: '광주우량관측소', code: '1018829', river: '영산강', location: '광주' },
      { name: '대전우량관측소', code: '1018830', river: '금강', location: '대전' },
      { name: '문경시(농암리)', code: '1018831', river: '낙동강', location: '문경시' },
      { name: '문경시(화산리)', code: '1018833', river: '낙동강', location: '문경시' },
      { name: '가평군(가평교)', code: '1018832', river: '한강', location: '가평군' },
    ];

    // 데모 데이터로 매핑 생성
    [...demoDams, ...demoWaterlevels, ...demoRainfalls].forEach(station => {
      const dataType = demoDams.includes(station as any) ? 'dam' : 
                      demoWaterlevels.includes(station as any) ? 'waterlevel' : 'rainfall';
      
      // 1. 정확한 이름으로 매핑
      this.stationMapping[station.name] = {
        code: station.code,
        data_type: dataType,
        name: station.name,
        river: station.river,
        location: station.location
      };
      
      // 2. 지역명 + 관측소명 조합으로 매핑
      if (station.location) {
        const locationKey = `${station.location}${station.name}`;
        this.stationMapping[locationKey] = {
          code: station.code,
          data_type: dataType,
          name: station.name,
          river: station.river,
          location: station.location
        };
      }
      
      // 3. 관측소명에서 키워드 추출하여 매핑
      const keywords = this.extractKeywords(station.name);
      keywords.forEach(keyword => {
        if (keyword.length > 1) {
          this.stationMapping[keyword] = {
            code: station.code,
            data_type: dataType,
            name: station.name,
            river: station.river,
            location: station.location
          };
        }
      });
      
      // 4. 지역명으로도 매핑
      if (station.location) {
        this.stationMapping[station.location] = {
          code: station.code,
          data_type: dataType,
          name: station.name,
          river: station.river,
          location: station.location
        };
      }
    });

    this.isInitialized = true;
    console.log(`✅ 데모 매핑 데이터 ${Object.keys(this.stationMapping).length}개 생성 완료`);
  }

  // 데모 관측소 정보 생성
  private getDemoStationInfo(dataType: string): StationInfo[] {
    const demoData: Record<string, StationInfo[]> = {
      dam: [
        { obs_code: '1018680', obs_name: '대청댐', river_name: '금강', location: '대전', data_type: 'dam' },
        { obs_code: '1018681', obs_name: '소양댐', river_name: '한강', location: '춘천', data_type: 'dam' },
        { obs_code: '1018682', obs_name: '충주댐', river_name: '한강', location: '충주', data_type: 'dam' },
      ],
      waterlevel: [
        { obs_code: '1018700', obs_name: '한강대교', river_name: '한강', location: '서울', data_type: 'waterlevel' },
        { obs_code: '1018701', obs_name: '잠실대교', river_name: '한강', location: '서울', data_type: 'waterlevel' },
        { obs_code: '1018702', obs_name: '성산대교', river_name: '한강', location: '서울', data_type: 'waterlevel' },
      ],
      rainfall: [
        { obs_code: '1018825', obs_name: '서울우량관측소', river_name: '한강', location: '서울', data_type: 'rainfall' },
        { obs_code: '1018826', obs_name: '부산우량관측소', river_name: '낙동강', location: '부산', data_type: 'rainfall' },
        { obs_code: '1018827', obs_name: '대구우량관측소', river_name: '낙동강', location: '대구', data_type: 'rainfall' },
      ]
    };

    return demoData[dataType] || [];
  }

  // 매핑 통계 정보
  getMappingStats(): { total: number; byType: Record<string, number> } {
    const stats = { total: 0, byType: { dam: 0, waterlevel: 0, rainfall: 0 } };
    
    Object.values(this.stationMapping).forEach(mapping => {
      stats.total++;
      stats.byType[mapping.data_type]++;
    });
    
    return stats;
  }
}

// 싱글톤 인스턴스
export const stationMapper = new StationMapper();