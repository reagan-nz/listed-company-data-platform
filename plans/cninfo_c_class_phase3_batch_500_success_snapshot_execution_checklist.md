# CNINFO C-Class Phase 3 Batch 500 Success-Subset Snapshot Execution Checklist

_生成时间：2026-07-09_

> 491 家 success-subset snapshot 执行前检查清单。**本轮仅规划** · **不执行 build**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**batch_id：** `phase3_batch_500_001`

**snapshot root（未来）：** `outputs/snapshot/cninfo_c_class/phase3_batch_500_001_success/`

---

# Preflight

| # | 检查项 | 预期 | 状态 |
|---|--------|------|------|
| 1 | universe count = **491** | subset design `include_for_snapshot=true` | **PLANNED** |
| 2 | excluded count = **9** | identity caveat ledger | **PLANNED** |
| 3 | no overlap with full snapshot | 863 `full/` 路径独立 | **PLANNED** |
| 4 | no phase2 overwrite | `phase2_smoke_188/` · `phase2_smoke_200/` 不触碰 | **PLANNED** |
| 5 | output root isolated | `phase3_batch_500_001_success/` | **PLANNED** |
| 6 | harvest root isolated | `phase3_batch_500_001/` | **PASS**（已存在） |
| 7 | identity caveat resolved offline | triage gate **READY_FOR_REVIEW** | **PASS** |
| 8 | subset design exists | `cninfo_c_class_phase3_batch_500_success_snapshot_subset_design.csv` | **PASS** |
| 9 | planning gate | `phase3_batch_500_success_snapshot_planning_gate = DESIGN_COMPLETE` | **PASS** |
| 10 | explicit approval for snapshot build | 用户显式批准 | **NOT APPROVED** |

---

# Dry-Run Checks（未来）

| # | 检查项 | 预期 |
|---|--------|------|
| 1 | JSON count expectation | **491** snapshot JSON |
| 2 | module coverage | 18 模块 mapper 全覆盖 |
| 3 | quality status | `company_snapshot_status.csv` 生成 |
| 4 | excluded codes absent | 9 家 caveat 公司无 JSON |
| 5 | completeness report | 491 行 build report |
| 6 | no CNINFO calls | dry-run only |
| 7 | no raw/normalized writes | read-only from harvest root |

---

# Build Checks（未来 · 未批准）

| # | 检查项 | 预期 |
|---|--------|------|
| 1 | build count | **491** / **491** |
| 2 | excluded verification | 9 家无输出 |
| 3 | 863 isolation | full/ mtime 不变 |
| 4 | phase2 isolation | phase2_smoke_188/ 不变 |
| 5 | QA gate | `PASS` or `PASS_WITH_CAVEAT` |

---

# Excluded Companies (9)

| company_code | identity_status | snapshot_policy |
|--------------|-----------------|-----------------|
| 600102 | delisted_or_reorganized | exclude |
| 600270 | delisted_or_reorganized | exclude |
| 600317 | delisted_or_reorganized | exclude |
| 600625 | delisted_or_reorganized | exclude |
| 600627 | delisted_or_reorganized | exclude |
| 600840 | delisted_or_reorganized | exclude |
| 601989 | delisted_or_reorganized | exclude |
| 600705 | manual_identity_review | exclude_pending_review |
| 601028 | manual_identity_review | exclude_pending_review |

---

# Status

```
NOT APPROVED YET — snapshot build not executed
```

**Red lines：** no CNINFO · no live · no harvest rerun · no snapshot build（本轮）
