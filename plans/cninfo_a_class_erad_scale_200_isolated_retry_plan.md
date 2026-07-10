# CNINFO A 类 Era D ~200 — Isolated Retry Plan

_生成时间：2026-07-10_

> **offline planning only** · **CNINFO 0** · **NOT APPROVED live** · **不是 verified**

---

## Scope

| 项 | 值 |
|----|-----|
| parent execution | Era D ~200 live · **192/200 acceptable** · gate **`PASS_WITH_CAVEAT`** |
| failed cases triaged | **8** |
| retry universe draft | **7**（retry_recommended=yes） |
| deferred | **1**（AD2E146 · true_not_found · retry=no） |
| cohort | **new_erad only**（retained 50/50 clean） |
| matching_logic | **v2**（unchanged） |
| metadata only | **yes** · 无 PDF / OCR / extraction |

---

## Retry Universe

Source: [cninfo_a_class_erad_scale_200_isolated_retry_universe_draft.csv](../outputs/validation/cninfo_a_class_erad_scale_200_isolated_retry_universe_draft.csv)

| likely_cause bucket | cases | retry_strategy |
|---------------------|-------|----------------|
| network_or_empty_response | 4 | `broadened_date_window_v2_requery` |
| matching_logic_miss | 3 | `v2_rematch_*_expanded_candidates` |

---

## Request Cap Estimate

| 项 | 值 |
|----|-----|
| retry cases | **7** |
| planned requests per case | **2** |
| planned requests total | **14** |
| cap reference | parent Era D cap **480** · retry isolated cap **≤32**（planning） |

---

## Output Root Isolation

**Proposed retry output root（mandatory）：**

```text
outputs/validation/cninfo_a_class_erad_scale_200_failed_retry/
```

**Must NOT write：**

- `outputs/validation/cninfo_a_class_erad_scale_200/` main live root（except lineage notes in planning docs）
- Phase 1 / Phase 2 / Phase 3 expansion / A3M017 retry production roots
- B / C / D validation prefixes
- `outputs/harvest`

**May read（lineage only）：**

- Main Era D live report + raw_metadata for failed case context

---

## Retained Cohort

Retained **50/50** acceptable — **no retry** · **no Phase 3 root rewrite**

---

## Explicit Prohibitions

- No rerun full Era D 200 live
- No Phase 1/2/3/A3M017 production-root rerun
- No amend **bbc15c3** / **cb9f3fc**
- No PDF / DB / MinIO / RAG
- No verified / production_ready / bare PASS
- Do not claim 8 failures are verified found

---

## Future Live Threshold（document only）

If isolated retry live executed: **≥6/7 acceptable** → `PASS_WITH_CAVEAT` for retry execution gate（planning suggestion only）

---

## Gates

```text
a_class_erad_scale_200_failed_case_triage_gate = PASS_OFFLINE
a_class_erad_scale_200_isolated_retry_planning_gate = READY_FOR_APPROVAL
```

**NOT APPROVED live** · **NOT verified**

---

## Next Implementation Steps（future · separate approval）

1. Runner extension: `--erad-a-scale-200-failed-retry` or mode flag under existing runner
2. Dry-run + mock tests（CNINFO 0）
3. Human approval with exact phrase
4. Isolated retry live（7 cases max）

See [command draft](cninfo_a_class_erad_scale_200_isolated_retry_command_draft.md)
