# Glama MCP 서버 배포 스크립트 (PowerShell)
# 사용법: .\scripts\deploy-to-glama.ps1 [API_KEY]

param(
    [Parameter(Mandatory=$true)]
    [string]$ApiKey
)

# 색상 정의
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"

# 로그 함수
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor $Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor $Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Red
}

# 변수 설정
$ImageName = "hrfco-service"
$ContainerName = "hrfco-mcp-server"
$Port = 8000

Write-Info "HRFCO 서비스를 Glama MCP 서버에 배포합니다..."

# 1. 기존 컨테이너 정리
Write-Info "기존 컨테이너 정리 중..."
$existingContainer = docker ps -a --format "table {{.Names}}" | Select-String $ContainerName
if ($existingContainer) {
    docker stop $ContainerName 2>$null
    docker rm $ContainerName 2>$null
    Write-Info "기존 컨테이너가 제거되었습니다."
}

# 2. Docker 이미지 빌드
Write-Info "Docker 이미지 빌드 중..."
$buildResult = docker build --build-arg HRFCO_API_KEY="$ApiKey" -t "$ImageName`:latest . 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Info "Docker 이미지 빌드가 완료되었습니다."
} else {
    Write-Error "Docker 이미지 빌드에 실패했습니다."
    Write-Host $buildResult
    exit 1
}

# 3. 컨테이너 실행
Write-Info "MCP 서버 컨테이너를 시작합니다..."
$runResult = docker run -d --name $ContainerName -p "$Port`:$Port" -e HRFCO_API_KEY="$ApiKey" -e LOG_LEVEL=INFO -e CACHE_TTL_SECONDS=300 -e MAX_CONCURRENT_REQUESTS=5 --restart unless-stopped "$ImageName`:latest" 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Info "컨테이너가 성공적으로 시작되었습니다."
} else {
    Write-Error "컨테이너 시작에 실패했습니다."
    Write-Host $runResult
    exit 1
}

# 4. 헬스체크
Write-Info "서비스 헬스체크 중..."
Start-Sleep -Seconds 10

for ($i = 1; $i -le 30; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$Port/health" -UseBasicParsing -TimeoutSec 5 2>$null
        if ($response.StatusCode -eq 200) {
            Write-Info "서비스가 정상적으로 실행되고 있습니다."
            break
        }
    } catch {
        if ($i -eq 30) {
            Write-Error "서비스 시작 시간이 초과되었습니다."
            docker logs $ContainerName
            exit 1
        }
        Write-Warn "서비스 시작 대기 중... ($i/30)"
        Start-Sleep -Seconds 2
    }
}

# 5. 서비스 정보 출력
Write-Info "=== 배포 완료 ==="
Write-Host "서비스 URL: http://localhost:$Port"
Write-Host "헬스체크: http://localhost:$Port/health"
Write-Host "API 문서: http://localhost:$Port/docs"
Write-Host ""
Write-Host "컨테이너 관리 명령어:"
Write-Host "  로그 확인: docker logs $ContainerName"
Write-Host "  실시간 로그: docker logs -f $ContainerName"
Write-Host "  컨테이너 중지: docker stop $ContainerName"
Write-Host "  컨테이너 재시작: docker restart $ContainerName"
Write-Host "  컨테이너 제거: docker rm -f $ContainerName"

# 6. Glama 설정 파일 생성
Write-Info "Glama 설정 파일을 생성합니다..."
$GlamaConfigDir = "$env:APPDATA\glama"
if (!(Test-Path $GlamaConfigDir)) {
    New-Item -ItemType Directory -Path $GlamaConfigDir -Force | Out-Null
}

$configContent = @"
{
  "mcpServers": {
    "hrfco-service": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-p", "$Port`:$Port",
        "-e", "HRFCO_API_KEY=$ApiKey",
        "-e", "LOG_LEVEL=INFO",
        "-e", "CACHE_TTL_SECONDS=300",
        "-e", "MAX_CONCURRENT_REQUESTS=5",
        "--name", "$ContainerName",
        "$ImageName`:latest"
      ],
      "env": {
        "HRFCO_API_KEY": "$ApiKey"
      }
    }
  }
}
"@

$configContent | Out-File -FilePath "$GlamaConfigDir\mcp-servers.json" -Encoding UTF8
Write-Info "Glama 설정 파일이 생성되었습니다: $GlamaConfigDir\mcp-servers.json"

# 7. 테스트 실행
Write-Info "서비스 테스트를 실행합니다..."
try {
    $healthResponse = Invoke-WebRequest -Uri "http://localhost:$Port/health" -UseBasicParsing
    if ($healthResponse.Content -match '"status".*"ok"') {
        Write-Info "헬스체크 테스트 통과"
    } else {
        Write-Warn "헬스체크 테스트 실패"
    }
} catch {
    Write-Warn "헬스체크 테스트 실패"
}

# API 테스트
try {
    $apiResponse = Invoke-WebRequest -Uri "http://localhost:$Port/api/water-level?station=HRFCO" -UseBasicParsing
    Write-Info "API 테스트 통과"
} catch {
    Write-Warn "API 테스트 실패 (API 키 확인 필요)"
}

Write-Info "배포가 완료되었습니다!"
Write-Info "Glama에서 MCP 서버를 사용할 수 있습니다." 