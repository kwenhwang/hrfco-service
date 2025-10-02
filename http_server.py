#!/usr/bin/env python3
"""
HTTP MCP Server for ChatGPT API
"""
import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Any

try:
    from fastapi import FastAPI, HTTPException, Body
    from fastapi.middleware.cors import CORSMiddleware
    import httpx
    import uvicorn
except ImportError as e:
    print(f"필수 패키지 설치: pip install fastapi httpx uvicorn")
    exit(1)

# 환경변수
HRFCO_API_KEY = os.getenv('HRFCO_API_KEY', '')

app = FastAPI(title="HRFCO HTTP MCP Server", version="1.0.0")

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
    
    async def get_observatories(self, hydro_type: str = "waterlevel"):
        if not self.api_key:
            raise ValueError("API 키가 필요합니다")
        
        url = f"{self.base_url}/{self.api_key}/{hydro_type}/info.json"
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    
    async def get_waterlevel_data(self, obs_code: str, time_type: str = "1H"):
        if not self.api_key:
            raise ValueError("API 키가 필요합니다")
        
        url = f"{self.base_url}/{self.api_key}/waterlevel/data.json"
        params = {"obs_code": obs_code, "time_type": time_type}
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()

client = HRFCOClient()

@app.get("/")
async def root():
    return {"message": "HRFCO HTTP MCP Server", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/mcp")
async def mcp_endpoint(payload: Dict[str, Any] = Body(...)):
    try:
        method = payload.get("method")
        params = payload.get("params", {})
        request_id = payload.get("id")

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "hrfco-http-mcp", "version": "1.0.0"}
                }
            }

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": [
                        {
                            "name": "get_observatories",
                            "description": "홍수통제소 관측소 정보 조회",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "hydro_type": {"type": "string", "default": "waterlevel"}
                                }
                            }
                        },
                        {
                            "name": "get_waterlevel_data",
                            "description": "수위 데이터 조회",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "obs_code": {"type": "string"},
                                    "time_type": {"type": "string", "default": "1H"}
                                },
                                "required": ["obs_code"]
                            }
                        }
                    ]
                }
            }
        
        elif method == "tools/call":
            tool_name = params.get("name")
            args = params.get("arguments", {})
            
            if tool_name == "get_observatories":
                result = await client.get_observatories(args.get("hydro_type", "waterlevel"))
            elif tool_name == "get_waterlevel_data":
                result = await client.get_waterlevel_data(args.get("obs_code"), args.get("time_type", "1H"))
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
                }
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]}
            }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Unknown method: {method}"}
            }
    
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": payload.get("id"),
            "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
        }

if __name__ == "__main__":
    print("🌐 HTTP MCP 서버 시작...")
    print("📡 URL: http://0.0.0.0:8000")
    print("🔗 MCP 엔드포인트: http://0.0.0.0:8000/mcp")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
