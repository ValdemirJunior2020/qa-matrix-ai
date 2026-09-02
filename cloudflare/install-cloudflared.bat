@echo off
where cloudflared >nul 2>&1 && (echo cloudflared is already installed.& pause & exit /b 0)
where winget >nul 2>&1 || (echo winget is required for this helper. Install cloudflared manually from Cloudflare.& pause & exit /b 1)
winget install --id Cloudflare.cloudflared -e --accept-package-agreements --accept-source-agreements
cloudflared --version
pause
