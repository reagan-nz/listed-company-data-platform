# CNINFO B 类 Phase 3 100-Company — Failed-case Isolated Retry Plan

_生成时间：2026-07-09_

> **性质：** 未来 isolated retry 规划 only · **NOT APPROVED** · **无 CNINFO** · **无 live** · **无 retry**

---

## 1. Why Retry Is Needed

Phase 3 live execution 结果：

- **1/100 acceptable**（B3E087）
- **99/100 failed** with `network_error` at EP002 orgId resolution
- execution gate = `FAIL_REVIEW_REQUIRED`

与 Phase 2.5 经验一致：transient network / proxy / orgId 失败可通过 **isolated retry** 恢复，无需修改 schema 或 universe。

---

## 2. Why Retry Universe Is 99 Not 100

| 分组 | 数量 | 处理 |
|------|------|------|
| failed retry candidates | **99** | isolated retry batch |
| accepted original success | **1**（B3E087） | hold ledger · **不 rerun** |
| **total Phase 3 universe** | **100** | 不变 |

---

## 3. Why B3E087 Is Excluded

- `found` / `pass` / `discovered`
- PDF URL lineage present
- 计入 [success hold ledger](../outputs/validation/cninfo_b_class_phase3_100_success_hold_ledger.csv)
- 未来 merge：`1 accepted + N retry recovered`

---

## 4. Why Prior B Phases Are Excluded

Retry universe 仅来自 Phase 3 原始 live report 失败 subset：

- **不**包含 Phase 1 / 2 / 2.5 / 2.5 retry 任何 case
- **不**添加 replacement cases
- **不**修改 [universe draft](../outputs/validation/cninfo_b_class_phase3_100_universe_draft.csv)

---

## 5. Expected Request Count

| 项 | 值 |
|----|-----|
| retry cases | **99** |
| planned requests per case | **2**（EP002 + EP001） |
| **planned_request_count total** | **198** |

> 实际 CNINFO 请求数取决于网络恢复情况；本规划回合 **CNINFO = 0**。

---

## 6. Output Isolation Plan

**专用 retry 输出根：**

```text
outputs/validation/cninfo_b_class_phase3_100_failed_retry/
```

**Write-blocked：**

- `outputs/validation/cninfo_b_class_phase3_100_expansion/`（Phase 3 原始 live 报告根）
- `outputs/validation/cninfo_b_class_phase25_expansion/`
- `outputs/validation/cninfo_b_class_phase25_failed_retry/`
- Phase 1 / Phase 2 / TLC002 根
- `outputs/harvest/`

---

## 7. Approval Flag Requirement

未来 live retry 须：

```bash
--approve-b-class-phase3-100-failed-retry
```

无此 flag → 拒绝 live · 不调用 CNINFO

---

## 8. Acceptance Threshold

| 条件 | Gate |
|------|------|
| retry acceptable **>= 90/99** · 无 red-line violation | `b_class_phase3_100_failed_retry_execution_gate = PASS_WITH_CAVEAT` |
| retry acceptable **< 90/99** | `b_class_phase3_100_failed_retry_execution_gate = FAIL_REVIEW_REQUIRED` |

**Never：** PASS · verified · production_ready

---

## 9. Failure Interpretation

| 项 | 结论 |
|----|------|
| dominant pattern | EP002 orgId resolution failed |
| schema_impact | **none** |
| quality_impact | **retry_needed** |
| environment | transient CNINFO / proxy（高度可能） |
| schema change | **not recommended** |

---

## 10. Runner Extension Requirements（本回合不实现）

当前 `lab/run_cninfo_b_class_phase25_expansion_validation.py` **不支持**：

| 扩展项 | 说明 |
|--------|------|
| `--phase3-100-failed-retry` | 启用 Phase 3 99-case isolated retry 模式 |
| `--approve-b-class-phase3-100-failed-retry` | 独立批准 flag |
| default universe | `cninfo_b_class_phase3_100_failed_retry_universe.csv` |
| default output root | `cninfo_b_class_phase3_100_failed_retry/` |
| successful case exclusion | B3E087 及所有 non-failed cases 拒绝 |
| Phase 3 original root write-block | enforced |

未来回合：runner 扩展 + dry-run + tests + approval 后方可 live。

---

## 11. Red Lines

- No CNINFO in this planning round
- No live retry execution
- No B3E087 rerun
- No prior-phase rerun
- No universe mutation
- No PDF / OCR / extraction / DB / MinIO / RAG
- No verified · No production_ready · No testing_stable_sample

---

## Gate

```text
b_class_phase3_100_failed_retry_planning_gate = READY_FOR_APPROVAL
```

**NOT APPROVED** · **NOT live_ready**
