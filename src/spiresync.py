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
from urllib.error import URLError, HTTPError


def _get_config_path():
    if getattr(sys, "frozen", False):
        return Path(os.path.dirname(sys.executable)) / "config.json"
    return Path(__file__).parent.parent / "config.json"

CONFIG_PATH = _get_config_path()

GAME_EXE = "SlayTheSpire2.exe"
GAME_FOLDER_NAME = "Slay the Spire 2"
MODS_FOLDER = "mods"

# 云端配置地址
REMOTE_CONFIG_URL = "https://github.com/shangxueink/SpireSync/blob/main/config.json"

# 镜像源列表（按优先级排序）
MIRROR_SOURCES = [
    "https://edgeone.gh-proxy.com",
    "https://hk.gh-proxy.com",
    "https://gh-proxy.com",
    "https://gh.llkk.cc",
]


def try_fetch_url(url: str, timeout: int = 10) -> tuple[bool, str]:
    """尝试访问URL并返回内容"""
    try:
        req = Request(url, headers={"User-Agent": "SpireSync/1.0"})
        with urlopen(req, timeout=timeout) as resp:
            content = resp.read().decode("utf-8")
            return True, content
    except (URLError, HTTPError, Exception) as e:
        return False, str(e)


def fetch_remote_config() -> dict | None:
    """从云端获取配置，使用镜像源"""
    print("[云端] 正在获取最新配置...")
    
    # 转换为 raw URL
    raw_url = REMOTE_CONFIG_URL.replace("/blob/", "/raw/")
    
    # 只使用镜像源，不直连
    for mirror in MIRROR_SOURCES:
        mirror_url = f"{mirror}/{raw_url}"
        print(f"[尝试] {mirror}")
        
        success, content = try_fetch_url(mirror_url, timeout=10)
        if success:
            try:
                config = json.loads(content)
                print(f"[成功] 获取配置成功")
                return config
            except json.JSONDecodeError as e:
                print(f"[警告] 配置解析失败: {e}")
                continue
    
    print("[失败] 所有镜像源均无法访问")
    return None


def load_config() -> dict:
    """从云端加载配置"""
    # 获取云端配置
    remote_config = fetch_remote_config()
    if remote_config and remote_config.get("download_url"):
        return remote_config
    
    # 云端获取失败
    print("[错误] 无法获取云端配置")
    print("       请检查网络连接")
    return None


def apply_mirror_to_url(url: str) -> list:
    """为GitHub URL生成所有镜像源URL列表"""
    if not url or not url.startswith("https://github.com"):
        return [url]
    
    # 返回所有镜像源URL
    mirror_urls = []
    for mirror in MIRROR_SOURCES:
        mirror_urls.append(f"{mirror}/{url}")
    
    return mirror_urls


def check_game_exe_in_current_dir() -> Path | None:
    """检查当前目录是否存在游戏 EXE"""
    if getattr(sys, "frozen", False):
        # 打包后的 EXE，检查同目录
        current_dir = Path(os.path.dirname(sys.executable))
    else:
        # 开发环境，检查项目根目录（仅用于测试）
        current_dir = Path(__file__).parent.parent
    
    game_exe = current_dir / GAME_EXE
    if game_exe.exists():
        return game_exe
    return None


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
    """下载并解压mod包，尝试所有镜像源"""
    if not download_url:
        print("[错误] 未配置下载地址")
        return False

    mods_dir = game_dir / MODS_FOLDER
    
    # 获取所有镜像源URL
    mirror_urls = apply_mirror_to_url(download_url)
    print(f"[下载] 正在下载 mod 包...")
    
    tmp_file = tempfile.mktemp(suffix=".zip")
    
    # 尝试每个镜像源
    for idx, url in enumerate(mirror_urls, 1):
        try:
            print(f"[尝试] 镜像源 {idx}/{len(mirror_urls)}")
            
            req = Request(url, headers={"User-Agent": "SpireSync/1.0"})
            with urlopen(req, timeout=180) as resp:
                total_size = resp.headers.get("Content-Length")
                if total_size:
                    total_size = int(total_size)
                    print(f"[大小] {total_size / 1024 / 1024:.2f} MB")
                
                downloaded = 0
                with open(tmp_file, "wb") as f:
                    while True:
                        chunk = resp.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size:
                            progress = (downloaded / total_size) * 100
                            print(f"\r[进度] {progress:.1f}% ({downloaded / 1024 / 1024:.2f} MB)", end="")
                
                if total_size:
                    print()  # 换行

            print(f"[解压] 正在解压到 {mods_dir} ...")
            with zipfile.ZipFile(tmp_file, "r") as zf:
                zf.extractall(mods_dir)

            print(f"[完成] mod 文件已放置到 {mods_dir}")
            if os.path.exists(tmp_file):
                os.remove(tmp_file)
            return True
            
        except (URLError, HTTPError) as e:
            print(f"\n[失败] 此镜像源不可用: {e}")
            if idx < len(mirror_urls):
                print("[继续] 尝试下一个镜像源...")
                if os.path.exists(tmp_file):
                    try:
                        os.remove(tmp_file)
                    except:
                        pass
                continue
        except zipfile.BadZipFile:
            print("\n[错误] 下载的文件不是有效的 zip 包")
            if os.path.exists(tmp_file):
                os.remove(tmp_file)
            return False
        except Exception as e:
            print(f"\n[错误] 未知错误: {e}")
            if idx < len(mirror_urls):
                if os.path.exists(tmp_file):
                    try:
                        os.remove(tmp_file)
                    except:
                        pass
                continue
    
    if os.path.exists(tmp_file):
        os.remove(tmp_file)
    print("\n[错误] 所有镜像源均下载失败")
    return False


def launch_game(game_dir: Path):
    exe_path = game_dir / GAME_EXE
    if not exe_path.exists():
        print(f"[错误] 找不到游戏可执行文件: {exe_path}")
        return False
    print(f"[启动] 正在启动 {exe_path} ...")
    subprocess.Popen(str(exe_path), cwd=str(game_dir))
    return True


def main():
    """主函数"""
    print("=" * 60)
    print("  SpireSync - 杀戮尖塔2 Mod 同步启动器 v1.0")
    print("  GitHub: https://github.com/shangxueink/SpireSync")
    print("=" * 60)
    print()

    try:
        # 检查游戏 EXE 是否在同目录
        print("[检查] 正在检查游戏 EXE...")
        game_path = check_game_exe_in_current_dir()

        if game_path is None:
            print()
            print("=" * 60)
            print("[错误] 未找到 SlayTheSpire2.exe")
            print("=" * 60)
            print()
            print("请将 SpireSync.exe 放到杀戮尖塔2游戏目录下")
            print()
            print("如何找到游戏目录：")
            print("  1. 打开 Steam")
            print("  2. 右键点击【杀戮尖塔2】")
            print("  3. 选择【管理】->【浏览本地文件】")
            print("  4. 将 SpireSync.exe 复制到该目录")
            print("  5. 确保 SpireSync.exe 和 SlayTheSpire2.exe 在同一文件夹")
            print()
            input("按任意键退出...")
            sys.exit(1)

        game_dir = game_path.parent
        print(f"[找到] 游戏路径: {game_dir}")
        print()

        # 加载云端配置
        config = load_config()
        if config is None:
            print()
            input("按任意键退出...")
            sys.exit(1)
        print()

        # 备份现有mods
        print("[备份] 正在检查现有 mods 文件夹...")
        backup_path = backup_mods(game_dir)
        if backup_path:
            print(f"[备份] 原有 mods 已备份至: {backup_path.name}")
        else:
            print("[备份] 无需备份（mods 文件夹为空或不存在）")
        print()

        # 清理mods文件夹
        print("[清理] 正在清空 mods 文件夹...")
        clean_mods(game_dir)
        print("[清理] 完成")
        print()

        # 下载最新mod包
        print("[同步] 正在下载最新 mod 包...")
        success = download_mods(game_dir, config["download_url"])
        
        if not success:
            print()
            print("=" * 60)
            print("[失败] mod 下载失败")
            print("=" * 60)
            print("\n可能的解决方案:")
            print("  1. 检查网络连接")
            print("  2. 稍后重试")
            print("  3. 检查云端配置是否正确")
            if backup_path:
                print(f"  4. 手动恢复备份: {backup_path}")
            input("\n按回车键退出...")
            sys.exit(1)

        print()
        print("=" * 60)
        print("[成功] Mod 同步完成!")
        print("=" * 60)
        print()
        print("[提示] 请手动启动游戏")
        input("\n按任意键退出...")

    except KeyboardInterrupt:
        print("\n\n[中断] 用户取消操作")
        input("\n按任意键退出...")
        sys.exit(0)
    except Exception as e:
        print(f"\n[错误] 发生未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        input("\n按任意键退出...")
        sys.exit(1)


if __name__ == "__main__":
    main()
