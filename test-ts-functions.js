// Simple test for TypeScript functions
const { normalizeQuery, calculateSimilarity, REGION_MAPPING } = require('./netlify/functions/utils.ts');

// Test Korean text processing
console.log('🧪 Testing TypeScript Korean Processing');

// Test 1: Query normalization
const testQuery = normalizeQuery('한강 수위');
console.log('✅ Query normalization:', testQuery);

// Test 2: Region mapping
console.log('✅ Region mapping keys:', Object.keys(REGION_MAPPING).slice(0, 5));

// Test 3: Mock station similarity
const mockStation = {
  obsnm: '한강대교',
  addr: '서울특별시 용산구',
  wlobscd: '1001001'
};

const similarity = calculateSimilarity(mockStation, testQuery);
console.log('✅ Similarity score:', similarity);

console.log('\n🎉 TypeScript conversion test completed!');
