# CNINFO C-Class Phase 3 Batch 500 Success-Subset Snapshot Build Approval Checklist

_生成时间：2026-07-09_

> Phase 3 **491** 家 success-subset snapshot build **审批前检查清单**。**仅审批准备** · **本轮不执行 build**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**batch_id：** `phase3_batch_500_001`

---

# 1. Universe Check

| 项 | 预期 | 状态 |
|----|------|------|
| harvest universe | **500** | **PASS**（live harvest 已完成） |
| snapshot candidate | **491** | **PASS**（subset design + YAML） |
| excluded identity caveat | **9** | **PASS**（caveat ledger） |
| universe YAML | [eval_companies_c_class_phase3_batch_500_success_snapshot_491.yaml](../../lab/eval_companies_c_class_phase3_batch_500_success_snapshot_491.yaml) | **PASS** |
| hold overlap | **0** | **PASS**（dry-run 验证） |
| no BSE | true | **PASS** |
| no manual review identity in YAML | true | **PASS**（600705 · 601028 排除） |

**Excluded codes（不得进入 build）：** `600102` `600270` `600317` `600625` `600627` `600705` `600840` `601028` `601989`

---

# 2. Output Isolation

| 项 | 路径 | 状态 |
|----|------|------|
| snapshot output root | `outputs/snapshot/cninfo_c_class/phase3_batch_500_001_success/` | **PLANNED** |
| 863 full snapshot | `outputs/snapshot/cninfo_c_class/full/` | **不覆盖** |
| phase2 smoke 188 | `outputs/snapshot/cninfo_c_class/phase2_smoke_188/` | **不覆盖** |
| phase3 harvest | `outputs/harvest/cninfo_c_class/phase3_batch_500_001/` | **只读** |

---

# 3. Input Path Verification

| 项 | 路径 | 状态 |
|----|------|------|
| harvest normalized root | `outputs/harvest/cninfo_c_class/phase3_batch_500_001/normalized/` | **PASS**（存在 · 只读） |
| harvest raw | `.../raw/` | **只读** · build 不依赖写入 |
| subset design | [cninfo_c_class_phase3_batch_500_success_snapshot_subset_design.csv](cninfo_c_class_phase3_batch_500_success_snapshot_subset_design.csv) | **PASS** |
| dry-run report | [cninfo_c_class_phase3_batch_500_success_snapshot_dryrun_report.csv](cninfo_c_class_phase3_batch_500_success_snapshot_dryrun_report.csv) | **PASS**（**491** rows） |

**CNINFO calls：** **0**（dry-run 已验证 · build **未执行**）

**raw / normalized modification：** **none**（build 未启动）

---

# 4. Resume Safety

| 项 | 路径 | 状态 |
|----|------|------|
| status CSV | `outputs/snapshot/cninfo_c_class/phase3_batch_500_001_success/quality/company_snapshot_status.csv` | **PASS**（dry-run 初始化 **491** pending） |
| error CSV | `.../quality/company_snapshot_error.csv` | **PASS**（header only） |
| resume marker isolation | under `phase3_batch_500_001_success/` only | **PASS** |
| 863 / phase2 status CSV | 独立路径 | **不共享** |

**Resume 规则：** terminal status（`complete` / `complete_with_caveat` / `failed`）跳过；`--force` 可重建。

---

# 5. Quality Policy

| 规则 | 说明 |
|------|------|
| planned modules | **18** per company |
| security | observe-only · 不绑定主 gate |
| partial harvest | 允许 `complete_with_caveat`（identity-clean partial 行） |
| identity caveat | **9** 家 hard exclude · 不得生成 JSON |
| derived modules | 从 basic 派生 · 无独立 HTTP |
| no verified | build 不写 verified |
| no DB / MinIO / RAG | 不适用 |

---

# 6. Preflight Gates

| gate | 值 | 状态 |
|------|-----|------|
| `phase3_batch_500_success_snapshot_planning_gate` | `DESIGN_COMPLETE` | **PASS** |
| `phase3_batch_500_success_snapshot_dryrun_planning_gate` | `READY_FOR_DRYRUN` | **PASS** |
| `phase3_success_subset_snapshot_dryrun_execution` | `PASS_WITH_CAVEAT` | **PASS** |
| `phase3_batch_500_failure_identity_triage_gate` | `READY_FOR_REVIEW` | **PASS** |

---

# 7. Approval Flag

| 项 | 要求 |
|----|------|
| required | `--approve-phase3-success-snapshot-build` |
| forbidden alone | `--approve-full-snapshot-batch` |
| forbidden alone | `--approve-phase2-smoke-188-snapshot` |
| execute switch | `--execute` + dedicated approval flag |

> Runner approval flag extension **已实现**（见 [extension summary](cninfo_c_class_phase3_success_snapshot_approval_extension_summary.md)）。批准后可使用 command draft 执行 build。

---

# 8. Approval Gate

```
phase3_batch_500_success_snapshot_build_approval_gate = READY_FOR_APPROVAL
```

**Snapshot build：** **NOT APPROVED YET** · **NOT EXECUTED**

---

# 9. Red Lines

- **no CNINFO**
- **no harvest rerun**
- **no snapshot build**（本轮）
- **no raw / normalized modification**
- **no verified**
