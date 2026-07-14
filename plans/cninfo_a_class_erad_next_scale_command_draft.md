# CNINFO A 类 Era D Next-Scale — Command Draft

_生成时间：2026-07-10 · runner extension complete · dry-run complete · **NOT APPROVED live**_

> **approval_status = NOT_APPROVED** · **approved_for_live = false** · **approved_for_runner = false**

---

## Dry-run（Complete · CNINFO 0）

```bash
cd listed_company_data_collector

python lab/run_cninfo_a_class_phase2_metadata_expansion.py \
  --erad-a-scale-500-slice1 \
  --universe-csv outputs/validation/cninfo_a_class_erad_next_scale_candidate_universe_draft.csv \
  --output-root outputs/validation/cninfo_a_class_erad_next_scale_slice1/ \
  --dry-run
```

**Result：** CNINFO **0** · planned_ok **300/300** · planned_request_count_total **600** · gate **`READY_FOR_APPROVAL`**

**Tests：**

```bash
python lab/test_cninfo_a_class_erad_next_scale_slice1_runner.py
```

**Tests（live-path mock）：**

```bash
python lab/test_cninfo_a_class_erad_next_scale_slice1_live_path.py
```

---

## Live（Future · **NOT APPROVED — DO NOT RUN without human approval**）

Live path **implemented** · mock tests **17/17 PASS** · CNINFO **0** in tests.

**Summary:** [live path summary](../outputs/validation/cninfo_a_class_erad_next_scale_slice1_live_path_summary.md)

```bash
# NOT APPROVED — DO NOT RUN without:
# I approve A-class Era D next-scale slice1 live metadata validation.

python lab/run_cninfo_a_class_phase2_metadata_expansion.py \
  --erad-a-scale-500-slice1 \
  --approve-a-class-erad-scale-500-slice1 \
  --universe-csv outputs/validation/cninfo_a_class_erad_next_scale_candidate_universe_draft.csv \
  --output-root outputs/validation/cninfo_a_class_erad_next_scale_slice1/ \
  --live
```

**Acceptance threshold:** ≥270/300 acceptable → `PASS_WITH_CAVEAT` · <270 → `FAIL_REVIEW_REQUIRED`

---

## Session Split（Future Live · Planning）

```bash
# Session 1 — cases AD2E201–350（150）
python lab/run_cninfo_a_class_phase2_metadata_expansion.py \
  --erad-a-scale-500-slice1 \
  --approve-a-class-erad-scale-500-slice1 \
  --universe-csv outputs/validation/cninfo_a_class_erad_next_scale_candidate_universe_draft.csv \
  --output-root outputs/validation/cninfo_a_class_erad_next_scale_slice1/ \
  --live \
  --case-range AD2E201:AD2E350

# Session 2 — cases AD2E351–500（150）
python lab/run_cninfo_a_class_phase2_metadata_expansion.py \
  --erad-a-scale-500-slice1 \
  --approve-a-class-erad-scale-500-slice1 \
  --universe-csv outputs/validation/cninfo_a_class_erad_next_scale_candidate_universe_draft.csv \
  --output-root outputs/validation/cninfo_a_class_erad_next_scale_slice1/ \
  --live \
  --case-range AD2E351:AD2E500
```

---

## Red Lines

- **不得**写入 `cninfo_a_class_erad_scale_200/` · `cninfo_a_class_erad_scale_200_failed_retry/` · Phase 3 / A3M017 production roots
- **不得**rerun AD2E001–200（lineage-reference only）
- **不得**rerun 8 scale-200 unresolved
- **无** PDF / DB / MinIO / RAG / verified
- mock 输出仅 `_mock_*` 子目录

---

## Gates

```text
a_class_erad_next_scale_planning_gate = READY_FOR_APPROVAL
a_class_erad_next_scale_slice1_runner_extension_gate = READY_FOR_APPROVAL
a_class_erad_next_scale_slice1_live_path_gate = READY_FOR_APPROVAL
```

**CNINFO = 0**（本规划/测试任务 · mock only）
