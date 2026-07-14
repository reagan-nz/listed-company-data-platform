# CNINFO D 类 restricted_shares_unlock First-Slice Plan（Draft）

_生成时间：2026-07-10_

> **性质：** Era D 离线第一切片规划草案 only · **NOT APPROVED** · **CNINFO calls = 0** · **无 runner** · **无 live** · **不是 verified**

---

## 1. Component Definition

| 项 | 值 |
|----|-----|
| component | `restricted_shares_unlock` |
| source_layer | `company_event` |
| target_logical_table | `d_company_event`（metadata only） |
| endpoint | `https://www.cninfo.com.cn/data20/liftBan/detail` |
| registry path | `restricted_shares_unlock/liftBan/detail` |
| query mode | **`tdate_daily`** |
| method | POST |
| params_location | query |
| records_path | `data.records` |
| date_param | **`tdate`**（解禁日锚点 · 全宇宙共享） |

---

## 2. Universe Scope（提案）

| 项 | 值 |
|----|-----|
| universe size | **5** companies |
| case_id scheme | **DRU001–DRU005** |
| anchor `tdate` policy | **2026-06-08**（registry `default_params.tdate` · 离线固定 · **非** CNINFO 探测） |
| markets | sse_main · szse_main · star（与 prior slices 对齐） |

### Exclusions（primary cases）

| 排除 | 原因 |
|------|------|
| **688671** | DLC003R 主案例 · known-event track closed |
| **301259** | DLC006R 关联 · known-event track closed |

DRU001 建议引用 DLC003（300009）`empty_but_valid` 先例 · **独立 DRU case_id**。

---

## 3. Expected Behavior Mix（吸收 block_trade 教训）

| 语义 | 说明 |
|------|------|
| `empty_but_valid` | 公司级零行 · 稀疏解禁日合法空态（DLC003 先例） |
| `captured_normal_or_empty_but_valid` | **默认推荐** — 避免 DBT002 式 sparse-day expectation mismatch |
| `needs_review` | 字段映射不确定时 acceptable + ledger caveat |

**禁止：** 将唯一案例标为 sole `captured_normal_candidate` 且绑定可能稀疏的单一 anchor。

---

## 4. Request Budget（future live · 规划）

| 项 | 值 |
|----|-----|
| per-case requests | **≤ 4**（multi-probe · runner 已有 anchor 窗口逻辑） |
| total cap | **≤ 20** CNINFO requests |
| planned (5-case) | **~5–20**（取决于 probe 计划） |
| early_stop | per-case 命中公司行后停止 |

---

## 5. Success Criteria（future live）

| 项 | 标准 |
|----|------|
| acceptable threshold | **≥ 3/5** cases acceptable |
| execution gate | **`PASS_WITH_CAVEAT`**（若 ≥3/5） |
| closure gate | **`PASS_WITH_CAVEAT`** with caveat ledger |
| **不是** bare PASS · **不是** verified · **不是** production_ready |

---

## 6. Output Root

```text
outputs/validation/cninfo_d_class_restricted_shares_unlock_first_slice/
```

**写入阻断：** known-event · margin_trading · disclosure_schedule · block_trade · tiny-live v1/v2 roots

---

## 7. Planned Flags Naming

| 用途 | 提案 |
|------|------|
| mode flag | `--restricted-shares-unlock-first-slice` |
| live approval | `--approve-d-class-restricted-shares-unlock-first-slice` |
| universe | `--universe-csv outputs/validation/cninfo_d_class_restricted_shares_unlock_first_slice_universe_draft.csv` |
| output root | `--output-root outputs/validation/cninfo_d_class_restricted_shares_unlock_first_slice/` |

---

## 8. Scope Limits

- metadata / structured-table only
- **无** PDF / OCR / extraction / DB / MinIO / RAG
- **无** verified / production_ready / testing_stable_sample
- **无** disclosure→captured_normal 升级
- **无** DLC003R / DLC006R rerun

---

## 9. Gate

```text
d_class_restricted_shares_unlock_first_slice_plan_draft_gate = NOT_APPROVED
approval_status = NOT_APPROVED
approved_for_live = false
```

---

## 10. Next Step

Human approve component choice → **approval package**（universe draft + checklist + command draft · **仍无 runner · 仍无 live**）
