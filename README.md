# A2E Bilibili Video

[English](README.en.md) | [简体中文](README.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Codex Skill](https://img.shields.io/badge/Codex-Skill-000000)](https://openai.com/codex)
[![Remotion](https://img.shields.io/badge/Remotion-4.x-0B84F3)](https://www.remotion.dev/)
[![Edge TTS](https://img.shields.io/badge/TTS-Edge%20TTS-0078D4)](https://github.com/rany2/edge-tts)
[![Bilibili](https://img.shields.io/badge/Publish-Bilibili-00A1D6)](https://www.bilibili.com/)

给一个主题、文章或文档，生成原创的代码动画讲解视频；制作配套的
16:9 与 4:3 双封面；验证后发布到 B 站。

这是一个**编排型 skill**，连接三个已有项目，而不是替代它们：

- [anything2explainer](https://github.com/Vincentwei1021/anything2explainer)
  提供制作流程、Remotion 模板与视觉规范。
- [ppt-master](https://github.com/hugohe3/ppt-master) 提供封面设计流程与
  可编辑 PPTX 输出。
- [bilibili-ai-skills](https://github.com/sukai213/bilibili-ai-skills)
  提供 B 站发布与验证流程。

本仓库只包含集成层、可移植脚本、校验器和文档，不重新分发上游源码、
凭据、成片或机器专属路径。

## 功能

| 阶段 | 产出 |
|---|---|
| 调研与文案 | 带来源的调研文档、解说词、分镜和镜头计划 |
| 配音 | 由 Agent 选择音色的 Edge TTS 配音 |
| 动效视频 | 使用 Remotion 渲染的 1920×1080 成片 |
| 质检 | 静态检查、运动检查、帧指标和视觉审查 |
| 封面 | PPT Master 生成的独立 1920×1080 与 1440×1080 封面 |
| 发布 | CDP 登录态、双封面上传、`add/v3` 和发布后验证 |

## 环境要求

### 必需软件

- Node.js 18 或更高版本，以及 `npx`
- Python 3.10 或更高版本
- `ffmpeg` 和 `ffprobe`
- Git
- 支持 skill 的 Codex

### 必需的上游 Skill

需要单独安装：

1. [anything2explainer](https://github.com/Vincentwei1021/anything2explainer)
2. [bilibili-ai-skills](https://github.com/sukai213/bilibili-ai-skills)
3. [ppt-master](https://github.com/hugohe3/ppt-master)

### 平台说明

- 当前 B 站发布流程主要面向 macOS，因为它通过 CDP 使用已登录的 B 站
  桌面客户端。
- Remotion 渲染和 PPT Master 封面生成在依赖满足时可用于其他平台。
- 本 skill 不使用 PowerPoint 的原生视频导出，最终视频由 Remotion 渲染。

## 安装说明

请按使用方式选择“人类安装”或“Agent 安装”。

### 人类安装

#### 1. 安装基础工具

macOS：

```bash
brew install node ffmpeg
```

Ubuntu / Debian：

```bash
sudo apt update
sudo apt install nodejs npm ffmpeg
```

检查：

```bash
node --version
npx --version
ffmpeg -version
ffprobe -version
python3 --version
```

#### 2. 安装三个上游 Skill

安装 `anything2explainer`：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
git clone https://github.com/Vincentwei1021/anything2explainer.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/anything2explainer"
```

安装 B 站 skill：

```bash
git clone https://github.com/sukai213/bilibili-ai-skills.git /tmp/bilibili-ai-skills
cp -R /tmp/bilibili-ai-skills/skills/bilibili-ai-video \
  "${CODEX_HOME:-$HOME/.codex}/skills/bilibili-ai-video"
```

安装 PPT Master：

```bash
git clone https://github.com/hugohe3/ppt-master.git "$HOME/ppt-master"
```

如果安装到其他位置，请设置 `A2E_SKILL_DIR`、`BILIBILI_SKILL_DIR` 和
`PPT_MASTER_DIR`。脚本不假定用户名或固定主目录。

#### 3. 安装本 Skill

```bash
git clone https://github.com/Lucas-Qh-Lai/a2e-bilibili-video.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/a2e-bilibili-video"
```

#### 4. 安装 Python 依赖

使用项目内虚拟环境：

```bash
cd "${CODEX_HOME:-$HOME/.codex}/skills/a2e-bilibili-video"
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r scripts/requirements.txt
```

PPT Master 可能有独立依赖，请遵循它的安装文档，不要全局安装本项目依赖。

#### 5. 验证安装

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export A2E_SKILL_DIR="$CODEX_HOME/skills/anything2explainer"
export BILIBILI_SKILL_DIR="$CODEX_HOME/skills/bilibili-ai-video"
export PPT_MASTER_DIR="$HOME/ppt-master/skills/ppt-master"

python3 scripts/check_dependencies.py
```

必需项目都应显示 `OK`。安装完成后重启 Codex，使新 skill 进入索引。

### Agent 安装

Agent 应按以下顺序确定性执行：

1. 检测操作系统，确认 `git`、`node`、`npx`、`ffmpeg`、`ffprobe` 和
   Python 可用。
2. 从环境读取 `CODEX_HOME`，缺省为 `$HOME/.codex`。
3. 将 `anything2explainer` 克隆或更新到
   `$CODEX_HOME/skills/anything2explainer`。
4. 克隆或更新 `bilibili-ai-skills`，只把
   `skills/bilibili-ai-video` 安装到
   `$CODEX_HOME/skills/bilibili-ai-video`。
5. 除非用户指定其他位置，否则将 `ppt-master` 安装到
   `$HOME/ppt-master`。
6. 将本仓库安装到 `$CODEX_HOME/skills/a2e-bilibili-video`。
7. 创建项目内 Python 虚拟环境并安装 `scripts/requirements.txt`。
8. 为当前命令设置 `A2E_SKILL_DIR`、`BILIBILI_SKILL_DIR` 和
   `PPT_MASTER_DIR`。
9. 运行 `scripts/check_dependencies.py`，逐项报告问题。
10. 不得复制、打印或提交 Cookie、Token、API Key 或本地账号数据。

除非用户明确要求，不要修改用户已有的本地 skill。

## 快速开始

设置依赖目录：

```bash
export CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
export A2E_SKILL_DIR="$CODEX_HOME/skills/anything2explainer"
export BILIBILI_SKILL_DIR="$CODEX_HOME/skills/bilibili-ai-video"
export PPT_MASTER_DIR="$HOME/ppt-master/skills/ppt-master"
export SKILL_DIR="$CODEX_HOME/skills/a2e-bilibili-video"
```

向 Codex 描述任务：

```text
使用 a2e-bilibili-video，把这个主题做成一条 4 分钟中文讲解视频，
制作 B 站双封面，展示最终 metadata 等我确认后发布。
```

skill 会沿用 A2E 工作流，选择 Edge 音色，生成双封面，验证交付物，
等待确认，然后同时提交两个封面。

## 输出约定

```text
renders/<slug>_bilibili_v1.mp4
delivery/bilibili/<slug>_delivery.json
covers/<slug>_cover_16x9.png
covers/<slug>_cover_4x3.png
covers/<slug>_cover_16x9.svg
covers/<slug>_cover_4x3.svg
delivery/bilibili/publish_result.json
```

最终视频为 1920×1080、30fps、H.264、AAC 44.1kHz。A2E 的
1280×720 是设计坐标和质检基准，不是交付分辨率。

## 目录结构

```text
.
├── SKILL.md
├── agents/openai.yaml
├── assets/publish.example.json
├── docs/architecture.md
├── references/bilibili-publish.md
├── references/ppt-master-covers.md
├── scripts/check_dependencies.py
├── scripts/publish_bilibili_dual_cover.py
├── scripts/render_bilibili.py
├── scripts/render_svg_cover.py
├── scripts/validate_publish_assets.py
└── scripts/requirements.txt
```

## 隐私与安全

- 本仓库不保存任何凭据。
- Cookie JSON 必须临时、保存在版本控制之外。
- `.gitignore` 排除 `.env`、Cookie、密钥、生成媒体和项目工作区。
- 报告与 Issue 模板不得索取秘密信息。
- 调用 `add/v3` 前必须获得一次明确的人工发布确认。

详见 [SECURITY.md](SECURITY.md)。

## 限制

- B 站上传依赖外部 skill 与 B 站 API。
- macOS CDP 流程依赖官方 B 站桌面客户端。
- 最终视频由 Remotion 渲染，不使用 PPT Master 的 PowerPoint 视频导出。
- 三个上游项目遵循各自许可证，必须单独安装。
- 生成的视频与封面属于用户产物，不随本仓库分发。

## 参与贡献

提交 Pull Request 前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 致谢

### 上游项目

本项目依赖并感谢：

1. [anything2explainer](https://github.com/Vincentwei1021/anything2explainer)
   提供制作流程、Remotion 模板、动效语言和 QC 体系。
2. [ppt-master](https://github.com/hugohe3/ppt-master) 提供演示文稿和封面
   设计流程。
3. [bilibili-ai-skills](https://github.com/sukai213/bilibili-ai-skills)
   提供 B 站发布与验证流程。

原作者保留其作品的全部权利。

### 共同创作者

- **OpenAI Codex**
- **DeepSeek V4.1 Flash**

本集成层由两个系统参与的 Agent 协作流程开发完成。

## 许可证

本仓库的集成层采用 [MIT License](LICENSE)。上游项目遵循各自的许可证。

## 路线图

- 跨平台 B 站 Cookie 提取
- 更多封面模板与版式预设
- 可选字幕导出
- 更多发布校验器
- 更多平台适配器

