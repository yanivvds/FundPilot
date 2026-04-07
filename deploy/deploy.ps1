<#
.SYNOPSIS
    Deploy FundPilot: pull latest code, rebuild frontend, restart service.
    Called automatically by GitHub Actions on every push to main.
    Can also be run manually from the VM.
#>
$ErrorActionPreference = "Stop"
$AppDir = "C:\FundPilot"

function Write-Step([string]$msg) {
    Write-Host ""
    Write-Host ">> $msg" -ForegroundColor Cyan
}

Write-Host "================================================"
Write-Host " FundPilot Deploy  $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host "================================================"

Set-Location $AppDir

# ── 1. Pull latest code ───────────────────────────────────────────────────────
Write-Step "Pulling latest code from main..."
git fetch origin main
git reset --hard origin/main
Write-Host "   OK: $(git log -1 --oneline)"

# ── 2. Install / update Python dependencies ───────────────────────────────────
Write-Step "Installing Python dependencies..."
.\.venv\Scripts\pip install -r requirements.txt -q --no-warn-script-location
Write-Host "   OK"

# ── 3. Build frontend ─────────────────────────────────────────────────────────
Write-Step "Building frontend web component..."
Set-Location frontends\webcomponent
npm ci --prefer-offline --silent
npm run build
Set-Location $AppDir
Write-Host "   OK: built vanna-components.js"

# ── 4. Copy built bundle into static/ ────────────────────────────────────────
Write-Step "Copying static assets..."
New-Item -ItemType Directory -Force -Path "$AppDir\static" | Out-Null
Copy-Item -Force frontends\webcomponent\dist\vanna-components.js static\vanna-components.js
Write-Host "   OK"

# ── 5. Restart the Windows Service ───────────────────────────────────────────
Write-Step "Restarting FundPilot service..."
nssm restart FundPilot
Write-Host "   OK: service restarted"

# ── 6. Health check ───────────────────────────────────────────────────────────
Write-Step "Waiting for server to become healthy..."
$maxAttempts = 10
$attempt = 0
$healthy = $false

while ($attempt -lt $maxAttempts -and -not $healthy) {
    Start-Sleep -Seconds 3
    $attempt++
    try {
        $resp = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -UseBasicParsing -TimeoutSec 5
        if ($resp.StatusCode -eq 200) {
            $healthy = $true
        }
    } catch {
        Write-Host "   Attempt $attempt/$maxAttempts — not ready yet..."
    }
}

if ($healthy) {
    Write-Host ""
    Write-Host "================================================"
    Write-Host " Deploy successful!" -ForegroundColor Green
    Write-Host "================================================"
} else {
    Write-Error "Health check failed after $maxAttempts attempts. Check logs at C:\FundPilot\logs\"
    exit 1
}
