# CNINFO B 类 Phase 2.5 Failed-case Isolated Retry — Package Summary

_生成时间：2026-07-09_

> **性质：** 5-case isolated retry 批准包离线准备完成；**无 CNINFO** · **无 live** · **NOT APPROVED for execution**

---

## Failed Cases

| case_id | company | failure_type | retry_priority |
|---------|---------|--------------|----------------|
| B25E003 | 工商银行 | network_timeout | high |
| B25E008 | 中兴通讯 | proxy_503 | high |
| B25E032 | 传音控股 | network_timeout | high |
| B25E039 | 比亚迪 | ep002_orgid_resolution_failed | medium |
| B25E040 | 牧原股份 | ep002_orgid_resolution_failed | medium |

**45 successful cases excluded** — no rerun

---

## Failure Categories

| Category | Count | schema_impact |
|----------|-------|---------------|
| network_timeout | **2** | none |
| proxy_503 | **1** | none |
| ep002_orgid_resolution_failed | **2** | none |

**quality_impact：** retry_needed（全 5 例）· **非 schema failure**

---

## Artifacts

| 项 | 路径 |
|----|------|
| retry universe | [cninfo_b_class_phase25_failed_retry_universe.csv](cninfo_b_class_phase25_failed_retry_universe.csv) |
| command draft | [cninfo_b_class_phase25_failed_retry_command_draft.md](../plans/cninfo_b_class_phase25_failed_retry_command_draft.md) |
| approval checklist | [cninfo_b_class_phase25_failed_retry_approval_checklist.md](cninfo_b_class_phase25_failed_retry_approval_checklist.md) |
| approval summary | [cninfo_b_class_phase25_failed_retry_approval_summary.md](cninfo_b_class_phase25_failed_retry_approval_summary.md) |
| runner | [lab/run_cninfo_b_class_phase25_expansion_validation.py](../lab/run_cninfo_b_class_phase25_expansion_validation.py) |
| tests | [lab/test_cninfo_b_class_phase25_failed_retry_runner.py](../lab/test_cninfo_b_class_phase25_failed_retry_runner.py) |
| test summary | [cninfo_b_class_phase25_failed_retry_runner_test_summary.md](cninfo_b_class_phase25_failed_retry_runner_test_summary.md) |
| dry-run report | [b_class_phase25_failed_retry_dryrun_report.csv](cninfo_b_class_phase25_failed_retry/reports/b_class_phase25_failed_retry_dryrun_report.csv) |
| dry-run summary | [b_class_phase25_failed_retry_dryrun_summary.md](cninfo_b_class_phase25_failed_retry/reports/b_class_phase25_failed_retry_dryrun_summary.md) |

---

## Runner Changes

| 项 | 值 |
|----|-----|
| mode flag | `--retry-failed-only` |
| approval flag | `--approve-b-class-phase25-failed-retry` |
| retry universe size | **5** |
| allowed case IDs | B25E003 · B25E008 · B25E032 · B25E039 · B25E040 |
| successful case rejection | enforced |
| Phase 2.5 baseline write-block | enforced |

---

## Test Result

| 指标 | 值 |
|------|-----|
| tests run | **14** |
| passed | **14** |
| failed | **0** |
| CNINFO calls | **0** |

---

## Dry-Run Result

| 指标 | 值 |
|------|-----|
| cases planned | **5** |
| planned_ok | **5** |
| planned_request_count total | **10** |
| CNINFO calls | **0** |
| PDF download | **0** |
| PDF parse | **0** |
| OCR | **0** |
| extraction | **0** |

---

## Configuration

| 项 | 值 |
|----|-----|
| output root | `outputs/validation/cninfo_b_class_phase25_failed_retry/` |
| approval flag | `--approve-b-class-phase25-failed-retry` |
| planning gate | `b_class_phase25_failed_retry_planning_gate = READY_FOR_APPROVAL` |
| package gate | `b_class_phase25_failed_retry_package_gate = READY_FOR_APPROVAL` |

---

## Safety Checks

| 检查 | 状态 |
|------|------|
| live 须 `--approve-b-class-phase25-failed-retry` | enforced |
| wrong approval flags rejected | enforced |
| retry output root isolation | enforced |
| Phase 2.5 expansion baseline write blocked | enforced |
| universe size == 5 | enforced |
| only failed B25E cases | enforced |
| successful 45 excluded | enforced |
| PDF / OCR / extraction blocked | enforced |
| DB / MinIO / RAG blocked | enforced |
| verified / production_ready blocked | enforced |

---

## Gate

```text
b_class_phase25_failed_retry_package_gate = READY_FOR_APPROVAL
b_class_phase25_failed_retry_planning_gate = READY_FOR_APPROVAL
```

**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**

---

## Parallel Status

| Track | Status |
|-------|--------|
| Phase 2.5 closure | `b_class_phase25_expansion_closure_gate = PASS_WITH_CAVEAT` |
| Phase 2.5 execution | `b_class_phase25_expansion_execution_gate = PASS_WITH_CAVEAT` |
| C-class | `SNAPSHOT_GENERATED_QA_REVIEW` |

---

## Next Step（须人工）

1. 审阅 dry-run report（5 cases · all `planned_ok`）
2. 批准 isolated retry scope
3. 未来回合：`--retry-failed-only --live --approve-b-class-phase25-failed-retry`

**Never：** verified · production_ready · 45-case rerun · 100-company expansion
