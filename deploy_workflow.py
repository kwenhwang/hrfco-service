#!/usr/bin/env python3
"""
HRFCO MCP 서버 배포 워크플로우
응답 크기 최적화 및 ChatGPT 연동 자동화
"""
import json
import os
import subprocess
from pathlib import Path

class MCPDeploymentWorkflow:
    def __init__(self):
        self.project_root = Path("/home/ubuntu/hrfco-service")
        self.config_file = self.project_root / "chatgpt_mcp_config.json"
        
    def optimize_response_size(self):
        """MCP 응답 크기 최적화"""
        print("🔧 MCP 응답 크기 최적화...")
        
        # 이미 수정된 mcp_server.py 확인
        server_file = self.project_root / "mcp_server.py"
        if "limit: int = 10" in server_file.read_text():
            print("✅ 응답 크기 제한 이미 적용됨")
        else:
            print("❌ 응답 크기 제한 필요")
            return False
        return True
    
    def create_netlify_config(self):
        """Netlify 배포 설정 생성"""
        print("🌐 Netlify 배포 설정 생성...")
        
        netlify_config = {
            "functions": {
                "api/mcp.py": {"runtime": "python3.9"}
            },
            "routes": [
                {"src": "/mcp", "dest": "/api/mcp.py"},
                {"src": "/health", "dest": "/api/health.py"},
                {"src": "/(.*)", "dest": "/api/mcp.py"}
            ],
            "env": {
                "HRFCO_API_KEY": "@hrfco_api_key"
            }
        }
        
        with open(self.project_root / "netlify.toml", "w") as f:
            f.write(f"""[build]
  functions = "api"

[functions]
  python_runtime = "3.9"

[[redirects]]
  from = "/mcp"
  to = "/.netlify/functions/mcp"
  status = 200

[[redirects]]
  from = "/health"
  to = "/.netlify/functions/health"
  status = 200
""")
        
        print("✅ Netlify 설정 완료")
        return True
    
    def create_api_functions(self):
        """Netlify Functions API 생성"""
        print("⚡ Netlify Functions 생성...")
        
        api_dir = self.project_root / "api"
        api_dir.mkdir(exist_ok=True)
        
        # MCP 함수
        mcp_function = api_dir / "mcp.py"
        mcp_function.write_text("""
import json
import os
from http.server import BaseHTTPRequestHandler
import sys
sys.path.append('/var/task')

from mcp_server import HRFCOClient

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            request = json.loads(post_data.decode('utf-8'))
            client = HRFCOClient()
            
            method = request.get("method")
            if method == "tools/call":
                params = request.get("params", {})
                tool_name = params.get("name")
                args = params.get("arguments", {})
                
                if tool_name == "get_observatories":
                    result = await client.get_observatories(
                        args.get("hydro_type", "waterlevel"),
                        limit=5  # Netlify 응답 크기 제한
                    )
                else:
                    result = {"error": f"Unknown tool: {tool_name}"}
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]}
                }
            else:
                response = {"jsonrpc": "2.0", "id": request.get("id"), "error": {"code": -32601, "message": "Method not found"}}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = {"error": str(e)}
            self.wfile.write(json.dumps(error_response).encode())
""")
        
        print("✅ API Functions 생성 완료")
        return True
    
    def create_chatgpt_config(self):
        """ChatGPT MCP 설정 생성"""
        print("🤖 ChatGPT MCP 설정 생성...")
        
        config = {
            "mcpServers": {
                "hrfco-optimized": {
                    "command": "python3",
                    "args": [str(self.project_root / "mcp_server.py")],
                    "env": {
                        "HRFCO_API_KEY": os.getenv("HRFCO_API_KEY", ""),
                        "PYTHONPATH": str(self.project_root / "src")
                    }
                }
            }
        }
        
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ ChatGPT 설정 저장: {self.config_file}")
        return True
    
    def test_mcp_server(self):
        """MCP 서버 테스트"""
        print("🧪 MCP 서버 테스트...")
        
        test_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "get_observatories",
                "arguments": {"hydro_type": "waterlevel"}
            }
        }
        
        try:
            result = subprocess.run(
                ["python3", str(self.project_root / "mcp_server.py")],
                input=json.dumps(test_request),
                text=True,
                capture_output=True,
                timeout=30
            )
            
            if result.returncode == 0:
                response = json.loads(result.stdout)
                if "result" in response:
                    print("✅ MCP 서버 테스트 성공")
                    return True
            
            print(f"❌ MCP 서버 테스트 실패: {result.stderr}")
            return False
            
        except Exception as e:
            print(f"❌ 테스트 오류: {e}")
            return False
    
    def deploy(self):
        """전체 배포 프로세스 실행"""
        print("🚀 HRFCO MCP 서버 배포 시작")
        
        steps = [
            ("응답 크기 최적화", self.optimize_response_size),
            ("Netlify 설정", self.create_netlify_config),
            ("API Functions", self.create_api_functions),
            ("ChatGPT 설정", self.create_chatgpt_config),
            ("서버 테스트", self.test_mcp_server)
        ]
        
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            if not step_func():
                print(f"❌ {step_name} 실패")
                return False
        
        print("\n🎉 배포 완료!")
        print(f"📁 ChatGPT 설정: {self.config_file}")
        print("🔗 다음 단계:")
        print("  1. ChatGPT 개발자 모드에서 MCP 설정 파일 적용")
        print("  2. Netlify에 배포 (선택사항)")
        print("  3. MCP 서버 연결 테스트")
        
        return True

if __name__ == "__main__":
    workflow = MCPDeploymentWorkflow()
    workflow.deploy()
