#!/usr/bin/env pwsh

# GitHub Codespaces SSH 접속 스크립트

Write-Host "GitHub Codespaces에 SSH로 접속합니다..." -ForegroundColor Green

# Codespace 목록 가져오기
$codespaces = gh codespace list --json name,displayName,repository,state | ConvertFrom-Json

# 사용 가능한 Codespace만 필터링
$availableCodespaces = $codespaces | Where-Object { $_.state -eq "Available" }

if ($availableCodespaces.Count -eq 0) {
    Write-Host "사용 가능한 Codespace가 없습니다." -ForegroundColor Yellow
    Write-Host "새로운 Codespace를 생성하려면: gh codespace create" -ForegroundColor Cyan
    exit 1
}

# Codespace 선택
Write-Host "`n사용 가능한 Codespaces:" -ForegroundColor Cyan
for ($i = 0; $i -lt $availableCodespaces.Count; $i++) {
    $cs = $availableCodespaces[$i]
    Write-Host "$($i + 1). $($cs.displayName) ($($cs.name))" -ForegroundColor White
}

$selection = Read-Host "`n접속할 Codespace 번호를 선택하세요 (1-$($availableCodespaces.Count))"

if ($selection -match '^\d+$' -and [int]$selection -ge 1 -and [int]$selection -le $availableCodespaces.Count) {
    $selectedCodespace = $availableCodespaces[[int]$selection - 1]
    Write-Host "`n$($selectedCodespace.displayName)에 접속합니다..." -ForegroundColor Green
    
    # SSH 접속
    gh codespace ssh $selectedCodespace.name
} else {
    Write-Host "잘못된 선택입니다." -ForegroundColor Red
    exit 1
} 