# CNINFO C-Class Snapshot Source Priority Rules

_生成时间：2026-07-08_

> **性质：** Company Snapshot 多源优先级规则（规划）。当前 C-class 仅 **cninfo_f10** 已 harvest；年报/公告为 **future** 源占位。

**C-class 状态：** `HARVEST_COMPLETED_QA_ONGOING`

---

## 1. 优先级记号

| 记号 | 含义 | 当前可用 |
|------|------|----------|
| **cninfo_f10** | 巨潮 F10 / companyOverview 系列（C-class harvest） | **是** |
| **annual_report** | Era A/B 年报结构化抽取 | 否（future） |
| **quarterly_report** | 季报结构化抽取 | 否（future） |
| **announcement** | Era B 公告 metadata + 文本 | 否（future） |
| **market_data** | 行情/交易侧数据 | 否（future） |
| **raw_source** | harvest raw 文件 | **是** |
| **harvest_metadata** | quality/ 与 harvest status | **是** |

**语法：** `A > B > C` 表示 A 优先；若 A 不可用或无效则降级 B。

---

## 2. 按模块优先级

### 2.1 `company_identity`

```
cninfo_f10 > annual_report > announcement
```

| 字段 | preferred | fallback | 说明 |
|------|-----------|----------|------|
| company_code | cninfo_f10 | — | 主键，不冲突 |
| company_name | cninfo_f10 | annual_report | 简称以 F10 为准 |
| legal_name | annual_report | cninfo_f10 | 法定名称年报更权威 |
| english_name | cninfo_f10 | annual_report | |
| establishment_date | cninfo_f10 | annual_report | patch 后 863/863 |
| listing_date | cninfo_f10 | annual_report | |
| registered_address | annual_report | cninfo_f10 | |

---

### 2.2 `securities_profile`

```
cninfo_f10 > market_data > annual_report
```

| 字段 | preferred | fallback |
|------|-----------|----------|
| listed_board, exchange | cninfo_f10 | market_data |
| security_code, listing_status | market_data | cninfo_f10 |
| observe 字段 | cninfo_f10 security | 侧轨，不进主槽 |

---

### 2.3 `business_profile`

```
annual_report > cninfo_f10 > announcement
```

| 字段 | preferred | fallback |
|------|-----------|----------|
| business_scope | annual_report | cninfo_f10 derived |
| main_business_summary | annual_report | cninfo_f10 |
| company_profile_text | cninfo_f10 | announcement |

**说明：** 长文本年报更完整；F10 公司简介用于快速展示兜底。

---

### 2.4 `industry_profile`

```
annual_report > cninfo_f10 > announcement
```

| 字段 | preferred | fallback |
|------|-----------|----------|
| industry | annual_report | cninfo_f10 F032V |
| index_or_plate_labels | cninfo_f10 | —（review_later） |

---

### 2.5 `financial_snapshot`

```
annual_report > quarterly_report > cninfo_f10
```

| 字段 | preferred | fallback |
|------|-----------|----------|
| 注册资本/股本 | annual_report | cninfo_f10 |
| compensation_candidate | annual_report | cninfo_f10 executive |

---

### 2.6 `technology_profile`

```
annual_report > announcement > cninfo_f10
```

**当前：** 无 C-class 字段；规则预留。

---

### 2.7 `organization_profile` / `investor_relation`

```
cninfo_f10 > annual_report > announcement
```

| 字段 | preferred | fallback |
|------|-----------|----------|
| contact_email/phone/fax | cninfo_f10 contact derived | annual_report |
| company_website | cninfo_f10 | annual_report |

---

### 2.8 `shareholder_profile`

```
cninfo_f10 > annual_report > announcement
```

| 字段 | preferred | fallback |
|------|-----------|----------|
| top10 / top10 float | cninfo_f10 | annual_report 股东章节 |

**说明：** F10 更新频率高于年报；年报用于交叉验证。

---

### 2.9 `executive_profile` / `governance_profile`

```
cninfo_f10 > annual_report > announcement
```

| 字段 | preferred | fallback |
|------|-----------|----------|
| 高管列表 | cninfo_f10 | annual_report 董事监事高管 |
| legal_representative | annual_report | cninfo_f10 basic |

---

### 2.10 `dividend_profile`

```
cninfo_f10 > announcement > annual_report
```

| 字段 | preferred | fallback |
|------|-----------|----------|
| 分红历史 | cninfo_f10 dividend_history | announcement 分红公告 |

---

### 2.11 `capital_action_profile`

```
cninfo_f10 > announcement > annual_report
```

| 字段 | preferred | fallback |
|------|-----------|----------|
| 股本变动 | cninfo_f10 share_capital | announcement 股本变动公告 |

---

### 2.12 `risk_profile`

```
announcement > cninfo_f10 > annual_report
```

| 字段 | preferred | fallback |
|------|-----------|----------|
| ST/退市/风险提示 | announcement | cninfo_f10 security observe |

---

### 2.13 `event_timeline`

```
announcement > cninfo_f10 > annual_report
```

| 事件类型 | preferred |
|----------|-----------|
| 公告披露日 | announcement |
| 除权除息日 | cninfo_f10 dividend |
| 股本变动日 | cninfo_f10 share_capital |

---

### 2.14 `market_behavior`

```
market_data > cninfo_f10 > announcement
```

**当前：** 仅 security observe 侧轨数据。

---

### 2.15 `document_evidence`

```
raw_source > normalized > derived
```

**硬规则：** 任何冲突场景，raw 证据层不可被 normalized 覆盖删除，只可标注 superseded。

---

### 2.16 `data_quality`

```
harvest_metadata > computed
```

来源：`company_harvest_status.csv` · `source_quality.csv` · per-field parse_status。

---

## 3. 源不可用时的降级链

```
1. preferred_source 有值且 parse_status=parsed → 采用
2. preferred_source null_but_valid → 尝试 fallback
3. fallback 仍空 → 字段 status=missing；模块可能 source_partial
4. needs_review → 保留值 + manual_review_queue 标签
```

---

## 4. 当前实证（863 harvest）

| 源 | 可达性摘要 |
|----|-----------|
| cninfo_f10 basic | 853/863 endpoint_found |
| executive | 844 found + 9 empty_but_valid |
| share_capital | 843 found + 10 empty_but_valid |
| top_sh / top_float | 838/835 found + empty_but_valid |
| dividend | 815 found + 38 valid_empty |
| security | 853 observe（不进主 gate） |

**结论：** 当前 snapshot **仅 cninfo_f10 单源可构建**；priority 规则为多源接入预置。

---

## 5. Gate

```
snapshot_source_priority_rules_gate = PASS
```

**禁止：** verified · testing_stable_sample · registry backfill 执行
