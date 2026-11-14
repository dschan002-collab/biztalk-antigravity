# ==============================================================================
# BizTalk Vercel 자동 배포 스크립트 (deploy.ps1)
# Vercel 웹 콘솔에 들어가지 않고 터미널에서 원클릭으로 배포합니다.
# ==============================================================================

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🚀 업무 말투 변환기 (BizTalk) Vercel CLI 배포" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. .env 파일에서 UPSTAGE_API_KEY 확인
$envFile = Join-Path $PSScriptRoot ".env"
$apiKey = ""

if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        $line = $_.Trim()
        if ($line -match "^UPSTAGE_API_KEY\s*=\s*(.*)$") {
            $apiKey = $matches[1].Trim().Trim('"').Trim("'")
        }
    }
}

if (-not $apiKey) {
    Write-Host "❌ .env 파일에서 UPSTAGE_API_KEY를 찾을 수 없습니다." -ForegroundColor Red
    Write-Host "   .env 파일에 UPSTAGE_API_KEY=your_key 형식으로 설정해 주세요." -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ .env 파일에서 UPSTAGE_API_KEY 로드 완료 (보안을 위해 마스킹)" -ForegroundColor Green

# 2. Vercel 로그인 상태 확인
Write-Host "`n🔍 Vercel CLI 로그인 상태 확인 중..." -ForegroundColor Cyan
$whoamiOutput = npx vercel whoami 2>&1 | Out-String

if ($LASTEXITCODE -ne 0 -or $whoamiOutput -match "Logged out") {
    Write-Host "⚠️  Vercel CLI에 로그인이 필요합니다." -ForegroundColor Yellow
    Write-Host "👉 지금 브라우저를 통해 Vercel CLI 로그인을 진행합니다..." -ForegroundColor Yellow
    npx vercel login
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Vercel 로그인에 실패했습니다. 다시 시도해 주세요." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ Vercel 로그인 확인 완료" -ForegroundColor Green
}

# 3. Vercel 프로젝트 배포 (환경 변수 자동 주입)
Write-Host "`n📦 Vercel 프로덕션 배포를 시작합니다 (FastAPI + Vanilla Frontend)..." -ForegroundColor Cyan

$deployCmd = "npx vercel deploy --prod --yes --env UPSTAGE_API_KEY=$apiKey --build-env UPSTAGE_API_KEY=$apiKey"
Invoke-Expression $deployCmd

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n🎉 Vercel 배포가 성공적으로 완료되었습니다!" -ForegroundColor Green
    Write-Host "   출력된 Production URL로 접속하여 업무 말투 변환기를 사용해 보세요." -ForegroundColor Green
} else {
    Write-Host "`n❌ 배포 중 오류가 발생했습니다. 로그를 확인해 주세요." -ForegroundColor Red
}
