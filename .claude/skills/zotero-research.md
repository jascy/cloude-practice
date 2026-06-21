---
name: zotero-research
description: Zotero 学术研究 — 文献管理、检索、引用、笔记、导入导出
---

# zotero-research — Zotero 学术文献管理

通过 `cli-anything-zotero` 操控 Zotero，支持文献检索、分类管理、引用生成、笔记和导入导出。

## 前置条件

- Zotero 7+ 已安装
- `cli-anything-wps` 已安装（包含 zotero 模块）
- Zotero 运行时需开启 Local API（`app enable-local-api`）

## 何时使用

当用户需要：
- 检索、浏览 Zotero 文献库
- 管理文献分类和标签
- 生成引用和参考文献
- 导入文献文件（BibTeX、RIS、JSON 等）
- 分析和问答文献内容
- 执行学术研究流水线

---

## 命令体系

```
cli-anything-zotero [--json] [--backend auto|sqlite|api]
├── app               # 应用管理
│   ├── status/version/launch/ping
│   └── enable-local-api
├── collection        # 分类管理
│   ├── list          # 列出所有分类
│   ├── find <query>  # 搜索分类 (--limit 20)
│   ├── tree          # 分类树
│   ├── get [ref]     # 分类详情
│   ├── items [ref]   # 分类中的文献
│   ├── use-selected  # 使用 Zotero 中当前选中的分类
│   └── create <name> # 创建分类 (--experimental, --parent)
├── item              # 文献操作
│   ├── list          # 列出文献 (--limit 20)
│   ├── find <query>  # 搜索文献 (--collection, --exact-title)
│   ├── get [ref]     # 文献详情
│   ├── children      # 子条目
│   ├── notes         # 文献笔记
│   ├── attachments   # 附件列表
│   ├── file          # 附件文件路径
│   ├── export        # 导出文献 (--format bibtex|ris|csljson|...)
│   ├── citation      # 生成引用 (--style, --locale)
│   ├── bibliography  # 生成参考文献 (--style, --locale)
│   ├── context       # 文献上下文（供 AI 分析）
│   ├── analyze       # 问答分析 (--question, --model)
│   ├── add-to-collection    # 添加到分类 (--experimental)
│   └── move-to-collection   # 移动到分类 (--experimental)
├── search            # 保存的搜索
│   ├── list/get/items
├── tag               # 标签管理
│   ├── list/items
├── style             # CSL 引用样式
│   └── list          # 列出已安装样式
├── import            # 导入
│   ├── file <path>   # 导入文献文件 (--collection, --tag)
│   └── json <path>   # 导入 JSON 文献 (--collection, --tag)
├── note              # 笔记管理
│   ├── get <ref>     # 获取笔记内容
│   └── add <ref>     # 添加笔记 (--text, --file, --format text|markdown|html)
├── session           # 会话管理
│   ├── status/history
│   └── use-library|use-collection|use-item
└── skills            # 27 个学术研究 Skill（详见 /zotero-academic）
    ├── list          # 列出所有 Skill
    ├── pipeline      # 推荐任务流水线
    └── journal       # 期刊格式指南
```

---

## 常用工作流

### 1. 查找并阅读文献

```bash
# 搜索文献
cli-anything-zotero item find "deep learning image recognition" --limit 10

# 获取文献完整上下文（供 AI 分析）
cli-anything-zotero item context ABC123 --include-notes --include-bibtex

# 对文献提问
cli-anything-zotero item analyze ABC123 \
  --question "这篇论文的创新点是什么？" \
  --model "claude-sonnet-4-6"
```

### 2. 生成引用和参考文献

```bash
# 生成单条引用
cli-anything-zotero item citation ABC123 --style "apa"

# 生成参考文献列表
cli-anything-zotero item bibliography ABC123 --style "chinese-gb7714-2005-numeric"

# 导出为 BibTeX
cli-anything-zotero item export ABC123 --format bibtex
```

### 3. 管理文献分类

```bash
# 查看分类树
cli-anything-zotero collection tree

# 同步 Zotero 当前选中的分类
cli-anything-zotero collection use-selected

# 查看分类中的文献
cli-anything-zotero collection items
```

### 4. 导入文献

```bash
# 导入 BibTeX 文件
cli-anything-zotero import file ~/Downloads/references.bib --collection "论文参考文献"

# 导入带标签
cli-anything-zotero import file paper.pdf --tag "重要" --tag "AI"
```

### 5. 文献笔记

```bash
# 查看笔记
cli-anything-zotero note get NOTE123

# 添加 Markdown 笔记
cli-anything-zotero note add ITEM123 \
  --text "## 关键发现\n\n1. 该方法优于 baseline 15%\n2. 数据集规模较小" \
  --format markdown
```

---

## 后端模式

| 模式 | 说明 |
|------|------|
| `auto`（默认） | 自动选择可用后端 |
| `sqlite` | 直接读取 zotero.sqlite（快速只读） |
| `api` | 通过 Zotero Local API（需要 Zotero 运行中） |

实验性写操作（create、add-to-collection、move-to-collection）需要 `--experimental` 标志。

## 相关 Skills

- [[zotero-academic]] — 27 个学术研究流水线 Skill
- [[wps-writer]] — 导出后可用 WPS 进行排版
