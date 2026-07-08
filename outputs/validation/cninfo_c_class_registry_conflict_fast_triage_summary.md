# CNINFO C-Class Registry Conflict Fast Triage Summary

_生成时间：2026-07-08T09:26:48Z_

> **性质：** 508 冲突快速分桶摘要。**设计/分析 only** · **不合并** · **不修改 candidate**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**Gate：** `registry_conflict_fast_triage_gate = READY_FOR_MANUAL_SIGNOFF`

---

## Total

| 指标 | 值 |
|------|-----|
| conflict total | **508** |
| actionable candidates（设计层） | **259** |
| remaining manual queue（优先处理） | **9** |
| deferred（likely_safe_later） | **241** |

---

## Fast Triage Distribution

### BSE legacy mapping（251）

| recommended_action | count |
|--------------------|-------|
| approved_mapping_candidate | **248** |
| manual_review_required | **3** |

### Rename history（15）

| recommended_action | count |
|--------------------|-------|
| rename_candidate | **10** |
| manual_review_required | **5** |

### Duplicate identity（1）

| 项 | 值 |
|----|-----|
| cases | **1** |
| decision | 见 [duplicate_identity_decision.md](duplicate_identity_decision.md) |

### Manual high risk（241）

| risk_bucket | count |
|-------------|-------|
| identity_risk_high | **0** |
| evidence_missing | **0** |
| likely_safe_later | **241** |

---

## Recommended Review Order

1. **P0** duplicate_identity（1）
2. **P1** BSE manual_review_required（3）
3. **P2** rename manual_review_required（5）
4. **P3** manual identity_risk_high（0）
5. **P4** manual evidence_missing（0）
6. **Defer** likely_safe_later（241）

---

## Important Rule

**Fast triage ≠ identity merge.** 所有 `approved_mapping_candidate` / `rename_candidate` 仅为设计层分桶，须 manual signoff 后方可写入 identity decision ledger。

---

## Recommended Next Action

**manual identity signoff** — 优先处理 remaining manual queue **9** 条；`likely_safe_later` **241** 条可延后。

---

## 产出路径

| 产出 | 路径 |
|------|------|
| BSE fast triage | [bse_legacy_mapping_fast_triage.csv](bse_legacy_mapping_fast_triage.csv) |
| Rename fast triage | [rename_history_fast_triage.csv](rename_history_fast_triage.csv) |
| Manual fast triage | [manual_high_risk_fast_triage.csv](manual_high_risk_fast_triage.csv) |
| Duplicate decision | [duplicate_identity_decision.md](duplicate_identity_decision.md) |

---

## 红线确认

- 无 CNINFO · 无 live · 无 harvest · 无 identity merge
- 未修改 registry candidate CSV
