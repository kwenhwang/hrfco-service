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

    const location = params.location;
    const radius = parseInt(params.radius || '20');
    const priority = params.priority || 'distance';

    if (!location) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ error: 'location parameter required' })
      };
    }

    // Search for stations near the location
    const queryInfo = normalizeQuery(location);
    const data = await fetchHRFCOData('waterlevel/info.json');
    const stations: Station[] = data.content || [];

    // Find relevant stations
    const scoredStations = stations
      .map(station => ({
        station,
        score: calculateSimilarity(station, queryInfo)
      }))
      .filter(item => item.score > 0.05)
      .sort((a, b) => b.score - a.score)
      .slice(0, 10);

    const recommendations = scoredStations
      .slice(0, 5)
      .map(({ station }) => ({
        code: station.wlobscd || '',
        name: station.obsnm,
        address: station.addr,
        agency: station.agcnm
      }));

    const result = {
      location,
      radius_km: radius,
      priority,
      recommendations
    };

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify(result)
    };

  } catch (error) {
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ error: error.message })
    };
  }
};
