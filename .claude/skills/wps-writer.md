---
name: wps-writer
description: WPS Writer 文字处理 — 段落、标题、列表、表格、图片、查找替换
---

# wps-writer — WPS Writer 文字处理

通过 `cli-anything-wps` 操控 WPS 文字（Writer），完成文档正文内容的增删改查。

## 何时使用

当用户需要：
- 撰写报告、论文、公文等结构化文档
- 批量添加段落、标题、列表、表格
- 插入图片并排版
- 查找替换文本内容

## 命令详解

所有命令都在已加载项目的基础上执行：
```bash
cli-anything-wps --project <项目.json> writer <子命令> [参数]
```

### add-paragraph — 添加段落

```bash
cli-anything-wps --project doc.json writer add-paragraph \
  -t "段落文本内容" \
  [--position 0] \       # 插入位置（默认追加到末尾）
  [--font-size "12pt"] \ # 字体大小
  [--bold] \             # 粗体
  [--italic] \           # 斜体
  [--alignment left|center|right|justify]
```

### add-heading — 添加标题

```bash
cli-anything-wps --project doc.json writer add-heading \
  -t "第一章 绪论" \
  -l 1                   # 标题级别 1-6
```

### add-list — 添加列表

```bash
cli-anything-wps --project doc.json writer add-list \
  -i "第一点" -i "第二点" -i "第三点" \
  --style bullet          # bullet | number
```

### add-table — 添加表格

```bash
cli-anything-wps --project doc.json writer add-table \
  -r 5 -c 3              # 5行3列
```

### add-image — 添加图片

```bash
cli-anything-wps --project doc.json writer add-image \
  "C:\图片\chart.png" \
  -w "8cm" -h "6cm"
```

### add-page-break — 添加分页符

```bash
cli-anything-wps --project doc.json writer add-page-break
```

### 编辑操作

```bash
# 列出所有内容项
cli-anything-wps --project doc.json writer list

# 按索引删除内容
cli-anything-wps --project doc.json writer remove 3

# 修改内容文本
cli-anything-wps --project doc.json writer set-text 2 "新文本"

# 查找替换
cli-anything-wps --project doc.json writer find-replace "旧词" "新词"
```

## 完整工作流示例

```bash
# 1. 创建文档
cli-anything-wps document new --type writer --name "研究报告" -o report.json

# 2. 添加标题
cli-anything-wps --project report.json writer add-heading -t "研究报告" -l 1
cli-anything-wps --project report.json writer add-heading -t "背景介绍" -l 2

# 3. 添加正文段落
cli-anything-wps --project report.json writer add-paragraph \
  -t "本文研究了..." --font-size "14pt"

# 4. 添加列表
cli-anything-wps --project report.json writer add-list \
  -i "方法一" -i "方法二" -i "方法三" --style number

# 5. 插入表格
cli-anything-wps --project report.json writer add-table -r 4 -c 3

# 6. 导出
cli-anything-wps --project report.json export render report.docx -p docx
cli-anything-wps --project report.json export render report.pdf -p pdf
```

## 提示

- 用 `--json` 获取机器可读的 JSON 输出
- 用 `--dry-run` 预览操作而不保存
- 操作顺序即是文档内容顺序，按需使用 `--position` 控制位置

## 相关 Skills

- [[wps-office]] — 文档管理基础操作
- [[wps-calc]] — 电子表格
- [[wps-impress]] — 演示文稿
