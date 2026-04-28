"""
SpireSync - 杀戮尖塔2 Mod 同步启动器
主入口文件
"""
import os
import sys
from pathlib import Path


def get_base_dir() -> Path:
    """获取程序基础目录"""
    if getattr(sys, "frozen", False):
        # 打包后的exe运行时
        return Path(os.path.dirname(sys.executable))
    # 开发环境
    return Path(__file__).parent.parent


def init_local_config():
    """初始化本地配置文件（仅作为备用）"""
    import json
    
    base = get_base_dir()
    config_path = base / "config.json"

    default = {
        "download_url": "https://github.com/shangxueink/SpireSync/releases/download/2026-4-28/mods.zip"
    }

    # 仅在打包后且配置文件不存在时创建
    if getattr(sys, "frozen", False):
        if not config_path.exists():
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(default, f, indent=4, ensure_ascii=False)
            print(f"[初始化] 已创建本地配置文件: {config_path}")
            print("[提示] 程序将优先使用云端配置，本地配置仅作备用")

    return config_path


if __name__ == "__main__":
    # 设置控制台编码为UTF-8
    if sys.platform == "win32":
        try:
            import locale
            if locale.getpreferredencoding().upper() != 'UTF-8':
                os.system('chcp 65001 >nul 2>&1')
        except:
            pass
    
    # 初始化本地配置
    init_local_config()
    
    # 导入并运行主程序
    from spiresync import main
    main()
