# CNINFO A 类 Era D ~200 — Merge Closure Decision

_生成时间：2026-07-10_

> **offline decision record** · **CNINFO 0** · **无 live** · **无 commit**

---

## Decision

**CLOSE Era D ~200 metadata expansion track with caveat NOW.**

| 项 | 值 |
|----|-----|
| effective accepted | **192/200** |
| unresolved final | **8** |
| merge closure gate | **`a_class_erad_scale_200_merge_closure_gate = PASS_WITH_CAVEAT`** |
| verified | **no** |
| production_ready | **no** |

---

## Rationale

1. **Main live** achieved **192/200** acceptable with gate **`PASS_WITH_CAVEAT`**（CNINFO **423**）。
2. **Isolated retry live** executed on **7** triage-recommended cases; **0/7** recovered（CNINFO **21**）；gate **`FAIL_REVIEW_REQUIRED`**。
3. **AD2E146** deferred at triage（`true_not_found` · filing-delay hypothesis）；excluded from retry universe。
4. Merge does **not** improve effective count; **192/200** is final for this track.
5. Retained Phase 3 cohort **50/50** intact; all failures confined to **new_erad**（8 unresolved）。

---

## Actions Taken（this package）

- Produced effective accepted ledger（**192** rows · `accepted_effective`）
- Produced unresolved final ledger（**8** rows · final disposition assigned）
- Recorded merge closure summary + this decision
- **No CNINFO** · **no live** · **no retry execution**

---

## Actions NOT Taken

| 项 | 状态 |
|----|------|
| Schedule another live retry | **NO** |
| Full Era D 200 live rerun | **NO** |
| Phase 3 / A3M017 root mutation | **NO** |
| PDF / OCR / extraction | **NO** |
| verified / production_ready labeling | **NO** |
| commit / push | **NO** |
| amend bbc15c3 / cb9f3fc | **NO** |

---

## Unresolved Disposition Summary

| final_disposition | count | case_ids |
|-------------------|-------|----------|
| accept_unresolved_with_caveat | **4** | AD2E066 · AD2E088 · AD2E119 · AD2E190 |
| matching_logic_followup_later | **3** | AD2E121 · AD2E122 · AD2E185 |
| defer_filing_delay | **1** | AD2E146 |

All **retry_again = no** in this package.

---

## Optional Later（separate scope · NOT in this package）

**Matching-logic investigation offline** for AD2E121 / AD2E122 / AD2E185:

- Use retry `raw_metadata` under `cninfo_a_class_erad_scale_200_failed_retry/raw_metadata/`
- Offline analysis only; **no CNINFO** unless separately approved
- Does **not** block Era D track closure at **192/200**

**AD2E146 filing-delay follow-up** — monitor-only; no live retry scheduled.

---

## Historical Gates（preserved）

```text
a_class_erad_scale_200_execution_gate = PASS_WITH_CAVEAT
a_class_erad_scale_200_isolated_retry_execution_gate = FAIL_REVIEW_REQUIRED
```

---

## Next Step

**Commit boundary review**（explicit-path · offline）— Era D ~200 main + retry reports/summaries/ledgers; exclude bulk `raw_metadata/`（main **200** + retry **7**）unless human separately scopes inclusion.
