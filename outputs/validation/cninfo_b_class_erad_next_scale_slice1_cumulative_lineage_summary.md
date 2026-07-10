# CNINFO B 类 Era D — Cumulative Lineage Summary（Scale-200 + Slice1）

_生成时间：2026-07-10_

> **性质：** offline lineage reference · **CNINFO = 0** · **不是 verified**

---

## Staged Expansion Path

| Stage | Case range | Effective accepted | Unresolved / side-track |
|-------|------------|-------------------|-------------------------|
| **Scale-200** | BD2E001–200 | **198/200** | **2**（BD2E090 · BD2E092 · `network_error`） |
| **Next-scale slice1** | BD2E201–500 | **300/300** | **0 failed** · **9 edge caveat** |
| **Cumulative** | BD2E001–500 | **498 effective** | **2 side-track** + **9 caveat** |

**Toward ~500 staged target：** **498/500** effective accepted（excluding side-track only）。

---

## Cohort Detail

### Scale-200（reference · not rerun）

| Cohort | Total | Effective | Notes |
|--------|-------|-----------|-------|
| retained_phase3（BD2E001–100） | 100 | **98** | BD2E090/092 network_error |
| new_expansion（BD2E101–200） | 100 | **100** | — |

Commit：`e738fa9` · gate `b_class_erad_scale_200_commit_gate = PASS_WITH_CAVEAT` · **NOT pushed**

### Slice1（fresh_metadata only）

| Cohort | Total | Effective | Edge caveat |
|--------|-------|-----------|-------------|
| next_scale_slice1（BD2E201–500） | 300 | **300** | 9（8 empty + 1 not_found） |

All slice1 cases：`retained_evidence_mode=fresh_metadata` · scale-200 lineage reference only.

---

## Side-Track（not in slice1 · not merged into slice1 ledger）

| case_id | company_code | source | failure |
|---------|--------------|--------|---------|
| BD2E090 | 000807 | scale-200 retained | network_error |
| BD2E092 | 300033 | scale-200 retained | network_error |

Optional 2-case retry：**DEFERRED** · separate approval.

---

## Overlap Check

- Slice1 universe（BD2E201–500）vs scale-200（BD2E001–200）：**0 overlap**
- BD2E090/092：**not in slice1 universe**

---

## Request Budget（live，已发生）

| Stage | CNINFO | Cap |
|-------|--------|-----|
| scale-200 live | **397** | ≤480 |
| slice1 live | **600** | ≤720 |
| **Total live（Era D B-class）** | **997** | — |

Closure / lineage review CNINFO：**0**

---

## Gates（unchanged for scale-200）

```text
b_class_erad_scale_200_commit_gate = PASS_WITH_CAVEAT
b_class_erad_next_scale_slice1_execution_gate = PASS_WITH_CAVEAT
b_class_erad_next_scale_slice1_merge_closure_gate = PASS_WITH_CAVEAT
```

**NOT verified** · **NOT production_ready**
