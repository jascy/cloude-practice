---
name: wps-impress
description: WPS Impress 演示文稿 + PPT 设计系统 — 幻灯片增删、4套预设×14种布局、一键美化
---

# wps-impress — WPS Impress 演示文稿

通过 `cli-anything-wps` 操控 WPS 演示（Impress），内置 4 套设计预设、14 种布局模板、4 种演讲类型预设和 5 维度质量审查。

## 何时使用

当用户需要：
- 创建 PPT 演示文稿（学术答辩、商务汇报、产品发布等）
- 一键应用设计风格和布局模板
- 批量生成结构化幻灯片
- 导出 PPTX + PDF 双格式

## 快速流程

```
1. 创建演示文稿 → 2. 应用设计预设 → 3. 逐页生成 → 4. 导出
```

---

## 一、设计预设（Design Presets）

通过 `preset apply <名称>` 一键切换。**在创建 PPT 前先调用此命令。**

### 4 套预设概览

| 预设名 | 风格 | 配色 | 适用场景 |
|--------|------|------|---------|
| `academic` | 学术答辩 | 深蓝#1A3C8B / 橙#E67733 / 绿#188050 | 学术会议、论文答辩、基金申请 |
| `consultant` | 咨询顾问 | 深蓝#003366 / 亮青#00A8E8 / 橙#FF8C00 | 商业计划书、咨询报告、年度汇报 |
| `business` | 商务汇报 | 商务蓝#005294 / 强调红#C82828 / 绿#2DA050 | 会议汇报、项目提案、教学课件 |
| `tech` | 科技极简 | 近黑#0F1423 / 亮青#00C8FF / 橙红#FF643C | 科技产品发布、AI/技术演示、数据报告 |

```bash
# 列出所有预设
cli-anything-wps preset list

# 查看预设详情
cli-anything-wps preset info academic

# 应用预设（可指定演讲类型）
cli-anything-wps preset apply academic --talk-type defense
```

---

## 二、布局模板（14 种）

| 模板 | 分类 | 用途 | 关键元素 |
|------|------|------|---------|
| cover | 封面 | 开场标题页 | 72pt大字 + 装饰线 + 副标题 |
| toc | 目录 | 内容导航 | 蓝色竖线 + 圆角方块编号 |
| overview | 概览 | 信息总览 | 深色横幅 + 2x4卡片 |
| timeline | 时间轴 | 历史/发展 | 圆点+竖线 + 日期+事件 |
| grid_cards | 卡片网格 | 人物/地标/产品 | 4x2网格 + 头像 |
| quadrant | 四象限 | 对比/分类 | 2x2布局 + 彩色标题块 |
| stats | 数字统计 | 数据展示 | 6大数字 + 底部说明 |
| three_col | 三列对比 | 三种方案对比 | 深色全屏 + 三列并排 |
| pipeline | 流程图 | 管道/流程 | 6个彩色模块 + 连接箭头 |
| data_table | 数据表格 | 排名/指标 | 左表格 + 右解读区 |
| content_image | 图文 | 图文并茂 | 左文右图 / 左图右文 |
| closing | 结语 | 收尾页 | 深色全屏 + 总结 + 联系方式 |

---

## 三、演讲类型预设

### conference（学术会议，12-20页）
cover → toc → overview → timeline → quadrant → grid_cards → stats → pipeline → data_table → content_image → quadrant → timeline → stats → closing

### business（商务汇报，8-15页）
cover → toc → overview → stats → three_col → pipeline → grid_cards → data_table → closing

### defense（论文答辩，45-65页）
cover → toc → overview → timeline → quadrant → content_image → pipeline → data_table → stats → quadrant → timeline → stats → closing

### school（学校介绍，14页）
cover → toc → overview → timeline → three_col → grid_cards → quadrant → stats → closing

---

## 四、幻灯片操作命令

```bash
# 添加幻灯片
cli-anything-wps --project ppt.json impress add-slide \
  -t "标题" -c "内容文本" [--position 0]

# 删除幻灯片
cli-anything-wps --project ppt.json impress remove-slide 2

# 更新幻灯片内容
cli-anything-wps --project ppt.json impress set-content 0 \
  -t "新标题" -c "新内容"

# 列出所有幻灯片
cli-anything-wps --project ppt.json impress list-slides

# 向幻灯片添加元素（文本框等）
cli-anything-wps --project ppt.json impress add-element 0 \
  --type text_box -t "元素文本" \
  --x "3cm" --y "5cm" -w "15cm" -h "4cm"
```

---

## 五、完整 Agent 做 PPT 标准流程

```bash
# 步骤 1：创建文档并应用预设
cli-anything-wps document new --type impress --name "论文答辩" -o defense.json
cli-anything-wps --project defense.json preset apply academic --talk-type defense

# 步骤 2：按演讲类型序列逐页生成
# 封面页 (cover)
cli-anything-wps --project defense.json impress add-slide \
  -t "基于深度学习的图像识别研究" -c "答辩人：XXX | 导师：XXX"

# 目录页 (toc)
cli-anything-wps --project defense.json impress add-slide \
  -t "目录" -c "1. 研究背景\n2. 相关工作\n3. 方法设计\n4. 实验结果\n5. 总结展望"

# 概览页 (overview)
cli-anything-wps --project defense.json impress add-slide \
  -t "研究概览" -c "研究问题 → 方法创新 → 实验验证 → 结论"

# ... 按序列继续生成各页 ...

# 结语页 (closing)
cli-anything-wps --project defense.json impress add-slide \
  -t "感谢聆听" -c "联系方式：xxx@example.com"

# 步骤 3：导出双格式
cli-anything-wps --project defense.json export render defense.pptx -p pptx
cli-anything-wps --project defense.json export render defense.pdf -p pdf-impress
```

---

## 六、质量审查标准（5 维度）

| 维度 | 检查项 | 阈值 |
|------|--------|------|
| visual（视觉） | 字体层级、颜色对比度、留白比例、布局一致性 | 70分 |
| pedagogy（教学法） | 叙事弧完整性、预备知识、示例、符号一致性 | 75分 |
| proofreading（校对） | 拼写、语法、术语、标点、字体溢出 | 80分 |
| parity（格式一致） | PPTX/PDF一致、字体嵌入、图片兼容 | 85分 |
| substance（内容实质） | 数据准确性、引用完整、结论支撑 | 90分 |

## 相关 Skills

- [[wps-office]] — 文档管理基础操作
- [[wps-writer]] — 文字处理
- [[wps-calc]] — 电子表格
