# CNINFO C-Class dividend_history 字段映射说明（Era C Phase 4）

_生成时间：2026-07-07_

> **目的：** 冻结 `cninfo_dividend_financing_profile` → **`dividend_history`** 的 raw → normalized 字段映射，解除 harvest live 前的 mapper 规格缺口。**本轮仅 mapping**；**不请求 CNINFO**；**不 harvest**；**不写 verified**。

**机器可读配置：** [cninfo_dividend_history_mapper.yaml](../config/cninfo_dividend_history_mapper.yaml)

**关联：**

- [field inventory](cninfo_c_class_field_inventory.md)
- [harvest plan](cninfo_c_class_harvest_plan.md)
- [source status decision](cninfo_c_class_source_status_decision.md)
- P2-B probe：`fixtures/c_class/probe/records/c_class_p2b_probe_records.yaml`

---

## 1. Source 与逻辑名

| 项 | 值 |
|----|-----|
| registry `source_id` | `cninfo_dividend_financing_profile` |
| **逻辑名（harvest）** | **`dividend_history`** |
| endpoint | `GET /data20/companyOverview/getCompanyHisDividend` |
| `records_path` | `data.records`（**一条分红事件一行**） |
| source_status | **proceed_testing** |
| yaml_backfill | **GO（decision only）** — **不执行** |

---

## 2. 设计原则

### 2.1 dividend_history ≠ financing

- 停止使用 **financing** 作为逻辑名或 normalized 表名。
- `getCompanyHisDividend` 仅覆盖 **历史现金/送股/转增分红事件**。
- **不**承诺配股、增发、可转债等融资事件（不在本 mapper 范围）。

### 2.2 分红事件 = 公司历史事件

- 每条 record 代表一次报告期下的分红方案/实施记录。
- **不是**单次融资行为；不与 D 类 `dividend_event` 时间线混表（边界见 C/B/D 文档）。

### 2.3 保留报告期（多期并存）

同一公司可同时存在：

- 2022 年报分红
- 2023 年报分红
- 2024 年报分红

**主键维度：** `company_code` + `report_period` + `record_date`（及 `raw_record_hash`）。

### 2.4 保留 evidence（支持追溯问答）

未来需支持：

> 「过去五年是否持续分红？」

因此 harvest **必须**保留：

- `raw_record_json`（单条 `data.records[i]`）
- `raw_record_hash`
- `dividend_plan_text_raw`（F007V 原文）

normalized 解析字段不得替代 raw 证据。

---

## 3. 观测 Raw 字段（endpoint）

| raw_field | probe 含义 | 889 fill（非空 records） |
|-----------|------------|--------------------------|
| `F001V` | 报告期标签 | ~98.5% |
| `F007V` | 分红方案文本 | 100% |
| `F018D` | 股权登记日 | ~100% |
| `F020D` | 除权除息日 | ~99% |
| `F023D` | 派息日 | ~95% |

**未观测到的列**（不可臆造为 normalized_core）：现金分红总额、股东大会状态、分红政策全文。

---

## 4. 字段分类

### 4.1 normalized_core（9 字段 · 进入 normalized snapshot）

| normalized_field | raw / 派生 | 说明 |
|------------------|------------|------|
| `report_period` | `F001V` | 报告期原文 |
| `dividend_year` | 派生自 `F001V` | 提取四位年份 |
| `record_date` | `F018D` | 股权登记日 |
| `ex_dividend_date` | `F020D` | 除权除息日 |
| `payment_date` | `F023D` | 派息日 |
| `cash_dividend_per_share` | 解析 `F007V` | 如 10派4.1元 → 0.41 |
| `stock_dividend_ratio` | 解析 `F007V` | 10送X股 |
| `transfer_ratio` | 解析 `F007V` | 10转增X股 |
| `dividend_method` | 分类 `F007V` | cash / stock / transfer / mixed / other |

**说明：** 用户目标清单中 `announcement_date` · `cash_dividend_total` · `distribution_status` 因 **无稳定 raw 列**，归入 **review_later**（见下节），不计入 v1 normalized_core 数量。

### 4.2 review_later（8 字段）

| normalized_field | 原因 |
|------------------|------|
| `announcement_date` | 无独立公告日列；F018D 更偏登记日 |
| `cash_dividend_total` | endpoint 未返回总额 |
| `distribution_status` | 需从文本推断，语义不稳 |
| `special_dividend_note` | 需从 F007V 抽取 |
| `historical_anomaly_flag` | harvest 后规则引擎 |
| `shareholder_meeting_review_status` | 非本 endpoint |
| `dividend_policy_text` | 公司概况文本，非 events |
| `cumulative_dividend_label` | F10 展示标签 |

### 4.3 raw_only（4 字段）

| 字段 | 说明 |
|------|------|
| `dividend_plan_text_raw` | F007V 全文 |
| `data_total` | 响应级 total/count |
| `data_result_code` | data.resultCode |
| `raw_record_json` | 单条 record 完整 JSON |

另：lineage 级 `raw_record_hash` · `source_status` · `field_confidence` 随 harvest 框架写入，见 [field inventory](cninfo_c_class_field_inventory.md)。

---

## 5. F007V 解析规则（v1 草案）

配置见 mapper YAML `parse_rules_v1`。

| 文本示例 | 解析结果 |
|----------|----------|
| `10派4.1元(含税)` | cash_dividend_per_share=0.41 · dividend_method=cash |
| `10送2股` | stock_dividend_ratio=0.2 · dividend_method=stock |
| `10转增3股` | transfer_ratio=0.3 · dividend_method=transfer |
| 含派+送 | dividend_method=mixed |

**caveat：** 复杂方案、含税标注、分期派息需 harvest 后统计失败率；解析失败时保留 `dividend_plan_text_raw`，normalized 数值字段为 null。

---

## 6. Quality Rules

### 6.1 valid_empty

| 条件 | 判定 |
|------|------|
| HTTP 200 · `data.records` = `[]` | **valid_empty** |
| harvest | **不算失败** |
| 语义 | 公司暂无历史分红记录（或合法空） |

与 validate runner `allow_valid_empty: true` 一致。

### 6.2 missing

| 条件 | 判定 |
|------|------|
| endpoint 可达 · record 存在 · normalized_core 字段为 null | **missing** |
| 示例 | 老记录 `F023D` 为空 |

计入 quality 层 `field_fill_rate.csv`，**不**等同接口失败。

### 6.3 source_partial

| 条件 | 判定 |
|------|------|
| 字段结构存在但公司覆盖不足 | **source_partial** |
| 示例 | F007V 非标准文本导致解析失败率偏高 |

dividend_history 整体 reachability **≥97%**（889），但 **解析覆盖率** 需 harvest 后单独统计。

---

## 7. Normalized 输出形状（规划）

**路径：** `outputs/harvest/cninfo_c_class/normalized/dividend_history/{company_code}.jsonl`

**每行一条分红事件：**

```json
{
  "dividend_history_id": "<hash>",
  "source_id": "cninfo_dividend_financing_profile",
  "logical_source_id": "dividend_history",
  "company_code": "600000",
  "report_period": "2024年报",
  "dividend_year": 2024,
  "record_date": "2025-07-15",
  "ex_dividend_date": "2025-07-16",
  "payment_date": "2025-07-16",
  "cash_dividend_per_share": 0.41,
  "stock_dividend_ratio": null,
  "transfer_ratio": null,
  "dividend_method": "cash",
  "raw_record_json": { "F001V": "2024年报", "F007V": "10派4.1元(含税)", "...": "..." },
  "raw_record_hash": "...",
  "source_status": "testing",
  "field_confidence": "medium"
}
```

**实现：** `lab/cninfo_c_class_mappers.py` · `map_dividend_history()` · `parse_dividend_f007v()`；fixture test **5/5 PASS**（[summary](../outputs/validation/cninfo_c_class_dividend_history_mapper_test_summary.md)）。

---

## 8. Harvest Gate 影响

| 门槛 | 变更 |
|------|------|
| dividend mapper 规格 | **已完成**（本文档 + YAML） |
| harvest live 字段阻塞 | **已解除** |
| harvest live 执行阻塞 | **仍在** — 需人工批准 + runner `--live`（mapper 已实现 §7bc） |

---

## 9. 红线确认

| 项 | 本轮 |
|----|------|
| CNINFO 请求 | **无** |
| harvest live | **无** |
| raw / normalized 文件 | **无** |
| YAML registry backfill 执行 | **无** |
| DB / MinIO / RAG | **无** |
| verified | **不写** |

---

## 10. 字段统计

| status | 数量 |
|--------|------|
| **normalized_core** | **9** |
| **review_later** | **8** |
| **raw_only** | **4** |
| **合计（映射条目）** | **21** |
