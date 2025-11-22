@echo off
REM Build script for Docker container (Windows)
REM Usage: build-docker.bat [tag]

setlocal enabledelayedexpansion

REM Default tag
set TAG=%1
if "%TAG%"=="" set TAG=draft-ministers:latest

echo Building Docker container for Draft Ministers Flask App...

REM Check if Docker is installed
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Docker is not installed. Please install Docker Desktop first.
    exit /b 1
)

REM Check if Dockerfile exists
if not exist "Dockerfile" (
    echo Error: Dockerfile not found.
    exit /b 1
)

REM Build the Docker image
echo Building image with tag: %TAG%
docker build -t %TAG% .

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Build successful!
    echo Image tagged as: %TAG%
    echo.
    echo To run the container:
    echo   docker run -p 5000:5000 %TAG%
    echo.
    echo Or use docker-compose:
    echo   docker-compose up -d
) else (
    echo Build failed!
    exit /b 1
)

endlocal

