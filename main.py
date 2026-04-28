import os
import sys


def get_base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def init_config():
    import json
    base = get_base_dir()
    config_path = os.path.join(base, "config.json")

    default = {
        "download_url": "",
        "download_method": "direct",
        "auto_launch": True,
    }

    if getattr(sys, "frozen", False):
        if not os.path.exists(config_path):
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(default, f, indent=4, ensure_ascii=False)
            print(f"[初始化] 已创建默认配置文件: {config_path}")

    return config_path


if __name__ == "__main__":
    init_config()
    from spiresync import main
    main()
