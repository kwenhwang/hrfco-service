import { Handler } from '@netlify/functions';

export const handler: Handler = async (event) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json'
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers, body: '' };
  }

  const baseUrl = process.env.URL || 'https://hrfco-mcp.netlify.app';

  const functions = {
    functions: [
      {
        name: 'search_water_station_by_name',
        description: '지역명이나 강 이름으로 관측소를 검색하고 실시간 데이터까지 조회',
        parameters: {
          type: 'object',
          properties: {
            location_name: {
              type: 'string',
              description: '서울, 한강, 낙동강, 부산 등 자연어 입력'
            },
            data_type: {
              type: 'string',
              enum: ['waterlevel', 'rainfall', 'dam'],
              description: 'waterlevel 또는 rainfall',
              default: 'waterlevel'
            },
            limit: {
              type: 'integer',
              minimum: 1,
              maximum: 10,
              description: '결과 개수 제한',
              default: 5
            }
          },
          required: ['location_name']
        }
      },
      {
        name: 'get_water_info_by_location',
        description: '한 번의 요청으로 지역 검색부터 실시간 데이터까지 모든 것을 처리',
        parameters: {
          type: 'object',
          properties: {
            query: {
              type: 'string',
              description: '한강 수위, 서울 강우량, 부산 낙동강 등 자연어 질의'
            },
            limit: {
              type: 'integer',
              minimum: 1,
              maximum: 10,
              description: '결과 개수 제한',
              default: 5
            }
          },
          required: ['query']
        }
      },
      {
        name: 'recommend_nearby_stations',
        description: '입력된 지역 주변의 관련 관측소들을 추천',
        parameters: {
          type: 'object',
          properties: {
            location: {
              type: 'string',
              description: '기준 위치 (지명)'
            },
            radius: {
              type: 'integer',
              description: '반경 (km)',
              default: 20
            },
            priority: {
              type: 'string',
              enum: ['distance', 'data_quality'],
              description: 'distance(거리순) 또는 data_quality(데이터 품질순)',
              default: 'distance'
            }
          },
          required: ['location']
        }
      }
    ],
    api_endpoints: {
      search_station: `${baseUrl}/.netlify/functions/search-station`,
      water_info: `${baseUrl}/.netlify/functions/get-water-info`,
      nearby_stations: `${baseUrl}/.netlify/functions/recommend-stations`
    }
  };

  return {
    statusCode: 200,
    headers,
    body: JSON.stringify(functions)
  };
};
