# CNINFO A 类 Era D — Cumulative Lineage Summary（Scale-200 + Slice1）

_生成时间：2026-07-13_

> **offline lineage reference** · **CNINFO = 0** · **不是 verified**

---

## Numbering Convention（explicit）

| Metric | Definition | Value |
|--------|------------|-------|
| **Cumulative effective company codes** | scale-200 effective **192** + slice1 effective **294**（zero code overlap） | **486** |
| **Cumulative case slots executed** | scale-200 **200** + slice1 **300** case_ids | **500** |
| **Cumulative acceptable cases** | scale-200 **192** + slice1 **294** | **486/500** |
| **Cumulative unresolved cases** | scale-200 **8** + slice1 **6**（side-track only） | **14** |

**Note:** **486** is the authoritative cumulative **effective company-code lineage** count. **500** is cumulative **executed case slots** toward the staged ~500 target. Do **not** conflate with 492 — that figure does not apply to A-class arithmetic (192+294=**486**, not 492).

---

## Staged Expansion Path

| Stage | Case range | Executed | Effective accepted | Unresolved |
|-------|------------|----------|-------------------|------------|
| **Scale-200** | AD2E001–200 | **200** | **192** | **8** |
| **Next-scale slice1** | AD2E201–500 | **300** | **294** | **6** |
| **Cumulative** | AD2E001–500 | **500** | **486** | **14** |

**Progress toward staged ~500 company-code target:** **486/500** effective codes (**97.2%**).

---

## Side-Track Inventory（not in effective）

### Scale-200 unresolved（8 · unchanged）

AD2E066 · AD2E088 · AD2E119 · AD2E121 · AD2E122 · AD2E146 · AD2E185 · AD2E190

Ledger: [scale-200 unresolved final](../cninfo_a_class_erad_scale_200_unresolved_final_ledger.csv)

### Slice1 unresolved（6 · this package）

AD2E216 · AD2E270 · AD2E284 · AD2E308 · AD2E323 · AD2E373

Ledger: [slice1 unresolved final](cninfo_a_class_erad_next_scale_slice1_unresolved_final_ledger.csv)

---

## Overlap Lint

- scale-200 effective **192** codes ∩ slice1 effective **294** codes = **∅**（verified at closure）
- slice1 universe ∩ scale-200 universe = **∅**（planning + live）

---

## CNINFO（historical · already occurred）

| Track | CNINFO |
|-------|--------|
| scale-200 main live | **423** |
| scale-200 isolated retry | **21** |
| slice1 live（2 sessions） | **637** |
| **This closure review** | **0** |
