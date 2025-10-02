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
  // 주요 댐 (기존 + 추가)
  { "code": "1012110", "name": "소양강댐", "region": "춘천", "type": "dam", "keywords": ["소양강", "춘천"], "agency": "한국수자원공사" },
  { "code": "1003110", "name": "충주댐", "region": "충주", "type": "dam", "keywords": ["충주"], "agency": "한국수자원공사" },
  { "code": "3011110", "name": "안동댐", "region": "안동", "type": "dam", "keywords": ["안동"], "agency": "한국수자원공사" },
  { "code": "3008110", "name": "대청댐", "region": "대전", "type": "dam", "keywords": ["대청"], "agency": "한국수자원공사" },
  { "code": "2015110", "name": "합천댐", "region": "합천", "type": "dam", "keywords": ["합천"], "agency": "한국수자원공사" },
  { "code": "3010110", "name": "임하댐", "region": "안동", "type": "dam", "keywords": ["임하", "안동"], "agency": "한국수자원공사" },
  { "code": "2001110", "name": "남강댐", "region": "진주", "type": "dam", "keywords": ["남강", "진주"], "agency": "한국수자원공사" },
  { "code": "2016110", "name": "밀양댐", "region": "밀양", "type": "dam", "keywords": ["밀양"], "agency": "한국수자원공사" },
  { "code": "2018110", "name": "운문댐", "region": "청도", "type": "dam", "keywords": ["운문", "청도"], "agency": "한국수자원공사" },
  { "code": "1001210", "name": "광동댐", "region": "삼척", "type": "dam", "keywords": ["광동"], "agency": "한국수자원공사" },

  // 4대강 주요 지점 (추가)
  { "code": "2009540", "name": "낙동강(구미)", "region": "구미", "type": "waterlevel", "keywords": ["낙동강", "구미"], "agency": "환경부" },
  { "code": "3007550", "name": "금강(공주)", "region": "공주", "type": "waterlevel", "keywords": ["금강", "공주"], "agency": "환경부" },
  { "code": "1018690", "name": "한강(잠실)", "region": "서울", "type": "waterlevel", "keywords": ["한강", "잠실"], "agency": "환경부" },
  { "code": "4001550", "name": "영산강(광주)", "region": "광주", "type": "waterlevel", "keywords": ["영산강", "광주"], "agency": "환경부" },
  { "code": "4006550", "name": "섬진강(하동)", "region": "하동", "type": "waterlevel", "keywords": ["섬진강", "하동"], "agency": "환경부" },
  { "code": "1018700", "name": "한강대교", "region": "서울", "type": "waterlevel", "keywords": ["한강", "대교"], "agency": "한국수자원공사" },
  { "code": "2009560", "name": "낙동강하구둑", "region": "부산", "type": "waterlevel", "keywords": ["낙동강", "부산", "하구"], "agency": "한국수자원공사" },
  { "code": "3007570", "name": "금강(강경)", "region": "논산", "type": "waterlevel", "keywords": ["금강", "강경"], "agency": "환경부" },

  // 지역별 강우 관측소 (추가)
  { "code": "10124010", "name": "춘천시(신북읍)", "region": "춘천", "type": "rainfall", "keywords": ["춘천", "강우"], "agency": "환경부" },
  { "code": "30114020", "name": "안동시(와룡면)", "region": "안동", "type": "rainfall", "keywords": ["안동", "강우"], "agency": "환경부" },
  { "code": "20014030", "name": "진주시(집현면)", "region": "진주", "type": "rainfall", "keywords": ["진주", "강우"], "agency": "환경부" },
  { "code": "40024040", "name": "전주시(완산구)", "region": "전주", "type": "rainfall", "keywords": ["전주", "강우"], "agency": "환경부" },
  { "code": "20104050", "name": "포항시(북구)", "region": "포항", "type": "rainfall", "keywords": ["포항", "강우"], "agency": "환경부" },
  { "code": "40014060", "name": "목포시(옥암동)", "region": "목포", "type": "rainfall", "keywords": ["목포", "강우"], "agency": "환경부" },
  { "code": "10074070", "name": "강릉시(성산면)", "region": "강릉", "type": "rainfall", "keywords": ["강릉", "강우"], "agency": "환경부" },
  { "code": "30084080", "name": "청주시(상당구)", "region": "청주", "type": "rainfall", "keywords": ["청주", "강우"], "agency": "환경부" },
  { "code": "20154090", "name": "창원시(의창구)", "region": "창원", "type": "rainfall", "keywords": ["창원", "강우"], "agency": "환경부" },
  { "code": "50014100", "name": "제주시(아라동)", "region": "제주", "type": "rainfall", "keywords": ["제주", "강우"], "agency": "환경부" },

  // 기존 데이터 유지
  { "code": "5002201", "name": "평림댐", "region": "장성군", "type": "waterlevel", "keywords": ["평림", "댐"], "agency": "한국수자원공사" },
  { "code": "20174030", "name": "의령군(청계리)", "region": "의령군", "type": "rainfall", "keywords": ["의령", "청계"], "agency": "환경부" },
  { "code": "2017630", "name": "의령군(대곡교)", "region": "의령군", "type": "waterlevel", "keywords": ["의령", "대곡"], "agency": "환경부" }
];
