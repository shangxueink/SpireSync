# SpireSync

杀戮尖塔2 (Slay the Spire 2) Mod 同步启动器

## 简介

SpireSync 解决多人联机时 Mod 不同步的问题，让所有玩家快速同步到相同的 Mod 配置。

## 使用方法

1. 下载 [SlayTheSpire2_Sync_MOD.exe](https://github.com/shangxueink/SpireSync/releases)

2. 双击运行 `SlayTheSpire2_Sync_MOD.exe`

3. 程序自动完成：
   - 🔍 自动检测游戏安装路径（支持多个 Steam 库）
   - 💾 备份现有 Mod
   - ⬇️ 下载最新 Mod 包
   - ✅ 提示前往 Steam 启动游戏

**注意**：程序会自动从 Steam 注册表和库文件中查找游戏。如果检测失败，可以将 EXE 放到游戏目录手动运行。

## 功能特性

- 🔍 自动检测游戏路径（Steam 注册表 + 多库支持）
- ☁️ 云端配置管理
- 🌐 镜像源加速下载（支持国内访问）
- 💾 自动备份现有 Mod
- 🚀 一键同步启动

## 发布新 Mod 包

1. 前往游戏目录 打包 mods文件夹 为 `mods.zip`
2. 上传到 [GitHub Release](https://github.com/shangxueink/SpireSync/releases)
3. 更新 [`config.json`](config.json) 的 `download_url`
4. 推送到 GitHub

用户下次运行时自动获取更新。

## 构建

```bash
# 安装 uv
pip install uv

# 安装依赖
uv pip install -r requirements.txt

# 构建
build.bat
```

## 许可证

本项目（SpireSync 同步工具）采用 MIT License - 详见 [LICENSE](LICENSE)

## 重要说明

本工具仅提供 Mod 同步功能，所分发的 Mod 内容版权归各 Mod 原作者所有。

使用本工具下载和使用的 Mod 需遵循各 Mod 原作者的许可协议。
