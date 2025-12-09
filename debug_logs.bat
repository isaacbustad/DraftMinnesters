@echo off
echo Capturing logs using 'docker compose'...
docker compose logs flask-app > debug_output.txt 2>&1
echo. >> debug_output.txt
echo Container Status: >> debug_output.txt
docker compose ps >> debug_output.txt 2>&1
echo Done. Logs saved to debug_output.txt
