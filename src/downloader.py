"""
下载和镜像源管理模块
"""
import tempfile
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen


# 镜像源列表（按优先级排序）
MIRROR_SOURCES = [
    "https://edgeone.gh-proxy.com",
    "https://hk.gh-proxy.com",
    "https://gh-proxy.com",
    "https://gh.llkk.cc",
]

# 远程配置文件 URL
REMOTE_CONFIG_URL = "https://github.com/shangxueink/SpireSync/blob/main/config.json"


def try_fetch_url(url: str, timeout: int = 10) -> tuple[bool, str]:
    """尝试访问URL并返回内容"""
    try:
        req = Request(url, headers={"User-Agent": "SpireSync/1.0"})
        with urlopen(req, timeout=timeout) as response:
            return True, response.read().decode("utf-8")
    except Exception as e:
        return False, str(e)


def fetch_remote_config() -> dict | None:
    """从云端获取配置文件"""
    import json
    
    # 将 GitHub blob URL 转换为 raw URL
    raw_url = REMOTE_CONFIG_URL.replace("/blob/", "/raw/")
    print(f"[地址] {raw_url}")
    
    # 尝试所有镜像源
    for idx, mirror in enumerate(MIRROR_SOURCES, 1):
        mirror_url = f"{mirror}/{raw_url}"
        print(f"[尝试] 使用镜像源 {idx}/{len(MIRROR_SOURCES)}")
        
        success, content = try_fetch_url(mirror_url, timeout=10)
        if success:
            try:
                config = json.loads(content)
                return config
            except json.JSONDecodeError:
                continue
    
    print("[失败] 所有镜像源均无法访问")
    return None


def apply_mirror_to_url(url: str) -> list:
    """为 URL 应用所有镜像源，返回镜像 URL 列表"""
    # 如果不是 GitHub URL，直接返回原 URL
    if "github.com" not in url:
        return [url]
    
    # 返回所有镜像源URL
    mirror_urls = []
    for mirror in MIRROR_SOURCES:
        mirror_urls.append(f"{mirror}/{url}")
    
    return mirror_urls


def download_file_with_progress(url: str, dest_path: Path, timeout: int = 180) -> bool:
    """下载文件并显示进度条"""
    try:
        req = Request(url, headers={"User-Agent": "SpireSync/1.0"})
        with urlopen(req, timeout=timeout) as resp:
            total_size = resp.headers.get("Content-Length")
            if total_size:
                total_size = int(total_size)
            else:
                total_size = 0
            
            downloaded = 0
            with open(dest_path, "wb") as f:
                while True:
                    chunk = resp.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    # 显示进度条
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        bar_length = 40
                        filled = int(bar_length * downloaded / total_size)
                        bar = '█' * filled + '░' * (bar_length - filled)
                        print(f"\r[进度] {bar} {progress:.1f}% ({downloaded / 1024 / 1024:.2f} MB)", end="")
        
        print()  # 换行
        return True
    except Exception as e:
        print(f"\n[错误] {e}")
        return False


def download_mods(game_dir: Path, download_url: str) -> bool:
    """下载并解压mod包，尝试所有镜像源"""
    if not download_url:
        print("[错误] 未配置下载地址")
        return False

    mods_dir = game_dir / "mods"
    
    # 获取所有镜像源URL
    mirror_urls = apply_mirror_to_url(download_url)
    print(f"[下载] 正在下载 mod 包...")
    print(f"[地址] {download_url}")
    
    tmp_file = tempfile.mktemp(suffix=".zip")
    
    # 尝试每个镜像源
    for idx, mirror_url in enumerate(mirror_urls, 1):
        print(f"[尝试] 使用镜像源 {idx}/{len(mirror_urls)}")
        
        if "[大小]" not in locals():
            # 获取文件大小
            try:
                req = Request(mirror_url, headers={"User-Agent": "SpireSync/1.0"})
                with urlopen(req, timeout=10) as resp:
                    size = resp.headers.get("Content-Length")
                    if size:
                        print(f"[大小] {int(size) / 1024 / 1024:.2f} MB")
            except:
                pass
        
        # 下载文件
        if download_file_with_progress(mirror_url, Path(tmp_file)):
            # 解压
            try:
                print(f"[解压] 正在解压...")
                with zipfile.ZipFile(tmp_file, "r") as zf:
                    # 检查是否有嵌套的 mods 文件夹
                    file_list = zf.namelist()
                    
                    if file_list and all(f.startswith('mods/') for f in file_list if not f.endswith('/')):
                        print(f"[检测] ZIP 包含 mods 文件夹，自动处理...")
                        # 提取时去掉 mods/ 前缀
                        for file_info in zf.infolist():
                            if file_info.filename.startswith('mods/'):
                                # 去掉前缀
                                file_info.filename = file_info.filename[5:]
                                if file_info.filename:  # 跳过空文件名
                                    try:
                                        zf.extract(file_info, mods_dir)
                                    except:
                                        pass
                    else:
                        # 直接解压
                        zf.extractall(mods_dir)
                
                print(f"[完成] mod 文件已放置到 {mods_dir}")
                
                # 清理临时文件
                try:
                    Path(tmp_file).unlink()
                except:
                    pass
                
                return True
            except Exception as e:
                print(f"[错误] 解压失败: {e}")
                continue
    
    # 所有镜像源都失败
    print("[失败] 所有镜像源下载均失败")
    try:
        Path(tmp_file).unlink()
    except:
        pass
    
    return False
