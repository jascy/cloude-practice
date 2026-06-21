---
name: wps-office
description: WPS Office 文档管理 — 创建、打开、保存、导出 WPS 文字/表格/演示文稿
---

# wps-office — WPS Office 文档管理

通过 COM 自动化接口操控 WPS Office 的命令行工具。支持 WPS 文字（Writer）、WPS 表格（Calc）和 WPS 演示（Impress）。

## 前置条件

- Windows 操作系统，WPS Office 2019+ 已安装
- `cli-anything-wps` 已安装：`pip install git+https://github.com/yb2460/harness-anything.git`
- `pywin32` 已安装：`pip install pywin32`

## 何时使用

当用户需要：
- 创建或编辑 Word 文档（.docx）
- 创建或编辑 Excel 电子表格（.xlsx）
- 创建或编辑 PPT 演示文稿（.pptx）
- 导出文档为 PDF 等格式

## 命令体系

```
cli-anything-wps [--json] [--project <json文件>]
├── document          # 文档管理
│   ├── new           # 创建新文档 (--type writer|calc|impress, --name, -o)
│   ├── open          # 打开项目 JSON 文件
│   ├── save          # 保存文档
│   ├── info          # 文档信息
│   ├── profiles      # 页面配置列表
│   └── json          # 打印原始 JSON
├── writer            # WPS 文字（详见 /wps-writer）
├── calc              # WPS 表格（详见 /wps-calc）
├── impress           # WPS 演示（详见 /wps-impress）
├── style             # 样式管理
│   ├── create        # 创建样式 (--family paragraph|text, --prop key=value)
│   ├── modify        # 修改样式
│   ├── list          # 列出样式
│   ├── apply         # 应用样式到内容项
│   └── remove        # 删除样式
├── preset            # PPT 设计预设（详见 /wps-impress）
├── export            # 导出
│   ├── presets       # 列出导出预设
│   ├── preset-info   # 预设详情
│   └── render        # 导出到文件 (-p docx|xlsx|pptx|pdf|...)
└── session           # 会话管理
    ├── status/undo/redo/history
```

## 使用示例

### 创建并导出文档

```bash
# 创建新文档
cli-anything-wps document new --type writer --name "报告" -o report.json

# 添加内容后导出为 DOCX
cli-anything-wps --project report.json export render report.docx -p docx

# 导出为 PDF
cli-anything-wps --project report.json export render report.pdf -p pdf
```

### 使用电子表格

```bash
cli-anything-wps document new --type calc --name "数据" -o data.json
cli-anything-wps --project data.json calc set-cell A1 "姓名"
cli-anything-wps --project data.json calc set-cell B1 "年龄"
cli-anything-wps --project data.json calc set-range A2 -d '[["张三",28],["李四",35]]'
cli-anything-wps --project data.json export render data.xlsx -p xlsx
```

## 导出预设

| 预设 | 说明 | 适用类型 |
|------|------|---------|
| docx | Word 文档 | writer |
| pdf | PDF（从 Writer） | writer |
| txt | 纯文本 | writer |
| html | 网页 | writer |
| xlsx | Excel 工作簿 | calc |
| csv | CSV | calc |
| pptx | PowerPoint | impress |
| pdf-impress | PDF（从 Impress） | impress |

## Agent 使用指南

1. **所有命令支持 `--json`** — 返回结构化 JSON
2. **使用 `--project` 链式执行** — 加载项目后连续操作
3. **`--dry-run`** — 预览不保存
4. **REPL 交互模式** — 直接运行 `cli-anything-wps` 进入

## 相关 Skills

- [[wps-writer]] — WPS 文字处理
- [[wps-calc]] — WPS 电子表格
- [[wps-impress]] — WPS 演示文稿 + PPT 设计系统
