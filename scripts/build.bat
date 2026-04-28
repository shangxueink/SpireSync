@echo off
chcp 65001 >nul
echo ========================================
echo   SpireSync - 构建脚本
echo ========================================
echo.

REM 检查 PyInstaller 是否安装
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [安装] 正在安装 PyInstaller...
    python -m pip install pyinstaller
)

echo [构建] 正在打包 SpireSync.exe...

pyinstaller --onefile --console --name SpireSync --clean main.py

echo.
echo ========================================
echo   构建完成!
echo   输出目录: dist\SpireSync.exe
echo ========================================
echo.
echo 首次运行时会在同目录下自动生成 config.json，请编辑其中的下载地址后再次运行。

pause
