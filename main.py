#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HRFCO Service Main Entry Point
"""
import sys
import os
import logging
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from hrfco_service.config import Config
from hrfco_service.server import create_server

def main():
    """HRFCO Service 메인 함수"""
    try:
        # 로깅 설정
        logging.basicConfig(**Config.get_logging_config())
        logger = logging.getLogger("hrfco-service")
        
        # 설정 검증
        Config.validate()
        
        # 서버 생성 및 실행
        server = create_server()
        logger.info("HRFCO Service started successfully!")
        
        # 서버 실행 (FastMCP가 자동으로 처리)
        
    except Exception as e:
        logger.error(f"Failed to start HRFCO Service: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
