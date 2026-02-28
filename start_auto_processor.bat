@echo off
chcp 65001 >nul
title 视频自动处理器 / Video Auto Processor
cd /d "%~dp0"

echo.
echo ========================================
echo   视频自动处理器 / Video Auto Processor
echo ========================================
echo.

REM 使用 SoraWatermarkCleaner 虚拟环境的 Python
REM 可通过环境变量 SORA_WM_PYTHON 指定 Python 路径
if defined SORA_WM_PYTHON (
    "%SORA_WM_PYTHON%" "%~dp0auto_processor.py"
) else (
    "%~dp0..\SoraWatermarkCleaner\.venv\Scripts\python.exe" "%~dp0auto_processor.py"
)

pause
