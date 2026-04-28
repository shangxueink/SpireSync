@echo off
chcp 65001 >nul
echo ========================================
echo   SpireSync - 构建脚本 v1.0
echo ========================================
echo.

REM 切换到项目根目录
cd /d "%~dp0.."

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

REM 检查 uv 是否安装
uv --version >nul 2>&1
if errorlevel 1 (
    echo [安装] 正在安装 uv...
    python -m pip install uv
)

REM 安装依赖
echo [依赖] 正在安装依赖包...
uv pip install pyinstaller>=6.0.0

REM 清理旧的构建文件
echo [清理] 正在清理旧的构建文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist SpireSync.spec del /f /q SpireSync.spec

echo.
echo [构建] 正在打包 SpireSync.exe...
echo.

REM 使用 PyInstaller 打包
pyinstaller --onefile ^
    --console ^
    --name SpireSync ^
    --icon NONE ^
    --clean ^
    --noconfirm ^
    --add-data "config.json;." ^
    src/main.py

if errorlevel 1 (
    echo.
    echo [错误] 构建失败！
    pause
    exit /b 1
)

echo.
echo ========================================
echo   构建完成!
echo ========================================
echo.
echo 输出文件: dist\SpireSync.exe
echo.
echo [提示] 程序会自动从云端获取配置
echo.

pause
