# CNINFO D 类 Known Event Targeted Probe — Runner Extension Design

_生成时间：2026-07-09_

> **性质：** 离线 runner 扩展设计 only · **无实现** · **无 CNINFO** · **NOT APPROVED**

**关联：** [targeted probe plan](cninfo_d_class_known_event_targeted_probe_plan.md) · [universe draft](../outputs/validation/cninfo_d_class_known_event_targeted_probe_universe_draft.csv)

---

## 1. Current Runner Status

`lab/run_cninfo_d_class_tiny_live_validation.py` **尚未支持** `--known-event-targeted-probe`。

现有模式：

- Phase 1 v1 tiny live
- v2 bounded probe（DLC003/DLC006）
- known-event replacement（DLC003R/DLC006R）

**本设计不实现代码。**

---

## 2. Required CLI Flags

| Flag | 类型 | 说明 |
|------|------|------|
| `--known-event-targeted-probe` | bool | 启用 targeted probe 模式；与 replacement/v1/v2 互斥 |
| `--approve-d-class-known-event-targeted-probe` | bool | live 必需 |
| `--universe-csv` | path | targeted probe universe draft |
| `--output-root` | path | 默认 `cninfo_d_class_known_event_targeted_probe/` |
| `--dry-run` / `--live` | mode | dry-run 默认 |

**禁止：** `--pdf-download` · `--ocr` · `--extraction` · `--db-write` · `--minio-write` · `--rag-run` · harvest flags

---

## 3. Targeted Probe Universe Loader

读取 [universe draft](../outputs/validation/cninfo_d_class_known_event_targeted_probe_universe_draft.csv)：

- 必须 **exactly 2 rows**
- `targeted_probe_include = yes`
- `replacement_case_id` ∈ `{DLC003R, DLC006R}`

---

## 4. Allowed / Blocked Case IDs

| 允许 | 禁止 |
|------|------|
| DLC003R-T01 → DLC003R | DLC003 · DLC006 |
| DLC006R-T01 → DLC006R | DLC001/002/004/005/007 |
| | placeholder · full tiny-live IDs |

---

## 5. Anchor-Date Handling

### DLC003R `restricted_shares_unlock`

- anchor：**2024-02-19**
- endpoint：既有 `liftBan/detail`
- 策略：anchor ±7d · ±30d · 月末邻近日 `tdate` 参数（去重后 ≤12）
- 不以 v1 baseline replay 为主 — **以 anchor 为中心**

### DLC006R `shareholder_change`

- anchor：**2024-07-16**
- endpoint：既有 `shareholeder/detail`
- 策略：anchor ±7d · `type=inc/desc` + `tdate` 组合（去重后 ≤12）

---

## 6. Component-Specific Targeted Probe Behavior

| component | 可接受 | caveat | 不可接受 |
|-----------|--------|--------|----------|
| restricted_shares_unlock | `found` + records≥1 | `needs_review` + records≥1 | empty_after_budget · network · schema |
| shareholder_change | 同上 | 同上 | 同上 |

**不得**从 disclosure description 推断 `captured_normal`。

---

## 7. Request Cap Enforcement

| case | cap |
|------|-----|
| DLC003R-T01 | ≤ **12** |
| DLC006R-T01 | ≤ **12** |
| total | ≤ **24** |

Preflight 拒绝超 cap plan · live 后 validate stats

---

## 8. Approval Guard

| 模式 | 要求 |
|------|------|
| dry-run | 无需 approval flag |
| live | `--approve-d-class-known-event-targeted-probe` 必需 |
| wrong flag | 拒绝 · **0 CNINFO** |

与 `--approve-d-class-known-event-replacement-validation` **独立**

---

## 9. Output-Root Isolation & Write-Block

```text
outputs/validation/cninfo_d_class_known_event_targeted_probe/
├── reports/
│   ├── d_class_known_event_targeted_probe_dryrun_report.csv
│   ├── d_class_known_event_targeted_probe_live_report.csv
│   ├── d_class_known_event_targeted_probe_quality_report.csv
│   └── d_class_known_event_targeted_probe_summary.md
└── live_snapshots/
```

**写保护：**

- replacement validation output root
- v1 / v2 tiny-live output roots
- original / calibrated universe paths

---

## 10. Report Paths（未来 live）

| 报告 | 路径 |
|------|------|
| live report | `reports/d_class_known_event_targeted_probe_live_report.csv` |
| quality report | `reports/d_class_known_event_targeted_probe_quality_report.csv` |
| summary | `reports/d_class_known_event_targeted_probe_summary.md` |

---

## 11. Dry-Run Behavior（未来）

- `cninfo_calls=0`
- 输出 planned probe list per anchor
- validate universe · caps · output isolation
- gate：`NOT_APPROVED` until live approval

---

## 12. Future Live Behavior（After Approval）

1. 仅 DLC003R-T01 · DLC006R-T01 发起 CNINFO
2. early stop on company-level hit
3. 写入隔离 output root
4. 评估 execution gate

---

## 13. Execution Gate Logic

| 结果 | gate |
|------|------|
| 双 case 可接受（found+records 或 needs_review+records） | `d_class_known_event_targeted_probe_execution_gate = PASS_WITH_CAVEAT` |
| 一成功一失败 | `FAIL_REVIEW_REQUIRED` |
| 双失败 | `FAIL_REVIEW_REQUIRED` |

**永不使用 `PASS`** · **不自动升级** replacement execution gate

---

## 14. Boundary

| 项 | 要求 |
|----|------|
| PDF/OCR/extraction | **禁止** |
| DB/MinIO/RAG | **禁止** |
| verified / production_ready | **禁止** |
| replacement live report mutation | **禁止** |

---

## 15. Gate

```text
runner_extension_design_gate = READY_FOR_IMPLEMENTATION
d_class_known_event_targeted_probe_planning_gate = READY_FOR_APPROVAL
approval_status = NOT_APPROVED
```

**CNINFO calls（本回合）：0**
