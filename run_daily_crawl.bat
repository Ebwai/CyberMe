@echo off
setlocal
REM =====================================================================
REM spider_Unit 每日采集任务 (22:00)
REM =====================================================================

cd /d "f:\project\spider_TRAE"
call conda activate yolov5

echo [TIME: %DATE% %TIME%] Starting Daily Crawl...
python main.py --now

if %ERRORLEVEL% neq 0 (
    echo [ERROR] Crawl task failed.
) else (
    echo [SUCCESS] Crawl task completed.
)

endlocal
