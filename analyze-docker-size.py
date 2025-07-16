#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Docker 이미지 용량 분석 스크립트
"""
import os
import subprocess
import json

def analyze_docker_image_size():
    """Docker 이미지 용량 분석"""
    print("🔍 Docker 이미지 용량 분석")
    print("=" * 50)
    
    try:
        # Docker 이미지 정보 조회
        result = subprocess.run(
            ["docker", "images", "--format", "json"],
            capture_output=True, text=True
        )
        
        if result.returncode != 0:
            print("❌ Docker 명령어 실행 실패")
            return
        
        images = []
        for line in result.stdout.strip().split('\n'):
            if line:
                try:
                    image_info = json.loads(line)
                    images.append(image_info)
                except json.JSONDecodeError:
                    continue
        
        # hrfco 관련 이미지 찾기
        hrfco_images = [img for img in images if 'hrfco' in img.get('Repository', '').lower()]
        
        if not hrfco_images:
            print("❌ hrfco 관련 Docker 이미지를 찾을 수 없습니다.")
            print("다음 명령어로 이미지를 빌드해주세요:")
            print("docker build -t hrfco-service .")
            return
        
        print("📊 HRFCO Docker 이미지 용량:")
        for img in hrfco_images:
            repo = img.get('Repository', 'Unknown')
            tag = img.get('Tag', 'latest')
            size = img.get('Size', 'Unknown')
            created = img.get('CreatedAt', 'Unknown')
            
            print(f"  📦 {repo}:{tag}")
            print(f"     크기: {size}")
            print(f"     생성: {created}")
            print()
    
    except Exception as e:
        print(f"❌ 분석 중 오류: {str(e)}")

def analyze_project_size():
    """프로젝트 파일 크기 분석"""
    print("📁 프로젝트 파일 크기 분석")
    print("=" * 50)
    
    large_files = []
    total_size = 0
    
    for root, dirs, files in os.walk('.'):
        # .git 디렉토리 제외
        if '.git' in root:
            continue
        
        for file in files:
            file_path = os.path.join(root, file)
            try:
                size = os.path.getsize(file_path)
                total_size += size
                
                # 1MB 이상 파일만 기록
                if size > 1024 * 1024:
                    large_files.append((file_path, size))
            except (OSError, PermissionError):
                continue
    
    # 큰 파일 순으로 정렬
    large_files.sort(key=lambda x: x[1], reverse=True)
    
    print(f"📊 총 프로젝트 크기: {total_size / (1024*1024):.2f} MB")
    print()
    
    if large_files:
        print("🔍 큰 파일들 (1MB 이상):")
        for file_path, size in large_files[:10]:  # 상위 10개만
            size_mb = size / (1024 * 1024)
            print(f"  📄 {file_path}: {size_mb:.2f} MB")
    else:
        print("✅ 1MB 이상의 큰 파일이 없습니다.")

def suggest_optimizations():
    """용량 최적화 제안"""
    print("\n💡 용량 최적화 제안")
    print("=" * 50)
    
    suggestions = [
        "1. 멀티 스테이지 빌드 사용 (Dockerfile.optimized)",
        "2. .dockerignore 최적화 (.dockerignore.optimized)",
        "3. 불필요한 파일 제거 (tests/, docs/, *.log 등)",
        "4. Python 캐시 파일 제거 (__pycache__/)",
        "5. 개발 도구 파일 제거 (.vscode/, .idea/)",
        "6. 로그 파일 제거 (*.log)",
        "7. 임시 파일 제거 (tmp/, temp/)",
        "8. Git 히스토리 제거 (.git/)",
        "9. Docker 레이어 최적화",
        "10. 베이스 이미지 최소화 (alpine 사용 고려)"
    ]
    
    for suggestion in suggestions:
        print(f"  ✅ {suggestion}")

def main():
    """메인 함수"""
    print("🚀 Docker 이미지 용량 분석")
    print("=" * 50)
    
    # 프로젝트 크기 분석
    analyze_project_size()
    
    # Docker 이미지 크기 분석
    analyze_docker_image_size()
    
    # 최적화 제안
    suggest_optimizations()
    
    print("\n📋 최적화 실행 방법:")
    print("1. 최적화된 Dockerfile 사용:")
    print("   docker build -f Dockerfile.optimized -t hrfco-service-optimized .")
    print()
    print("2. 최적화된 .dockerignore 사용:")
    print("   cp .dockerignore.optimized .dockerignore")
    print()
    print("3. 용량 비교:")
    print("   docker images | grep hrfco")

if __name__ == "__main__":
    main() 