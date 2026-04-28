"""
Steam 游戏路径查找模块
"""
import os
import sys
from pathlib import Path


GAME_EXE = "SlayTheSpire2.exe"
GAME_FOLDER = "Slay the Spire 2"


def read_steam_registry() -> Path | None:
    """从注册表读取 Steam 安装路径"""
    try:
        import winreg
        
        # 尝试 32 位注册表视图（Steam 通常是 x86）
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                r"SOFTWARE\WOW6432Node\Valve\Steam")
            install_path, _ = winreg.QueryValueEx(key, "InstallPath")
            winreg.CloseKey(key)
            path = Path(install_path)
            if path.exists():
                return path
        except:
            pass
        
        # 尝试原生注册表视图
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                r"SOFTWARE\Valve\Steam")
            install_path, _ = winreg.QueryValueEx(key, "InstallPath")
            winreg.CloseKey(key)
            path = Path(install_path)
            if path.exists():
                return path
        except:
            pass
        
        # 尝试当前用户
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                r"Software\Valve\Steam")
            install_path, _ = winreg.QueryValueEx(key, "SteamPath")
            winreg.CloseKey(key)
            path = Path(install_path)
            if path.exists():
                return path
        except:
            pass
    except:
        pass
    
    return None


def parse_library_folders(vdf_path: Path) -> list[Path]:
    """解析 Steam 的 libraryfolders.vdf 获取所有库路径"""
    if not vdf_path.exists():
        return []
    
    try:
        content = vdf_path.read_text(encoding='utf-8')
    except:
        return []
    
    paths = []
    current_path = None
    
    for line in content.splitlines():
        line = line.strip()
        
        # 匹配 "path" "VALUE"
        if line.startswith('"path"'):
            # 提取引号中的值
            parts = line.split('"')
            if len(parts) >= 4:
                path_value = parts[3]
                # 处理 Windows 路径中的双反斜杠
                path_value = path_value.replace('\\\\', '\\')
                current_path = Path(path_value)
        
        # 遇到闭合括号时，提交路径
        if line == '}' and current_path and current_path.exists():
            paths.append(current_path)
            current_path = None
    
    return paths


def get_all_drive_letters() -> list[str]:
    """获取所有可用的盘符（A-Z）"""
    drives = []
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        drive = f"{letter}:"
        if os.path.exists(drive):
            drives.append(drive)
    return drives


def find_game_install() -> Path | None:
    """自动查找游戏安装路径"""
    
    # 1. 优先检查当前目录（如果用户把 EXE 放在游戏目录）
    if getattr(sys, "frozen", False):
        current_dir = Path(os.path.dirname(sys.executable))
    else:
        current_dir = Path(__file__).parent.parent
    
    game_exe = current_dir / GAME_EXE
    if game_exe.exists():
        print(f"[检测] 在当前目录找到游戏")
        return game_exe
    
    # 2. 从 Steam 注册表获取路径
    steam_root = read_steam_registry()
    if steam_root:
        print(f"[检测] Steam 安装路径: {steam_root}")
        
        # 检查默认 steamapps/common
        default_game = steam_root / "steamapps" / "common" / GAME_FOLDER / GAME_EXE
        if default_game.exists():
            print(f"[检测] 在默认 Steam 库找到游戏")
            return default_game
        
        # 解析 libraryfolders.vdf 获取其他库
        vdf_path = steam_root / "steamapps" / "libraryfolders.vdf"
        libraries = parse_library_folders(vdf_path)
        
        if libraries:
            print(f"[检测] 找到 {len(libraries)} 个 Steam 库")
            for lib_path in libraries:
                game_path = lib_path / "steamapps" / "common" / GAME_FOLDER / GAME_EXE
                if game_path.exists():
                    print(f"[检测] 在 Steam 库找到游戏: {lib_path}")
                    return game_path
    
    # 3. 遍历所有盘符的常见安装位置
    print("[检测] 正在扫描所有盘符...")
    drives = get_all_drive_letters()
    
    for drive in drives:
        # 常见的 Steam 安装路径
        common_paths = [
            Path(f"{drive}/Steam/steamapps/common") / GAME_FOLDER / GAME_EXE,
            Path(f"{drive}/SteamLibrary/steamapps/common") / GAME_FOLDER / GAME_EXE,
            Path(f"{drive}/Program Files (x86)/Steam/steamapps/common") / GAME_FOLDER / GAME_EXE,
            Path(f"{drive}/Program Files/Steam/steamapps/common") / GAME_FOLDER / GAME_EXE,
        ]
        
        for path in common_paths:
            if path.exists():
                print(f"[检测] 在 {drive} 盘找到游戏: {path.parent}")
                return path
    
    return None
