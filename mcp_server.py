#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HRFCO API MCP Server
HTTP API를 MCP 프로토콜로 래핑하여 Claude에서 직접 사용할 수 있도록 함
"""
import asyncio
import json
import sys
import httpx
from pathlib import Path
from typing import Dict, Any, List, Optional

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from hrfco_service.api import fetch_observatory_info, fetch_observatory_data
from hrfco_service.config import Config

class HRFCOMCPServer:
    """HRFCO API를 MCP 프로토콜로 래핑하는 서버"""
    
    def __init__(self):
        self.config = Config()
        self.tools = [
            {
                "name": "get_observatory_info",
                "description": "수문 관측소 정보를 조회합니다. 수위, 강수량, 댐, 보 관측소의 목록과 위치 정보를 제공합니다. API 키 없이도 사용 가능합니다.",
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
                "description": "실시간 수문 데이터를 조회합니다. 관측소의 현재 수위, 강수량, 댐 방류량, 보 수위 등을 확인할 수 있습니다. API 키 없이도 사용 가능합니다.",
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
                "description": "HRFCO MCP 서버의 상태를 확인합니다. 서버가 정상적으로 작동하는지 확인할 수 있습니다.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_server_config",
                "description": "서버 설정 정보를 확인합니다. API 키 설정 상태 등을 확인할 수 있습니다.",
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
                            "name": "hrfco-mcp-server",
                            "version": "1.0.0"
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
                elif tool_name == "get_server_config":
                    result = await self._get_server_config()
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
        """관측소 정보 조회"""
        hydro_type = arguments.get("hydro_type")
        if not hydro_type:
            raise ValueError("hydro_type is required")
        
        result = await fetch_observatory_info(hydro_type)
        return {
            "type": "observatory_info",
            "hydro_type": hydro_type,
            "data": result
        }
    
    async def _get_hydro_data(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """수문 데이터 조회"""
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
            "data": result
        }
    
    async def _get_server_health(self) -> Dict[str, Any]:
        """서버 상태 확인"""
        return {
            "type": "server_health",
            "status": "ok",
            "message": "HRFCO MCP Server is running normally"
        }
    
    async def _get_server_config(self) -> Dict[str, Any]:
        """서버 설정 확인"""
        return {
            "type": "server_config",
            "config": {
                "api_base_url": self.config.BASE_URL,
                "cache_ttl_seconds": self.config.CACHE_TTL_SECONDS,
                "max_concurrent_requests": self.config.MAX_CONCURRENT_REQUESTS,
                "request_timeout": self.config.REQUEST_TIMEOUT,
                "log_level": self.config.LOG_LEVEL
            }
        }
    
    async def run(self):
        """MCP 서버를 실행합니다"""
        print("🚀 HRFCO MCP Server 시작 중...", file=sys.stderr)
        print(f"📡 API URL: {self.config.BASE_URL}", file=sys.stderr)
        print("✅ MCP 프로토콜 준비 완료", file=sys.stderr)
        
        while True:
            try:
                # STDIN에서 JSON-RPC 요청 읽기
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                
                request = json.loads(line.strip())
                response = await self.handle_request(request)
                
                # STDOUT으로 JSON-RPC 응답 출력
                print(json.dumps(response, ensure_ascii=False), flush=True)
                
            except json.JSONDecodeError as e:
                print(json.dumps({
                    "jsonrpc": "2.0",
                    "id": 0,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }, ensure_ascii=False), flush=True)
            except Exception as e:
                print(json.dumps({
                    "jsonrpc": "2.0",
                    "id": 0,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }, ensure_ascii=False), flush=True)

async def main():
    """메인 함수"""
    server = HRFCOMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main()) 