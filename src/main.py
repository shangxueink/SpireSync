"""
SpireSync - 杀戮尖塔2 Mod 同步启动器
主入口文件
"""
import os
import sys


if __name__ == "__main__":
    # 设置控制台编码为UTF-8
    if sys.platform == "win32":
        try:
            import locale
            if locale.getpreferredencoding().upper() != 'UTF-8':
                os.system('chcp 65001 >nul 2>&1')
        except:
            pass
    
    # 导入并运行主程序
    from spiresync import main
    main()
