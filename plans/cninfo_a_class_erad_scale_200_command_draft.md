# CNINFO A 类 Era D ~200 — Command Draft

_生成时间：2026-07-10_

> **NOT APPROVED for live** · dry-run **已实现** · live path **已实现**（mock tests only · **DO NOT RUN live**）

---

## Dry-Run（已实现 · offline）

```bash
cd listed_company_data_collector

python lab/run_cninfo_a_class_phase2_metadata_expansion.py \
  --erad-a-scale-200 \
  --dry-run \
  --universe-csv outputs/validation/cninfo_a_class_erad_scale_200_universe_draft.csv \
  --output-root outputs/validation/cninfo_a_class_erad_scale_200/
```

**实测（2026-07-10）：** CNINFO **0** · **200/200 planned_ok** · gate **`READY_FOR_APPROVAL`**

**产出：**

- `outputs/validation/cninfo_a_class_erad_scale_200/reports/a_class_erad_scale_200_dryrun_report.csv`
- `outputs/validation/cninfo_a_class_erad_scale_200/reports/a_class_erad_scale_200_dryrun_summary.md`

---

## Live（NOT APPROVED · DO NOT RUN）

需 explicit in-session approval：

> I approve A-class Era D scale-200 live execution.

```bash
python lab/run_cninfo_a_class_phase2_metadata_expansion.py \
  --erad-a-scale-200 \
  --live \
  --universe-csv outputs/validation/cninfo_a_class_erad_scale_200_universe_draft.csv \
  --output-root outputs/validation/cninfo_a_class_erad_scale_200/ \
  --approve-a-class-erad-scale-200
```

**当前状态：** live path **已实现** · approval **NOT APPROVED** · **本任务未执行 live** · CNINFO **0**

**约束（future live）：**

- request cap ≤ **480**
- metadata + URL lineage only · matching_logic **v2**
- 不重跑 Phase 1 / Phase 2 / Phase 3 50 / A3M017
- 不写入 Phase 3 expansion / A3M017 retry / B/C/D / harvest 根
- retained 50：引用 Phase 3 lineage · 仅写 Era D root

**future live 产出：**

- `outputs/validation/cninfo_a_class_erad_scale_200/reports/a_class_erad_scale_200_live_report.csv`
- `outputs/validation/cninfo_a_class_erad_scale_200/reports/a_class_erad_scale_200_live_quality_report.csv`
- `outputs/validation/cninfo_a_class_erad_scale_200/reports/a_class_erad_scale_200_live_summary.md`

---

## 错误批准示例（runner 拒绝）

```bash
--approve-a-class-phase3-50-company-expansion
--approve-a-class-phase2-metadata-expansion
--approve-a-class-phase2-retry-v3
```

---

## Tests

```bash
python lab/test_cninfo_a_class_erad_scale_200_runner.py
python lab/test_cninfo_a_class_erad_scale_200_live_path.py
```

**结果：** runner **27/27 PASS** · live-path **26/26 PASS** · CNINFO **0**
