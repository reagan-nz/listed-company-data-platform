# CNINFO D 类 equity_pledge First-Slice — Safe-to-Commit List

_生成时间：2026-07-10_

> **性质：** explicit-path commit 准备清单 only · **本任务不执行 git commit** · 需单独人工批准

**合计 safe-to-commit paths：~33**

---

## 1. Source Files（lab）

| # | 路径 | 说明 |
|---|------|------|
| 1 | `lab/run_cninfo_d_class_tiny_live_validation.py` | 共享 D-class runner；含 equity_pledge first-slice dry-run + live path + approval guards |
| 2 | `lab/test_cninfo_d_class_equity_pledge_first_slice_runner.py` | runner 测试 **20/20 PASS** |
| 3 | `lab/test_cninfo_d_class_equity_pledge_first_slice_live_path.py` | live-path mock 测试 **22/22 PASS** |

**caveat：** 共享 runner 亦服务 known-event / margin_trading / disclosure / block_trade / RSU / tiny-live；commit 时勿回归其他模式测试。

**合计 equity_pledge first-slice tests：** **42/42 PASS**

---

## 2. Plans

| # | 路径 | 说明 |
|---|------|------|
| 4 | `plans/cninfo_d_class_equity_pledge_first_slice_plan.md` | 第一切片规划 |
| 5 | `plans/cninfo_d_class_equity_pledge_first_slice_command_draft.md` | 命令草案（caveat 标签保留） |
| 6 | `plans/cninfo_d_class_equity_pledge_first_slice_closure_review.md` | closure review |
| 7 | `plans/cninfo_d_class_equity_pledge_first_slice_commit_boundary_review.md` | commit boundary review |

---

## 3. Validation — Universe & Approval

| # | 路径 |
|---|------|
| 8 | `outputs/validation/cninfo_d_class_equity_pledge_first_slice_universe_draft.csv` |
| 9 | `outputs/validation/cninfo_d_class_equity_pledge_first_slice_approval_checklist.md` |
| 10 | `outputs/validation/cninfo_d_class_equity_pledge_first_slice_approval_summary.md` |

---

## 4. Validation — Runner & Live Path

| # | 路径 |
|---|------|
| 11 | `outputs/validation/cninfo_d_class_equity_pledge_first_slice_runner_extension_summary.md` |
| 12 | `outputs/validation/cninfo_d_class_equity_pledge_first_slice_live_path_summary.md` |
| 13 | `outputs/validation/cninfo_d_class_equity_pledge_first_slice_live_execution_summary.md` |
| 14 | `outputs/validation/cninfo_d_class_equity_pledge_first_slice_live_outcome_ledger.csv` |

---

## 5. Validation — Dry-Run & Live Reports（CSV/MD only）

| # | 路径 |
|---|------|
| 15 | `outputs/validation/cninfo_d_class_equity_pledge_first_slice/reports/d_class_equity_pledge_first_slice_dryrun_report.csv` |
| 16 | `outputs/validation/cninfo_d_class_equity_pledge_first_slice/reports/d_class_equity_pledge_first_slice_dryrun_summary.md` |
| 17 | `outputs/validation/cninfo_d_class_equity_pledge_first_slice/reports/d_class_equity_pledge_first_slice_live_report.csv` |
| 18 | `outputs/validation/cninfo_d_class_equity_pledge_first_slice/reports/d_class_equity_pledge_first_slice_live_summary.md` |
| 19 | `outputs/validation/cninfo_d_class_equity_pledge_first_slice/reports/d_class_equity_pledge_first_slice_quality_report.csv` |

---

## 6. Validation — Closure & Boundary

| # | 路径 |
|---|------|
| 20 | `outputs/validation/cninfo_d_class_equity_pledge_first_slice_closure_summary.md` |
| 21 | `outputs/validation/cninfo_d_class_equity_pledge_first_slice_closure_decision.md` |
| 22 | `outputs/validation/cninfo_d_class_equity_pledge_first_slice_closure_metrics.csv` |
| 23 | `outputs/validation/cninfo_d_class_equity_pledge_first_slice_effective_result.csv` |
| 24 | `outputs/validation/cninfo_d_class_equity_pledge_first_slice_final_caveat_ledger.csv` |
| 25 | `outputs/validation/cninfo_d_class_equity_pledge_first_slice_post_closure_next_step_recommendation.md` |
| 26 | `outputs/validation/cninfo_d_class_equity_pledge_first_slice_commit_boundary_summary.md` |
| 27 | `outputs/validation/cninfo_d_class_equity_pledge_first_slice_safe_to_commit_list.md` |
| 28 | `outputs/validation/cninfo_d_class_equity_pledge_first_slice_do_not_commit_list.md` |
| 29 | `outputs/validation/cninfo_d_class_equity_pledge_first_slice_commit_message_draft.md` |

---

## 7. Status Docs（D-class equity_pledge 段增量）

| # | 路径 |
|---|------|
| 30 | `CURRENT_STATUS.md` |
| 31 | `PROJECT_MAP.md` |
| 32 | `plans/eraD_execution_plan.md` |
| 33 | `outputs/validation/cninfo_d_class_equity_pledge_first_slice_next_step_recommendation.md` |

---

## 8. Explicit Exclusions（见 do-not-commit list）

- `live_snapshots/*.json` — **local-only by default**
- `_mock_live_tests/` — mock test temp dirs
- next-component planning artifacts · Phase1 fixtures · unrelated track roots

---

## 9. Commit Scope Recommendation

建议 **单独 explicit-path commit** 仅含上表 **~33** 条路径。

**不** 与无关 A/B/C 工作区变更混 commit。

commit message 须保留：**PASS_WITH_CAVEAT** · **DEP004 caveat** · not verified · not production_ready。

---

## 10. Gate

```text
d_class_equity_pledge_first_slice_commit_boundary_gate = READY_FOR_COMMIT_REVIEW
d_class_equity_pledge_first_slice_closure_gate = PASS_WITH_CAVEAT
d_class_equity_pledge_first_slice_execution_gate = PASS_WITH_CAVEAT
```

**commit 仍需单独人工批准** · **本任务不 commit**
