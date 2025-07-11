from fastapi import FastAPI, Query, HTTPException
from hrfco_service.api import fetch_observatory_info, fetch_observatory_data
from hrfco_service.config import Config
from hrfco_service.utils import validate_hydro_type, validate_time_type
import uvicorn

app = FastAPI(title="HRFCO MCP HTTP API")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/config")
def get_config():
    return {
        "api_base_url": Config.BASE_URL,
        "cache_ttl_seconds": Config.CACHE_TTL_SECONDS,
        "max_concurrent_requests": Config.MAX_CONCURRENT_REQUESTS,
        "request_timeout": Config.REQUEST_TIMEOUT,
        "observatory_update_interval": Config.OBSERVATORY_UPDATE_INTERVAL,
        "log_level": Config.LOG_LEVEL,
        "log_file": Config.LOG_FILE,
        "default_page_size": Config.DEFAULT_PAGE_SIZE,
        "max_page_size": Config.MAX_PAGE_SIZE,
    }

@app.get("/observatories")
async def list_observatories(
    hydro_type: str = Query(..., description="수문 데이터 타입 (예: waterlevel, dam, rainfall 등)"),
    document_type: str = Query("json", description="문서 포맷 (json 또는 xml)")
):
    """관측소 정보 조회 - 내부 검증 없이 직접 HRFCO API 호출"""
    try:
        # hydro_type만 정규화하고 나머지는 그대로 전달
        normalized_type = validate_hydro_type(hydro_type)
        data = await fetch_observatory_info(normalized_type, document_type=document_type)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/hydro")
async def get_hydro_data(
    hydro_type: str = Query(..., description="수문 데이터 타입 (예: waterlevel, dam, rainfall 등)"),
    time_type: str = Query("10M", description="시간 단위 (예: 10M, 1H, 1D)"),
    obs_code: str = Query(None, description="관측소 코드 (선택)"),
    sdt: str = Query(None, description="검색 시작시간 (선택)"),
    edt: str = Query(None, description="검색 종료시간 (선택)"),
    document_type: str = Query("json", description="문서 포맷 (json 또는 xml)")
):
    """수문 데이터 조회 - 내부 검증 없이 직접 HRFCO API 호출"""
    try:
        # 기본 검증만 수행하고 나머지는 그대로 전달
        normalized_type = validate_hydro_type(hydro_type)
        validate_time_type(time_type)
        
        data = await fetch_observatory_data(
            normalized_type,
            time_type=time_type,
            obs_code=obs_code,
            sdt=sdt,
            edt=edt,
            document_type=document_type
        )
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("hrfco_service.http_server:app", host="0.0.0.0", port=8000, reload=True) 