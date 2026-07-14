# CNINFO B 类 Era D Fuller Next-Slice2 Safe-to-Commit List

_生成时间：2026-07-13_  
_共享文件核对：2026-07-13（git-boundary-reviewer shadow #1 follow-up）_

> **性质：** commit boundary · **本任务不执行 stage/commit** · **须单独批准**  
> **Exact whole-file safe count：36**  
> **Hunk-level-only count：0**  
> **禁止：** `git add .` / `git add -A` · **禁止** whole-file stage of mixed shared status/plan files

---

## Section A — WHOLE-FILE SAFE PATHS（36）

### Source / Runner

| 路径 | 说明 |
|------|------|
| `lab/run_cninfo_b_class_phase25_expansion_validation.py` | `--erad-b-fuller-slice2` runner extension + live path（shared B-class runner） |

### Tests

| 路径 | 说明 |
|------|------|
| `lab/test_cninfo_b_class_erad_fuller_next_slice2_runner.py` | slice2 dry-run runner tests |
| `lab/test_cninfo_b_class_erad_fuller_next_slice2_live_path.py` | slice2 live-path mock tests |

### Plans（B fuller only）

| 路径 | 说明 |
|------|------|
| `plans/cninfo_b_class_erad_fuller_next_slice_plan.md` | fuller next-slice plan |
| `plans/cninfo_b_class_erad_fuller_next_slice_command_draft.md` | command draft |

### Validation — Fuller Planning

| 路径 | 说明 |
|------|------|
| `outputs/validation/cninfo_b_class_erad_fuller_next_slice_candidate_universe_draft.csv` | fuller universe draft |
| `outputs/validation/cninfo_b_class_erad_fuller_next_slice_universe_strategy.md` | universe strategy |
| `outputs/validation/cninfo_b_class_erad_fuller_next_slice_request_budget.md` | request budget |
| `outputs/validation/cninfo_b_class_erad_fuller_next_slice_planning_summary.md` | planning summary |
| `outputs/validation/cninfo_b_class_erad_fuller_next_slice_approval_checklist.md` | approval checklist |
| `outputs/validation/cninfo_b_class_erad_fuller_next_slice_next_step_recommendation.md` | next-step recommendation |

### Validation — Slice2 Runner / Live / Closure / Boundary

| 路径 | 说明 |
|------|------|
| `outputs/validation/cninfo_b_class_erad_fuller_next_slice2_runner_extension_summary.md` | runner extension summary |
| `outputs/validation/cninfo_b_class_erad_fuller_next_slice2_live_path_summary.md` | live path summary |
| `outputs/validation/cninfo_b_class_erad_fuller_next_slice2_live_execution_summary.md` | live execution summary |
| `outputs/validation/cninfo_b_class_erad_fuller_next_slice2_unresolved_case_ledger.csv` | unresolved ledger（1 row · BD2E624） |
| `outputs/validation/cninfo_b_class_erad_fuller_next_slice2_merge_closure_summary.md` | merge closure summary |
| `outputs/validation/cninfo_b_class_erad_fuller_next_slice2_edge_case_classification.csv` | edge-case classification |
| `outputs/validation/cninfo_b_class_erad_fuller_next_slice2_shared_file_reconciliation.md` | shared-file reconciliation report |
| `outputs/validation/cninfo_b_class_erad_fuller_next_slice2_commit_boundary_summary.md` | boundary summary |
| `outputs/validation/cninfo_b_class_erad_fuller_next_slice2_commit_boundary_file_list.txt` | explicit-path list（36 whole-file） |
| `outputs/validation/cninfo_b_class_erad_fuller_next_slice2_safe_to_commit_list.md` | **本清单** |
| `outputs/validation/cninfo_b_class_erad_fuller_next_slice2_do_not_commit_list.md` | do-not-commit list |
| `outputs/validation/cninfo_b_class_erad_fuller_next_slice2_commit_message_draft.md` | commit message draft |
| `outputs/validation/cninfo_b_class_erad_fuller_next_slice2_session1_live.log` | session1 live log（package-approved） |
| `outputs/validation/cninfo_b_class_erad_fuller_next_slice2_session2_live.log` | session2 live log（package-approved） |

### Validation — Reports（compact）

| 路径 | 说明 |
|------|------|
| `outputs/validation/cninfo_b_class_erad_fuller_next_slice2/reports/b_class_erad_fuller_next_slice2_dryrun_report.csv` | dry-run report |
| `outputs/validation/cninfo_b_class_erad_fuller_next_slice2/reports/b_class_erad_fuller_next_slice2_dryrun_summary.md` | dry-run summary |
| `outputs/validation/cninfo_b_class_erad_fuller_next_slice2/reports/b_class_erad_fuller_next_slice2_report.csv` | combined live report（300 rows） |
| `outputs/validation/cninfo_b_class_erad_fuller_next_slice2/reports/b_class_erad_fuller_next_slice2_summary.md` | live summary |
| `outputs/validation/cninfo_b_class_erad_fuller_next_slice2/reports/b_class_erad_fuller_next_slice2_quality_report.csv` | quality report |
| `outputs/validation/cninfo_b_class_erad_fuller_next_slice2/reports/b_class_erad_fuller_next_slice2_session1_report.csv` | session1 report |
| `outputs/validation/cninfo_b_class_erad_fuller_next_slice2/reports/b_class_erad_fuller_next_slice2_session1_summary.md` | session1 summary |
| `outputs/validation/cninfo_b_class_erad_fuller_next_slice2/reports/b_class_erad_fuller_next_slice2_session1_quality_report.csv` | session1 quality |
| `outputs/validation/cninfo_b_class_erad_fuller_next_slice2/reports/b_class_erad_fuller_next_slice2_session2_report.csv` | session2 report |
| `outputs/validation/cninfo_b_class_erad_fuller_next_slice2/reports/b_class_erad_fuller_next_slice2_session2_summary.md` | session2 summary |
| `outputs/validation/cninfo_b_class_erad_fuller_next_slice2/reports/b_class_erad_fuller_next_slice2_session2_quality_report.csv` | session2 quality |

---

## Section B — HUNK-LEVEL STAGING REQUIRED

**None（0）.**

Shared mixed files were **excluded**（OPTION 1）rather than planned for hunk-level staging in this boundary.

---

## Section C — EXCLUDED PATHS（from B slice2 commit）

| 路径 | 原因 |
|------|------|
| `CURRENT_STATUS.md` | mixed A/B/C/D hunks · B state authoritative in slice2 validation artifacts |
| `PROJECT_MAP.md` | mixed hunks · WT count wording corrected but file **not** in B commit |
| `plans/eraD_execution_plan.md` | mixed §9.x A/C/D/B hunks · §9.5b authoritative in merge/boundary docs |
| `PROJECT_CONTROL.md` | Controller/subagent workflow · untracked · not a B data artifact |
| bulk `raw_metadata/` · `quality/` · mocks · scale-200 · slice1 · A/C/D roots | see do-not-commit list |

---

## Section D — HUMAN DECISION REQUIRED

**None（0）.**

---

## Gates（unchanged · do not inflate）

```text
b_class_erad_fuller_next_slice_execution_gate = PASS_WITH_CAVEAT
b_class_erad_fuller_next_slice_merge_closure_gate = PASS_WITH_CAVEAT
b_class_erad_fuller_next_slice_commit_boundary_gate = READY_FOR_COMMIT_REVIEW
commit approval_status = NOT_APPROVED
```

**NOT** bare PASS · **NOT** verified · **NOT** production_ready · **NOT** testing_stable_sample · **NOT** `READY_FOR_HUMAN_COMMIT_APPROVAL` until shadow trial #2
