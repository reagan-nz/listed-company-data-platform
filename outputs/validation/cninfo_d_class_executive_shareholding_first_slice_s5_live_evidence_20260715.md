# CNINFO D 类 executive_shareholding — S5 Live Evidence

_生成时间：2026-07-15 08:48:49 UTC_

> **性质：** S5 bounded first-slice live · **CNINFO calls = 5** · **NOT verified** · **NOT production_ready**
>
> **任务 ID：** D-FM-01 / S5
>
> **Standing auth：** D mission · dry-run green 后 bounded live（cap ≤20）

---

## 1. Results

| 指标 | 值 |
|------|-----|
| cases | **5** |
| acceptable | **4/5** |
| CNINFO calls | **5** |
| total cap | ≤20 |
| execution gate | **PASS_WITH_CAVEAT** |
| query | timeMark=oneMonth · varyType=b |

## 2. Case Outcomes

| case_id | company | expected | retrieval | records | acceptable | failure_type |
|---------|---------|----------|-----------|---------|------------|--------------|
| DES001 | 002415 | captured_normal_or_needs_review | empty_but_valid | 0 | no | expectation_mismatch |
| DES002 | 000895 | captured_normal_or_empty_but_valid | empty_but_valid | 0 | yes | — |
| DES003 | 600000 | captured_normal_or_empty_but_valid | empty_but_valid | 0 | yes | — |
| DES004 | 000550 | captured_normal_or_empty_but_valid | empty_but_valid | 0 | yes | — |
| DES005 | 601988 | empty_but_valid | empty_but_valid | 0 | yes | — |

## 3. Caveat

- **DES001**（002415）期望 `captured_normal_or_needs_review`，实际 `empty_but_valid` → `expectation_mismatch`
- 稀疏窗口全案零行；与 prior shareholder_change DSC004 sparse-day 模式同类
- **不是** bare PASS · **不是** verified

## 4. Artifacts

- live report / quality / summary under `cninfo_d_class_executive_shareholding_first_slice/reports/`
- outcome ledger: `cninfo_d_class_executive_shareholding_first_slice_live_outcome_ledger.csv`
- live_snapshots: DES001–DES005（local-only）

## 5. Gates

```text
d_class_executive_shareholding_first_slice_live_path_gate = READY_FOR_APPROVAL
d_class_executive_shareholding_first_slice_execution_gate = PASS_WITH_CAVEAT
cninfo_calls = 5
verified = false
production_ready = false
```
