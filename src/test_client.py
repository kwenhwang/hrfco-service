# test_client.py
import subprocess
import time

requests = [
    '{"method": "initialize", "params": {"client": {"type": "generic", "version": "1.0"}}, "jsonrpc": "2.0", "id": 0}',
    '{"method": "tools/call", "params": {"name": "get_hydro_data", "arguments": {"hydro_type": "dam", "obs_code": "소양강댐", "time_type": "10M", "start_date": "202503251330", "end_date": "202503251330"}}, "jsonrpc": "2.0", "id": 1}'
]

process = subprocess.Popen(
    ["python", "-m", "hrfco_service"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    cwd="D:\\python\\mcp\\hrfco_service\\src",
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