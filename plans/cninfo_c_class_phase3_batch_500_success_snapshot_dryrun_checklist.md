# CNINFO C-Class Phase 3 Batch 500 Success-Subset Snapshot Dry-Run Checklist

_生成时间：2026-07-09_

> 491 家 success-subset snapshot dry-run 命令检查清单。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**batch_id：** `phase3_batch_500_001`

---

# Preflight

| # | 检查项 | 预期 | 状态 |
|---|--------|------|------|
| 1 | universe count = **491** | YAML `company_count` + subset design | **PLANNED** |
| 2 | excluded count = **9** | caveat ledger | **PLANNED** |
| 3 | output root isolated | `phase3_batch_500_001_success/` | **PLANNED** |
| 4 | full snapshot untouched | `outputs/snapshot/cninfo_c_class/full/` | **PLANNED** |
| 5 | phase2 snapshot untouched | `outputs/snapshot/cninfo_c_class/phase2_smoke_188/` | **PLANNED** |
| 6 | harvest root isolated | `phase3_batch_500_001/` 只读 | **PLANNED** |
| 7 | no BSE in universe | board != bse | **PLANNED** |
| 8 | no manual review identity in YAML | 600705 · 601028 排除 | **PLANNED** |
| 9 | no excluded codes in YAML | 9 caveat codes absent | **PLANNED** |
| 10 | planning gate | `phase3_batch_500_success_snapshot_planning_gate = DESIGN_COMPLETE` | **PASS** |

---

# Dry-Run Command

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

# Expected Dry-Run Results

| 项 | 预期 |
|----|------|
| `company_count` | **491** |
| `snapshot_json` | **0** |
| `build_snapshot` called | **false** |
| `cninfo_requests` | **0** |
| dry-run report rows | **491** |
| `planned_modules` per row | **18** |
| status CSV rows | **491**（`pending`） |

---

# Post Dry-Run Verification

| # | 检查项 | 预期 |
|---|--------|------|
| 1 | dry-run gate | `PASS` or `PASS_WITH_CAVEAT` |
| 2 | no `*.json` under snapshot root | **0** company snapshot JSON |
| 3 | 863 full JSON count unchanged | 无写入 |
| 4 | phase2_smoke_188 unchanged | 无写入 |
| 5 | harvest normalized untouched | mtime / count 不变 |

---

# Excluded Companies (must remain absent)

`600102` `600270` `600317` `600625` `600627` `600705` `600840` `601028` `601989`

---

**Red lines：** no CNINFO · no live · no harvest · no snapshot build · no verified
