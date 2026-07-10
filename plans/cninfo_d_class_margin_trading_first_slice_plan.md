# CNINFO D 类 margin_trading First-Slice Plan

_生成时间：2026-07-10_

> **性质：** 离线第一切片规划 only · **CNINFO calls = 0** · **无 live** · **approval_status = NOT_APPROVED**

---

## 1. Component Definition

| 项 | 值 |
|----|-----|
| component | `margin_trading` |
| source_layer | `company_metric_daily` |
| target_logical_table | `d_company_metric_daily` |
| endpoint | `https://www.cninfo.com.cn/data20/marginTrading/detailList` |
| registry path | `margin_trading/detailList`（[registry draft](../config/cninfo_d_class_source_registry_draft.yaml)） |
| method | POST |
| records_path | `data.records` |
| date_param | detailList 主模式 **不显式传 date**；公司级过滤后取 anchor 日行 |

---

## 2. Universe Scope

| 项 | 值 |
|----|-----|
| universe size | **5** companies |
| case_id scheme | **DMT001–DMT005** |
| anchor trade date | 每公司 **1** 个 `anchor_tdate` |
| ±1 trade-day probe | **未来设计注记 only** — 可在 runner extension 中作为可选邻近探测；**本任务不实现** |
| universe draft | [cninfo_d_class_margin_trading_first_slice_universe_draft.csv](../outputs/validation/cninfo_d_class_margin_trading_first_slice_universe_draft.csv) |

### Exclusions (primary cases)

| 排除 | 原因 |
|------|------|
| **688671**（DLC003R 碧兴物联） | known-event replacement 主案例 · **不作第一切片主案例** |
| **301259**（DLC006R 艾布鲁） | known-event replacement 主案例 · **不作第一切片主案例** |

DMT001 可参考 DLC001（000895 双汇发展）Phase1 正向证据，但使用 **独立 case_id**。

---

## 3. Request Budget (future live)

| 项 | 值 |
|----|-----|
| per-case requests | **≤ 4**（1 primary + optional ±1 day design reserve） |
| total cap | **≤ 20** CNINFO requests |
| sleep default | 0.6s（与 Phase1 tiny live 一致 · 未来 live 规划值） |

---

## 4. Success Criteria (future live)

| 项 | 标准 |
|----|------|
| acceptable threshold | **≥ 3/5** cases acceptable |
| allowed outcomes | `found` · `empty_but_valid` · `needs_review` |
| acceptable definition | `found` with structured row **or** documented `empty_but_valid` **or** `needs_review` with field-mapping caveat |
| scope | metadata / structured-table only |
| raw lineage | retain snapshot JSON · no DB/MinIO/RAG |

**不使用：** PASS · verified · production_ready · testing_stable_sample

---

## 5. Explicit Non-Goals

- 不 reopen known-event replacement validation
- 不 rerun DLC003R / DLC006R
- 不将 disclosure-only 证据升级为 `captured_normal`
- 不下载/解析 PDF · 不 OCR · 不 extraction
- 不写 DB / MinIO / RAG
- 不做全市场 expansion
- 不做 identity merge 或 company code 变更
- 不标记 verified / production_ready / testing_stable_sample

---

## 6. Known-Event Track (frozen)

```text
d_class_known_event_replacement_final_closure_gate = PASS_WITH_CAVEAT
DLC003R = captured_normal_structured_evidence
DLC006R = accepted_component_gap_with_separate_disclosure_evidence
DLC006R captured_normal_allowed = no
```

known-event track **保持 closed-with-caveat** — 本切片与之 **正交**。

---

## 7. Runner Status

| 项 | 状态 |
|----|------|
| base runner | `lab/run_cninfo_d_class_tiny_live_validation.py` |
| margin_trading Phase1 path | **exists**（DLC001） |
| first-slice mode extension | **required later** — component-scoped universe loader + approval flag + request budget guard |
| this task | **no implementation** |

---

## 8. Output Root (future live)

```text
outputs/validation/cninfo_d_class_margin_trading_first_slice/
```

**禁止写入：** known-event replacement / targeted probe / Phase1 v1/v2 原始报告目录。

---

## 9. Approval Gate

```text
d_class_margin_trading_first_slice_approval_gate = READY_FOR_APPROVAL
```

**NOT APPROVED** · **NOT live_ready** · **NOT verified** · **NOT production_ready**

---

## 10. Artifacts

| 文档 | 路径 |
|------|------|
| universe draft | [cninfo_d_class_margin_trading_first_slice_universe_draft.csv](../outputs/validation/cninfo_d_class_margin_trading_first_slice_universe_draft.csv) |
| approval checklist | [cninfo_d_class_margin_trading_first_slice_approval_checklist.md](../outputs/validation/cninfo_d_class_margin_trading_first_slice_approval_checklist.md) |
| command draft | [cninfo_d_class_margin_trading_first_slice_command_draft.md](cninfo_d_class_margin_trading_first_slice_command_draft.md) |
| approval summary | [cninfo_d_class_margin_trading_first_slice_approval_summary.md](../outputs/validation/cninfo_d_class_margin_trading_first_slice_approval_summary.md) |
