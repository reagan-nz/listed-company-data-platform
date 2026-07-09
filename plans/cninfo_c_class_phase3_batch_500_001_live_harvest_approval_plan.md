# CNINFO C-Class Phase 3 Batch 500 Live Harvest Approval Plan

_生成时间：2026-07-09_

> 本计划用于决定是否允许 Phase 3 batch 500 进入 live harvest。**不执行 live harvest**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**batch_id：** `phase3_batch_500_001`

---

# 1. Purpose

This plan decides whether Phase 3 batch 500 can proceed to live harvest.

It does not execute live harvest.

本计划基于 dry-run 证据与 runner 安全扩展，评估 Phase 3 batch 500 live harvest 是否具备批准条件。批准本计划不等于批准 live 执行；live 仍需用户显式批准并携带专用 approval flag。

---

# 2. Dry-Run Evidence

| 项 | 值 |
|----|-----|
| dry-run gate | **`phase3_batch_500_001_harvest_dryrun_execution_gate = PASS`** |
| company_count | **500** |
| matrix_rows | **5000** |
| planned_http_cases | **3500** |
| direct_rows | **3000** |
| derived_rows | **1500** |
| observe_rows | **500** |
| CNINFO called | **false** |
| real harvest executed | **false** |
| raw_writes | **0** |
| normalized_writes | **0** |
| security | **observe-only**（500 rows） |

**Universe：** [lab/eval_companies_c_class_phase3_batch_500_001.yaml](../lab/eval_companies_c_class_phase3_batch_500_001.yaml)

**Dry-run QA：** [cninfo_c_class_phase3_batch_500_001_harvest_dryrun_qa_summary.md](../outputs/validation/cninfo_c_class_phase3_batch_500_001_harvest_dryrun_qa_summary.md)

**Evidence summary：**

- dry-run **PASS**
- CNINFO called = **false**
- real harvest executed = **false**
- raw / normalized **unchanged**（863 主轨与 Phase 2 smoke 产物均未修改）
- security **observe-only**（500 条 observe 行，无 live security fetch）

---

# 3. Live Execution Scope

If approved later:

| 项 | 值 |
|----|-----|
| Universe | `lab/eval_companies_c_class_phase3_batch_500_001.yaml` |
| Output root | `outputs/harvest/cninfo_c_class/phase3_batch_500_001/` |
| Live source calls | **500 × 7 = 3500** |
| Direct normal calls | **500 × 6 = 3000** |
| Security observe-only | **500** |
| Derived normalized rows | **500 × 3 = 1500** |

**Required approval flag：**

```
--approve-phase3-batch-500-harvest
```

**Required output root：**

```
--output-root outputs/harvest/cninfo_c_class/phase3_batch_500_001
```

---

# 4. Risk Controls

| 控制项 | 状态 |
|--------|------|
| dedicated approval flag required | **已实现**（`--approve-phase3-batch-500-harvest`） |
| output root isolated | **已实现**（强制 `phase3_batch_500_001/`） |
| no Phase 2 overlap | **已实现**（拒绝 `phase2_smoke_200/`） |
| no 863 overlap | **已实现**（拒绝默认 863 主轨） |
| listed only | **是**（universe selection gate PASS） |
| no delisted | **是** |
| no 退 / 退市 / *ST | **是** |
| no BSE | **是** |
| no hold | **是**（hold overlap = 0） |
| no manual review | **是** |
| no identity conflict | **是** |
| security observe-only | **是** |
| no snapshot during harvest | **是**（本轮仅 harvest，不触发 snapshot） |
| resume marker isolated | **是**（`run_status.json` / `company_harvest_status.csv` 在 phase3 root 下） |

**禁止使用的 approval flag：**

- `--approve-full-harvest`（单独使用不可通过 Phase 3 live gate）
- `--approve-phase2-smoke-harvest`（单独使用不可通过 Phase 3 live gate）

---

# 5. Approval Gate

```
phase3_batch_500_001_live_harvest_approval_gate = READY_FOR_APPROVAL
```

**Live execution still requires explicit user approval.**

本计划将 gate 设为 `READY_FOR_APPROVAL`，表示 runner 扩展与审批规划已完成，具备进入用户审批环节的条件。实际 live harvest **尚未执行**，也**未获批准**。

---

# 6. Related Artifacts

| 产物 | 路径 |
|------|------|
| approval checklist | [cninfo_c_class_phase3_batch_500_001_live_harvest_approval_checklist.md](../outputs/validation/cninfo_c_class_phase3_batch_500_001_live_harvest_approval_checklist.md) |
| command draft | [cninfo_c_class_phase3_batch_500_001_live_harvest_command_draft.md](cninfo_c_class_phase3_batch_500_001_live_harvest_command_draft.md) |
| extension summary | [cninfo_c_class_phase3_batch_500_001_harvest_approval_extension_summary.md](../outputs/validation/cninfo_c_class_phase3_batch_500_001_harvest_approval_extension_summary.md) |
| approval tests | [test_cninfo_c_class_phase3_batch_500_harvest_approval.py](../lab/test_cninfo_c_class_phase3_batch_500_harvest_approval.py) · **10/10 PASS** |

---

# 7. Next Step

等待用户显式批准 Phase 3 batch 500 live harvest。批准后方可使用 command draft 中的 live 命令（仍需 `--approve-phase3-batch-500-harvest`）。
