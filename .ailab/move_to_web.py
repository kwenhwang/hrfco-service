#!/usr/bin/env python3
"""
AI-Lab을 web 디렉토리로 안전하게 이동하는 스크립트
모든 경로 설정을 자동으로 업데이트합니다.
"""

import os
import json
import shutil
from pathlib import Path
import re

def backup_current_location():
    """현재 설정들 백업"""
    current_dir = Path(__file__).parent
    backup_dir = current_dir / "backup_before_move"
    backup_dir.mkdir(exist_ok=True)
    
    print("📦 현재 설정 백업 중...")
    
    # 중요한 설정 파일들 백업
    important_files = [
        "setup-aliases.ps1",
        "create_project_template.py", 
        "new-project.bat",
        "gemini_claude_wrapper.py",
        "claude_integration.py"
    ]
    
    for file in important_files:
        src = current_dir / file
        if src.exists():
            dst = backup_dir / file
            shutil.copy2(src, dst)
            print(f"   ✅ {file}")
    
    return backup_dir

def check_target_location():
    """대상 위치 확인 및 준비"""
    current_dir = Path(__file__).parent
    target_dir = Path("C:/Users/20172483/web/ai-lab")
    
    print(f"📁 현재 위치: {current_dir}")
    print(f"📁 대상 위치: {target_dir}")
    
    if target_dir.exists():
        print("⚠️  대상 위치에 이미 ai-lab 폴더가 존재합니다!")
        response = input("덮어쓰시겠습니까? (y/n): ").lower()
        if response != 'y':
            print("❌ 이동 취소됨")
            return False
        shutil.rmtree(target_dir)
    
    # 부모 디렉토리 확인
    target_dir.parent.mkdir(parents=True, exist_ok=True)
    return target_dir

def move_directory(source, target):
    """디렉토리 안전하게 이동"""
    print(f"🚚 ai-lab 이동 중: {source} → {target}")
    
    try:
        shutil.move(str(source), str(target))
        print("✅ 폴더 이동 완료!")
        return True
    except Exception as e:
        print(f"❌ 이동 실패: {e}")
        return False

def update_cursor_mcp_config(new_path):
    """Cursor MCP 설정 파일 경로 업데이트"""
    cursor_config = Path.home() / ".cursor" / "mcp.json"
    
    if not cursor_config.exists():
        print("⚠️  Cursor MCP 설정 파일이 없습니다.")
        return
    
    print("🔧 Cursor MCP 설정 업데이트 중...")
    
    try:
        with open(cursor_config, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 경로 치환
        old_path = "C:\\\\Users\\\\20172483\\\\web\\\\Mywater_webgame\\\\ai-lab"
        new_path_escaped = str(new_path).replace("\\", "\\\\")
        
        content = content.replace(old_path, new_path_escaped)
        
        with open(cursor_config, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("   ✅ Cursor MCP 설정 업데이트 완료")
        
    except Exception as e:
        print(f"   ❌ Cursor MCP 설정 업데이트 실패: {e}")

def update_powershell_aliases(new_path):
    """PowerShell 별칭 스크립트 업데이트"""
    script_path = new_path / "setup-aliases.ps1"
    
    if not script_path.exists():
        print("⚠️  PowerShell 별칭 스크립트가 없습니다.")
        return
    
    print("🔧 PowerShell 별칭 스크립트 업데이트 중...")
    
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 경로 치환
        old_path = "C:\\Users\\20172483\\web\\Mywater_webgame\\ai-lab"
        content = content.replace(old_path, str(new_path))
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("   ✅ PowerShell 별칭 스크립트 업데이트 완료")
        
    except Exception as e:
        print(f"   ❌ PowerShell 별칭 스크립트 업데이트 실패: {e}")

def update_project_template(new_path):
    """프로젝트 생성 템플릿 스크립트 업데이트"""
    script_path = new_path / "create_project_template.py"
    
    if not script_path.exists():
        print("⚠️  프로젝트 템플릿 스크립트가 없습니다.")
        return
    
    print("🔧 프로젝트 템플릿 스크립트 업데이트 중...")
    
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 기본 경로 참조는 상대 경로이므로 자동으로 처리됨
        # 추가 업데이트가 필요하면 여기서 처리
        
        print("   ✅ 프로젝트 템플릿 스크립트 확인 완료")
        
    except Exception as e:
        print(f"   ❌ 프로젝트 템플릿 스크립트 업데이트 실패: {e}")

def test_new_location(new_path):
    """새 위치에서 테스트"""
    print("🧪 새 위치에서 테스트 중...")
    
    # 가상환경 확인
    venv_path = new_path / "venv"
    if venv_path.exists():
        print("   ✅ 가상환경 확인됨")
    else:
        print("   ⚠️  가상환경이 없습니다")
    
    # 주요 스크립트들 확인
    scripts = ["create_project_template.py", "new-project.bat", "gemini_claude_wrapper.py"]
    for script in scripts:
        if (new_path / script).exists():
            print(f"   ✅ {script} 확인됨")
        else:
            print(f"   ❌ {script} 누락!")
    
    print("🎯 테스트 완료!")

def main():
    print("🚀 AI-Lab을 web 디렉토리로 이동합니다!")
    print("=" * 50)
    
    # 1. 현재 설정 백업
    backup_dir = backup_current_location()
    
    # 2. 대상 위치 확인
    target_dir = check_target_location()
    if not target_dir:
        return
    
    # 3. 확인 요청
    current_dir = Path(__file__).parent
    print(f"\n이동 계획:")
    print(f"  📂 현재: {current_dir}")
    print(f"  📂 대상: {target_dir}")
    print(f"  📦 백업: {backup_dir}")
    
    response = input("\n계속 진행하시겠습니까? (y/n): ").lower()
    if response != 'y':
        print("❌ 이동 취소됨")
        return
    
    # 4. 디렉토리 이동
    if not move_directory(current_dir, target_dir):
        print("❌ 이동 실패로 인해 작업을 중단합니다.")
        return
    
    # 5. 설정 파일들 업데이트
    print("\n🔧 설정 파일들 업데이트 중...")
    update_cursor_mcp_config(target_dir)
    update_powershell_aliases(target_dir)
    update_project_template(target_dir)
    
    # 6. 테스트
    print("\n🧪 새 위치에서 테스트...")
    test_new_location(target_dir)
    
    # 7. 완료 메시지
    print("\n" + "=" * 50)
    print("🎉 AI-Lab 이동 완료!")
    print(f"📁 새 위치: {target_dir}")
    print("\n🚀 다음 단계:")
    print(f"   1. cd {target_dir}")
    print("   2. new-project.bat test-app react")
    print("   3. Cursor에서 새 프로젝트 테스트")
    print("\n💡 문제 발생 시:")
    print(f"   백업 위치: {backup_dir}")
    print("   수동으로 복원 가능")

if __name__ == "__main__":
    main() 