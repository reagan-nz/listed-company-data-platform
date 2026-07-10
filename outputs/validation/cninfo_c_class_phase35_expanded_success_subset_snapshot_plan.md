# CNINFO C-Class Phase 3.5 Expanded Success-Subset Snapshot Plan

_生成时间：2026-07-10_

> Phase 3.5 expanded success-subset snapshot **离线规划 only**。**无 CNINFO** · **无 snapshot build** · **无 snapshot JSON**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**batch_id：** `phase35_batch_500_001_expanded_success_491`

**approval_status：** `NOT_APPROVED`

---

## 1. Snapshot Candidate Universe

| 项 | 值 |
|----|-----|
| snapshot candidate universe | **491** |
| prior original success (463) | **463** |
| resume recovered_complete (28) | **28** |
| remaining holdout | **9** |

来源：[cninfo_c_class_phase35_expanded_success_subset_universe.csv](cninfo_c_class_phase35_expanded_success_subset_universe.csv)

## 2. Source-Root Merge Manifest Design

| 角色 | 公司数 | harvest 根 |
|------|--------|------------|
| `original` | **463** | `outputs/harvest/cninfo_c_class/phase35_batch_500_001/` |
| `resume` | **28** | `outputs/harvest/cninfo_c_class/phase35_batch_500_001_resume/`（retried sources） + `outputs/harvest/cninfo_c_class/phase35_batch_500_001/`（non-retried 只读） |

**Precedence / conflict rules：**

1. Retried sources → resume root wins
2. Non-retried sources → original root
3. Derived modules → follow basic mapped root per company
4. Original `phase35_batch_500_001/` **never written** during snapshot build
5. Resume root **read-only** for planning; future build writes only to snapshot root

详见 [cninfo_c_class_phase35_snapshot_merge_manifest_design.csv](cninfo_c_class_phase35_snapshot_merge_manifest_design.csv)。

## 3. Exclusions

| 排除项 | 数量 | 原因 |
|--------|------|------|
| C35R016 / 301212 | **1** | still_partial · human_review_required · **不静默晋升** |
| hold_for_review | **8** | identity review · unchanged |

## 4. Future Output Isolation (NOT BUILT)

| snapshot root (planned) | `outputs/snapshot/cninfo_c_class/phase35_batch_500_001_expanded_success_491/` |
| harvest original | `outputs/harvest/cninfo_c_class/phase35_batch_500_001/` · **只读** |
| harvest resume | `outputs/harvest/cninfo_c_class/phase35_batch_500_001_resume/` · **只读** |

## 5. Boundaries

- **no snapshot build** in this task
- **no snapshot JSON** in this task
- **no DB / MinIO / RAG**
- **not verified** · **not production_ready**

## 6. Gate

```
phase35_expanded_success_subset_snapshot_planning_gate = READY_FOR_APPROVAL
```
