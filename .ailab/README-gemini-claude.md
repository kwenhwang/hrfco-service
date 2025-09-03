# Gemini CLI + Super Claude Integration

이 프로젝트는 **Gemini CLI를 메인으로 하고 Claude를 보조 AI로 통합**하여 두 AI가 협업할 수 있게 해주는 시스템입니다.

## 🎯 목표

- **Gemini CLI를 향상**: Claude의 추가적인 관점과 검토를 제공
- **자동 상담**: Gemini가 불확실할 때 자동으로 Claude 상담
- **수동 상담**: 언제든지 Claude의 의견 요청 가능
- **통합 워크플로**: 하나의 명령어로 두 AI의 강점 활용

## 🚀 설치 완료!

모든 파일이 성공적으로 설치되었습니다:

- ✅ **claude_integration.py** - Claude API 통합 모듈
- ✅ **gemini_claude_wrapper.py** - Gemini CLI + Claude 래퍼
- ✅ **claude-config.json** - Claude 설정 파일
- ✅ **setup-aliases.ps1** - PowerShell 별칭 설정
- ✅ **gemini-claude.bat** - Windows 배치 파일
- ✅ **Python 가상환경** - 모든 의존성 설치 완료

## 📋 설정 방법

### 1단계: Claude API 키 설정

1. [Anthropic Console](https://console.anthropic.com/)에서 API 키 생성
2. 환경 변수 설정:

```powershell
# PowerShell에서:
$env:ANTHROPIC_API_KEY = "your-claude-api-key-here"

# 영구 설정:
setx ANTHROPIC_API_KEY "your-claude-api-key-here"
```

### 2단계: PowerShell 별칭 설정 (선택사항)

```powershell
# 현재 세션에만:
. C:\Users\20172483\web\Mywater_webgame\ai-lab\setup-aliases.ps1

# PowerShell 프로필에 영구 추가:
echo '. C:\Users\20172483\web\Mywater_webgame\ai-lab\setup-aliases.ps1' >> $PROFILE
```

## 🎮 사용 방법

### 기본 사용법

```bash
cd C:\Users\20172483\web\Mywater_webgame\ai-lab
venv\Scripts\activate
python gemini_claude_wrapper.py [옵션] [Gemini 옵션들]
```

### 예시 명령어들

#### 1. 단순 질문 (Claude 비활성화)
```bash
python gemini_claude_wrapper.py --no-claude -p "What is Python?"
```

#### 2. Claude 통합 활성화
```bash
python gemini_claude_wrapper.py -p "What is quantum computing?"
# Gemini 응답 후 Claude 상담 옵션 제공
```

#### 3. 불확실성 자동 감지
```bash
python gemini_claude_wrapper.py -p "I'm not sure about this complex topic"
# Gemini가 불확실하면 자동으로 Claude 상담
```

#### 4. Claude만 사용
```bash
python gemini_claude_wrapper.py --claude-only -p "Explain AI ethics"
```

#### 5. 대화형 모드
```bash
python gemini_claude_wrapper.py --interactive
```

### PowerShell 별칭 사용 (설정한 경우)

```powershell
gemini-claude -p "What is machine learning?"
gemini-enhanced --interactive
```

## ⚙️ 고급 옵션

### 래퍼 전용 옵션:
- `--no-claude` - Claude 통합 비활성화
- `--no-auto-consult` - 자동 상담 비활성화  
- `--verbose` - 자세한 출력
- `--claude-only` - Claude만 사용 (Gemini 건너뛰기)
- `--interactive` - 대화형 모드

### Gemini CLI 옵션들 (모두 지원):
- `-p, --prompt` - 프롬프트 입력
- `-m, --model` - 모델 선택
- `-a, --all-files` - 모든 파일 포함
- `-d, --debug` - 디버그 모드
- 기타 모든 Gemini CLI 옵션

## 🎯 주요 기능

### 1. **스마트 불확실성 감지**
Claude가 다음 패턴을 감지하면 자동으로 Gemini 상담:
- "I'm not sure"
- "unclear"
- "uncertain" 
- "might be"
- "possibly"
- "it depends"
- "I think"
- "probably"

### 2. **대화형 모드**
```bash
python gemini_claude_wrapper.py --interactive

gemini> What is AI?
# Gemini 응답 + Claude 상담 옵션

gemini> claude Explain deep learning
# Claude에게 직접 질문

gemini> status
# 통합 상태 확인

gemini> claude
# Claude 토글 on/off

gemini> exit
# 종료
```

### 3. **유연한 워크플로**

#### 시나리오 A: 코딩 질문
```bash
python gemini_claude_wrapper.py -p "How do I implement binary search in Python?"
# 1. Gemini가 코드 제공
# 2. Claude 상담 제안 (y/N)
# 3. Claude가 추가 개선사항이나 대안 제공
```

#### 시나리오 B: 복잡한 개념
```bash
python gemini_claude_wrapper.py -p "Explain quantum entanglement"
# 1. Gemini가 설명
# 2. 불확실성 감지 시 자동 Claude 상담
# 3. Claude가 다른 관점이나 보완 설명 제공
```

#### 시나리오 C: 빠른 사실 확인
```bash
python gemini_claude_wrapper.py --claude-only -p "What's the capital of Australia?"
# Claude만 사용 (빠른 응답)
```

## ⚙️ 설정 파일

### claude-config.json
```json
{
  "model": "claude-3-5-sonnet-20241022",  // Claude 모델
  "api_key": "",                          // API 키 (환경변수 우선)
  "timeout": 60,                          // 타임아웃 (초)
  "rate_limit_delay": 1.0,                // 호출 간격 (초)
  "auto_consult": true,                   // 자동 상담 활성화
  "max_tokens": 4000,                     // 최대 토큰 수
  "temperature": 0.7                      // 창의성 레벨
}
```

## 🔧 문제 해결

### ❌ "Gemini CLI not found"
```bash
npm install -g @google/gemini-cli
```

### ❌ "Claude API key not set"
```powershell
$env:ANTHROPIC_API_KEY = "your-api-key"
```

### ❌ PowerShell 실행 정책 오류
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### ❌ 가상환경 활성화 실패
```bash
cd C:\Users\20172483\web\Mywater_webgame\ai-lab
venv\Scripts\activate
```

## 📊 성능 및 제한사항

### Claude API 제한:
- **Free Tier**: 제한적 사용량
- **Pro Plan**: 더 높은 사용량
- **속도 제한**: 기본 1초 간격

### Gemini CLI 제한:
- **무료 티어**: 일일 100회
- **API 키 사용**: 더 높은 제한

### 권장사항:
- 중요한 질문에만 Claude 상담 사용
- `--no-auto-consult`로 자동 상담 비활성화
- `claude-3-5-haiku` 사용 (빠르고 경제적)

## 🎮 고급 활용 예시

### 1. 코드 리뷰 워크플로
```bash
# 1단계: Gemini에게 코드 작성 요청
python gemini_claude_wrapper.py -p "Write a REST API in Python using FastAPI"

# 2단계: Claude에게 리뷰 요청 (자동 또는 수동)
# Claude가 보안, 성능, 베스트 프랙티스 관점에서 리뷰
```

### 2. 학습 도우미
```bash
# 개념 학습
python gemini_claude_wrapper.py -p "Explain machine learning algorithms"
# → Gemini 설명 + Claude의 다른 관점/예시

# 심화 학습  
python gemini_claude_wrapper.py --claude-only -p "What are the philosophical implications of AI?"
# → Claude의 심층 분석
```

### 3. 프로젝트 계획
```bash
# 아이디어 발전
python gemini_claude_wrapper.py --interactive

gemini> Plan a web application for task management
# Gemini가 기술적 계획 제공

gemini> claude What user experience considerations should I include?
# Claude가 UX/UI 관점 추가

gemini> status
# 토큰 사용량 확인
```

## 🚧 향후 개선 계획

- [ ] GUI 인터페이스 추가
- [ ] 대화 히스토리 저장/불러오기
- [ ] 더 정교한 불확실성 감지
- [ ] 비용 추적 및 관리
- [ ] 다른 AI 모델 통합 (GPT, PaLM 등)

## 💬 지원 및 문의

문제가 발생하면:
1. 환경 변수 설정 확인
2. API 키 유효성 검증
3. 네트워크 연결 상태 확인
4. 가상환경 활성화 상태 확인

---

**🎉 이제 Gemini CLI에서 Claude의 도움을 받는 강력한 AI 협업을 경험해보세요!**

### 🎯 핵심 가치
- **Gemini의 속도** + **Claude의 깊이**
- **자동화된 협업** + **수동 제어**
- **단일 인터페이스** + **두 AI의 강점** 