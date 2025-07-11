#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
공개 MCP 서버 - 사용자가 API 키 없이 접근 가능
API 키는 서버에서 관리하고, 사용자에게는 노출되지 않음
"""

import os
import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from hrfco_service.api import fetch_observatory_info, fetch_observatory_data
from hrfco_service.config import Config

class PublicMCPServer:
    """사용자가 API 키 없이 접근할 수 있는 공개 MCP 서버"""
    
    def __init__(self):
        self.config = Config()
        # API 키는 서버에서 관리 (환경변수에서 가져옴)
        self.api_key = os.getenv("HRFCO_API_KEY")
        
        self.tools = [
            {
                "name": "get_observatory_info",
                "description": "수문 관측소 정보를 조회합니다. API 키 없이도 사용 가능합니다.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "hydro_type": {
                            "type": "string",
                            "enum": ["waterlevel", "rainfall", "dam", "bo"],
                            "description": "수문 데이터 타입 (waterlevel: 수위, rainfall: 강수량, dam: 댐, bo: 보)"
                        }
                    },
                    "required": ["hydro_type"]
                }
            },
            {
                "name": "get_hydro_data",
                "description": "실시간 수문 데이터를 조회합니다. API 키 없이도 사용 가능합니다.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "hydro_type": {
                            "type": "string",
                            "enum": ["waterlevel", "rainfall", "dam", "bo"],
                            "description": "수문 데이터 타입 (waterlevel: 수위, rainfall: 강수량, dam: 댐, bo: 보)"
                        },
                        "time_type": {
                            "type": "string",
                            "enum": ["10M", "1H", "1D"],
                            "description": "시간 단위 (10M: 10분, 1H: 1시간, 1D: 1일)"
                        },
                        "obs_code": {
                            "type": "string",
                            "description": "관측소 코드 (get_observatory_info로 조회 가능)"
                        }
                    },
                    "required": ["hydro_type", "time_type", "obs_code"]
                }
            },
            {
                "name": "get_server_health",
                "description": "공개 MCP 서버의 상태를 확인합니다.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_server_info",
                "description": "서버 정보를 확인합니다. API 키는 노출되지 않습니다.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """MCP 요청을 처리합니다"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id", 0)
        
        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "hrfco-public-mcp-server",
                            "version": "1.0.0",
                            "description": "사용자가 API 키 없이 접근할 수 있는 공개 MCP 서버"
                        }
                    }
                }
            
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": self.tools
                    }
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name == "get_observatory_info":
                    result = await self._get_observatory_info(arguments)
                elif tool_name == "get_hydro_data":
                    result = await self._get_hydro_data(arguments)
                elif tool_name == "get_server_health":
                    result = await self._get_server_health()
                elif tool_name == "get_server_info":
                    result = await self._get_server_info()
                else:
                    raise ValueError(f"Unknown tool: {tool_name}")
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, ensure_ascii=False, indent=2)
                            }
                        ]
                    }
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
                
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
    
    async def _get_observatory_info(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """관측소 정보 조회 (API 키는 서버에서 관리)"""
        hydro_type = arguments.get("hydro_type")
        if not hydro_type:
            raise ValueError("hydro_type is required")
        
        result = await fetch_observatory_info(hydro_type)
        return {
            "type": "observatory_info",
            "hydro_type": hydro_type,
            "data": result,
            "note": "API 키 없이도 조회 가능합니다."
        }
    
    async def _get_hydro_data(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """수문 데이터 조회 (API 키는 서버에서 관리)"""
        hydro_type = arguments.get("hydro_type")
        time_type = arguments.get("time_type")
        obs_code = arguments.get("obs_code")
        
        if not all([hydro_type, time_type, obs_code]):
            raise ValueError("hydro_type, time_type, and obs_code are required")
        
        result = await fetch_observatory_data(str(hydro_type), str(time_type), str(obs_code))
        return {
            "type": "hydro_data",
            "hydro_type": hydro_type,
            "time_type": time_type,
            "obs_code": obs_code,
            "data": result,
            "note": "API 키 없이도 조회 가능합니다."
        }
    
    async def _get_server_health(self) -> Dict[str, Any]:
        """서버 상태 확인"""
        return {
            "type": "server_health",
            "status": "ok",
            "message": "공개 MCP 서버가 정상적으로 작동 중입니다",
            "api_key_configured": bool(self.api_key),
            "note": "API 키는 서버에서 관리되며 사용자에게는 노출되지 않습니다."
        }
    
    async def _get_server_info(self) -> Dict[str, Any]:
        """서버 정보 확인 (API 키는 노출되지 않음)"""
        return {
            "type": "server_info",
            "server_name": "hrfco-public-mcp-server",
            "version": "1.0.0",
            "description": "사용자가 API 키 없이 접근할 수 있는 공개 MCP 서버",
            "api_key_configured": bool(self.api_key),
            "api_key_visible": False,
            "note": "API 키는 서버 내부에서만 사용되며 사용자에게는 노출되지 않습니다."
        }
    
    async def run(self):
        """STDIO JSON-RPC 프로토콜로 서버 실행"""
        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                
                request = json.loads(line.strip())
                response = await self.handle_request(request)
                
                print(json.dumps(response, ensure_ascii=False))
                sys.stdout.flush()
                
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id", 0) if 'request' in locals() else 0,
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    }
                }
                print(json.dumps(error_response, ensure_ascii=False))
                sys.stdout.flush()

async def main():
    """메인 함수"""
    server = PublicMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main()) 