#!/bin/bash

# GitHub Codespaces SSH 접속 스크립트

echo "GitHub Codespaces에 SSH로 접속합니다..."

# Codespace 목록 가져오기
codespaces=$(gh codespace list --json name,displayName,repository,state)

# 사용 가능한 Codespace만 필터링
available_codespaces=$(echo "$codespaces" | jq -r '.[] | select(.state == "Available") | "\(.displayName)|\(.name)"')

if [ -z "$available_codespaces" ]; then
    echo "사용 가능한 Codespace가 없습니다."
    echo "새로운 Codespace를 생성하려면: gh codespace create"
    exit 1
fi

# Codespace 선택
echo ""
echo "사용 가능한 Codespaces:"
i=1
while IFS='|' read -r display_name name; do
    echo "$i. $display_name ($name)"
    i=$((i+1))
done <<< "$available_codespaces"

echo ""
read -p "접속할 Codespace 번호를 선택하세요 (1-$((i-1))): " selection

# 선택된 Codespace 찾기
selected_codespace=$(echo "$available_codespaces" | sed -n "${selection}p" | cut -d'|' -f2)

if [ -n "$selected_codespace" ]; then
    echo ""
    echo "$selected_codespace에 접속합니다..."
    
    # SSH 접속
    gh codespace ssh "$selected_codespace"
else
    echo "잘못된 선택입니다."
    exit 1
fi 