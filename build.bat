@echo off
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
pyinstaller --onefile --console --name SlayTheSpire2_Sync_MOD --icon icon.ico --clean --noconfirm --add-data "config.json;." src/main.py
pause