# CNINFO A 类 Era D ~200 — Failed-Case Triage Summary

_生成时间：2026-07-10_

> **offline triage only** · **CNINFO 0** · **无 live** · **不是 verified**

---

## Live Baseline（historical · do not rerun）

| 指标 | 值 |
|------|-----|
| acceptable | **192/200** |
| failed | **8**（all `not_found` · all **new_erad**） |
| retained | **50/50** acceptable |
| new cohort | **142/150** acceptable |
| execution gate | **`a_class_erad_scale_200_execution_gate = PASS_WITH_CAVEAT`** |
| CNINFO（live） | **423** |

**Retained cohort clean：** 50/50 acceptable · **zero failures in retained_phase3**

**Failures concentrated in new_erad：** 8/150 new cohort failures · 0/50 retained failures

---

## Triage Counts by `likely_cause`

| likely_cause | count | case_ids |
|--------------|-------|----------|
| network_or_empty_response | **4** | AD2E066, AD2E088, AD2E119, AD2E190 |
| matching_logic_miss | **3** | AD2E121, AD2E122, AD2E185 |
| true_not_found | **1** | AD2E146 |

**Not observed in this triage：** orgId_issue · title_routing_gap · other

---

## Retry Recommendation

| retry_recommended | count |
|-------------------|-------|
| **yes** | **7** |
| **no** | **1**（AD2E146 · defer） |

**Proposed isolated retry universe size：** **7**

---

## Per-Case Summary

| case_id | code | report_type | period | likely_cause | retry |
|---------|------|-------------|--------|--------------|-------|
| AD2E066 | 600930 | annual_report | 2024-12-31 | network_or_empty_response | yes |
| AD2E088 | 001393 | annual_report | 2024-12-31 | network_or_empty_response | yes |
| AD2E119 | 603370 | annual_report | 2024-12-31 | network_or_empty_response | yes |
| AD2E121 | 603737 | annual_report | 2024-12-31 | matching_logic_miss | yes |
| AD2E122 | 688636 | annual_report | 2024-12-31 | matching_logic_miss | yes |
| AD2E146 | 688755 | annual_report | 2024-12-31 | true_not_found | **no** |
| AD2E185 | 600849 | quarterly_report_q1 | 2024-03-31 | matching_logic_miss | yes |
| AD2E190 | 603409 | quarterly_report_q1 | 2024-03-31 | network_or_empty_response | yes |

---

## Evidence Source

- Read-only: `a_class_erad_scale_200_live_report.csv`
- Read-only: `raw_metadata/AD2E*.json`（8 failed snapshots present）

**Do not claim the 8 are verified found** — all remain `not_found` until any future approved retry.

---

## Gates

```text
a_class_erad_scale_200_failed_case_triage_gate = PASS_OFFLINE
a_class_erad_scale_200_isolated_retry_planning_gate = READY_FOR_APPROVAL
a_class_erad_scale_200_execution_gate = PASS_WITH_CAVEAT  (historical · unchanged)
```

**不是 PASS live** · **不是 verified** · **不是 production_ready**

---

## Artifacts

| 产物 | 路径 |
|------|------|
| triage ledger | [cninfo_a_class_erad_scale_200_failed_case_triage_ledger.csv](cninfo_a_class_erad_scale_200_failed_case_triage_ledger.csv) |
| retry universe draft | [cninfo_a_class_erad_scale_200_isolated_retry_universe_draft.csv](cninfo_a_class_erad_scale_200_isolated_retry_universe_draft.csv) |
| retry plan | [cninfo_a_class_erad_scale_200_isolated_retry_plan.md](../../plans/cninfo_a_class_erad_scale_200_isolated_retry_plan.md) |

---

## Next Step

See [next-step recommendation](cninfo_a_class_erad_scale_200_failed_case_triage_next_step_recommendation.md)
