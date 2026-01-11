@echo off
:: VittaSaathi WhatsApp Bot - Auto Start Script
:: Run this script at Windows startup to keep bot running 24/7

title VittaSaathi WhatsApp Bot

echo ============================================
echo    VittaSaathi WhatsApp Bot - Auto Start
echo ============================================
echo.

cd /d "C:\Users\dell\Desktop\vittasaathi\whatsapp-bot"

:start
echo [%date% %time%] Starting VittaSaathi Bot...
npm start

:: If bot crashes, wait 10 seconds and restart
echo.
echo [%date% %time%] Bot stopped. Restarting in 10 seconds...
timeout /t 10 /nobreak
goto start
