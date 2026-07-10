# CNINFO B 类 Era D ~200 Safe-to-Commit List

_生成时间：2026-07-10_

> **性质：** explicit-path commit boundary · **本任务不执行 commit** · **须单独批准**  
> **Approximate count：~30 paths**（不含 bulk raw_metadata / quality）

---

## Source / Runner

| 路径 | 说明 |
|------|------|
| `lab/run_cninfo_b_class_phase25_expansion_validation.py` | Era D `--erad-b-scale-200` runner extension + live path（shared B-class runner） |

---

## Tests

| 路径 | 说明 |
|------|------|
| `lab/test_cninfo_b_class_erad_scale_200_runner.py` | dry-run runner tests（15/15 PASS） |
| `lab/test_cninfo_b_class_erad_scale_200_live_path.py` | live-path mock tests（17/17 PASS） |

---

## Plans

| 路径 | 说明 |
|------|------|
| `plans/cninfo_b_class_erad_scale_200_plan.md` | Era D ~200 expansion plan |
| `plans/cninfo_b_class_erad_scale_200_command_draft.md` | command draft |
| `plans/cninfo_b_class_erad_scale_200_commit_boundary_review.md` | **本 commit boundary review** |
| `plans/eraD_execution_plan.md` | §9.5 B-class Era D status（section update only） |

---

## Validation — Universe / Planning / Runner / Live / Closure

| 路径 | 说明 |
|------|------|
| `outputs/validation/cninfo_b_class_erad_scale_200_universe_draft.csv` | 200-case universe |
| `outputs/validation/cninfo_b_class_erad_scale_200_planning_summary.md` | planning summary |
| `outputs/validation/cninfo_b_class_erad_scale_200_runner_extension_summary.md` | runner extension summary |
| `outputs/validation/cninfo_b_class_erad_scale_200_live_path_summary.md` | live path summary |
| `outputs/validation/cninfo_b_class_erad_scale_200_live_path_test_summary.md` | live-path test summary |
| `outputs/validation/cninfo_b_class_erad_scale_200_live_execution_summary.md` | live execution summary |
| `outputs/validation/cninfo_b_class_erad_scale_200_closure_summary.md` | closure summary |
| `outputs/validation/cninfo_b_class_erad_scale_200_closure_decision.md` | closure decision |
| `outputs/validation/cninfo_b_class_erad_scale_200_unresolved_case_ledger.csv` | **2-row unresolved ledger**（BD2E090/BD2E092） |
| `outputs/validation/cninfo_b_class_erad_scale_200_optional_retry_brief.md` | optional retry stub（NOT APPROVED） |
| `outputs/validation/cninfo_b_class_erad_scale_200_approval_checklist.md` | approval checklist |
| `outputs/validation/cninfo_b_class_erad_scale_200_next_step_recommendation.md` | next-step recommendation |
| `outputs/validation/cninfo_b_class_erad_scale_200_commit_boundary_summary.md` | boundary summary |
| `outputs/validation/cninfo_b_class_erad_scale_200_safe_to_commit_list.md` | **本清单** |
| `outputs/validation/cninfo_b_class_erad_scale_200_do_not_commit_list.md` | do-not-commit list |
| `outputs/validation/cninfo_b_class_erad_scale_200_commit_message_draft.md` | commit message draft |

---

## Validation — Reports（compact · metadata summaries only）

| 路径 | 说明 |
|------|------|
| `outputs/validation/cninfo_b_class_erad_scale_200/reports/b_class_erad_scale_200_dryrun_report.csv` | dry-run report（200/200） |
| `outputs/validation/cninfo_b_class_erad_scale_200/reports/b_class_erad_scale_200_dryrun_summary.md` | dry-run summary |
| `outputs/validation/cninfo_b_class_erad_scale_200/reports/b_class_erad_scale_200_report.csv` | live report（198/200 acceptable） |
| `outputs/validation/cninfo_b_class_erad_scale_200/reports/b_class_erad_scale_200_summary.md` | live summary |
| `outputs/validation/cninfo_b_class_erad_scale_200/reports/b_class_erad_scale_200_quality_report.csv` | quality report |

---

## Status Docs

| 路径 | 说明 |
|------|------|
| `CURRENT_STATUS.md` | B-class Era D final state |
| `PROJECT_MAP.md` | artifact navigation |

---

## Explicitly Excluded（see do-not-commit list）

- `outputs/validation/cninfo_b_class_erad_scale_200/raw_metadata/**`（**200** files · bulk）
- `outputs/validation/cninfo_b_class_erad_scale_200/quality/**`（**200** files · bulk）
- `_mock_test/` · `_mock_live_test/` temp trees

---

## Commit Still Requires Separate Approval

```text
b_class_erad_scale_200_commit_boundary_gate = READY_FOR_COMMIT_REVIEW
```

Phrase example:

```
I approve B-class Era D scale-200 explicit-path commit.
```

**NOT verified** · **NOT production_ready** · **no commit in this task**
