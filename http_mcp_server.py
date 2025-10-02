#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTTP MCP Server for ChatGPT
text/event-stream 헤더 요구 없이 일반 HTTP로 MCP 프로토콜 지원
"""
import os
import sys
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any

# FastAPI 및 관련 라이브러리
try:
    from fastapi import FastAPI, HTTPException, Response, Body
    from fastapi.responses import JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    import httpx
    import uvicorn
except ImportError as e:
    print(f"필수 패키지 설치가 필요합니다: {e}")
    print("다음 명령을 실행하세요:")
    print('pip install fastapi httpx uvicorn')
    sys.exit(1)

# 환경변수 설정
HRFCO_API_KEY = os.getenv('HRFCO_API_KEY', '')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', '')
WAMIS_API_KEY = os.getenv('WAMIS_API_KEY', '')

# FastAPI 앱 생성
app = FastAPI(title="HRFCO HTTP MCP Server", version="1.1.0")

# CORS 허용 (ChatGPT 등 외부에서 사전요청/검증 가능하도록)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class HRFCOClient:
    """홍수통제소 API 클라이언트"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.hrfco.go.kr"
    
    async def get_observatories(self, hydro_type: str = "waterlevel") -> Dict[str, Any]:
        """관측소 정보 조회"""
        if not self.api_key:
            raise ValueError("API 키가 필요합니다. HRFCO_API_KEY 환경변수를 설정해주세요.")
            
        try:
            url = f"http://api.hrfco.go.kr/{self.api_key}/{hydro_type}/info.json"
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=30.0)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            raise Exception(f"홍수통제소 API 호출 실패: {str(e)}")
    
    async def get_waterlevel_data(self, obs_code: str, time_type: str = "1H") -> Dict[str, Any]:
        """수위 데이터 조회"""
        if not self.api_key:
            raise ValueError("API 키가 필요합니다. HRFCO_API_KEY 환경변수를 설정해주세요.")
            
        try:
            url = f"http://api.hrfco.go.kr/{self.api_key}/waterlevel/data.json"
            params = {
                "obs_code": obs_code,
                "time_type": time_type
            }
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=30.0)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            raise Exception(f"수위 데이터 조회 실패: {str(e)}")

class WeatherClient:
    """기상청 API 클라이언트"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0"
    
    async def get_weather_data(self, nx: int, ny: int) -> Dict[str, Any]:
        """날씨 데이터 조회"""
        if not self.api_key:
            raise ValueError("API 키가 필요합니다. WEATHER_API_KEY 환경변수를 설정해주세요.")
            
        try:
            url = f"{self.base_url}/getVilageFcst"
            params = {
                "serviceKey": self.api_key,
                "numOfRows": 10,
                "pageNo": 1,
                "dataType": "JSON",
                "base_date": datetime.now().strftime("%Y%m%d"),
                "base_time": "0500",
                "nx": nx,
                "ny": ny
            }
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=30.0)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            raise Exception(f"기상청 API 호출 실패: {str(e)}")

# 클라이언트 인스턴스 생성
hrfco_client = HRFCOClient(HRFCO_API_KEY)
weather_client = WeatherClient(WEATHER_API_KEY)

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "HRFCO HTTP MCP Server",
        "version": "1.1.0",
        "endpoints": {
            "mcp": "/mcp",
            "health": "/health",
            "tools": "/tools"
        }
    }

@app.get("/health")
async def health():
    """헬스 체크"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "api_keys": {
            "hrfco": bool(HRFCO_API_KEY),
            "weather": bool(WEATHER_API_KEY),
            "wamis": bool(WAMIS_API_KEY)
        }
    }

@app.get("/.well-known/mcp")
async def mcp_well_known():
    """간단한 MCP 메타데이터(선택적)"""
    return {
        "protocol": "mcp",
        "version": "1.0.0",
        "capabilities": {
            "tools": True,
            "resources": False,
            "prompts": False
        }
    }

@app.get("/tools")
async def list_tools():
    """사용 가능한 도구 목록"""
    return {
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
                        "obs_code": {
                            "type": "string",
                            "description": "관측소 코드"
                        },
                        "time_type": {
                            "type": "string",
                            "description": "시간 유형 (1H, 1D 등)",
                            "default": "1H"
                        }
                    },
                    "required": ["obs_code"]
                }
            },
            {
                "name": "get_weather_data",
                "description": "날씨 데이터 조회",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "nx": {
                            "type": "integer",
                            "description": "격자 X 좌표"
                        },
                        "ny": {
                            "type": "integer",
                            "description": "격자 Y 좌표"
                        }
                    },
                    "required": ["nx", "ny"]
                }
            }
        ]
    }

@app.get("/mcp")
async def mcp_probe():
    """사전 점검용 엔드포인트 (GET)"""
    return {"status": "ok", "message": "MCP endpoint. Use POST JSON-RPC."}

@app.head("/mcp")
async def mcp_head():
    """사전 점검용 엔드포인트 (HEAD)"""
    return Response(status_code=200)

@app.options("/mcp")
async def mcp_options():
    return Response(status_code=204, headers={"Allow": "POST, GET, HEAD, OPTIONS"})

@app.post("/mcp")
async def mcp_endpoint(payload: Dict[str, Any] = Body(...)):
    """MCP 프로토콜 엔드포인트"""
    try:
        # JSON-RPC 요청 처리
        method = payload.get("method")
        params = payload.get("params", {})
        request_id = payload.get("id")

        # MCP initialize 핸드셰이크 지원 (OpenAI Platform 호환)
        if method == "initialize":
            result = {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {
                        # 서버가 도중에 도구 목록 변경 알림을 보낼 수 있는지 여부
                        "listChanged": False
                    },
                    # 일부 클라이언트가 키 존재를 기대할 수 있으므로 명시
                    "resources": {},
                    "prompts": {}
                },
                "serverInfo": {
                    "name": "hrfco-http-mcp",
                    "version": "1.1.0"
                }
            }
            return {"jsonrpc": "2.0", "id": request_id, "result": result}

        # 무시 가능한 알림/핑 처리
        if method in ("notifications/initialized", "ping"):
            return {"jsonrpc": "2.0", "id": request_id, "result": {"ok": True}}

        if method == "tools/list":
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
                                    "hydro_type": {
                                        "type": "string",
                                        "description": "수문 유형 (waterlevel, flow 등)",
                                        "default": "waterlevel"
                                    }
                                },
                                "additionalProperties": False
                            }
                        },
                        {
                            "name": "get_waterlevel_data",
                            "description": "수위 데이터 조회",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "obs_code": {
                                        "type": "string",
                                        "description": "관측소 코드"
                                    },
                                    "time_type": {
                                        "type": "string",
                                        "description": "시간 유형 (1H, 1D 등)",
                                        "default": "1H"
                                    }
                                },
                                "additionalProperties": False,
                                "required": ["obs_code"]
                            }
                        },
                        {
                            "name": "get_weather_data",
                            "description": "날씨 데이터 조회",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "nx": {
                                        "type": "integer",
                                        "description": "격자 X 좌표"
                                    },
                                    "ny": {
                                        "type": "integer",
                                        "description": "격자 Y 좌표"
                                    }
                                },
                                "additionalProperties": False,
                                "required": ["nx", "ny"]
                            }
                        }
                    ]
                }
            }
        
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name == "get_observatories":
                result = await hrfco_client.get_observatories(
                    hydro_type=arguments.get("hydro_type", "waterlevel")
                )
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
            
            elif tool_name == "get_waterlevel_data":
                result = await hrfco_client.get_waterlevel_data(
                    obs_code=arguments.get("obs_code"),
                    time_type=arguments.get("time_type", "1H")
                )
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
            
            elif tool_name == "get_weather_data":
                result = await weather_client.get_weather_data(
                    nx=arguments.get("nx"),
                    ny=arguments.get("ny")
                )
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
                        "message": f"Unknown tool: {tool_name}"
                    }
                }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Unknown method: {method}"
                }
            }
    
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": payload.get("id"),
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }

if __name__ == "__main__":
    print("🌐 HTTP MCP 서버를 시작합니다...")
    print("📡 URL: http://0.0.0.0:8000")
    print("🔗 MCP 엔드포인트: http://0.0.0.0:8000/mcp")
    print(f"API 키 상태:")
    print(f"  HRFCO: {'✅' if HRFCO_API_KEY else '❌'}")
    print(f"  WEATHER: {'✅' if WEATHER_API_KEY else '❌'}")
    print(f"  WAMIS: {'✅' if WAMIS_API_KEY else '❌'}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
