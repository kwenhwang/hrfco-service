#!/usr/bin/env python3
"""
GPT Actions용 HRFCO API HTTPS 프록시 서버
HTTP 전용 HRFCO API를 HTTPS로 래핑하여 GPT Actions에서 사용 가능하게 함
"""

from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
import httpx
import json
from typing import Optional
import uvicorn
from datetime import datetime, timedelta

app = FastAPI(
    title="HRFCO API Proxy for GPT Actions",
    description="홍수통제소 API를 GPT Actions에서 사용할 수 있도록 HTTPS 프록시 제공",
    version="1.0.0"
)

# CORS 설정 (GPT Actions에서 접근 가능하도록)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HRFCO API 설정
HRFCO_BASE_URL = "http://api.hrfco.go.kr"
HRFCO_API_KEY = "FE18B23B-A81B-4246-9674-E8D641902A42"

@app.get("/")
async def root():
    """API 상태 확인"""
    return {
        "message": "HRFCO API Proxy for GPT Actions",
        "status": "active",
        "endpoints": [
            "/waterlevel/data",
            "/waterlevel/observatories", 
            "/rainfall/data",
            "/rainfall/observatories"
        ]
    }

@app.get("/waterlevel/data")
async def get_water_level_data(
    obscd: str = Query(..., description="관측소 코드", example="4009670"),
    tm: str = Query("1H", description="시간 단위", enum=["10M", "1H", "1D"]),
    sdt: Optional[str] = Query(None, description="시작일시 (YYYYMMDDHH)", example="2025090300"),
    edt: Optional[str] = Query(None, description="종료일시 (YYYYMMDDHH)", example="2025090323"),
    hours: int = Query(48, description="조회할 시간 범위 (시간 단위)")
):
    """수위 관측소 데이터 조회"""
    
    # 날짜 범위 자동 계산 (sdt, edt가 없는 경우)
    if not sdt or not edt:
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        if tm == "1D":
            sdt = start_time.strftime("%Y%m%d")
            edt = end_time.strftime("%Y%m%d")
        else:
            sdt = start_time.strftime("%Y%m%d%H")
            edt = end_time.strftime("%Y%m%d%H")
    
    # HRFCO API 호출
    url = f"{HRFCO_BASE_URL}/{HRFCO_API_KEY}/waterlevel/list/{tm}/{obscd}/{sdt}/{edt}.json"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # 추가 정보 포함하여 응답
            return {
                "success": True,
                "observatory_code": obscd,
                "time_type": tm,
                "period": {"start": sdt, "end": edt},
                "data": data.get("content", []),
                "total_records": len(data.get("content", []))
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"HRFCO API 호출 오류: {str(e)}")

@app.get("/waterlevel/observatories")
async def get_water_level_observatories():
    """수위 관측소 정보 조회"""
    
    url = f"{HRFCO_BASE_URL}/{HRFCO_API_KEY}/waterlevel/info.json"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            return {
                "success": True,
                "observatories": data.get("content", []),
                "total_count": len(data.get("content", []))
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"HRFCO API 호출 오류: {str(e)}")

@app.get("/rainfall/data")
async def get_rainfall_data(
    obscd: str = Query(..., description="관측소 코드", example="4009665"),
    tm: str = Query("1H", description="시간 단위", enum=["10M", "1H", "1D"]),
    sdt: Optional[str] = Query(None, description="시작일시 (YYYYMMDDHH)"),
    edt: Optional[str] = Query(None, description="종료일시 (YYYYMMDDHH)"),
    hours: int = Query(48, description="조회할 시간 범위 (시간 단위)")
):
    """강우량 관측소 데이터 조회"""
    
    # 날짜 범위 자동 계산
    if not sdt or not edt:
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        if tm == "1D":
            sdt = start_time.strftime("%Y%m%d")
            edt = end_time.strftime("%Y%m%d")
        else:
            sdt = start_time.strftime("%Y%m%d%H")
            edt = end_time.strftime("%Y%m%d%H")
    
    url = f"{HRFCO_BASE_URL}/{HRFCO_API_KEY}/rainfall/list/{tm}/{obscd}/{sdt}/{edt}.json"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # 강우량 통계 계산
            content = data.get("content", [])
            rainfall_values = [float(item.get("rf", 0)) for item in content if item.get("rf", "").strip()]
            
            total_rainfall = sum(rainfall_values)
            max_rainfall = max(rainfall_values) if rainfall_values else 0
            
            return {
                "success": True,
                "observatory_code": obscd,
                "time_type": tm,
                "period": {"start": sdt, "end": edt},
                "statistics": {
                    "total_rainfall": round(total_rainfall, 1),
                    "max_rainfall": round(max_rainfall, 1),
                    "data_points": len(rainfall_values)
                },
                "data": content,
                "total_records": len(content)
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"HRFCO API 호출 오류: {str(e)}")

@app.get("/rainfall/observatories")  
async def get_rainfall_observatories():
    """강우량 관측소 정보 조회"""
    
    url = f"{HRFCO_BASE_URL}/{HRFCO_API_KEY}/rainfall/info.json"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            return {
                "success": True,
                "observatories": data.get("content", []),
                "total_count": len(data.get("content", []))
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"HRFCO API 호출 오류: {str(e)}")

@app.get("/analysis/water_level/{obscd}")
async def analyze_water_level(
    obscd: str = Path(..., description="관측소 코드"),
    hours: int = Query(48, description="분석할 시간 범위"),
    include_thresholds: bool = Query(True, description="위험 수위 기준 포함 여부")
):
    """수위 데이터 종합 분석"""
    
    try:
        # 관측소 정보 조회
        obs_url = f"{HRFCO_BASE_URL}/{HRFCO_API_KEY}/waterlevel/info.json"
        
        # 수위 데이터 조회
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        sdt = start_time.strftime("%Y%m%d%H")
        edt = end_time.strftime("%Y%m%d%H")
        
        data_url = f"{HRFCO_BASE_URL}/{HRFCO_API_KEY}/waterlevel/list/1H/{obscd}/{sdt}/{edt}.json"
        
        async with httpx.AsyncClient() as client:
            # 관측소 정보와 데이터 동시 조회
            obs_response = await client.get(obs_url, timeout=30)
            data_response = await client.get(data_url, timeout=30)
            
            obs_data = obs_response.json()
            water_data = data_response.json()
            
            # 해당 관측소 정보 찾기
            target_obs = None
            for obs in obs_data.get("content", []):
                if obs.get("wlobscd") == obscd:
                    target_obs = obs
                    break
            
            if not target_obs:
                raise HTTPException(status_code=404, detail=f"관측소 {obscd}를 찾을 수 없습니다")
            
            # 수위 데이터 분석
            water_records = water_data.get("content", [])
            water_levels = [float(item.get("wl", 0)) for item in water_records if item.get("wl", "").strip()]
            
            current_wl = water_levels[-1] if water_levels else 0
            
            analysis = {
                "observatory_info": {
                    "code": obscd,
                    "name": target_obs.get("obsnm", ""),
                    "address": target_obs.get("addr", ""),
                    "coordinates": {
                        "lat": target_obs.get("lat", ""),
                        "lon": target_obs.get("lon", "")
                    }
                },
                "current_water_level": current_wl,
                "statistics": {
                    "max_level": max(water_levels) if water_levels else 0,
                    "min_level": min(water_levels) if water_levels else 0,
                    "avg_level": round(sum(water_levels) / len(water_levels), 2) if water_levels else 0,
                    "data_points": len(water_levels)
                },
                "analysis_period": {
                    "start": sdt,
                    "end": edt,
                    "hours": hours
                }
            }
            
            # 위험 수위 기준 분석
            if include_thresholds:
                thresholds = {
                    "interest": float(target_obs.get("lvlinterest", 0)) if target_obs.get("lvlinterest") else None,
                    "caution": float(target_obs.get("lvlcaution", 0)) if target_obs.get("lvlcaution") else None,
                    "warning": float(target_obs.get("lvlwarning", 0)) if target_obs.get("lvlwarning") else None,
                    "severe": float(target_obs.get("lvlsevere", 0)) if target_obs.get("lvlsevere") else None
                }
                
                # 현재 위험도 평가
                alert_status = "안전"
                if thresholds["severe"] and current_wl >= thresholds["severe"]:
                    alert_status = "심각"
                elif thresholds["warning"] and current_wl >= thresholds["warning"]:
                    alert_status = "경보"
                elif thresholds["caution"] and current_wl >= thresholds["caution"]:
                    alert_status = "주의보"
                elif thresholds["interest"] and current_wl >= thresholds["interest"]:
                    alert_status = "관심"
                
                analysis["thresholds"] = thresholds
                analysis["alert_status"] = alert_status
                
                # 다음 단계까지 여유
                if alert_status == "안전" and thresholds["interest"]:
                    analysis["margin_to_next_level"] = round(thresholds["interest"] - current_wl, 2)
                elif alert_status == "관심" and thresholds["caution"]:
                    analysis["margin_to_next_level"] = round(thresholds["caution"] - current_wl, 2)
                elif alert_status == "주의보" and thresholds["warning"]:
                    analysis["margin_to_next_level"] = round(thresholds["warning"] - current_wl, 2)
                elif alert_status == "경보" and thresholds["severe"]:
                    analysis["margin_to_next_level"] = round(thresholds["severe"] - current_wl, 2)
            
            return analysis
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    print("🚀 HRFCO API Proxy 서버 시작")
    print("📍 GPT Actions에서 사용할 수 있는 HTTPS 프록시 서버입니다")
    print("🌐 접속 URL: https://your-domain.com")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        ssl_keyfile="key.pem",  # SSL 인증서 키 파일
        ssl_certfile="cert.pem"  # SSL 인증서 파일
    ) 