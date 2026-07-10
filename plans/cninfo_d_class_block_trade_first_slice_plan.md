# CNINFO D 类 block_trade First-Slice Plan

_生成时间：2026-07-10_

> **性质：** Era D 离线第一切片规划 only · **CNINFO calls = 0** · **无 live** · **approval_status = NOT_APPROVED**

---

## 1. Component Definition

| 项 | 值 |
|----|-----|
| component | `block_trade` |
| source_layer | `company_event` |
| target_logical_table | `d_company_event`（optional metric mapping · 本切片仅 metadata） |
| endpoint | `https://www.cninfo.com.cn/data20/ints/statistics` |
| registry path | `block_trade/ints/statistics`（[registry draft](../config/cninfo_d_class_source_registry_draft.yaml)） |
| query mode | **`tdate_daily`** |
| method | POST |
| params_location | query |
| records_path | `data.records` |
| date_param | **`tdate`**（单日锚点 · 全宇宙共享） |

---

## 2. Universe Scope

| 项 | 值 |
|----|-----|
| universe size | **5** companies |
| case_id scheme | **DBT001–DBT005** |
| anchor `tdate` policy | **2026-07-03**（registry default · 离线固定锚点 · **非** CNINFO 探测所得） |
| universe draft | [cninfo_d_class_block_trade_first_slice_universe_draft.csv](../outputs/validation/cninfo_d_class_block_trade_first_slice_universe_draft.csv) |

### Anchor `tdate` Policy（离线文档化）

- 全案例共享 **单一** `tdate = 2026-07-03`
- 依据：registry `default_params.tdate` 与 Phase2 稳定性记录（稀疏日 `empty_but_valid` 合法）
- **本任务不调用 CNINFO** 验证该日是否有成交；稀疏日零行属 **可接受** 结果

### Exclusions (primary cases)

| 排除 | 原因 |
|------|------|
| **688671**（DLC003R 碧兴物联） | known-event 主案例 · **不作第一切片主案例** |
| **301259**（DLC006R 艾布鲁） | known-event 主案例 · **不作第一切片主案例** |

DBT001 引用 DLC002（601988 中国银行）Phase1 **acceptable · empty_but_valid** 先例，使用 **独立 DBT case_id**。

---

## 3. Expected Behavior Mix

| 语义 | 说明 |
|------|------|
| `empty_but_valid` | 公司级零行 · 稀疏交易日合法空态（DLC002 先例） |
| `captured_normal_candidate` | 预期可能有结构化行；`found` 为正向结果 |
| `captured_normal_or_empty_but_valid` | 两种结果均可 acceptable |

**acceptable 定义（未来 live）：** `found` with ≥1 row **或** documented `empty_but_valid` **或** `needs_review` with field-mapping caveat。

---

## 4. Request Budget (future live)

| 项 | 值 |
|----|-----|
| per-case requests | **1**（单 `tdate` 查询） |
| total cap | **≤ 20** CNINFO requests |
| planned (5-case) | **~5** |
| sleep default | 0.6s（与 Phase1 tiny live 一致 · 未来 live 规划值） |

---

## 5. Success Criteria (future live)

| 项 | 标准 |
|----|------|
| acceptable threshold | **≥ 3/5** cases acceptable |
| execution gate | **`PASS_WITH_CAVEAT`**（若 ≥3/5）· **不是 bare PASS** |
| scope | metadata / structured-table only |
| raw lineage | retain snapshot JSON · no DB/MinIO/RAG |

**不使用：** PASS · verified · production_ready · testing_stable_sample

---

## 6. Era D Local-Only Note

本切片属 **Era D** D-line 本地稳定抽取广度扩展：

- 不接 DB / MinIO / verified
- 产物落盘 `outputs/validation/cninfo_d_class_block_trade_first_slice/`
- 与 A/B/C Era D ~200 / resume 轨 **并行** · **不互改** live 根

---

## 7. Closed Tracks（不得重开）

| Track | 状态 | Commit |
|-------|------|--------|
| known-event replacement | **closed** · `PASS_WITH_CAVEAT` | `389cd9c` |
| margin_trading first-slice | **closed** · `PASS_WITH_CAVEAT` | **`116f875`** |
| disclosure_schedule first-slice | **closed** · `PASS_WITH_CAVEAT` · DDS004 caveat retained | **`d37ce0a`** |

- **不** rerun DLC003R / DLC006R
- **不** 扩展 margin_trading / disclosure_schedule
- **不** 升级 disclosure-only → `captured_normal`

---

## 8. Explicit Non-Goals

- 不下载/解析 PDF · 不 OCR · 不 extraction
- 不写 DB / MinIO / RAG
- 不做全市场 expansion
- 不标记 verified / production_ready / testing_stable_sample
- **本任务不实现** `--block-trade-first-slice` runner 扩展

---

## 9. Runner Status

| 项 | 状态 |
|----|------|
| base runner | `lab/run_cninfo_d_class_tiny_live_validation.py` |
| block_trade Phase1 path | **exists**（DLC002） |
| first-slice mode extension | **required later** — **本任务不实现** |
| planned flags | `--block-trade-first-slice` · `--approve-d-class-block-trade-first-slice` |

---

## 10. Output Root (future live)

```text
outputs/validation/cninfo_d_class_block_trade_first_slice/
```

**禁止写入：** known-event · margin_trading · disclosure_schedule · tiny-live v1/v2 原始报告目录。

---

## 11. Approval Gate

```text
d_class_block_trade_first_slice_approval_gate = READY_FOR_APPROVAL
```

**NOT APPROVED** · **NOT live_ready** · **NOT verified** · **NOT production_ready**

---

## 12. Artifacts

| 文档 | 路径 |
|------|------|
| universe draft | [cninfo_d_class_block_trade_first_slice_universe_draft.csv](../outputs/validation/cninfo_d_class_block_trade_first_slice_universe_draft.csv) |
| approval checklist | [cninfo_d_class_block_trade_first_slice_approval_checklist.md](../outputs/validation/cninfo_d_class_block_trade_first_slice_approval_checklist.md) |
| command draft | [cninfo_d_class_block_trade_first_slice_command_draft.md](cninfo_d_class_block_trade_first_slice_command_draft.md) |
| approval summary | [cninfo_d_class_block_trade_first_slice_approval_summary.md](../outputs/validation/cninfo_d_class_block_trade_first_slice_approval_summary.md) |
