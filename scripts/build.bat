cd ..
pyinstaller --onefile --console --name SpireSync --icon NONE --clean --noconfirm --add-data "config.json;." src/main.py
pause