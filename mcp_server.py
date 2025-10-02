#!/usr/bin/env python3
"""
HRFCO MCP Server for ChatGPT API
수문 데이터 조회 전용 MCP 서버
"""
import asyncio
import json
import os
import sys
from pathlib import Path
import httpx
from datetime import datetime, timedelta

# 환경변수 로드 (dotenv 사용)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

HRFCO_API_KEY = os.getenv('HRFCO_API_KEY', '')

class HRFCOClient:
    """홍수통제소 API 클라이언트"""
    
    def __init__(self):
        self.base_url = "http://api.hrfco.go.kr"
        self.api_key = HRFCO_API_KEY
    
    async def get_observatories(self, hydro_type: str = "waterlevel", limit: int = 10):
        """관측소 정보 조회 (응답 크기 제한)"""
        if not self.api_key:
            return {"error": "API 키가 필요합니다", "demo": True}
        
        try:
            url = f"{self.base_url}/{self.api_key}/{hydro_type}/info.json"
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                content = data.get("content", [])
                
                # 응답 크기 제한 (최대 limit개)
                limited_content = content[:limit]
                
                return {
                    "observatories": limited_content,
                    "total_count": len(content),
                    "returned_count": len(limited_content),
                    "note": f"Showing first {limit} of {len(content)} observatories to prevent response overflow"
                }
        except Exception as e:
            return {"error": f"API 호출 실패: {str(e)}"}
    
    async def get_waterlevel_data(self, obs_code: str, time_type: str = "1H"):
        """수위 데이터 조회"""
        if not self.api_key:
            return {"error": "API 키가 필요합니다", "demo": True}
        
        try:
            url = f"{self.base_url}/{self.api_key}/waterlevel/data.json"
            params = {"obs_code": obs_code, "time_type": time_type}
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                return data.get("content", [])
        except Exception as e:
            return {"error": f"수위 데이터 조회 실패: {str(e)}"}

# MCP 서버 구현
async def handle_mcp_request():
    """MCP 요청 처리"""
    client = HRFCOClient()
    
    while True:
        try:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            
            request = json.loads(line.strip())
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")
            
            if method == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "hrfco-mcp", "version": "1.0.0"}
                    }
                }
            
            elif method == "tools/list":
                response = {
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
                                        "hydro_type": {
                                            "type": "string",
                                            "description": "수문 유형 (waterlevel, flow 등)",
                                            "default": "waterlevel"
                                        }
                                    }
                                }
                            },
                            {
                                "name": "get_waterlevel_data",
                                "description": "수위 데이터 조회",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "obs_code": {"type": "string", "description": "관측소 코드"},
                                        "time_type": {"type": "string", "description": "시간 유형", "default": "1H"}
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
                    result = {"error": f"Unknown tool: {tool_name}"}
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]
                    }
                }
            
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Unknown method: {method}"}
                }
            
            print(json.dumps(response), flush=True)
        
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": request.get("id") if 'request' in locals() else None,
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
            }
            print(json.dumps(error_response), flush=True)

if __name__ == "__main__":
    asyncio.run(handle_mcp_request())
