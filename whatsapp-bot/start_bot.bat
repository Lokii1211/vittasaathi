@echo off
echo ========================================
echo    VittaSaathi WhatsApp Bot v2.0
echo    Railway API Integration
echo ========================================
echo.

cd /d %~dp0

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing dependencies...
    npm install
    echo.
)

echo Starting bot...
echo Messages will be forwarded to Railway API
echo.
echo Press Ctrl+C to stop
echo.

node index.js

pause
