@echo off
REM Build script for Docker container (Windows)
REM Usage: docker\build-docker.bat [tag]
REM Run from project root directory

setlocal enabledelayedexpansion

REM Default tag
set TAG=%1
if "%TAG%"=="" set TAG=draft-ministers:latest

REM Get script directory and project root
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."

echo Building Docker container for Draft Ministers Flask App...

REM Check if Docker is installed
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Docker is not installed. Please install Docker Desktop first.
    exit /b 1
)

REM Check if Dockerfile exists
if not exist "%SCRIPT_DIR%Dockerfile" (
    echo Error: Dockerfile not found in docker\ directory.
    exit /b 1
)

REM Change to project root for build context
cd /d "%PROJECT_ROOT%"

REM Build the Docker image
echo Building image with tag: %TAG%
docker build -f docker\Dockerfile -t %TAG% .

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Build successful!
    echo Image tagged as: %TAG%
    echo.
    echo To run the container:
    echo   docker run -p 5000:5000 %TAG%
    echo.
    echo Or use docker-compose (from project root):
    echo   docker-compose -f docker\docker-compose.yml up -d
) else (
    echo Build failed!
    exit /b 1
)

endlocal

