# 公司画像 Ontology 计划（工程映射总说明）

_生成时间：2026-07-10 07:26 UTC_

## 来源

- 老师文档：`/Users/zhao/Downloads/上市公司完整属性体系_覆盖标红版.docx`
- 本文件为 **目标 ontology**；A/B/C/D 为 **填数管道**

## 三层模型

| 层 | 本阶段 | 说明 |
|----|--------|------|
| 证据层 | 只建指针 | `outputs/harvest|validation|snapshot` 只读引用 |
| 事实层 | schema + 试点 | `outputs/portrait/companies/<code>/facts.jsonl` |
| 画像层 | 延后 | M18 仅占位 |

## field_id 规范

```text
<module_id>.<subgroup>.<field_slug>
```

- 只增不改；改名走 `alias_of`
- 与现有 catalog 用 `existing_field_ref` 对账，不重造字段

## 标红抽取说明

- docx run 颜色解析：命中红色字段 **0** 条
- **解析结果：无可靠标红元数据**（`teacher_coverage_mark=plain/unknown`）；按模块 `fill_priority` 人工标 P0/P1/defer

## 18 模块映射

| 模块 | 名称 | 主轨道 | 优先级 | 子模块数 | 字段数 |
|------|------|--------|--------|----------|--------|
| M01 | 公司身份与基础档案 | C | P0 | 4 | 59 |
| M02 | 业务与商业模式 | none | defer | 5 | 62 |
| M03 | 行业与竞争格局 | C | P2 | 3 | 33 |
| M04 | 财务与经营表现 | A | P1 | 6 | 71 |
| M05 | 研发、技术与知识产权 | none | defer | 3 | 30 |
| M06 | 组织、人力与集团结构 | none | defer | 3 | 35 |
| M07 | 股权、股东与控制权 | C | P0 | 4 | 48 |
| M08 | 治理结构与管理层 | C | P1 | 3 | 41 |
| M09 | 资本运作与分红融资 | C | P1 | 3 | 41 |
| M10 | 客户、供应商与合同订单 | none | defer | 3 | 30 |
| M11 | 资产、产能与项目建设 | none | defer | 3 | 34 |
| M12 | 风险、合规与争议 | B | defer | 5 | 45 |
| M13 | 公告事件与时间线 | B | P1 | 5 | 46 |
| M14 | 市场表现与交易行为 | D | P1 | 3 | 30 |
| M15 | 投资者关系与外部沟通 | none | defer | 3 | 20 |
| M16 | 文档证据与知识库 | multi | P0 | 3 | 30 |
| M17 | 数据质量与更新状态 | multi | P0 | 4 | 35 |
| M18 | 公司画像总结与标签 | none | defer | 3 | 25 |

## 与四线关系

| 线 | 贡献模块 |
|----|----------|
| C | M01/M07/M08/M09 主源 |
| A | M04/M13 证据入口（非财报数值） |
| B | M13 事件壳 + 文档证据 |
| D | M14 及部分资本事件 |

## Gate

- `portrait_p0_catalog_gate` — 本步骤产出
- `portrait_p1_coverage_gate` — 覆盖矩阵 v0
