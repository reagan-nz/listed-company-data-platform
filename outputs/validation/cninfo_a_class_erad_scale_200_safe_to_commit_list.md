# CNINFO A 类 Era D ~200 Safe-to-Commit List

_生成时间：2026-07-10_

> **性质：** explicit-path commit boundary · **本任务不执行 commit** · **须单独批准**  
> **Approximate count：~47 paths**（不含 bulk raw_metadata）

---

## Source / Runner

| 路径 | 说明 |
|------|------|
| `lab/run_cninfo_a_class_phase2_metadata_expansion.py` | Era D `--erad-a-scale-200` + `--erad-a-scale-200-failed-retry` runner extension + live path（shared A-class runner） |

---

## Tests

| 路径 | 说明 |
|------|------|
| `lab/test_cninfo_a_class_erad_scale_200_runner.py` | main dry-run runner tests（27/27 PASS） |
| `lab/test_cninfo_a_class_erad_scale_200_live_path.py` | main live-path mock tests（26/26 PASS） |
| `lab/test_cninfo_a_class_erad_scale_200_isolated_retry_runner.py` | isolated retry runner tests（21/21 PASS） |
| `lab/test_cninfo_a_class_erad_scale_200_isolated_retry_live_path.py` | isolated retry live-path mock tests（18/18 PASS） |

---

## Plans

| 路径 | 说明 |
|------|------|
| `plans/cninfo_a_class_erad_scale_200_plan.md` | Era D ~200 expansion plan |
| `plans/cninfo_a_class_erad_scale_200_command_draft.md` | main command draft |
| `plans/cninfo_a_class_erad_scale_200_isolated_retry_plan.md` | isolated retry plan |
| `plans/cninfo_a_class_erad_scale_200_isolated_retry_command_draft.md` | isolated retry command draft |
| `plans/cninfo_a_class_erad_scale_200_commit_boundary_review.md` | **本 commit boundary review** |
| `plans/eraD_execution_plan.md` | §9.6 A-class Era D status（section update only） |

---

## Validation — Universe / Planning / Main Live

| 路径 | 说明 |
|------|------|
| `outputs/validation/cninfo_a_class_erad_scale_200_universe_draft.csv` | 200-case universe |
| `outputs/validation/cninfo_a_class_erad_scale_200_planning_summary.md` | planning summary |
| `outputs/validation/cninfo_a_class_erad_scale_200_runner_extension_summary.md` | runner extension summary |
| `outputs/validation/cninfo_a_class_erad_scale_200_live_path_summary.md` | live path summary |
| `outputs/validation/cninfo_a_class_erad_scale_200_execution_summary.md` | main live execution summary |
| `outputs/validation/cninfo_a_class_erad_scale_200_approval_checklist.md` | main approval checklist |
| `outputs/validation/cninfo_a_class_erad_scale_200_next_step_recommendation.md` | next-step recommendation |

---

## Validation — Failed-Case Triage / Isolated Retry

| 路径 | 说明 |
|------|------|
| `outputs/validation/cninfo_a_class_erad_scale_200_failed_case_triage_ledger.csv` | 8-row triage ledger |
| `outputs/validation/cninfo_a_class_erad_scale_200_failed_case_triage_summary.md` | triage summary |
| `outputs/validation/cninfo_a_class_erad_scale_200_failed_case_triage_next_step_recommendation.md` | triage next-step |
| `outputs/validation/cninfo_a_class_erad_scale_200_isolated_retry_universe_draft.csv` | 7-case retry universe |
| `outputs/validation/cninfo_a_class_erad_scale_200_isolated_retry_runner_extension_summary.md` | retry runner extension summary |
| `outputs/validation/cninfo_a_class_erad_scale_200_isolated_retry_live_path_summary.md` | retry live path summary |
| `outputs/validation/cninfo_a_class_erad_scale_200_isolated_retry_live_execution_summary.md` | retry live execution summary |
| `outputs/validation/cninfo_a_class_erad_scale_200_isolated_retry_approval_checklist.md` | retry approval checklist |
| `outputs/validation/cninfo_a_class_erad_scale_200_isolated_retry_next_step_recommendation.md` | retry next-step |

---

## Validation — Merge Closure / Commit Boundary

| 路径 | 说明 |
|------|------|
| `outputs/validation/cninfo_a_class_erad_scale_200_merge_closure_summary.md` | merge closure summary |
| `outputs/validation/cninfo_a_class_erad_scale_200_merge_closure_decision.md` | merge closure decision |
| `outputs/validation/cninfo_a_class_erad_scale_200_effective_accepted_ledger.csv` | **192-row** effective accepted ledger |
| `outputs/validation/cninfo_a_class_erad_scale_200_unresolved_final_ledger.csv` | **8-row unresolved final ledger** |
| `outputs/validation/cninfo_a_class_erad_scale_200_commit_boundary_summary.md` | boundary summary |
| `outputs/validation/cninfo_a_class_erad_scale_200_safe_to_commit_list.md` | **本清单** |
| `outputs/validation/cninfo_a_class_erad_scale_200_do_not_commit_list.md` | do-not-commit list |
| `outputs/validation/cninfo_a_class_erad_scale_200_commit_message_draft.md` | commit message draft |

---

## Validation — Reports（compact · metadata summaries only）

| 路径 | 说明 |
|------|------|
| `outputs/validation/cninfo_a_class_erad_scale_200/reports/a_class_erad_scale_200_dryrun_report.csv` | main dry-run report（200/200） |
| `outputs/validation/cninfo_a_class_erad_scale_200/reports/a_class_erad_scale_200_dryrun_summary.md` | main dry-run summary |
| `outputs/validation/cninfo_a_class_erad_scale_200/reports/a_class_erad_scale_200_live_report.csv` | main live report（192/200 acceptable） |
| `outputs/validation/cninfo_a_class_erad_scale_200/reports/a_class_erad_scale_200_live_summary.md` | main live summary |
| `outputs/validation/cninfo_a_class_erad_scale_200/reports/a_class_erad_scale_200_live_quality_report.csv` | main quality report |
| `outputs/validation/cninfo_a_class_erad_scale_200_failed_retry/reports/a_class_erad_scale_200_failed_retry_dryrun_report.csv` | retry dry-run report（7/7） |
| `outputs/validation/cninfo_a_class_erad_scale_200_failed_retry/reports/a_class_erad_scale_200_failed_retry_dryrun_summary.md` | retry dry-run summary |
| `outputs/validation/cninfo_a_class_erad_scale_200_failed_retry/reports/a_class_erad_scale_200_failed_retry_live_report.csv` | retry live report（0/7） |
| `outputs/validation/cninfo_a_class_erad_scale_200_failed_retry/reports/a_class_erad_scale_200_failed_retry_live_summary.md` | retry live summary |
| `outputs/validation/cninfo_a_class_erad_scale_200_failed_retry/reports/a_class_erad_scale_200_failed_retry_live_quality_report.csv` | retry quality report |

---

## Status Docs

| 路径 | 说明 |
|------|------|
| `CURRENT_STATUS.md` | A-class Era D final state |
| `PROJECT_MAP.md` | artifact navigation |

---

## Explicitly Excluded（see do-not-commit list）

- `outputs/validation/cninfo_a_class_erad_scale_200/raw_metadata/**`（**200** files · bulk）
- `outputs/validation/cninfo_a_class_erad_scale_200_failed_retry/raw_metadata/**`（**7** files · bulk）
- `outputs/validation/cninfo_a_class_erad_scale_200/_production_guard/**` · mock test temp trees
- Phase 3 / A3M017 production roots

---

## Approval Phrase（separate task）

```
I approve A-class Era D scale-200 explicit-path commit.
```

**NOT committed** · **NOT pushed** · **NOT verified**
