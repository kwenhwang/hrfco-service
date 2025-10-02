import { Handler } from '@netlify/functions';
import { normalizeQuery, calculateSimilarity, fetchHRFCOData, Station, SearchResult } from './utils';

export const handler: Handler = async (event) => {
  // CORS headers
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
    // Parse parameters
    const params = event.httpMethod === 'GET' 
      ? event.queryStringParameters || {}
      : JSON.parse(event.body || '{}');

    const locationName = params.location_name || params.locationName;
    const dataType = params.data_type || params.dataType || 'waterlevel';
    const limit = Math.min(parseInt(params.limit || '5'), 10);

    if (!locationName) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ error: 'location_name parameter required' })
      };
    }

    // Normalize query
    const queryInfo = normalizeQuery(locationName);
    const actualDataType = queryInfo.dataType !== 'waterlevel' ? queryInfo.dataType : dataType;

    // Fetch station data
    const data = await fetchHRFCOData(`${actualDataType}/info.json`);
    const stations: Station[] = data.content || [];

    // Calculate similarity and sort
    const scoredStations = stations
      .map(station => ({
        station,
        score: calculateSimilarity(station, queryInfo)
      }))
      .filter(item => item.score > 0.1)
      .sort((a, b) => b.score - a.score)
      .slice(0, limit);

    // Format result
    const result: SearchResult = {
      query: locationName,
      data_type: actualDataType,
      found_stations: scoredStations.length,
      total_available: stations.length,
      stations: scoredStations.map(({ station }) => ({
        code: station.wlobscd || station.rfobscd || station.damcd || '',
        name: station.obsnm,
        address: station.addr,
        agency: station.agcnm
      }))
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
