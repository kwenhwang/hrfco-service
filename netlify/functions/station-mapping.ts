// HRFCO 관측소 경량 매핑 테이블 (핵심 관측소만)
// 생성일: 2025-10-02T04:00:54.749Z
// 총 14개 핵심 관측소

export interface StationMapping {
  code: string;
  name: string;
  region: string;
  type: 'dam' | 'waterlevel' | 'rainfall';
  keywords: string[];
  agency: string;
}

export const STATION_MAPPING: StationMapping[] = [
  {
    "code": "3008110",
    "name": "대청댐",
    "region": "대전",
    "type": "dam",
    "keywords": [
      "대청",
      "댐"
    ],
    "agency": "한국수자원공사"
  },
  {
    "code": "1003110",
    "name": "충주댐",
    "region": "충주",
    "type": "dam",
    "keywords": [
      "충주",
      "댐"
    ],
    "agency": "한국수자원공사"
  },
  {
    "code": "1001210",
    "name": "광동댐",
    "region": "삼척",
    "type": "dam",
    "keywords": [
      "광동",
      "댐"
    ],
    "agency": "한국수자원공사"
  },
  {
    "code": "5002201",
    "name": "평림댐",
    "region": "장성군",
    "type": "waterlevel",
    "keywords": [
      "평림",
      "댐"
    ],
    "agency": "한국수자원공사"
  },
  {
    "code": "5002680",
    "name": "장성군(평림댐)",
    "region": "장성군",
    "type": "waterlevel",
    "keywords": [
      "평림",
      "장성"
    ],
    "agency": "한국수자원공사"
  },
  {
    "code": "5002677",
    "name": "광주광역시(평림교)",
    "region": "광주광역시",
    "type": "waterlevel",
    "keywords": [
      "평림",
      "광주"
    ],
    "agency": "한국수자원공사"
  },
  {
    "code": "50024051",
    "name": "장성군(평림댐)",
    "region": "장성군",
    "type": "rainfall",
    "keywords": [
      "평림",
      "장성"
    ],
    "agency": "한국수자원공사"
  },
  {
    "code": "99999999",
    "name": "평림댐",
    "region": "장성군",
    "type": "rainfall",
    "keywords": [
      "평림",
      "댐"
    ],
    "agency": "한국수자원공사"
  },
  {
    "code": "20054080",
    "name": "문경시(화산리)",
    "region": "문경시",
    "type": "rainfall",
    "keywords": [
      "문경",
      "화산"
    ],
    "agency": "환경부"
  },
  {
    "code": "20054010",
    "name": "문경시(농암리)",
    "region": "문경시",
    "type": "rainfall",
    "keywords": [
      "문경",
      "농암"
    ],
    "agency": "환경부"
  },
  {
    "code": "20054020",
    "name": "문경시(김용리)",
    "region": "문경시",
    "type": "rainfall",
    "keywords": [
      "문경",
      "김용"
    ],
    "agency": "환경부"
  },
  {
    "code": "10044110",
    "name": "청주시(성대리)",
    "region": "청주시",
    "type": "rainfall",
    "keywords": [
      "청주",
      "성대"
    ],
    "agency": "환경부"
  },
  {
    "code": "20174030",
    "name": "의령군(청계리)",
    "region": "의령군",
    "type": "rainfall",
    "keywords": [
      "의령",
      "청계"
    ],
    "agency": "환경부"
  },
  {
    "code": "2019695",
    "name": "의령군(성산리)",
    "region": "의령군",
    "type": "waterlevel",
    "keywords": [
      "의령",
      "성산"
    ],
    "agency": "환경부"
  },
  {
    "code": "2017630",
    "name": "의령군(대곡교)",
    "region": "의령군",
    "type": "waterlevel",
    "keywords": [
      "의령",
      "대곡"
    ],
    "agency": "환경부"
  },
  {
    "code": "1018700",
    "name": "한강대교",
    "region": "서울",
    "type": "waterlevel",
    "keywords": [
      "한강",
      "대교"
    ],
    "agency": "한국수자원공사"
  },
  {
    "code": "1018701",
    "name": "잠실대교",
    "region": "서울",
    "type": "waterlevel",
    "keywords": [
      "잠실",
      "대교"
    ],
    "agency": "한국수자원공사"
  }
];

// 매핑 통계
export const MAPPING_STATS = {
  total: 17,
  byType: {
    dam: 3,
    waterlevel: 7,
    rainfall: 7
  }
};
