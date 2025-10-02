#!/usr/bin/env python3
"""
OpenAI Function Calling Example with HRFCO API
"""
import json
import httpx
import asyncio
from typing import Dict, Any

# Function definition for OpenAI
FUNCTION_DEFINITION = {
    "name": "get_korean_water_observatories",
    "description": "Get Korean water level or rainfall observatory information from HRFCO",
    "parameters": {
        "type": "object",
        "properties": {
            "hydro_type": {
                "type": "string",
                "enum": ["waterlevel", "rainfall", "dam"],
                "description": "Type of hydrological data",
                "default": "waterlevel"
            },
            "limit": {
                "type": "integer",
                "minimum": 1,
                "maximum": 10,
                "description": "Maximum number of observatories to return",
                "default": 5
            }
        }
    }
}

async def call_hrfco_api(hydro_type: str = "waterlevel", limit: int = 5) -> Dict[str, Any]:
    """Call HRFCO API endpoint"""
    url = f"http://localhost:8000/observatories"
    params = {"hydro_type": hydro_type, "limit": limit}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()

async def simulate_openai_function_call():
    """Simulate OpenAI function calling workflow"""
    print("🤖 OpenAI Function Calling 시뮬레이션")
    
    # 1. Function call from OpenAI
    function_call = {
        "name": "get_korean_water_observatories",
        "arguments": {"hydro_type": "waterlevel", "limit": 3}
    }
    
    print(f"📞 Function Call: {json.dumps(function_call, indent=2)}")
    
    # 2. Execute function
    args = function_call["arguments"]
    result = await call_hrfco_api(args["hydro_type"], args["limit"])
    
    print(f"📊 API Response: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    # 3. Return to OpenAI
    function_response = {
        "role": "function",
        "name": function_call["name"],
        "content": json.dumps(result, ensure_ascii=False)
    }
    
    print(f"✅ Function Response Size: {len(function_response['content'])} bytes")
    return function_response

if __name__ == "__main__":
    asyncio.run(simulate_openai_function_call())
