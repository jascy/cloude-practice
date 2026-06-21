# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 仓库概览

这是一个多功能个人工作区，包含三个主要子项目和多个辅助目录。

## 项目组件

### 1. QA 知识库系统 (`qa-knowledge-base/`)

全栈 Web 应用：Vue 3 + Element Plus 前端，Express + sql.js 后端。

```bash
cd qa-knowledge-base
npm run install:all     # 安装前后端依赖
npm run dev             # 同时启动 server(:3000) + client(:5173)
```

- **前端** (`client/`): Vite + Vue 3 + Vue Router + Element Plus + Axios，4 个视图（首页/详情/导入/管理）
- **后端** (`server/`): Express REST API，multer 文件上传，sql.js 纯 JS SQLite 存储
- **搜索引擎**: 自定义中英文混合分词（中文 bigram），多字段加权评分
- **导入**: 支持 Markdown（`#`=分类, `##`=问题）和 JSON 格式批量导入
- `.gitignore` 已排除 `node_modules/`，`dist/` 未排除（当前包含构建产物）

### 2. CNN 反向传播教学脚本 (`cnn_backprop.py`)

纯 NumPy 手写实现，含详细中文注释（849 行）：

- **层**: Conv → ReLU → MaxPool/AvgPool → Flatten → FC → Softmax+CE
- **验证**: 数值梯度检查 + 10 步训练 loss 监控
- **运行**: 需要 Python + NumPy，VS Code launch.json 已配置 Anaconda 解释器
- `python cnn_backprop.py` 或 VS Code F5 调试

### 3. 小说 Wiki (`wiki/`)

仙侠小说《青云问道》的世界设定文档，5 个 Markdown 文件：

| 文件 | 内容 |
|------|------|
| `project.md` | 项目概述、风格定位 |
| `characters.md` | 人物档案 |
| `plot.md` | 7 卷大纲 + 第一卷详细章节 |
| `world.md` | 世界观：地理、修炼体系、宗门势力 |
| `themes.md` | 核心主题 |

设计用于配合 `novel-wiki`、`novel-write`、`novel-setup` 等技能。

## Claude Code 配置 (`.claude/`)

- **Settings** (`settings.json`): 使用 DeepSeek API (`deepseek-v4-pro`)，Sandbox 已禁用
- **StatusLine**: 显示当前目录 + 模型 + 上下文剩余百分比 (`statusline.cjs`)
- **Skills**: 6 个自定义技能（WPS Office 系列 ×4, Zotero ×2）
- **定时任务**: 每个交易日上午 9:23 自动生成 A 股涨停板分析报告
- **MCP**: 已配置 Context7、Memory、Playwright、GitHub、Brave Search（见 `~/.claude/.mcp.json`）

## 环境约束

- **Shell**: Git Bash (Windows)，不要用 PowerShell 语法
- **Python**: VS Code 配置指向 `C:/ProgramData/Anaconda3/python.exe`，直接 `python` 可能因 Windows Store 重定向而失败（exit code 49），遇到时用 Anaconda 完整路径
- **Node.js**: v24.14.1，可直接使用
- **包管理**: npm，无 yarn/pnpm
- **Git**: 已配置 SSH Key 绑定 GitHub 账号 `jascy`
- **远程仓库**: `git@github.com:jascy/cloude-practice.git`，分支 `master`
- **编码**: Windows GBK 终端可能导致中文乱码，Python 脚本中需设置 `sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')`
