#!/bin/bash
echo "🚀 HRFCO MCP 서버 배포"

# 1. HTTP 서버 실행 (ChatGPT API 연결용)
echo "🌐 HTTP 서버 시작..."
python3 http_server.py &

# 2. MCP 서버 테스트
echo "🔧 MCP 서버 테스트..."
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}' | python3 mcp_server.py

echo "✅ 배포 완료!"
echo "📡 HTTP API: http://localhost:8000/mcp"
echo "🔗 ChatGPT 설정: chatgpt_mcp_config.json 사용"
