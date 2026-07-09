# CNINFO C-Class Phase 2 Smoke 188 Snapshot Dry-Run Plan

_生成时间：2026-07-09_

> **性质：** Phase 2 smoke **188 成功子集** snapshot dry-run **规划**。**本轮不执行 snapshot build** · **不写 verified**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**依据：**
- [live harvest QA summary](../outputs/validation/cninfo_c_class_phase2_smoke_200_live_harvest_qa_summary.md)（gate **PASS_WITH_CAVEAT**）
- [company failure summary](../outputs/validation/cninfo_c_class_phase2_smoke_200_live_harvest_company_failure_summary.csv)
- [subset design](../outputs/validation/cninfo_c_class_phase2_smoke_188_snapshot_subset_design.csv)
- [snapshot architecture plan](cninfo_c_class_company_snapshot_architecture_plan.md)
- [863 full batch plan](cninfo_c_class_snapshot_full_batch_plan.md)

---

# 1. Purpose

Plan snapshot generation for the **188 successful Phase 2 smoke companies** only.

Do **not** snapshot the **12 all-direct-failure companies**.

Snapshot consumes **existing Phase 2 isolated harvest normalized** outputs only. No CNINFO, no harvest rerun, no registry merge.

---

# 2. Input Scope

## Input harvest root

```
outputs/harvest/cninfo_c_class/phase2_smoke_200/
├── raw/           # 1400 files（只读参考，snapshot 不读 raw）
├── normalized/    # 1928 files（snapshot 主输入）
└── quality/       # harvest QA 侧车
```

## Successful subset

| 项 | 值 |
|----|-----|
| **companies** | **188** |
| **selection basis** | [subset design CSV](../outputs/validation/cninfo_c_class_phase2_smoke_188_snapshot_subset_design.csv) |
| **universe parent** | [phase2 smoke 200 YAML](../lab/eval_companies_c_class_phase2_smoke_200.yaml) |

## Excluded

| 项 | 值 |
|----|-----|
| **companies** | **12** |
| **pattern** | `all_direct_failed=true` |
| **codes** | `000038` `000616` `000956` `002087` `002231` `300023` `300356` `600005` `600290` `600634` `600646` `600696` |
| **rationale** | 6 direct sources failed · concentrated delisted / 退 / ST / legacy inactive caveat |

---

# 3. Subset Selection Rule

## Include when

- basic source available（normalized `company_basic_profile` 存在且可读）
- direct source failure count **< 6**
- `all_direct_failed != true`
- not a delisted/inactive **all-failure** case

## Exclude when

- `all_direct_failed = true`
- `basic_failed = true` **and** all six direct sources failed
- failure pattern indicates delisted/inactive caveat（7/7 YAML `listing_status=delisted` rows + 5 ST/退市/legacy names in 12-failure set）

## Implementation note

Subset manifest: `include_for_snapshot=true` rows in subset design CSV (**188** rows).

Future derived universe YAML（规划，本轮不生成执行文件）：

```
lab/eval_companies_c_class_phase2_smoke_188.yaml
```

---

# 4. Expected Snapshot Output

## Future snapshot output root

```
outputs/snapshot/cninfo_c_class/phase2_smoke_188/
```

## Expected files

| 项 | 值 |
|----|-----|
| per-company JSON | **188** |
| naming | `{company_code}.json` |
| quality sidecar（规划） | `quality/company_snapshot_status.csv` · `quality/company_snapshot_error.csv` |

## Isolation from 863

| 863 path | Phase 2 path |
|----------|----------------|
| `outputs/snapshot/cninfo_c_class/full/` | `outputs/snapshot/cninfo_c_class/phase2_smoke_188/` |
| harvest `outputs/harvest/cninfo_c_class/` | harvest `outputs/harvest/cninfo_c_class/phase2_smoke_200/` |

**No overwrite risk** when output root is isolated.

---

# 5. Snapshot Gate

Dry-run must confirm:

| # | check |
|---|-------|
| 1 | input company count = **188** |
| 2 | no all-direct-failure companies included |
| 3 | no delisted all-failure companies included |
| 4 | output root isolated from 863 snapshot `full/` output |
| 5 | no snapshot build executed in planning round |
| 6 | `snapshot_builder_extension_required` assessed（见 command checklist） |

**Planning gate（本轮）：**

**`phase2_smoke_188_snapshot_dryrun_planning_gate = DESIGN_COMPLETE`**

**Future execution dry-run gate（待执行轮）：**

`phase2_smoke_188_snapshot_dryrun_execution_gate = READY_FOR_DRYRUN`（extension 完成后）

---

# 6. Future QA

After snapshot build（未来执行轮，本轮不做）， run offline review:

| check | 说明 |
|-------|------|
| JSON validity | 每文件可 parse |
| module coverage | 10 modules per company |
| snapshot_status distribution | complete / complete_with_caveat / failed |
| source linkage | normalized path 与 harvest phase2 root 一致 |
| caveat propagation | ST / valid_empty dividend 等 caveat 写入 `data_quality` |

Review script candidate: extend `lab/review_cninfo_c_class_snapshot_full_quality.py` for phase2 path.

---

# 7. Red Lines（本轮）

- **No CNINFO**
- **No live / harvest rerun**
- **No snapshot build**
- **No raw / normalized / field_inventory modification**
- **No registry / DB / MinIO / RAG / merge / verified**

---

# 8. Next Step

1. **Snapshot builder extension**（`--harvest-root` · `--output-dir` · 188 universe YAML）
2. **Snapshot dry-run execution**（`--dry-run` only）
3. **Explicit approval** before `--execute` snapshot build
