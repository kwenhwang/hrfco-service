# test_client.py
import subprocess
import time
import os
import sys
from pathlib import Path

# 프로젝트 루트 디렉토리 찾기
project_root = Path(__file__).parent.parent
src_path = project_root / "src"

requests = [
    '{"method": "initialize", "params": {"client": {"type": "generic", "version": "1.0"}}, "jsonrpc": "2.0", "id": 0}',
    '{"method": "tools/call", "params": {"name": "get_hydro_data", "arguments": {"hydro_type": "dam", "obs_code": "소양강댐", "time_type": "10M", "start_date": "202503251330", "end_date": "202503251330"}}, "jsonrpc": "2.0", "id": 1}'
]

# Python 실행 파일 경로 확인
python_executable = sys.executable

try:
    process = subprocess.Popen(
        [python_executable, "-m", "hrfco_service"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(src_path),
        text=True,
        encoding="utf-8"
    )

    for req in requests:
        process.stdin.write(req + "\n")
        process.stdin.flush()
        time.sleep(0.5)  # 초기화 대기

    stdout, stderr = process.communicate()
    print("출력:", stdout)
    print("오류:", stderr if stderr else "없음")
    
except Exception as e:
    print(f"테스트 실행 중 오류 발생: {e}")
    print(f"Python 실행 파일: {python_executable}")
    print(f"작업 디렉토리: {src_path}")
    print(f"디렉토리 존재 여부: {src_path.exists()}")