@echo off
setlocal
chcp 65001 >nul
set "PYTHONUTF8=1"
where py >nul 2>&1
if not errorlevel 1 (
  py -3 "%~dp0Word配置.py" %*
) else (
  python "%~dp0Word配置.py" %*
)
set "result=%errorlevel%"
if not "%result%"=="0" echo See readme.txt for setup and troubleshooting.
pause
exit /b %result%
