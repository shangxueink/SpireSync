# SpireSync

杀戮尖塔2 (Slay the Spire 2) Mod 同步启动器

## 简介

SpireSync 解决多人联机时 Mod 不同步的问题，让所有玩家快速同步到相同的 Mod 配置。

## 使用方法

1. 下载 [SlayTheSpire2_Sync_MOD.exe](https://github.com/shangxueink/SpireSync/releases)

2. 找到游戏安装目录：
   - 打开 Steam
   - 右键点击【杀戮尖塔2】
   - 选择【管理】→【浏览本地文件】

3. 将 `SlayTheSpire2_Sync_MOD.exe` 复制到游戏目录（与 `SlayTheSpire2.exe` 同一文件夹）

4. 双击运行 `SlayTheSpire2_Sync_MOD.exe`

5. 程序自动完成：备份旧 Mod → 下载新 Mod → 提示前往 Steam 启动游戏

## 功能特性

- ☁️ 云端配置管理
- 🌐 镜像源加速下载
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
