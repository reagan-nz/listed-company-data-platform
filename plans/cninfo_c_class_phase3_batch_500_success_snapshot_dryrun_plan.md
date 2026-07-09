# CNINFO C-Class Phase 3 Batch 500 Success-Subset Snapshot Dry-Run Plan

_生成时间：2026-07-09_

> Phase 3 batch 500 **491** 家 success-subset snapshot dry-run 规划。**本轮 dry-run only** · **无 snapshot build**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**batch_id：** `phase3_batch_500_001`

**planning gate：** `phase3_batch_500_success_snapshot_planning_gate = DESIGN_COMPLETE`

**dry-run planning gate：** `phase3_batch_500_success_snapshot_dryrun_planning_gate = READY_FOR_DRYRUN`

---

# 1. Purpose

Prepare isolated snapshot dry-run for **491** identity-clean companies from Phase 3 batch 500 harvest.

Dry-run validates universe · output paths · status/error framework · module expectations — **without** calling `build_snapshot` or writing snapshot JSON.

---

# 2. Input Universe

| 项 | 值 |
|----|-----|
| harvest universe | **500** |
| snapshot eligible | **491** |
| excluded caveat | **9** |

## Input harvest root

```
outputs/harvest/cninfo_c_class/phase3_batch_500_001/
├── normalized/    # snapshot 主输入（只读）
├── raw/           # 只读参考
└── quality/       # harvest QA 侧车
```

## Universe YAML

```
lab/eval_companies_c_class_phase3_batch_500_success_snapshot_491.yaml
```

## Subset design

[cninfo_c_class_phase3_batch_500_success_snapshot_subset_design.csv](../outputs/validation/cninfo_c_class_phase3_batch_500_success_snapshot_subset_design.csv)

---

# 3. Excluded Universe (9)

| identity_status | count |
|-----------------|-------|
| `delisted_or_reorganized` | **7** |
| `manual_identity_review` | **2** |

**Excluded codes：** `600102` `600270` `600317` `600625` `600627` `600705` `600840` `601028` `601989`

**Ledger：** [cninfo_c_class_phase3_batch_500_failure_identity_caveat_ledger.csv](../outputs/validation/cninfo_c_class_phase3_batch_500_failure_identity_caveat_ledger.csv)

**Policy：** 暂不 snapshot；dry-run / build 均不得包含上述代码。

---

# 4. Output Isolation

| 项 | 路径 |
|----|------|
| **snapshot root（dry-run 规划）** | `outputs/snapshot/cninfo_c_class/phase3_batch_500_001_success/` |
| quality status | `.../quality/company_snapshot_status.csv` |
| error ledger | `.../quality/snapshot_build_errors.csv` |
| 863 full snapshot | `outputs/snapshot/cninfo_c_class/full/` — **不覆盖** |
| phase2 snapshot | `outputs/snapshot/cninfo_c_class/phase2_smoke_188/` — **不覆盖** |

---

# 5. Module Expectations

| 项 | 值 |
|----|-----|
| planned modules per company | **18** |
| security module | observe-only（不绑定主 gate） |
| derived modules | contact · business_scope · industry（from basic） |
| direct modules | basic · executive · share_capital · top_shareholders · top_float · dividend |

Dry-run 预期每行 `planned_modules=18`，`status=pending`；**snapshot JSON count = 0**。

---

# 6. QA Rules

| 规则 | 说明 |
|------|------|
| universe count | **491** declared == actual |
| hold overlap | **0** |
| excluded absent | 9 caveat codes 不在 YAML |
| no BSE | universe 无 BSE board |
| no manual review identity | 2 `manual_identity_review` 排除 |
| snapshot JSON | dry-run **0** 文件 |
| raw/normalized | **只读** · 不修改 |
| identity merge | **不做** |

---

# 7. Dry-Run Command

```bash
python lab/build_cninfo_c_class_snapshot_batch.py \
  --dry-run \
  --sample-file lab/eval_companies_c_class_phase3_batch_500_success_snapshot_491.yaml \
  --harvest-root outputs/harvest/cninfo_c_class/phase3_batch_500_001 \
  --output-dir outputs/snapshot/cninfo_c_class/phase3_batch_500_001_success \
  --output-csv outputs/validation/cninfo_c_class_phase3_batch_500_success_snapshot_dryrun_report.csv \
  --output-md outputs/validation/cninfo_c_class_phase3_batch_500_success_snapshot_dryrun_summary.md
```

---

# 8. Expected Dry-Run Outputs

| 产物 | 路径 |
|------|------|
| dry-run report | `outputs/validation/cninfo_c_class_phase3_batch_500_success_snapshot_dryrun_report.csv` |
| dry-run summary | `outputs/validation/cninfo_c_class_phase3_batch_500_success_snapshot_dryrun_summary.md` |
| status framework | `outputs/snapshot/cninfo_c_class/phase3_batch_500_001_success/quality/company_snapshot_status.csv` |

---

# 9. Red Lines

- **no CNINFO**
- **no harvest rerun**
- **no snapshot JSON build**（dry-run）
- **no raw / normalized modification**
- **no registry merge**
- **no verified**
