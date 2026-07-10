# CNINFO A 类 Era D ~200 — Isolated Retry Command Draft

_更新：2026-07-10（live path implementation 后）_

> **NOT APPROVED for live** · dry-run **已实现** · live path **已实现**（mock tests only · **DO NOT RUN live**）

---

## Scope

| 项 | 值 |
|----|-----|
| retry universe | [cninfo_a_class_erad_scale_200_isolated_retry_universe_draft.csv](../outputs/validation/cninfo_a_class_erad_scale_200_isolated_retry_universe_draft.csv)（**7** cases） |
| deferred | AD2E146（retry=no · **excluded**） |
| output root | `outputs/validation/cninfo_a_class_erad_scale_200_failed_retry/` |
| matching | v2 · metadata only |
| request cap | **≤24**（planned **14**） |

---

## Dry-Run（已实现 · offline）

```bash
cd listed_company_data_collector

python lab/run_cninfo_a_class_phase2_metadata_expansion.py \
  --erad-a-scale-200-failed-retry \
  --dry-run \
  --universe-csv outputs/validation/cninfo_a_class_erad_scale_200_isolated_retry_universe_draft.csv \
  --output-root outputs/validation/cninfo_a_class_erad_scale_200_failed_retry/
```

**实测：** CNINFO **0** · **7/7 planned_ok**

---

## Live（NOT APPROVED · DO NOT RUN）

Requires explicit in-session approval phrase:

> I approve A-class Era D scale-200 isolated retry live for the triage-recommended not_found cases.

```bash
python lab/run_cninfo_a_class_phase2_metadata_expansion.py \
  --erad-a-scale-200-failed-retry \
  --live \
  --universe-csv outputs/validation/cninfo_a_class_erad_scale_200_isolated_retry_universe_draft.csv \
  --output-root outputs/validation/cninfo_a_class_erad_scale_200_failed_retry/ \
  --approve-a-class-erad-scale-200-failed-retry
```

**Note：** historical phrase may reference 8 not_found cases; **enforce universe = 7** from draft CSV（AD2E146 deferred）

**当前状态：** live path **已实现** · approval **NOT APPROVED** · **本任务未执行 live** · CNINFO **0**

**future live 产出：**

- `outputs/validation/cninfo_a_class_erad_scale_200_failed_retry/reports/a_class_erad_scale_200_failed_retry_live_report.csv`
- `outputs/validation/cninfo_a_class_erad_scale_200_failed_retry/reports/a_class_erad_scale_200_failed_retry_live_quality_report.csv`
- `outputs/validation/cninfo_a_class_erad_scale_200_failed_retry/reports/a_class_erad_scale_200_failed_retry_live_summary.md`

---

## Tests

```bash
python lab/test_cninfo_a_class_erad_scale_200_isolated_retry_runner.py
python lab/test_cninfo_a_class_erad_scale_200_isolated_retry_live_path.py
```

**结果：** runner **21/21 PASS** · live-path **18/18 PASS** · CNINFO **0**

---

## Explicit Prohibitions

- No full Era D 200 rerun
- No main Era D live root mutation
- No Phase 3 / A3M017 production-root writes
- No PDF / DB / MinIO / RAG
- No verified / production_ready

---

## Prerequisites（before any live）

- [x] failed-case triage complete
- [x] isolated retry universe draft（7）
- [x] runner extension + dry-run（**7/7 planned_ok**）
- [x] live path implementation（mock **18/18 PASS**）
- [ ] explicit isolated retry live approval phrase
- [ ] human review AD2E146 defer
