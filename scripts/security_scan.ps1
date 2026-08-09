# Runs dependency vulnerability scans locally.
# Requires: pip-audit (pip install pip-audit) and npm.

$ErrorActionPreference = "Continue"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Write-Host "=== Python dependency audit (pip-audit) ===" -ForegroundColor Cyan
& python -m pip_audit -r requirements.txt
$pyExit = $LASTEXITCODE

Write-Host ""
Write-Host "=== Frontend dependency audit (npm audit) ===" -ForegroundColor Cyan
Push-Location "frontend"
& npm audit --audit-level=high
$npmExit = $LASTEXITCODE
Pop-Location

Write-Host ""
Write-Host "=== Scan complete ===" -ForegroundColor Green
Write-Host "Python audit exit code: $pyExit"
Write-Host "npm audit exit code:    $npmExit"

if ($pyExit -ne 0 -or $npmExit -ne 0) {
    Write-Host "Vulnerabilities found. Review and remediate before release." -ForegroundColor Yellow
    exit 1
}
exit 0
