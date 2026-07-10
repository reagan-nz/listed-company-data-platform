# CNINFO B 类 Phase 3 100-Company Failed-case Isolated Retry — Command Draft

_生成时间：2026-07-09_

> **性质：** 未来 isolated retry live 命令草案。**不执行** · **NOT APPROVED**

**Phase 3 execution gate：** `b_class_phase3_100_execution_gate = FAIL_REVIEW_REQUIRED`

**runner extension：** **complete**（`--phase3-100-failed-retry` · dry-run **99/99 planned_ok**）

**live path：** **implemented**（本回合未执行真实 live · mock tests **24/24 PASS**）

---

## 1. 范围约束

| 项 | 值 |
|----|-----|
| retry universe | [cninfo_b_class_phase3_100_failed_retry_universe.csv](../outputs/validation/cninfo_b_class_phase3_100_failed_retry_universe.csv)（**99** 家） |
| excluded success | B3E087（[hold ledger](../outputs/validation/cninfo_b_class_phase3_100_success_hold_ledger.csv)） |
| schema | phase1_freeze_v1（**不变**） |
| endpoints | EP001 · EP002 · EP004 · EP005 only |
| CNINFO calls（本回合） | **0** |

### 禁止

- rerun B3E087
- rerun Phase 1 / 2 / 2.5 cases
- PDF download / parse / OCR / extraction
- DB / MinIO / RAG
- verified / production_ready
- 写入 Phase 3 原始 live 输出根

---

## 2. 输出隔离

**专用 retry 输出根（强制）：**

```text
outputs/validation/cninfo_b_class_phase3_100_failed_retry/
```

**Write-blocked：**

- `outputs/validation/cninfo_b_class_phase3_100_expansion/`
- `outputs/validation/cninfo_b_class_phase25_expansion/`
- `outputs/validation/cninfo_b_class_phase25_failed_retry/`

---

## 3. Runner + Live Path（offline prep complete）

| 扩展项 | 状态 |
|--------|------|
| `--phase3-100-failed-retry` | **implemented** |
| `--approve-b-class-phase3-100-failed-retry` | **implemented** |
| live path (`process_phase3_retry_live`) | **implemented** |
| live report writers | **implemented** |
| universe validation | **99** rows · B3E087 excluded |
| dry-run | **99/99 planned_ok** · planned_request_count **198** |
| runner tests | **20/20 PASS** |
| live-path tests | **24/24 PASS** |
| acceptance threshold | **>= 90/99** → PASS_WITH_CAVEAT |

---

## 4. Live Retry Command Draft（NOT APPROVED · Do not execute）

```bash
# NOT APPROVED — 须用户显式批准后方可执行

cd listed_company_data_collector

python lab/run_cninfo_b_class_phase25_expansion_validation.py \
  --phase3-100-failed-retry \
  --live \
  --universe-csv outputs/validation/cninfo_b_class_phase3_100_failed_retry_universe.csv \
  --output-root outputs/validation/cninfo_b_class_phase3_100_failed_retry/ \
  --approve-b-class-phase3-100-failed-retry
```

> **Do not execute.** approval_status = **NOT_APPROVED**

---

## 5. Dry-Run Command（completed this round）

```bash
cd listed_company_data_collector

python lab/run_cninfo_b_class_phase25_expansion_validation.py \
  --phase3-100-failed-retry \
  --dry-run \
  --universe-csv outputs/validation/cninfo_b_class_phase3_100_failed_retry_universe.csv \
  --output-root outputs/validation/cninfo_b_class_phase3_100_failed_retry/
```

**Result：** 99/99 planned_ok · planned_request_count_total **198** · CNINFO **0**

---

## 6. Acceptance Threshold

| 条件 | Gate |
|------|------|
| retry acceptable **>= 90/99** | `b_class_phase3_100_failed_retry_execution_gate = PASS_WITH_CAVEAT` |
| retry acceptable **< 90/99** | `b_class_phase3_100_failed_retry_execution_gate = FAIL_REVIEW_REQUIRED` |

---

## 7. Approval Gate

```text
b_class_phase3_100_failed_retry_planning_gate = READY_FOR_APPROVAL
b_class_phase3_100_failed_retry_runner_extension_gate = READY_FOR_APPROVAL
b_class_phase3_100_failed_retry_live_implementation_gate = READY_FOR_APPROVAL
```

**NOT APPROVED**
