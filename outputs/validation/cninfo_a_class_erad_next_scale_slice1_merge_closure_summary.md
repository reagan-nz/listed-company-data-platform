# CNINFO A 类 Era D Next-Scale Slice1 — Merge Closure Summary

_生成时间：2026-07-13_

> **性质：** offline merge closure review · **CNINFO 0** · **无 live** · **无 further retry** · **不是 verified** · **不是 production_ready**

---

## Effective State

| 指标 | 值 |
|------|-----|
| universe executed（slice1 live） | **300/300** |
| **effective accepted final** | **294/300** |
| **unresolved final** | **6** |
| effective acceptance rate | **98%** |
| CNINFO（slice1 live，已发生） | **637** |
| closure review CNINFO | **0** |

---

## Merge Logic

| 来源 | 结果 | 并入 effective |
|------|------|----------------|
| slice1 live acceptable | **294** | **accepted_effective** |
| unresolved（6） | 不变 | **caveat retained** |

Slice1 live is authoritative. **No retry pass** was executed for slice1.

---

## Session Split

| Session | Range | Executed | Effective | Unresolved |
|---------|-------|----------|-----------|------------|
| Session 1 | AD2E201–350 | **150** | **145** | **5** |
| Session 2 | AD2E351–500 | **150** | **149** | **1** |
| Combined | AD2E201–500 | **300** | **294** | **6** |

---

## Unresolved Final（6）

| case_id | company_code | session | status | disposition |
|---------|--------------|---------|--------|-------------|
| AD2E216 | 601206 | session1 | not_found | accept_unresolved_with_caveat |
| AD2E270 | 603262 | session1 | not_found | accept_unresolved_with_caveat |
| AD2E284 | 603400 | session1 | not_found | accept_unresolved_with_caveat |
| AD2E308 | 603698 | session1 | not_found | accept_unresolved_with_caveat |
| AD2E323 | 000559 | session1 | network_error | accept_unresolved_with_caveat |
| AD2E373 | 002710 | session2 | not_found | accept_unresolved_with_caveat |

详见 [unresolved final ledger](cninfo_a_class_erad_next_scale_slice1_unresolved_final_ledger.csv) · [triage summary](cninfo_a_class_erad_next_scale_slice1_unresolved_triage_summary.md)。

---

## Cumulative Lineage（with scale-200）

| Metric | Value |
|--------|-------|
| scale-200 effective codes | **192** |
| slice1 effective codes | **294** |
| **cumulative effective company codes** | **486**（zero overlap） |
| cumulative case slots executed | **500** |
| scale-200 unresolved（side-track） | **8** |
| slice1 unresolved（side-track） | **6** |

见 [cumulative lineage summary](cninfo_a_class_erad_next_scale_slice1_cumulative_lineage_summary.md)。

---

## Closure Decision

**Close slice1 track with caveat NOW** at **294/300 effective accepted**.

见 [merge closure decision](cninfo_a_class_erad_next_scale_slice1_merge_closure_decision.md)。

---

## Artifacts

| 产物 | 路径 |
|------|------|
| effective accepted ledger | [cninfo_a_class_erad_next_scale_slice1_effective_accepted_ledger.csv](cninfo_a_class_erad_next_scale_slice1_effective_accepted_ledger.csv)（**294** rows） |
| unresolved final ledger | [cninfo_a_class_erad_next_scale_slice1_unresolved_final_ledger.csv](cninfo_a_class_erad_next_scale_slice1_unresolved_final_ledger.csv)（**6** rows） |
| live report（authoritative） | [a_class_erad_next_scale_slice1_live_report.csv](cninfo_a_class_erad_next_scale_slice1/reports/a_class_erad_next_scale_slice1_live_report.csv) |
| live execution summary | [cninfo_a_class_erad_next_scale_slice1_live_execution_summary.md](cninfo_a_class_erad_next_scale_slice1_live_execution_summary.md) |

---

## Gates

```text
a_class_erad_next_scale_slice1_merge_closure_gate = PASS_WITH_CAVEAT
a_class_erad_next_scale_slice1_execution_gate = PASS_WITH_CAVEAT
```

**NOT bare PASS** · **NOT verified** · **NOT production_ready**

---

## Next Recommended A-Class Task

**Commit boundary review**（explicit-path · offline）for slice1 — then human approve explicit-path commit（separate phrase）.
