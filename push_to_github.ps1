# ============================================================
#  CQJTU News - one-click push to GitHub
#
#  HOW TO USE:
#   1. Replace YOUR_USERNAME_HERE below with your GitHub username.
#      Find it at https://github.com/settings/profile
#      Read the "Your profile" URL: https://github.com/XXXXXX
#      (letter "l" and "i" look identical in some fonts)
#   2. Right-click this file -> "Run with PowerShell"
#
#  NOTE: this file is intentionally ASCII-only.
#  Windows PowerShell 5.1 decodes BOM-less UTF-8 as GBK,
#  which mangles Chinese text and breaks quote pairing.
# ============================================================

$ErrorActionPreference = "Stop"
$YourUsername = "liyy66"
$Repo        = "cqjtu-news"

if ($YourUsername -eq "YOUR_USERNAME_HERE") {
    Write-Host ""
    Write-Host "  [STEP 1] Fill in your GitHub username first." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Open this file in a text editor, find the line:"
    Write-Host '      $YourUsername = "YOUR_USERNAME_HERE"'
    Write-Host "  and replace YOUR_USERNAME_HERE with your real username."
    Write-Host ""
    Write-Host "  To find it: open https://github.com/settings/profile"
    Write-Host "  and read the 'Your profile' URL (https://github.com/XXXXXX)."
    Write-Host ""
    Read-Host "  Press Enter to close"
    exit 1
}

if ($YourUsername -notmatch '^[A-Za-z0-9-]+$') {
    Write-Host ""
    Write-Host "  Invalid username: '$YourUsername'" -ForegroundColor Red
    Write-Host "  Allowed: letters, digits and hyphens only." -ForegroundColor Yellow
    Read-Host "  Press Enter to close"
    exit 1
}

$Url  = "https://github.com/$YourUsername/$Repo.git"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

Write-Host ""
Write-Host "  Repository : $Url" -ForegroundColor Cyan
Write-Host "  Local path : $Root"
Write-Host ""

if ((git remote) -contains "origin") { git remote remove origin | Out-Null }
git remote add origin $Url
git branch -M main

Write-Host "  Pushing... (1-2 min first run; GitHub will ask you to sign in)" -ForegroundColor Cyan
Write-Host ""
git push -u origin main
$code = $LASTEXITCODE

Write-Host ""
if ($code -ne 0) {
    Write-Host "  PUSH FAILED." -ForegroundColor Red
    Write-Host "  Usual causes:" -ForegroundColor Yellow
    Write-Host "    - wrong username"
    Write-Host "    - repo '$Repo' not created yet (create an EMPTY repo on GitHub first)"
    Write-Host "    - network problem, just retry"
    Write-Host ""
    Read-Host "  Press Enter to close"
    exit $code
}

Write-Host "  PUSH OK" -ForegroundColor Green
Write-Host ""
Write-Host "  Now finish two steps in the browser:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  1) Open:  https://github.com/$YourUsername/$Repo/settings/pages"
Write-Host "     Set Source = GitHub Actions, then Save"
Write-Host ""
Write-Host "  2) Open:  https://github.com/$YourUsername/$Repo/actions"
Write-Host "     Pick the crawl workflow on the left, click 'Run workflow'"
Write-Host "     First run is a FULL crawl of ~2400 articles, 10-30 min. Normal."
Write-Host ""
Write-Host "  Site will live at:  https://$YourUsername.github.io/$Repo/" -ForegroundColor Green
Write-Host ""
Read-Host "  Press Enter to close"
