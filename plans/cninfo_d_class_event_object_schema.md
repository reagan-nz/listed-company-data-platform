# CNINFO D 类 Event Object Schema（Phase 1）

_最后更新：2026-07-09_

> **性质：** 设计文档 only；不调用 CNINFO；不入库。  
> **关联：** [cninfo_d_class_phase1_schema_freeze_review.md](cninfo_d_class_phase1_schema_freeze_review.md) · [schemas/d_class/](../schemas/d_class/)

---

## 1. Purpose

定义 D-class Phase 1 统一 **market_event** 对象：把各市场行为组件 payload 收敛到同一信封，支撑公司级时间线聚合。

**不是** C-class profile snapshot；**不是** B-class document。

---

## 2. Object Hierarchy

```
company (identity from C-class / eval YAML)
    │
    ▼
market_event (统一信封)
    │
    ├── component_payload (7 类之一)
    │
    ▼
timeline (读模型 · 按 company_code + event_time 排序)
```

- **company**：仅引用 `company_code`（及可选 `company_name`）；不在 D-class Phase 1 重复维护 identity registry。
- **market_event**：采集与 QA 的原子单元。
- **timeline**：离线聚合视图；Phase 1 不生成全市场 timeline 文件。

---

## 3. market_event Envelope

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `event_id` | string | yes | 逻辑主键；建议 hash(source_id, query_mode, company_code, event_time, raw keys) |
| `company_code` | string | yes | 证券代码 |
| `event_type` | string | yes | 组件类型：`margin_trading` · `block_trade` · `restricted_shares_unlock` · `disclosure_schedule` · `equity_pledge` · `shareholder_change` · `executive_shareholding` |
| `event_time` | date / datetime | yes | 主时间键：`trade_date` · `unlock_date` · `change_date` · `planned_date` 等 |
| `source_endpoint` | uri | yes | CNINFO API URL（来自 registry） |
| `source_record_id` | string | yes | 源内记录标识；无官方 id 时用稳定 hash |
| `event_status` | enum | yes | `captured` · `empty_but_valid` · `failed` · `pending` |
| `quality_status` | enum | yes | `pass` · `caveat` · `blocked` · `needs_review` |
| `lineage` | object | no | 见 §4 |

### event_type 与逻辑表映射

| event_type | record_kind | target_logical_table |
|------------|-------------|----------------------|
| margin_trading | metric_daily | d_company_metric_daily |
| block_trade | event | d_company_event |
| restricted_shares_unlock | event | d_company_event |
| disclosure_schedule | schedule | d_disclosure_schedule |
| equity_pledge | event | d_company_event |
| shareholder_change | event | d_company_event |
| executive_shareholding | event | d_company_event |

---

## 4. lineage Object

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `registry_source_id` | string | yes | 对应 `cninfo_d_class_source_registry_draft.yaml` 的 source_id |
| `query_mode` | string | no | 如 `type_inc` · `tdate_daily` · `detailList_default` |
| `query_params` | object | no | 实际请求参数 |
| `fetch_time` | datetime | yes | 等同组件级 `retrieval_time`（margin_trading） |
| `raw_record_hash` | string | yes | 原始行 hash |
| `raw_record_json` | object | recommended | 完整 CNINFO 行；Phase 1 强烈建议保留 |

---

## 5. Component Payload

每个 `market_event` 在信封同级携带 **一个** 组件 payload 对象，键名等于 `event_type`：

```json
{
  "market_event": { "...envelope..." },
  "margin_trading": { "...component fields..." }
}
```

组件字段契约见 [cninfo_d_class_phase1_schema_freeze_review.md](cninfo_d_class_phase1_schema_freeze_review.md) §3。

### 一致性规则

1. `market_event.company_code` **必须等于** 组件 payload 中的 `company_code`（若组件含该字段）。
2. `market_event.event_time` **必须等于** 组件主日期字段（`trade_date` / `unlock_date` / `change_date` / `planned_date` / `pledge_date`）。
3. `market_event.quality_status` 与组件 `quality_status` **必须一致**（若组件层存在该字段）。
4. `market_event.source_endpoint` 与组件 `source_endpoint`（若存在）**必须一致**。

---

## 6. event_id 生成（设计口径）

```
event_id = sha256_short(
  registry_source_id
  + "|" + query_mode
  + "|" + company_code
  + "|" + event_time
  + "|" + source_record_id
)
```

Phase 1 仅文档化；实现留待 mapper / harvest runner。

---

## 7. Timeline Read Model（设计 only）

| 字段 | 说明 |
|------|------|
| `timeline_company_code` | 聚合键 |
| `timeline_event_time` | 排序键 |
| `timeline_event_id` | 引用 market_event |
| `timeline_event_type` | 组件类型 |
| `timeline_quality_status` | 继承信封 |

Phase 1 **不生成** timeline 产物文件。

---

## 8. Relationship to Other Classes

| 类 | 关系 |
|----|------|
| **C-class** | 提供 `company_code` / `company_name` 上下文；不合并 schema |
| **B-class** | 未来 `event_document_link` 挂接 PDF 证据；Phase 1 不实现 |
| **A-class** | `disclosure_schedule` 可与报告期 PDF 联动；Phase 1 不抓取 PDF |

---

## 9. Phase 1 Fixture Shape

见 `fixtures/d_class/phase1/*.json` — 合成示例，`_fixture_meta.cninfo_called = false`。
