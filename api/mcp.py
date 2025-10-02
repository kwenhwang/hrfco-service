
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
