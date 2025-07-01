[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/kwenhwang-hrfco-service-badge.png)](https://mseep.ai/app/kwenhwang-hrfco-service)

# HRFCO Service

실시간 수문정보 조회 서비스(MCP Server)

## Features
- 수위, 강수량, 댐방류량 등 실시간 수문정보 조회
- 관측소별 상세 정보 조회
- 시계열 데이터 필터링 및 통계
- 관측소 위치 정보 조회

## Prerequisites
- Python 3.8+
- [Claude Desktop](https://github.com/anthropic-labs/claude-desktop)

## Installation
1. Install the package:
   ```bash
   git clone https://github.com/kwenhwang/hrfco-service.git
   cd hrfco_service
   pip install -e .
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure HRFCO API Key:

   Windows:
   ```powershell
   # PowerShell
   [Environment]::SetEnvironmentVariable("HRFCO_API_KEY", "your-api-key", "User")
   ```
   ```cmd
   # Command Prompt
   setx HRFCO_API_KEY "your-api-key"
   ```
   또는 제어판 > 시스템 > 고급 시스템 설정 > 환경 변수 > 사용자 변수에서 추가

   Linux/macOS:
   ```bash
   # Add to ~/.bashrc or ~/.zshrc
   export HRFCO_API_KEY="your-api-key"
   
   # Apply changes
   source ~/.bashrc  # or source ~/.zshrc
   ```
   
   또는 .env 파일 생성:
   ```bash
   echo "HRFCO_API_KEY=your-api-key" > .env
   ```

## Configuration
1. Update `claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "hrfco": {
         "command": "C:\\Users\\{USERNAME}\\AppData\\Local\\Programs\\Python\\Python313\\python.exe",
         "args": ["-m", "hrfco_service"],
         "cwd": "D:\\python\\mcp\\hrfco_service",
         "env": {
           "PYTHONPATH": "D:\\python\\mcp\\hrfco_service"
         }
       }
     }
   }
   ```

2. Cursor Configuration:
   - Open Cursor Settings (Ctrl+,)
   - Navigate to Extensions > Python
   - Update Python Path to your Python installation:
     ```
     C:\Users\{USERNAME}\AppData\Local\Programs\Python\Python313\python.exe
     ```
   - Set PYTHONPATH in workspace settings:
     ```json
     {
       "python.analysis.extraPaths": ["D:/python/mcp/hrfco_service"]
     }
     ```

3. Ensure `HRFCO_API_KEY` is set as a system environment variable.

## Usage Examples


