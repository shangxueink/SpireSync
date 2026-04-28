import os
import sys
import json
import shutil
import zipfile
import tempfile
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError


def _get_config_path():
    if getattr(sys, "frozen", False):
        return Path(os.path.dirname(sys.executable)) / "config.json"
    return Path(__file__).parent / "config.json"

CONFIG_PATH = _get_config_path()

GAME_EXE = "SlayTheSpire2.exe"
GAME_FOLDER_NAME = "Slay the Spire 2"
MODS_FOLDER = "mods"


def load_config() -> dict:
    default = {
        "download_url": "",
        "download_method": "direct",
        "auto_launch": True,
    }
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            for k, v in default.items():
                cfg.setdefault(k, v)
            return cfg
    return default


def get_available_drives():
    drives = []
    for letter in range(65, 91):
        drive = f"{chr(letter)}:\\"
        if os.path.exists(drive):
            drives.append(drive)
    return drives


def find_game_path() -> Path | None:
    drives = get_available_drives()
    candidate_paths = []

    for drive in drives:
        steam_lib = Path(drive) / "SteamLibrary" / "steamapps" / "common" / GAME_FOLDER_NAME / GAME_EXE
        if steam_lib.exists():
            candidate_paths.append(steam_lib)

    if not candidate_paths:
        steam_path = Path(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")) / "Steam"
        vdf_path = steam_path / "steamapps" / "libraryfolders.vdf"
        if vdf_path.exists():
            lib_paths = _parse_libraryfolders_vdf(vdf_path)
            for lib_path in lib_paths:
                full = Path(lib_path) / "steamapps" / "common" / GAME_FOLDER_NAME / GAME_EXE
                if full.exists():
                    candidate_paths.append(full)

    return candidate_paths[0] if candidate_paths else None


def _parse_libraryfolders_vdf(vdf_path: str) -> list:
    paths = []
    with open(vdf_path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith('"path"'):
                parts = stripped.split('"')
                if len(parts) >= 4:
                    p = parts[3].replace("\\\\", "\\")
                    paths.append(p)
    return paths


def backup_mods(game_dir: Path) -> Path | None:
    mods_dir = game_dir / MODS_FOLDER
    if not mods_dir.exists() or not any(mods_dir.iterdir()):
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"mods_backup_{timestamp}"
    backup_dir = game_dir / backup_name
    mods_dir.rename(backup_dir)

    zip_path = game_dir / f"{backup_name}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(backup_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(backup_dir)
                zf.write(file_path, arcname)

    shutil.rmtree(backup_dir)
    return zip_path


def clean_mods(game_dir: Path):
    mods_dir = game_dir / MODS_FOLDER
    if mods_dir.exists():
        shutil.rmtree(mods_dir)
    mods_dir.mkdir(parents=True, exist_ok=True)


def download_mods(game_dir: Path, download_url: str):
    if not download_url:
        print("[错误] 未配置下载地址，请在 config.json 中设置 download_url")
        return False

    mods_dir = game_dir / MODS_FOLDER

    print(f"[下载] 正在从 {download_url} 下载 mod 包...")

    tmp_file = tempfile.mktemp(suffix=".zip")
    try:
        req = Request(download_url, headers={"User-Agent": "SpireSync/1.0"})
        with urlopen(req, timeout=120) as resp:
            with open(tmp_file, "wb") as f:
                shutil.copyfileobj(resp, f)

        print(f"[解压] 正在解压到 {mods_dir} ...")
        with zipfile.ZipFile(tmp_file, "r") as zf:
            zf.extractall(mods_dir)

        print(f"[完成] mod 文件已放置到 {mods_dir}")
        return True
    except URLError as e:
        print(f"[错误] 下载失败: {e}")
        return False
    except zipfile.BadZipFile:
        print("[错误] 下载的文件不是有效的 zip 包")
        return False
    finally:
        if os.path.exists(tmp_file):
            os.remove(tmp_file)


def launch_game(game_dir: Path):
    exe_path = game_dir / GAME_EXE
    if not exe_path.exists():
        print(f"[错误] 找不到游戏可执行文件: {exe_path}")
        return False
    print(f"[启动] 正在启动 {exe_path} ...")
    subprocess.Popen(str(exe_path), cwd=str(game_dir))
    return True


def main():
    print("=" * 50)
    print("  SpireSync - 杀戮尖塔2 Mod 同步启动器")
    print("=" * 50)

    config = load_config()

    print("[扫描] 正在搜索 Steam 游戏目录...")
    game_path = find_game_path()

    if game_path is None:
        print("[错误] 未找到杀戮尖塔2的安装路径!")
        print("       请确保游戏已通过 Steam 安装。")
        input("\n按回车键退出...")
        sys.exit(1)

    game_dir = game_path.parent
    print(f"[找到] 游戏路径: {game_dir}")

    print("[备份] 正在检查现有 mods 文件夹...")
    backup_path = backup_mods(game_dir)
    if backup_path:
        print(f"[备份] 原有 mods 已备份至: {backup_path}")

    print("[清理] 正在清空 mods 文件夹...")
    clean_mods(game_dir)

    print("[同步] 正在下载最新 mod 包...")
    success = download_mods(game_dir, config["download_url"])
    if not success:
        print("\n[提示] mod 下载失败，您可以:")
        print("  1. 检查 config.json 中的 download_url 是否正确")
        print("  2. 检查网络连接")
        if backup_path:
            print(f"  3. 手动恢复备份: {backup_path}")
        input("\n按回车键退出...")
        sys.exit(1)

    if config.get("auto_launch", True):
        print()
        launch_game(game_dir)

    print()
    print("=" * 50)
    print("  同步完成!")
    print("=" * 50)
    input("\n按回车键退出...")


if __name__ == "__main__":
    main()
