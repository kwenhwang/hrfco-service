@echo off
REM AI-Lab 지원 신규 프로젝트 생성 스크립트

echo 🚀 AI-Lab 지원 신규 프로젝트 생성기
echo.

if "%1"=="" (
    echo ❌ 사용법: new-project.bat [프로젝트명] [타입]
    echo.
    echo 예시:
    echo   new-project.bat my-react-app react
    echo   new-project.bat my-python-api python  
    echo   new-project.bat my-node-server node
    echo   new-project.bat my-website web
    echo.
    echo 타입: web, react, python, node
    goto :eof
)

set PROJECT_NAME=%1
set PROJECT_TYPE=%2
if "%PROJECT_TYPE%"=="" set PROJECT_TYPE=web

echo 📁 프로젝트명: %PROJECT_NAME%
echo 🎯 프로젝트 타입: %PROJECT_TYPE%
echo.

REM ai-lab의 가상환경 활성화
cd /d "%~dp0"
call venv\Scripts\activate.bat

REM 프로젝트 생성 스크립트 실행
python create_project_template.py %PROJECT_NAME% --type %PROJECT_TYPE%

echo.
echo 🎉 완료! 다음 단계:
echo   1. cd ..\%PROJECT_NAME%
echo   2. Cursor에서 폴더 열기
echo   3. 채팅에서: "이 %PROJECT_TYPE% 프로젝트를 분석해줘"
echo.

pause 