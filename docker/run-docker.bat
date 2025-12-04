@echo off
REM Run script for Docker container (Windows)
REM Usage: docker\run-docker.bat [tag] [port]
REM Run from project root directory

setlocal enabledelayedexpansion

REM Default values
set TAG=%1
if "%TAG%"=="" set TAG=draft-ministers:latest

set PORT=%2
if "%PORT%"=="" set PORT=5000

REM Get script directory and project root
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."

echo Running Draft Ministers Flask App in Docker...

REM Check if Docker is installed
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Docker is not installed. Please install Docker Desktop first.
    exit /b 1
)

REM Check if image exists
docker images | findstr "draft-ministers" >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Image not found. Building first...
    call "%SCRIPT_DIR%build-docker.bat" %TAG%
)

REM Change to project root
cd /d "%PROJECT_ROOT%"

REM Create necessary directories if they don't exist
if not exist "logs" mkdir logs
if not exist "machine_learning" mkdir machine_learning

REM Stop and remove existing container if it exists
docker stop draft-ministers-app >nul 2>nul
docker rm draft-ministers-app >nul 2>nul

REM Run the container
echo Starting container on port %PORT%...
docker run -d ^
    --name draft-ministers-app ^
    -p %PORT%:5000 ^
    -v "%PROJECT_ROOT%\draft_ministers.db:/app/draft_ministers.db" ^
    -v "%PROJECT_ROOT%\logs:/app/logs" ^
    -v "%PROJECT_ROOT%\machine_learning\football_database.sqlite:/app/machine_learning/football_database.sqlite" ^
    --restart unless-stopped ^
    %TAG%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Container started successfully!
    echo Application available at: http://localhost:%PORT%
    echo.
    echo Useful commands:
    echo   docker logs draft-ministers-app          # View logs
    echo   docker stop draft-ministers-app          # Stop container
    echo   docker start draft-ministers-app         # Start container
    echo   docker rm draft-ministers-app            # Remove container
) else (
    echo Failed to start container!
    exit /b 1
)

endlocal

