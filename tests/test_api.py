# -*- coding: utf-8 -*-
"""
HRFCO Service API Tests
"""
import pytest
import asyncio
import os
from unittest.mock import Mock, patch
from typing import Dict, Any

from hrfco_service.config import Config
from hrfco_service.cache import CacheManager
from hrfco_service.api import HRFCOAPIClient
from hrfco_service.observatory import ObservatoryManager
from hrfco_service.utils import validate_hydro_type, validate_time_type


class TestConfig:
    """설정 테스트"""
    
    def test_config_validation(self):
        """설정 검증 테스트"""
        # API 키가 하드코딩되어 있으므로 항상 통과
        Config.validate()
        assert Config.API_KEY == os.getenv("HRFCO_API_KEY", "your-api-key-here")
    
    def test_logging_config(self):
        """로깅 설정 테스트"""
        config = Config.get_logging_config()
        assert 'level' in config
        assert 'format' in config
        assert 'handlers' in config


class TestCacheManager:
    """캐시 관리자 테스트"""
    
    def setup_method(self):
        """테스트 설정"""
        self.cache = CacheManager(ttl_seconds=60)
    
    def test_cache_set_get(self):
        """캐시 설정/조회 테스트"""
        self.cache.set("test_key", "test_value")
        result = self.cache.get("test_key")
        assert result == "test_value"
    
    def test_cache_expiration(self):
        """캐시 만료 테스트"""
        self.cache.set("test_key", "test_value")
        # TTL을 0으로 설정하여 즉시 만료
        self.cache.ttl_seconds = 0
        result = self.cache.get("test_key")
        assert result is None
    
    def test_cache_stats(self):
        """캐시 통계 테스트"""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        stats = self.cache.get_stats()
        assert stats['size'] == 2


class TestObservatoryManager:
    """관측소 관리자 테스트"""
    
    def setup_method(self):
        """테스트 설정"""
        self.manager = ObservatoryManager()
    
    def test_update_observatory_info(self):
        """관측소 정보 업데이트 테스트"""
        test_data = [
            {
                "wlobscd": "TEST001",
                "obsnm": "테스트 관측소",
                "addr": "테스트 주소",
                "lon": "127.0",
                "lat": "36.0"
            }
        ]
        
        self.manager.update("waterlevel", test_data)
        assert "TEST001" in self.manager.info["waterlevel"]
        assert self.manager.info["waterlevel"]["TEST001"]["obsnm"] == "테스트 관측소"
    
    def test_get_observatory_code(self):
        """관측소 코드 조회 테스트"""
        test_data = [
            {
                "wlobscd": "TEST001",
                "obsnm": "테스트 관측소"
            }
        ]
        
        self.manager.update("waterlevel", test_data)
        
        # 코드로 직접 조회
        code = self.manager.get_observatory_code("waterlevel", "TEST001")
        assert code == "TEST001"
        
        # 이름으로 조회
        code = self.manager.get_observatory_code("waterlevel", "테스트 관측소")
        assert code == "TEST001"
    
    def test_search_observatories(self):
        """관측소 검색 테스트"""
        test_data = [
            {
                "wlobscd": "TEST001",
                "obsnm": "테스트 관측소",
                "addr": "테스트 주소"
            }
        ]
        
        self.manager.update("waterlevel", test_data)
        results = self.manager.search_observatories("테스트")
        assert len(results) == 1
        assert results[0]["obs_code"] == "TEST001"


class TestUtils:
    """유틸리티 함수 테스트"""
    
    def test_validate_hydro_type(self):
        """수문 타입 검증 테스트"""
        # 유효한 타입
        result = validate_hydro_type("waterlevel")
        assert result == "waterlevel"
        
        # 대소문자 무시
        result = validate_hydro_type("WATERLEVEL")
        assert result == "waterlevel"
        
        # 잘못된 타입
        with pytest.raises(Exception):
            validate_hydro_type("invalid_type")
    
    def test_validate_time_type(self):
        """시간 타입 검증 테스트"""
        # 유효한 타입들
        validate_time_type("10M")
        validate_time_type("1H")
        validate_time_type("1D")
        
        # 잘못된 타입
        with pytest.raises(Exception):
            validate_time_type("invalid")


@pytest.mark.asyncio
class TestAPIClient:
    """API 클라이언트 테스트"""
    
    def setup_method(self):
        """테스트 설정"""
        self.cache = CacheManager()
        self.client = HRFCOAPIClient(self.cache)
    
    @patch('httpx.AsyncClient.get')
    async def test_fetch_data_success(self, mock_get):
        """API 데이터 조회 성공 테스트"""
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.json.return_value = {"content": [{"test": "data"}]}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = await self.client.fetch_data("waterlevel", "info")
        assert "content" in result
    
    @patch('httpx.AsyncClient.get')
    async def test_fetch_data_error(self, mock_get):
        """API 데이터 조회 실패 테스트"""
        # Mock 에러 응답 설정
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_get.return_value = mock_response
        
        with pytest.raises(Exception):
            await self.client.fetch_data("waterlevel", "info")


if __name__ == "__main__":
    pytest.main([__file__]) 