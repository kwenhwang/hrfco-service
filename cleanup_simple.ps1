Write-Host "Project Cleanup Starting..." -ForegroundColor Green

# Create directories
New-Item -ItemType Directory -Path "docs\setup" -Force | Out-Null
New-Item -ItemType Directory -Path "docs\api" -Force | Out-Null
New-Item -ItemType Directory -Path "docs\examples" -Force | Out-Null
New-Item -ItemType Directory -Path "tools" -Force | Out-Null
New-Item -ItemType Directory -Path "temp" -Force | Out-Null

Write-Host "Directories created" -ForegroundColor Green

# Move documentation files to docs/setup/
if (Test-Path "CHATGPT_SETUP.md") { Move-Item "CHATGPT_SETUP.md" "docs\setup\chatgpt-setup.md" -Force }
if (Test-Path "GPT_ACTIONS_SOLUTION.md") { Move-Item "GPT_ACTIONS_SOLUTION.md" "docs\setup\gpt-actions-setup.md" -Force }
if (Test-Path "cloudflare_tunnel_setup.md") { Move-Item "cloudflare_tunnel_setup.md" "docs\setup\" -Force }
if (Test-Path "ngrok_setup.md") { Move-Item "ngrok_setup.md" "docs\setup\" -Force }
if (Test-Path "free_hosting_alternatives.md") { Move-Item "free_hosting_alternatives.md" "docs\setup\" -Force }

Write-Host "Setup docs moved" -ForegroundColor Green

# Move API documentation to docs/api/
if (Test-Path "WAMIS_API_SPEC.md") { Move-Item "WAMIS_API_SPEC.md" "docs\api\wamis-api-spec.md" -Force }
if (Test-Path "WAMIS_COMPLETE_API_SPEC.md") { Move-Item "WAMIS_COMPLETE_API_SPEC.md" "docs\api\wamis-complete-spec.md" -Force }

Write-Host "API docs moved" -ForegroundColor Green

# Move example files to docs/examples/
if (Test-Path "chatgpt_functions.py") { Move-Item "chatgpt_functions.py" "docs\examples\chatgpt-functions.py" -Force }
if (Test-Path "chatgpt_usage_example.py") { Move-Item "chatgpt_usage_example.py" "docs\examples\chatgpt-usage.py" -Force }
if (Test-Path "chatgpt_real_example.py") { Move-Item "chatgpt_real_example.py" "docs\examples\chatgpt-real-demo.py" -Force }
if (Test-Path "test_chatgpt_functions.py") { Move-Item "test_chatgpt_functions.py" "docs\examples\" -Force }
if (Test-Path "gpt_actions_proxy_schema.json") { Move-Item "gpt_actions_proxy_schema.json" "docs\examples\" -Force }
if (Test-Path "gpt_actions_schema.json") { Move-Item "gpt_actions_schema.json" "docs\examples\" -Force }

Write-Host "Example files moved" -ForegroundColor Green

# Move tools to tools/
if (Test-Path "run_proxy_server.py") { Move-Item "run_proxy_server.py" "tools\" -Force }
if (Test-Path "setup_api_keys.py") { Move-Item "setup_api_keys.py" "tools\" -Force }
if (Test-Path "test_wamis_complete_api.py") { Move-Item "test_wamis_complete_api.py" "tools\" -Force }

Write-Host "Tools moved" -ForegroundColor Green

# Move cleanup docs to docs/
if (Test-Path "project_cleanup_plan.md") { Move-Item "project_cleanup_plan.md" "docs\" -Force }
if (Test-Path "CLEANUP_SUMMARY.md") { Move-Item "CLEANUP_SUMMARY.md" "docs\" -Force }

# Remove temporary files
if (Test-Path "ngrok.exe") { Remove-Item "ngrok.exe" -Force }

Write-Host "Cleanup completed!" -ForegroundColor Green
Write-Host "Run: git add . && git commit -m 'feat: organize project structure'" -ForegroundColor Cyan 