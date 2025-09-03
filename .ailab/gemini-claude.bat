@echo off
REM Gemini CLI + Claude Integration Wrapper
REM This replaces the 'gemini' command with Claude-enhanced version

cd /d "C:\Users\20172483\web\Mywater_webgame\ai-lab"
call venv\Scripts\activate.bat
python gemini_claude_wrapper.py %* 