# CNINFO B 类 Era D Next-Scale — Command Draft

_生成时间：2026-07-10 · dry-run **已实现** · live **NOT IMPLEMENTED** · **NOT APPROVED live**_

> **approval_status = NOT_APPROVED** · **approved_for_live = false**

---

## Dry-run（已实现 · 可执行）

```bash
cd listed_company_data_collector

python lab/run_cninfo_b_class_phase25_expansion_validation.py \
  --erad-b-scale-500-slice1 \
  --universe-csv outputs/validation/cninfo_b_class_erad_next_scale_candidate_universe_draft.csv \
  --output-root outputs/validation/cninfo_b_class_erad_next_scale_slice1/ \
  --dry-run
```

**实测：** CNINFO **0** · planned_ok **300/300** · planned_request_count_total **600** · cap **≤720**

**Tests:**

```bash
python lab/test_cninfo_b_class_erad_next_scale_slice1_runner.py
```

（**14/14 PASS**）

---

## Live（路径已实现 · **NOT APPROVED — DO NOT RUN**）

```bash
# NOT APPROVED — DO NOT RUN without:
# I approve B-class Era D next-scale slice1 live metadata validation.

python lab/run_cninfo_b_class_phase25_expansion_validation.py \
  --erad-b-scale-500-slice1 \
  --approve-b-class-erad-scale-500-slice1 \
  --universe-csv outputs/validation/cninfo_b_class_erad_next_scale_candidate_universe_draft.csv \
  --output-root outputs/validation/cninfo_b_class_erad_next_scale_slice1/ \
  --live
```

**Live-path mock tests（已实现）：**

```bash
python lab/test_cninfo_b_class_erad_next_scale_slice1_live_path.py
```

（**15/15 PASS** · mock CNINFO **0**）

**Acceptance threshold:** ≥270/300 acceptable → `PASS_WITH_CAVEAT` · <270 → `FAIL_REVIEW_REQUIRED`

---

## Session Split（Future Live · Wired）

```bash
# Session 1 — cases BD2E201–350（150）
python lab/run_cninfo_b_class_phase25_expansion_validation.py \
  --erad-b-scale-500-slice1 \
  --approve-b-class-erad-scale-500-slice1 \
  --universe-csv outputs/validation/cninfo_b_class_erad_next_scale_candidate_universe_draft.csv \
  --output-root outputs/validation/cninfo_b_class_erad_next_scale_slice1/ \
  --live \
  --case-range BD2E201:BD2E350

# Session 2 — cases BD2E351–500（150）
python lab/run_cninfo_b_class_phase25_expansion_validation.py \
  --erad-b-scale-500-slice1 \
  --approve-b-class-erad-scale-500-slice1 \
  --universe-csv outputs/validation/cninfo_b_class_erad_next_scale_candidate_universe_draft.csv \
  --output-root outputs/validation/cninfo_b_class_erad_next_scale_slice1/ \
  --live \
  --case-range BD2E351:BD2E500
```

---

## Red Lines

- **不得**写入 `cninfo_b_class_erad_scale_200/` · Phase 3 production roots
- **不得**rerun BD2E001–200（lineage-reference only）
- **无** PDF / DB / MinIO / RAG / verified
- mock 输出仅 `_mock_*` 子目录

---

## Gates

```text
b_class_erad_next_scale_slice1_runner_extension_gate = READY_FOR_APPROVAL
b_class_erad_next_scale_slice1_live_path_gate = READY_FOR_APPROVAL
b_class_erad_next_scale_planning_gate = READY_FOR_APPROVAL
```

**CNINFO = 0**（dry-run / mock live-path 任务）
