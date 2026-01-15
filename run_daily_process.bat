@echo off
setlocal
REM =====================================================================
REM spider_Unit 每日内容处理任务 (23:00)
REM =====================================================================

cd /d "f:\project\spider_TRAE"
call conda activate yolov5

echo [TIME: %DATE% %TIME%] Starting Daily Processing (OCR/Whisper)...
python main.py --process

if %ERRORLEVEL% neq 0 (
    echo [ERROR] Processing task failed.
) else (
    echo [SUCCESS] Processing task completed.
)

endlocal
