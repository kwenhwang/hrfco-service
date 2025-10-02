import { Handler } from '@netlify/functions';
import { normalizeQuery, calculateSimilarity, fetchHRFCOData, Station } from './utils';

export const handler: Handler = async (event) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json'
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers, body: '' };
  }

  try {
    const params = event.httpMethod === 'GET' 
      ? event.queryStringParameters || {}
      : JSON.parse(event.body || '{}');

    const query = params.query;
    const limit = Math.min(parseInt(params.limit || '5'), 10);

    if (!query) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ error: 'query parameter required' })
      };
    }

    // Normalize and search
    const queryInfo = normalizeQuery(query);
    const data = await fetchHRFCOData(`${queryInfo.dataType}/info.json`);
    const stations: Station[] = data.content || [];

    if (stations.length === 0) {
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          status: 'no_match',
          message: `'${query}'에 대한 관측소를 찾을 수 없습니다`,
          suggestions: []
        })
      };
    }

    // Find best matches
    const scoredStations = stations
      .map(station => ({
        station,
        score: calculateSimilarity(station, queryInfo)
      }))
      .filter(item => item.score > 0.1)
      .sort((a, b) => b.score - a.score)
      .slice(0, limit);

    if (scoredStations.length === 0) {
      // Suggest alternatives
      const suggestions = stations
        .slice(0, 5)
        .map(s => `${s.obsnm} (${s.addr})`)
        .filter(s => s.includes(query.slice(0, 1)));

      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          status: 'no_match',
          message: `'${query}'에 대한 관측소를 찾을 수 없습니다`,
          suggestions: suggestions.slice(0, 3)
        })
      };
    }

    const result = {
      status: 'success',
      summary: `${query} 관련 ${scoredStations.length}개 관측소 발견`,
      data: {
        query,
        data_type: queryInfo.dataType,
        found_stations: scoredStations.length,
        total_available: stations.length,
        stations: scoredStations.map(({ station }) => ({
          code: station.wlobscd || station.rfobscd || station.damcd || '',
          name: station.obsnm,
          address: station.addr,
          agency: station.agcnm
        }))
      }
    };

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify(result)
    };

  } catch (error: any) {
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: error?.message || 'Unknown error' })
    };
  }
};
