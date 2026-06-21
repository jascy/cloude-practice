---
name: zotero-academic
description: Zotero 学术研究流水线 — 27个Skill覆盖文献检索/论文写作/审稿/可视化
---

# zotero-academic — 27 个学术研究 Skill

通过 `cli-anything-zotero skills` 调用 27 个预设的学术研究流水线，覆盖从文献检索到论文发表的完整学术工作流。

## 何时使用

当用户需要：
- 系统性检索文献（快速检索、系统评价、深度搜索）
- 撰写论文（IMRAD 结构、引用、修改润色）
- 模拟审稿（5人审稿团、同行评审）
- 学术可视化（幻灯片、海报、期刊图表）
- 执行完整的论文/基金申请流水线

## 27 个 Skill 清单

### 🔍 search（检索，3个）

| 命令 | 名称 | 用途 |
|------|------|------|
| `quick` | 快速检索 | 关键词快速搜索 + 10篇摘要提取 |
| `systematic` | 系统评价 | PRISMA 流程，文献筛选 + 质量评估 |
| `deep` | 深度文献搜索 | 引文追踪 + 多数据库 + 饱和检验 |

### 📝 writing（写作，7个）

| 命令 | 名称 | 用途 |
|------|------|------|
| `imrad` | IMRAD 稿件 | 结构化论文写作（Introduction-Methods-Results-Discussion） |
| `introduction` | 引言写作 | 文献综述 + 研究空白识别 |
| `method` | 方法写作 | 实验/方法学描述 |
| `result` | 结果写作 | 数据呈现 + 图表描述 |
| `discussion` | 讨论写作 | 结果解读 + 局限分析 |
| `abstract` | 摘要写作 | 结构化摘要（300字内） |
| `citation` | 引用助手 | 自动插入引用 + 格式化 |

### 🔬 review（审稿，5个）

| 命令 | 名称 | 用途 |
|------|------|------|
| `five_person` | 5人审稿 | 5个角度独立审稿意见 |
| `peer_review` | 同行评审 | 标准学术审稿流程 |
| `citation_check` | 引用验证 | 引用准确性 + 格式一致性 |
| `method_audit` | 方法审查 | 方法论严谨性评估 |
| `ethics_scan` | 伦理扫描 | 科研伦理 + 利益冲突 |

### 📊 visualization（可视化，5个）

| 命令 | 名称 | 用途 |
|------|------|------|
| `slide_deck` | 幻灯片制作 | 学术报告幻灯片 |
| `poster` | 海报设计 | 学术会议海报 |
| `journal_figure` | 期刊图表 | 符合期刊规范的图表 |
| `graphical_abstract` | 图形摘要 | TOC/图形化摘要 |
| `data_viz` | 数据可视化 | 统计分析图表 |

### 🔬 analysis（分析，3个）

| 命令 | 名称 | 用途 |
|------|------|------|
| `gap_analysis` | 研究空白分析 | 识别研究空白和机会 |
| `trend_analysis` | 趋势分析 | 领域发展趋势 |
| `bibliometric` | 文献计量 | 引文分析 + 合著网络 |

### ⚙️ pipeline（流水线，4个）

| 命令 | 名称 | 用途 |
|------|------|------|
| `literature_review` | 文献综述流水线 | 搜索 → 筛选 → 提取 → 综合 |
| `original_article` | 原创论文流水线 | IMRAD 全流程 |
| `grant_proposal` | 基金申请流水线 | 背景 → 目标 → 方法 → 预算 |
| `thesis` | 学位论文流水线 | 章节组织 + 全面覆盖 |

---

## 使用命令

### 列出所有 Skills

```bash
# 列出全部
cli-anything-zotero skills list

# 按分类筛选
cli-anything-zotero skills list --category search
cli-anything-zotero skills list --category writing
cli-anything-zotero skills list --category review
```

### 推荐任务流水线

```bash
# 文献综述流程
cli-anything-zotero skills pipeline literature_review

# 原创论文流程
cli-anything-zotero skills pipeline original_article

# 学位论文流程
cli-anything-zotero skills pipeline thesis

# 基金申请流程
cli-anything-zotero skills pipeline grant_proposal
```

### 期刊指南

```bash
# 获取特定期刊的图表规范
cli-anything-zotero skills journal "Nature"
cli-anything-zotero skills journal "Science"
cli-anything-zotero skills journal "Cell"
```

---

## 典型使用场景

### 场景一：写一篇综述论文

```bash
# 1. 深度文献检索
cli-anything-zotero skills deep

# 2. 文献综述流水线
cli-anything-zotero skills pipeline literature_review

# 3. 写作（可依次调用）
# IMRAD → introduction → discussion → abstract → citation
```

### 场景二：准备学术会议

```bash
# 1. 摘要写作
cli-anything-zotero skills abstract

# 2. 幻灯片制作
cli-anything-zotero skills slide_deck

# 3. 海报设计
cli-anything-zotero skills poster
```

### 场景三：投稿前自查

```bash
# 1. 5人模拟审稿
cli-anything-zotero skills five_person

# 2. 引用验证
cli-anything-zotero skills citation_check

# 3. 伦理扫描
cli-anything-zotero skills ethics_scan
```

---

## Skills 桥接说明

这些 Skills 通过 `cli_anything.zotero.utils.skills_bridge` 模块实现，本质上是结构化的 prompt 模板。每个 Skill 会：
1. 构建上下文（从 Zotero 获取相关文献）
2. 生成分析 prompt
3. 输出结构化结果

大部分 Skills 是 **只读的**（读取 Zotero 数据 + AI 分析），不会修改 Zotero 数据库。

## 相关 Skills

- [[zotero-research]] — Zotero 基础操作（文献管理、引用生成）
- [[wps-impress]] — 学术幻灯片制作（配合 WPS）
