# PowerShell script to set up Gemini+Claude integration aliases

$scriptPath = "C:\Users\20172483\web\Mywater_webgame\ai-lab"

# Create function for gemini-claude
function global:gemini-claude {
    $currentDir = Get-Location
    try {
        Set-Location $scriptPath
        & .\venv\Scripts\Activate.ps1
        python gemini_claude_wrapper.py @args
    }
    finally {
        Set-Location $currentDir
    }
}

# Create alias to override gemini command
Set-Alias -Name gemini-enhanced -Value gemini-claude -Scope Global

Write-Host "🚀 Gemini+Claude integration aliases created!" -ForegroundColor Green
Write-Host ""
Write-Host "Available commands:" -ForegroundColor Cyan
Write-Host "  gemini-claude          - Enhanced Gemini with Claude integration"
Write-Host "  gemini-enhanced        - Alias for gemini-claude"
Write-Host ""
Write-Host "Examples:" -ForegroundColor Yellow
Write-Host "  gemini-claude -p 'What is quantum computing?'"
Write-Host "  gemini-claude --interactive"
Write-Host "  gemini-claude --claude-only -p 'Explain AI ethics'"
Write-Host ""
Write-Host "To make this permanent, add this to your PowerShell profile:"
Write-Host "  echo '. C:\Users\20172483\web\Mywater_webgame\ai-lab\setup-aliases.ps1' >> `$PROFILE" 