const fetch = require('node-fetch');

const MCP_URL = 'https://hrfco-mcp-functions.netlify.app/.netlify/functions/mcp';

async function testMCPServer() {
  console.log('🧪 MCP 서버 테스트 시작...\n');

  // 1. Initialize 테스트
  console.log('1️⃣ Initialize 테스트');
  try {
    const initResponse = await fetch(MCP_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: "2.0",
        id: 1,
        method: "initialize",
        params: {}
      })
    });
    const initResult = await initResponse.json();
    console.log('✅ Initialize 성공:', JSON.stringify(initResult, null, 2));
  } catch (error) {
    console.log('❌ Initialize 실패:', error.message);
  }

  console.log('\n' + '='.repeat(50) + '\n');

  // 2. Tools List 테스트
  console.log('2️⃣ Tools List 테스트');
  try {
    const toolsResponse = await fetch(MCP_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: "2.0",
        id: 2,
        method: "tools/list",
        params: {}
      })
    });
    const toolsResult = await toolsResponse.json();
    console.log('✅ Tools List 성공:');
    console.log(`📋 총 ${toolsResult.result?.tools?.length || 0}개 도구 발견:`);
    toolsResult.result?.tools?.forEach((tool, index) => {
      console.log(`   ${index + 1}. ${tool.name}: ${tool.description}`);
    });
  } catch (error) {
    console.log('❌ Tools List 실패:', error.message);
  }

  console.log('\n' + '='.repeat(50) + '\n');

  // 3. Tools Call 테스트 - 한강 수위 검색
  console.log('3️⃣ Tools Call 테스트 - 한강 수위 검색');
  try {
    const callResponse = await fetch(MCP_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: "2.0",
        id: 3,
        method: "tools/call",
        params: {
          name: "get_water_info_by_location",
          arguments: {
            query: "한강 수위",
            limit: 3
          }
        }
      })
    });
    const callResult = await callResponse.json();
    console.log('✅ Tools Call 성공:');
    console.log(JSON.stringify(callResult, null, 2));
  } catch (error) {
    console.log('❌ Tools Call 실패:', error.message);
  }

  console.log('\n' + '='.repeat(50) + '\n');

  // 4. 지역명 검색 테스트
  console.log('4️⃣ 지역명 검색 테스트 - 서울');
  try {
    const searchResponse = await fetch(MCP_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: "2.0",
        id: 4,
        method: "tools/call",
        params: {
          name: "search_water_station_by_name",
          arguments: {
            location_name: "서울",
            limit: 3
          }
        }
      })
    });
    const searchResult = await searchResponse.json();
    console.log('✅ 지역명 검색 성공:');
    console.log(JSON.stringify(searchResult, null, 2));
  } catch (error) {
    console.log('❌ 지역명 검색 실패:', error.message);
  }

  console.log('\n' + '='.repeat(50) + '\n');

  // 5. 주변 관측소 추천 테스트
  console.log('5️⃣ 주변 관측소 추천 테스트');
  try {
    const recommendResponse = await fetch(MCP_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: "2.0",
        id: 5,
        method: "tools/call",
        params: {
          name: "recommend_nearby_stations",
          arguments: {
            location: "부산",
            radius: 30
          }
        }
      })
    });
    const recommendResult = await recommendResponse.json();
    console.log('✅ 주변 관측소 추천 성공:');
    console.log(JSON.stringify(recommendResult, null, 2));
  } catch (error) {
    console.log('❌ 주변 관측소 추천 실패:', error.message);
  }

  console.log('\n🎉 MCP 서버 테스트 완료!');
}

// 테스트 실행
testMCPServer().catch(console.error);
