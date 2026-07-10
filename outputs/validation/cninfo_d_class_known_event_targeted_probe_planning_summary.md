# CNINFO D 类 Known Event Targeted Probe — Planning Summary

_生成时间：2026-07-09_

> **性质：** Option A 规划包摘要 · **CNINFO calls = 0** · **无 live** · **无实现** · **NOT APPROVED**

**人工决策：** Option A planning only · 不实现 targeted probe · 不 run targeted probe live

---

## 1. Why Targeted Probe Exists

Replacement bounded live（CNINFO **40**）双 case 均为 `empty_but_valid_after_budget`，而人工披露证据存在。Targeted probe 以 **anchor event date** 为中心检验 metadata 端点是否可返回公司级行 — **假设检验**，非披露文本推断。

---

## 2. Target Cases

| targeted_probe_id | replacement | company | component | anchor_date | cap |
|-------------------|-------------|---------|-----------|-------------|-----|
| DLC003R-T01 | DLC003R | 688671 碧兴物联 | restricted_shares_unlock | 2024-02-19 | 12 |
| DLC006R-T01 | DLC006R | 301259 艾布鲁 | shareholder_change | 2024-07-16 | 12 |

**target case count：2**

---

## 3. Request Cap

| 项 | 值 |
|----|-----|
| DLC003R | ≤ **12** |
| DLC006R | ≤ **12** |
| **total** | ≤ **24** |

---

## 4. Output Root

```text
outputs/validation/cninfo_d_class_known_event_targeted_probe/
```

---

## 5. Artifacts

| 项 | 路径 |
|----|------|
| plan | [cninfo_d_class_known_event_targeted_probe_plan.md](../plans/cninfo_d_class_known_event_targeted_probe_plan.md) |
| universe draft | [cninfo_d_class_known_event_targeted_probe_universe_draft.csv](cninfo_d_class_known_event_targeted_probe_universe_draft.csv) |
| approval checklist | [cninfo_d_class_known_event_targeted_probe_approval_checklist.md](cninfo_d_class_known_event_targeted_probe_approval_checklist.md) |
| command draft | [cninfo_d_class_known_event_targeted_probe_command_draft.md](../plans/cninfo_d_class_known_event_targeted_probe_command_draft.md) |
| runner design | [cninfo_d_class_known_event_targeted_probe_runner_extension_design.md](../plans/cninfo_d_class_known_event_targeted_probe_runner_extension_design.md) |
| prior failure review | [cninfo_d_class_known_event_replacement_live_failure_review_summary.md](cninfo_d_class_known_event_replacement_live_failure_review_summary.md) |

---

## 6. Approval Status

```text
approval_status = NOT_APPROVED
approved_for_implementation = false
approved_for_live = false
```

---

## 7. Runner Support Status

| 项 | 状态 |
|----|------|
| `--known-event-targeted-probe` | **未实现** |
| `--approve-d-class-known-event-targeted-probe` | **未实现** |
| runner extension design | [已准备](../plans/cninfo_d_class_known_event_targeted_probe_runner_extension_design.md) |

---

## 8. Safety Confirmations

| 项 | 状态 |
|----|------|
| CNINFO calls | **0** |
| live / rerun / harvest | **0** |
| old DLC003/DLC006 | **excluded** |
| replacement live reports | **untouched** |
| original / calibrated universe | **untouched** |
| v1/v2 execution reports | **untouched** |
| PDF/OCR/extraction/DB/MinIO/RAG | **0** |
| verified / production_ready | **not marked** |

---

## 9. Gates

```text
d_class_known_event_targeted_probe_planning_gate = READY_FOR_APPROVAL
d_class_known_event_replacement_validation_execution_gate = FAIL_REVIEW_REQUIRED
d_class_known_event_replacement_live_failure_review_gate = READY_FOR_HUMAN_DECISION
```

**NOT PASS** · **NOT live_ready** · **NOT verified** · **NOT production_ready**

---

## 10. Next Recommended Task

人工评审 targeted probe planning package → 批准后 **离线实现** runner extension + dry-run tests（**无 live**）
