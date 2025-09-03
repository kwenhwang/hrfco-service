#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 키 설정 스크립트
사용자가 API 키를 입력하면 안전하게 저장하고, 서버에서는 자동으로 로드합니다.
"""

import os
import sys
import json
import getpass
from pathlib import Path
from cryptography.fernet import Fernet
import base64

def generate_key():
    """암호화 키 생성"""
    return Fernet.generate_key()

def encrypt_api_key(key: bytes, api_key: str) -> str:
    """API 키 암호화"""
    f = Fernet(key)
    encrypted = f.encrypt(api_key.encode())
    return base64.b64encode(encrypted).decode()

def decrypt_api_key(key: bytes, encrypted_key: str) -> str:
    """API 키 복호화"""
    f = Fernet(key)
    encrypted = base64.b64decode(encrypted_key.encode())
    decrypted = f.decrypt(encrypted)
    return decrypted.decode()

def setup_api_keys():
    """API 키 설정"""
    print("🔐 API 키 설정")
    print("=" * 50)
    print("사용자의 API 키를 안전하게 저장합니다.")
    print("키는 암호화되어 저장되며, 서버에서 자동으로 로드됩니다.")
    print()
    
    # 키 파일 경로
    keys_file = Path(".api_keys.json")
    key_file = Path(".encryption_key")
    
    # 기존 키 확인
    existing_keys = {}
    if keys_file.exists():
        try:
            with open(keys_file, 'r', encoding='utf-8') as f:
                existing_keys = json.load(f)
            print("📁 기존 API 키 파일을 발견했습니다.")
        except:
            pass
    
    # 암호화 키 로드 또는 생성
    if key_file.exists():
        with open(key_file, 'rb') as f:
            encryption_key = f.read()
        print("🔑 기존 암호화 키를 사용합니다.")
    else:
        encryption_key = generate_key()
        with open(key_file, 'wb') as f:
            f.write(encryption_key)
        print("🔑 새로운 암호화 키를 생성했습니다.")
    
    # API 키 입력
    api_keys = {}
    
    print("\n📝 API 키를 입력해주세요 (입력하지 않으면 기존 키를 유지합니다):")
    
    # HRFCO API 키
    if "hrfco_api_key" in existing_keys:
        print(f"현재 HRFCO API 키: {existing_keys['hrfco_api_key'][:8]}...")
    hrfco_key = getpass.getpass("HRFCO API 키 (Enter로 건너뛰기): ").strip()
    if hrfco_key:
        api_keys["hrfco_api_key"] = encrypt_api_key(encryption_key, hrfco_key)
    elif "hrfco_api_key" in existing_keys:
        api_keys["hrfco_api_key"] = existing_keys["hrfco_api_key"]
    
    # 기상청 API 키
    if "weather_api_key" in existing_keys:
        print(f"현재 기상청 API 키: {existing_keys['weather_api_key'][:8]}...")
    weather_key = getpass.getpass("기상청 API 키 (Enter로 건너뛰기): ").strip()
    if weather_key:
        api_keys["weather_api_key"] = encrypt_api_key(encryption_key, weather_key)
    elif "weather_api_key" in existing_keys:
        api_keys["weather_api_key"] = existing_keys["weather_api_key"]
    
    # WAMIS API 키
    if "wamis_api_key" in existing_keys:
        print(f"현재 WAMIS API 키: {existing_keys['wamis_api_key'][:8]}...")
    wamis_key = getpass.getpass("WAMIS API 키 (Enter로 건너뛰기): ").strip()
    if wamis_key:
        api_keys["wamis_api_key"] = encrypt_api_key(encryption_key, wamis_key)
    elif "wamis_api_key" in existing_keys:
        api_keys["wamis_api_key"] = existing_keys["wamis_api_key"]
    
    # 파일 저장
    if api_keys:
        with open(keys_file, 'w', encoding='utf-8') as f:
            json.dump(api_keys, f, indent=2, ensure_ascii=False)
        
        # 파일 권한 설정 (소유자만 읽기/쓰기)
        keys_file.chmod(0o600)
        key_file.chmod(0o600)
        
        print(f"\n✅ API 키가 안전하게 저장되었습니다:")
        print(f"   - 키 파일: {keys_file}")
        print(f"   - 암호화 키: {key_file}")
        print(f"   - 파일 권한: 600 (소유자만 읽기/쓰기)")
        
        # 저장된 키 확인
        print(f"\n📋 저장된 API 키:")
        for key_type, encrypted_key in api_keys.items():
            try:
                decrypted = decrypt_api_key(encryption_key, encrypted_key)
                print(f"   - {key_type}: {decrypted[:8]}...")
            except:
                print(f"   - {key_type}: (암호화됨)")
    else:
        print("\n❌ 저장할 API 키가 없습니다.")

def test_api_keys():
    """저장된 API 키 테스트"""
    print("\n🧪 저장된 API 키 테스트")
    print("=" * 30)
    
    keys_file = Path(".api_keys.json")
    key_file = Path(".encryption_key")
    
    if not keys_file.exists() or not key_file.exists():
        print("❌ API 키 파일이 없습니다.")
        return
    
    try:
        # 암호화 키 로드
        with open(key_file, 'rb') as f:
            encryption_key = f.read()
        
        # API 키 로드
        with open(keys_file, 'r', encoding='utf-8') as f:
            api_keys = json.load(f)
        
        print("✅ API 키 파일을 성공적으로 로드했습니다.")
        
        for key_type, encrypted_key in api_keys.items():
            try:
                decrypted = decrypt_api_key(encryption_key, encrypted_key)
                print(f"   - {key_type}: {decrypted[:8]}...")
            except Exception as e:
                print(f"   - {key_type}: 복호화 실패 - {e}")
                
    except Exception as e:
        print(f"❌ API 키 테스트 실패: {e}")

def main():
    """메인 함수"""
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_api_keys()
    else:
        setup_api_keys()

if __name__ == "__main__":
    main() 