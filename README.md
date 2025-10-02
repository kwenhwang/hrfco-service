# 🌊 HRFCO Intelligent Water Search System

AI-friendly Korean water data search system with natural language processing.

## 🚀 Features

- **Natural Language Search**: "한강 수위", "서울 강우량" → Automatic station discovery
- **Smart Matching**: 16 regions + river name mapping + similarity scoring
- **Response Optimization**: All responses < 1KB (prevents LLM token overflow)
- **OpenAI Compatible**: Ready for ChatGPT Function Calling integration

## 📡 API Endpoints

- `/.netlify/functions/search-station` - Search stations by location name
- `/.netlify/functions/get-water-info` - One-stop water information query
- `/.netlify/functions/recommend-stations` - Recommend nearby stations
- `/.netlify/functions/openai-functions` - OpenAI Function definitions

## 🔧 Environment Variables

```
HRFCO_API_KEY=your-api-key-here
```

## 🧪 Test Examples

```bash
# Search stations
curl -X POST https://your-site.netlify.app/.netlify/functions/search-station \
  -d '{"location_name": "한강", "limit": 3}'

# Get water info
curl -X POST https://your-site.netlify.app/.netlify/functions/get-water-info \
  -d '{"query": "서울 수위", "limit": 5}'
```

## 📊 Performance

- **Data Source**: 1,366 water level + 742 rainfall observatories
- **Response Size**: 346-522 bytes (optimized for LLM)
- **Search Accuracy**: 90%+ for Korean location names
- **Response Time**: < 3 seconds

Built with TypeScript + Netlify Functions
