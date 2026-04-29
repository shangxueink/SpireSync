"""
SpireSync - 杀戮尖塔2 Mod 同步工具
核心逻辑模块
"""
import os
import sys
import shutil
import zipfile
import msvcrt
from pathlib import Path
from datetime import datetime

# 导入自定义模块
from steam_finder import find_game_install
from downloader import fetch_remote_config, download_mods


# 常量定义
MODS_FOLDER = "mods"


def load_config() -> dict:
    """加载配置（从云端获取）"""
    print("[云端] 正在获取最新配置...")
    config = fetch_remote_config()
    
    if config is None:
        print("[错误] 无法获取云端配置")
        return None
    
    print("[成功] 获取配置成功")
    return config


def get_exe_dir() -> Path:
    """获取 EXE 所在目录"""
    if getattr(sys, "frozen", False):
        # 打包后的 EXE
        return Path(os.path.dirname(sys.executable))
    else:
        # 开发环境
        return Path(__file__).parent.parent


def backup_mods(game_dir: Path) -> Path | None:
    """备份现有 mods 文件夹到游戏目录的 temp 文件夹"""
    mods_dir = game_dir / MODS_FOLDER
    if not mods_dir.exists() or not any(mods_dir.iterdir()):
        return None

    # 备份到游戏目录的 temp 文件夹
    temp_dir = game_dir / "temp"
    temp_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"mods_backup_{timestamp}"
    zip_path = temp_dir / f"{backup_name}.zip"
    
    # 直接打包，不移动文件夹
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(mods_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(mods_dir)
                zf.write(file_path, arcname)

    return zip_path


def clean_mods(game_dir: Path):
    """清理mods文件夹"""
    mods_dir = game_dir / MODS_FOLDER
    if mods_dir.exists():
        shutil.rmtree(mods_dir)
        print("[清理] 正在清空 mods 文件夹...")
    else:
        print("[清理] mods 文件夹不存在，无需清理")
    mods_dir.mkdir(parents=True, exist_ok=True)


def show_mod_source_menu(sources: dict) -> tuple[str, list[str]] | None:
    """
    显示 mod 源选择菜单
    返回: (选中的源名称, 该源的URL列表) 或 None（用户取消）
    """
    source_list = list(sources.items())
    selected_index = 0
    
    def render_menu():
        """渲染菜单"""
        # 清屏（Windows）
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("=" * 60)
        print("  SpireSync - 杀戮尖塔2 Mod 同步启动器 v1.0")
        print("  GitHub: https://github.com/shangxueink/SpireSync")
        print("=" * 60)
        print()
        print("=" * 60)
        print("  选择 Mod 源")
        print("=" * 60)
        print()
        print("使用 ↑↓ 方向键选择，Enter 或 Y 确认，Esc 或 N 取消")
        print()
        
        for i, (name, urls) in enumerate(source_list):
            if i == selected_index:
                print(f"  → {name}")
            else:
                print(f"    {name}")
        
        print()
        print("=" * 60)
    
    # 初始渲染
    render_menu()
    
    # 监听按键
    try:
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                
                # 方向键特殊处理（Windows 下方向键是两个字节）
                if key == b'\xe0':  # 方向键前缀
                    key = msvcrt.getch()
                    if key == b'H':  # 上箭头
                        selected_index = (selected_index - 1) % len(source_list)
                        render_menu()
                    elif key == b'P':  # 下箭头
                        selected_index = (selected_index + 1) % len(source_list)
                        render_menu()
                
                # Enter 或 Y 确认
                elif key in (b'\r', b'Y', b'y'):
                    selected_name, selected_urls = source_list[selected_index]
                    print(f"\n[选择] 已选择: {selected_name}")
                    print()
                    return (selected_name, selected_urls)
                
                # Esc 或 N 取消
                elif key in (b'\x1b', b'N', b'n'):
                    print("\n[取消] 用户取消操作")
                    return None
                    
    except KeyboardInterrupt:
        print("\n\n[取消] 用户取消操作")
        return None


def main():
    """主函数"""
    print("=" * 60)
    print("  SpireSync - 杀戮尖塔2 Mod 同步启动器 v1.0")
    print("  GitHub: https://github.com/shangxueink/SpireSync")
    print("=" * 60)
    print()
    
    # 显示警告和确认提示（在最开始）
    print("=" * 60)
    print("  重要提示")
    print("=" * 60)
    print()
    print("此操作将：")
    print("  • 替换你当前所有的 Mod")
    print("  • 使用远程 Mod 以确保多人联机统一")
    print("  • 你的 Mod 会被备份到 ZIP 压缩包")
    print()
    print("=" * 60)
    print()
    print("按 Enter 或 Y 键继续，按 Esc 或 N 键取消...")
    
    # 监听单个按键
    try:
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                # Enter (13), Y/y (89/121)
                if key in (b'\r', b'Y', b'y'):
                    print("\n[确认] 开始同步...")
                    print()
                    break
                # Esc (27), N/n (78/110)
                elif key in (b'\x1b', b'N', b'n'):
                    print("\n[取消] 用户取消操作")
                    try:
                        input("\n按任意键退出...")
                    except KeyboardInterrupt:
                        pass
                    sys.exit(0)
    except KeyboardInterrupt:
        print("\n\n[取消] 用户取消操作")
        try:
            input("\n按任意键退出...")
        except KeyboardInterrupt:
            pass
        sys.exit(0)

    try:
        # 加载云端配置
        config = load_config()
        if config is None:
            print()
            try:
                input("按任意键退出...")
            except KeyboardInterrupt:
                pass
            sys.exit(1)
        print()
        
        # 兼容旧格式配置（download_url 键）
        if "download_url" in config:
            # 旧格式：{"download_url": "https://..."}
            download_url = config["download_url"]
            print(f"[配置] 使用旧格式配置")
            print()
        else:
            # 新格式：{"source_name": ["url1", "url2"]}
            # 如果有多个 mod 源，显示选择菜单
            if len(config) > 1:
                result = show_mod_source_menu(config)
                if result is None:
                    try:
                        input("\n按任意键退出...")
                    except KeyboardInterrupt:
                        pass
                    sys.exit(0)
                
                selected_name, selected_urls = result
                download_url = selected_urls[0]  # 使用第一个 URL
            elif len(config) == 1:
                selected_name = list(config.keys())[0]
                selected_urls = list(config.values())[0]
                download_url = selected_urls[0]
                print(f"[自动] 使用唯一 mod 源: {selected_name}")
                print()
            else:
                print("[错误] 配置文件中没有可用的 mod 源")
                try:
                    input("\n按任意键退出...")
                except KeyboardInterrupt:
                    pass
                sys.exit(1)
        
        # 自动查找游戏安装路径
        print("[检查] 正在查找游戏安装路径...")
        print()
        game_path = find_game_install()

        if game_path is None:
            print()
            print("=" * 60)
            print("[错误] 未找到杀戮尖塔2游戏")
            print("=" * 60)
            print()
            print("请尝试：")
            print("  1. 将 SlayTheSpire2_Sync_MOD.exe 放到游戏目录")
            print("  2. 打开 Steam → 右键【杀戮尖塔2】→【管理】→【浏览本地文件】")
            print("  3. 将 SlayTheSpire2_Sync_MOD.exe 复制到该目录后重新运行")
            print()
            try:
                input("按任意键退出...")
            except KeyboardInterrupt:
                pass
            sys.exit(1)

        game_dir = game_path.parent
        print(f"[找到] 游戏路径: {game_dir}")
        print()

        # 备份现有mods
        print("[备份] 正在检查现有 mods 文件夹...")
        backup_path = backup_mods(game_dir)
        if backup_path:
            print(f"[备份] 原有 mods 已备份至: {backup_path}")
        else:
            print("[备份] 无需备份（mods 文件夹为空或不存在）")
        print()

        # 清理mods文件夹
        clean_mods(game_dir)
        print()

        # 下载最新mod包
        print("[同步] 正在下载最新 mod 包...")
        success = download_mods(game_dir, download_url)
        
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
            try:
                input("\n按回车键退出...")
            except KeyboardInterrupt:
                pass
            sys.exit(1)

        print()
        print("=" * 60)
        print("[成功] Mod 同步完成!")
        print("=" * 60)
        print()
        print("[提示] 请前往 Steam 启动游戏")
        try:
            input("\n按任意键退出...")
        except KeyboardInterrupt:
            pass

    except KeyboardInterrupt:
        print("\n\n[中断] 用户取消操作")
        try:
            input("\n按任意键退出...")
        except KeyboardInterrupt:
            pass
        sys.exit(0)
    except Exception as e:
        print(f"\n[错误] 发生未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        try:
            input("\n按任意键退出...")
        except KeyboardInterrupt:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()
