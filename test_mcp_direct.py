#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP 서버 직접 테스트
"""
import asyncio
import json
import subprocess
import sys
from pathlib import Path

async def test_mcp_server():
    """MCP 서버를 직접 테스트합니다"""
    
    print("🧪 MCP 서버 직접 테스트")
    print("=" * 40)
    
    # MCP 서버 프로세스 시작
    process = subprocess.Popen(
        [sys.executable, "mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=Path(__file__).parent
    )
    
    try:
        # 1. 초기화 요청
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("📤 초기화 요청 전송...")
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # 응답 읽기
        response = process.stdout.readline()
        init_response = json.loads(response)
        print(f"📥 초기화 응답: {init_response.get('result', {}).get('serverInfo', {})}")
        
        # 2. 도구 목록 요청
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        print("\n📤 도구 목록 요청 전송...")
        process.stdin.write(json.dumps(tools_request) + "\n")
        process.stdin.flush()
        
        response = process.stdout.readline()
        tools_response = json.loads(response)
        tools = tools_response.get('result', {}).get('tools', [])
        print(f"📥 사용 가능한 도구: {len(tools)}개")
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description']}")
        
        # 3. 관측소 정보 조회 테스트
        observatory_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_observatory_info",
                "arguments": {
                    "hydro_type": "waterlevel"
                }
            }
        }
        
        print("\n📤 관측소 정보 조회 요청 전송...")
        process.stdin.write(json.dumps(observatory_request) + "\n")
        process.stdin.flush()
        
        response = process.stdout.readline()
        observatory_response = json.loads(response)
        if 'result' in observatory_response:
            print("✅ 관측소 정보 조회 성공")
            content = observatory_response['result']['content'][0]['text']
            data = json.loads(content)
            stations = data.get('data', {}).get('content', [])
            print(f"  - 수위 관측소: {len(stations)}개")
        else:
            print(f"❌ 관측소 정보 조회 실패: {observatory_response.get('error')}")
        
        # 4. 수문 데이터 조회 테스트
        hydro_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "get_hydro_data",
                "arguments": {
                    "hydro_type": "dam",
                    "time_type": "10M",
                    "obs_code": "1001210"
                }
            }
        }
        
        print("\n📤 수문 데이터 조회 요청 전송...")
        process.stdin.write(json.dumps(hydro_request) + "\n")
        process.stdin.flush()
        
        response = process.stdout.readline()
        hydro_response = json.loads(response)
        if 'result' in hydro_response:
            print("✅ 수문 데이터 조회 성공")
            content = hydro_response['result']['content'][0]['text']
            data = json.loads(content)
            hydro_data = data.get('data', {}).get('content', [])
            if hydro_data:
                latest = hydro_data[0]
                print(f"  - 영천댐 최근 데이터: {latest.get('ymdhm', 'N/A')}")
                print(f"    저수위: {latest.get('swl', 'N/A')}m")
                print(f"    방류량: {latest.get('tototf', 'N/A')}m³/s")
        else:
            print(f"❌ 수문 데이터 조회 실패: {hydro_response.get('error')}")
        
        # 5. 서버 상태 확인
        health_request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "get_server_health",
                "arguments": {}
            }
        }
        
        print("\n📤 서버 상태 확인 요청 전송...")
        process.stdin.write(json.dumps(health_request) + "\n")
        process.stdin.flush()
        
        response = process.stdout.readline()
        health_response = json.loads(response)
        if 'result' in health_response:
            print("✅ 서버 상태 확인 성공")
            content = health_response['result']['content'][0]['text']
            data = json.loads(content)
            print(f"  - 상태: {data.get('status', 'N/A')}")
            print(f"  - 메시지: {data.get('message', 'N/A')}")
        else:
            print(f"❌ 서버 상태 확인 실패: {health_response.get('error')}")
        
        print("\n🎉 MCP 서버 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
    finally:
        # 프로세스 종료
        process.terminate()
        process.wait()

if __name__ == "__main__":
    asyncio.run(test_mcp_server()) 