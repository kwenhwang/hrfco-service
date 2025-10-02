#!/usr/bin/env python3
"""
HRFCO REST API for OpenAI Function Calling
"""
import asyncio
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    import httpx
    import uvicorn
except ImportError:
    print("Install: pip install fastapi httpx uvicorn")
    exit(1)

from dotenv import load_dotenv
load_dotenv()

HRFCO_API_KEY = os.getenv('HRFCO_API_KEY', '')

app = FastAPI(title="HRFCO OpenAI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class HRFCOClient:
    def __init__(self):
        self.base_url = "http://api.hrfco.go.kr"
        self.api_key = HRFCO_API_KEY
    
    async def get_observatories(self, hydro_type: str = "waterlevel", limit: int = 5):
        if not self.api_key:
            return {"error": "API key required"}
        
        try:
            url = f"{self.base_url}/{self.api_key}/{hydro_type}/info.json"
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                content = data.get("content", [])
                
                return {
                    "observatories": content[:limit],
                    "total_count": len(content),
                    "returned_count": min(limit, len(content))
                }
        except Exception as e:
            return {"error": str(e)}

client = HRFCOClient()

@app.get("/")
async def root():
    return {"service": "HRFCO OpenAI API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/observatories")
async def get_observatories(hydro_type: str = "waterlevel", limit: int = 5):
    """Get Korean water observatories data"""
    result = await client.get_observatories(hydro_type, limit)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

@app.get("/search/station")
async def search_station_by_name(location_name: str, data_type: str = "waterlevel", 
                                auto_fetch_data: bool = False, limit: int = 5):
    """지역명으로 관측소 검색"""
    from smart_water_search import SmartWaterSearch
    search_engine = SmartWaterSearch()
    return await search_engine.search_stations_by_name(location_name, data_type, auto_fetch_data, limit)

@app.get("/search/water-info")
async def get_water_info_by_location(query: str, limit: int = 5):
    """원스톱 수문 정보 조회"""
    from smart_water_search import SmartWaterSearch
    search_engine = SmartWaterSearch()
    return await search_engine.get_water_info_by_location(query, limit)

@app.get("/search/nearby")
async def recommend_nearby_stations(location: str, radius: int = 20, priority: str = "distance"):
    """주변 관측소 추천"""
    from smart_water_search import SmartWaterSearch
    search_engine = SmartWaterSearch()
    return await search_engine.recommend_nearby_stations(location, radius, priority)

@app.get("/openai/functions")
async def get_function_definitions():
    """OpenAI Function Calling definitions"""
    return {
        "functions": [
            {
                "name": "search_water_station_by_name",
                "description": "지역명이나 강 이름으로 관측소를 검색하고 실시간 데이터까지 조회",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location_name": {
                            "type": "string",
                            "description": "서울, 한강, 낙동강, 부산 등 자연어 입력"
                        },
                        "data_type": {
                            "type": "string",
                            "enum": ["waterlevel", "rainfall", "dam"],
                            "description": "waterlevel 또는 rainfall",
                            "default": "waterlevel"
                        },
                        "auto_fetch_data": {
                            "type": "boolean",
                            "description": "검색 후 자동으로 실시간 데이터 조회 여부",
                            "default": False
                        },
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 10,
                            "default": 5
                        }
                    },
                    "required": ["location_name"]
                }
            },
            {
                "name": "get_water_info_by_location",
                "description": "한 번의 요청으로 지역 검색부터 실시간 데이터까지 모든 것을 처리",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "한강 수위, 서울 강우량, 부산 낙동강 등 자연어 질의"
                        },
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 10,
                            "description": "결과 개수 제한",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "recommend_nearby_stations",
                "description": "입력된 지역 주변의 관련 관측소들을 추천",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "기준 위치 (지명)"
                        },
                        "radius": {
                            "type": "integer",
                            "description": "반경 (km)",
                            "default": 20
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["distance", "data_quality"],
                            "description": "distance(거리순) 또는 data_quality(데이터 품질순)",
                            "default": "distance"
                        }
                    },
                    "required": ["location"]
                }
            }
        ],
        "api_endpoints": {
            "search_station": "http://localhost:8000/search/station",
            "water_info": "http://localhost:8000/search/water-info",
            "nearby_stations": "http://localhost:8000/search/nearby"
        }
    }

if __name__ == "__main__":
    print("🌐 HRFCO OpenAI API Server")
    print("📡 URL: http://localhost:8000")
    print("🔧 Functions: http://localhost:8000/openai/functions")
    uvicorn.run(app, host="0.0.0.0", port=8000)
