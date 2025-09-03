# Gemini CLI + Super Claude Integration

이 프로젝트는 Google Gemini CLI와 Anthropic Claude를 MCP(Model Context Protocol)를 통해 통합하여 두 AI 모델이 협업할 수 있게 해주는 시스템입니다.

## 🚀 설치 완료!

모든 파일이 성공적으로 설치되었습니다:

- ✅ **gemini_integration.py** - Gemini CLI 통합 모듈
- ✅ **mcp-server.py** - MCP 서버 (Claude ↔ Gemini 브릿지)
- ✅ **gemini-config.json** - 설정 파일
- ✅ **claude_desktop_config.json** - Claude Desktop 설정 예시
- ✅ **Python 가상환경** - 모든 의존성 설치 완료

## 📋 사용 방법

### 1단계: MCP 서버 시작

```bash
cd C:\Users\20172483\web\Mywater_webgame\ai-lab
venv\Scripts\activate
python mcp-server.py --project-root .
```

서버가 시작되면 터미널이 대기 상태가 됩니다. 이는 정상적인 동작입니다.

### 2단계: Claude Desktop 설정

Claude Desktop을 사용하는 경우:

1. Claude Desktop을 종료합니다
2. 설정 파일 위치로 이동:
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

3. 설정 파일에 다음 내용을 추가하거나 기존 내용을 병합합니다:

```json
{
  "mcpServers": {
    "gemini-collaboration": {
      "command": "python",
      "args": ["C:\\Users\\20172483\\web\\Mywater_webgame\\ai-lab\\mcp-server.py", "--project-root", "C:\\Users\\20172483\\web\\Mywater_webgame\\ai-lab"],
      "env": {
        "GEMINI_ENABLED": "true",
        "GEMINI_AUTO_CONSULT": "true",
        "PYTHONPATH": "C:\\Users\\20172483\\web\\Mywater_webgame\\ai-lab"
      }
    }
  }
}
```

4. Claude Desktop을 다시 시작합니다

### 3단계: 사용하기

Claude에서 다음 명령어들을 사용할 수 있습니다:

#### 🤖 Gemini 상담하기
```
질문에 대해 Gemini의 의견도 들어보고 싶어요.
```
또는 직접:
```
/consult_gemini
Query: "Python과 JavaScript 중 어떤 것이 웹 개발 초보자에게 좋을까요?"
Context: "프론트엔드와 백엔드 모두 개발하고 싶습니다"
```

#### 📊 상태 확인
```
/gemini_status
```

#### ⚙️ 설정 변경
```
/toggle_gemini_auto_consult
Enabled: true
```

```
/update_gemini_config
Model: "gemini-2.5-pro"
Rate_limit_delay: 1.5
```

## 🎯 주요 기능

### 1. **Smart Consultation (스마트 상담)**
Claude가 불확실한 답변을 할 때 자동으로 Gemini에게 상담을 요청합니다.

**트리거 패턴들:**
- "잘 모르겠습니다"
- "확실하지 않습니다"
- "I'm not sure"
- "unclear" 등

### 2. **Manual Consultation (수동 상담)**
언제든지 명시적으로 Gemini의 의견을 요청할 수 있습니다.

### 3. **Configuration Management (설정 관리)**
- 모델 선택 (gemini-2.5-flash, gemini-2.5-pro 등)
- 호출 간격 조정 (rate limiting)
- 자동 상담 On/Off
- 타임아웃 설정

### 4. **Statistics & Monitoring (통계 및 모니터링)**
- 호출 횟수 추적
- 성공/실패 통계
- 마지막 상담 시간

## ⚙️ 설정 옵션

### gemini-config.json 파라미터:

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `model` | 사용할 Gemini 모델 | `"gemini-2.5-flash"` |
| `timeout` | 호출 타임아웃(초) | `60` |
| `rate_limit_delay` | 호출 간 대기시간(초) | `2.0` |
| `auto_consult` | 자동 상담 활성화 | `true` |
| `uncertainty_thresholds` | 불확실성 패턴 감지 | 모두 `true` |

## 🔧 문제 해결

### ❌ "Gemini CLI not found"
```bash
npm install -g @google/gemini-cli
```

### ❌ "Authentication required"
```bash
gemini  # 브라우저에서 Google 계정 로그인
```

### ❌ "MCP server connection failed"
1. MCP 서버가 실행 중인지 확인
2. Claude Desktop을 완전히 재시작
3. 설정 파일 경로가 올바른지 확인

### ❌ "Import error"
```bash
cd C:\Users\20172483\web\Mywater_webgame\ai-lab
venv\Scripts\activate
pip install mcp pydantic fastapi uvicorn aiofiles
```

## 🎮 예시 워크플로

### 시나리오 1: 코드 리뷰
```
Claude: "이 Python 코드를 검토해주세요"
→ Claude가 리뷰 제공
→ "Gemini의 의견도 궁금해요"
→ Gemini가 추가 관점 제시
→ Claude가 종합적인 최종 권장사항 제시
```

### 시나리오 2: 기술 선택
```
Claude: "React vs Vue.js, 어떤 것이 좋을까요?"
→ Claude: "둘 다 좋지만... 확실하지 않습니다" (자동 트리거)
→ Gemini 자동 상담
→ Claude가 두 AI의 의견을 종합하여 답변
```

### 시나리오 3: 디버깅
```
Claude: "이 에러를 해결할 수 없어요"
→ /consult_gemini "동일한 에러에 대한 다른 해결 방법"
→ Gemini가 대안적 접근 제시
→ Claude가 최적의 해결책 선택
```

## 📊 성능 및 제한사항

### API 제한:
- **Gemini 무료 티어**: 일일 100회, 분당 15회
- **속도 제한**: 기본 2초 간격 (설정 가능)
- **타임아웃**: 기본 60초 (설정 가능)

### 권장사항:
- 중요한 질문에만 Gemini 상담 사용
- `gemini-2.5-flash` 사용 (빠르고 효율적)
- 필요시 `gemini-2.5-pro`로 전환 (더 정확하지만 느림)

## 🚧 향후 개선 계획

- [ ] 웹 인터페이스 추가
- [ ] 대화 히스토리 저장
- [ ] 더 세밀한 불확실성 감지
- [ ] 다중 모델 동시 상담
- [ ] 상담 결과 캐싱

## 💬 지원

문제가 발생하면:
1. MCP 서버 로그 확인
2. Gemini CLI 상태 확인: `gemini --version`
3. 설정 파일 검증: `/gemini_status`

---

**🎉 이제 Claude와 Gemini가 협업하는 AI 팀을 경험해보세요!** 