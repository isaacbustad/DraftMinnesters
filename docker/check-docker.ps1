# Docker Installation Check Script for Windows
# Run this script to verify Docker installation

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Docker Installation Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$allGood = $true

# Check if Docker command exists
Write-Host "Checking Docker command..." -ForegroundColor Yellow
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "  ✓ Docker command found" -ForegroundColor Green
    $version = docker --version 2>&1
    Write-Host "  Version: $version" -ForegroundColor Gray
} else {
    Write-Host "  ✗ Docker command not found" -ForegroundColor Red
    Write-Host "    Docker may not be installed or not in PATH" -ForegroundColor Yellow
    $allGood = $false
}
Write-Host ""

# Check if Docker Compose exists
Write-Host "Checking Docker Compose..." -ForegroundColor Yellow
if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
    Write-Host "  ✓ Docker Compose found" -ForegroundColor Green
    $composeVersion = docker-compose --version 2>&1
    Write-Host "  Version: $composeVersion" -ForegroundColor Gray
} else {
    Write-Host "  ⚠ Docker Compose not found (may be integrated in newer Docker)" -ForegroundColor Yellow
}
Write-Host ""

# Check if Docker Desktop process is running
Write-Host "Checking Docker Desktop status..." -ForegroundColor Yellow
$dockerProcess = Get-Process "Docker Desktop" -ErrorAction SilentlyContinue
if ($dockerProcess) {
    Write-Host "  ✓ Docker Desktop is running" -ForegroundColor Green
} else {
    Write-Host "  ✗ Docker Desktop is not running" -ForegroundColor Red
    Write-Host "    Please start Docker Desktop from the Start Menu" -ForegroundColor Yellow
    $allGood = $false
}
Write-Host ""

# Check Docker daemon
Write-Host "Checking Docker daemon..." -ForegroundColor Yellow
try {
    $dockerInfo = docker info 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Docker daemon is accessible" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Docker daemon is not accessible" -ForegroundColor Red
        Write-Host "    Error: $dockerInfo" -ForegroundColor Yellow
        $allGood = $false
    }
} catch {
    Write-Host "  ✗ Cannot connect to Docker daemon" -ForegroundColor Red
    $allGood = $false
}
Write-Host ""

# Check WSL 2
Write-Host "Checking WSL 2..." -ForegroundColor Yellow
try {
    $wslStatus = wsl --status 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ WSL is available" -ForegroundColor Green
        Write-Host "  $wslStatus" -ForegroundColor Gray
    } else {
        Write-Host "  ⚠ WSL status check failed" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ⚠ WSL may not be installed" -ForegroundColor Yellow
}
Write-Host ""

# Test Docker with hello-world
Write-Host "Testing Docker with hello-world..." -ForegroundColor Yellow
try {
    $testResult = docker run --rm hello-world 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Docker test successful" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Docker test failed" -ForegroundColor Red
        Write-Host "    $testResult" -ForegroundColor Yellow
        $allGood = $false
    }
} catch {
    Write-Host "  ✗ Cannot run Docker test" -ForegroundColor Red
    $allGood = $false
}
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
if ($allGood) {
    Write-Host "✓ All checks passed! Docker is ready to use." -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now build your Flask app:" -ForegroundColor Cyan
    Write-Host "  docker\build-docker.bat" -ForegroundColor White
    Write-Host ""
    Write-Host "Or run it directly:" -ForegroundColor Cyan
    Write-Host "  docker\run-docker.bat" -ForegroundColor White
} else {
    Write-Host "✗ Some checks failed. Please fix the issues above." -ForegroundColor Red
    Write-Host ""
    Write-Host "Download Docker Desktop: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
}
Write-Host "========================================" -ForegroundColor Cyan

