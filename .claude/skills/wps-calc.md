---
name: wps-calc
description: WPS Calc 电子表格 — 工作表管理、单元格读写、区域填充、合并
---

# wps-calc — WPS Calc 电子表格

通过 `cli-anything-wps` 操控 WPS 表格（Calc），完成电子表格的创建、数据填充和导出。

## 何时使用

当用户需要：
- 创建数据表格、统计报表
- 批量写入单元格数据
- 管理多个工作表
- 导出为 Excel 或 CSV

## 命令详解

```bash
cli-anything-wps --project <项目.json> calc <子命令> [参数]
```

### 工作表管理

```bash
# 添加新工作表
cli-anything-wps --project data.json calc add-sheet \
  -n "季度报表" [--position 0]

# 删除工作表（按索引）
cli-anything-wps --project data.json calc remove-sheet 1

# 重命名工作表
cli-anything-wps --project data.json calc rename-sheet 0 "年度汇总"

# 列出所有工作表
cli-anything-wps --project data.json calc list-sheets
```

### 单元格操作

```bash
# 设置单个单元格
cli-anything-wps --project data.json calc set-cell A1 "姓名" [--sheet 0]
cli-anything-wps --project data.json calc set-cell B1 "年龄" --type float
cli-anything-wps --project data.json calc set-cell C1 "=SUM(B2:B10)" --formula "=SUM(B2:B10)"

# 获取单元格值
cli-anything-wps --project data.json calc get-cell A1 [--sheet 0]

# 批量写入区域（JSON 二维数组）
cli-anything-wps --project data.json calc set-range A2 \
  -d '[["张三",28,"男"],["李四",35,"女"],["王五",42,"男"]]'

# 合并单元格
cli-anything-wps --project data.json calc merge-cells A1 C1
```

## 完整工作流示例

```bash
# 1. 创建电子表格
cli-anything-wps document new --type calc --name "销售报表" -o sales.json

# 2. 写入表头
cli-anything-wps --project sales.json calc set-cell A1 "月份"
cli-anything-wps --project sales.json calc set-cell B1 "销售额(万)"
cli-anything-wps --project sales.json calc set-cell C1 "增长率"
cli-anything-wps --project sales.json calc set-cell D1 "备注"

# 3. 批量填充数据
cli-anything-wps --project sales.json calc set-range A2 \
  -d '[["1月",120,"-",""],
       ["2月",145,"+20.8%","春节旺季"],
       ["3月",132,"-9.0%","节后回落"],
       ["4月",158,"+19.7%","新品上市"]]'

# 4. 重命名工作表
cli-anything-wps --project sales.json calc rename-sheet 0 "Q1销售"

# 5. 导出
cli-anything-wps --project sales.json export render sales.xlsx -p xlsx
cli-anything-wps --project sales.json export render sales.csv -p csv
```

## 数据类型

`--type` 支持：
- `string`（默认）— 文本
- `float` — 数字

公式使用 `--formula` 单独指定，支持标准 Excel 公式语法。

## 相关 Skills

- [[wps-office]] — 文档管理基础操作
- [[wps-writer]] — 文字处理
- [[wps-impress]] — 演示文稿
