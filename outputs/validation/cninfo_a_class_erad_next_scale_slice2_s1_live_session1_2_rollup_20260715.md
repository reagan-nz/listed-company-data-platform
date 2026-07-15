# A-class Era D Next-Scale Slice2 S1 — Session1+2 Rollup Note（未 verified）

_日期：2026-07-15 · Run 12 · a-class-executor_

> **性质：** optional rollup · 两场 bounded live 结果汇总 · **不是 verified** · **不是 production_ready** · **不是 PASS** · **未 commit / 未 push**
>
> 本文件仅合并 session 证据计数，**不构成**正式 gate 认证或 production 放行。

## Combined Scope

| 项 | 值 |
|----|-----|
| track | A-class Era D next-scale slice2 S1 |
| cases | AD2E501:AD2E600（100） |
| session1 | AD2E501:AD2E550 · evidence `..._live_session1_20260715.md` |
| session2 | AD2E551:AD2E600 · evidence `..._live_session2_20260715.md` |
| HEAD（session2 起点） | `594866a` |
| request cap | ≤ **240** |

## Combined Counts（observational）

| 指标 | Session1 | Session2 | Combined |
|------|----------|----------|----------|
| executed | 50 | 50 | **100** |
| acceptable | 50 | 47 | **97** |
| failed / not_found | 0 | 3 | **3** |
| needs_review | 0 | 3 | **3** |
| CNINFO requests | 100 | 103 | **203** |
| pdf_downloaded | 0 | 0 | **0** |

### Combined not-found

- AD2E578（688605 · semi_annual_report · 2024-06-30）
- AD2E590（688688 · quarterly_report_q3 · 2024-09-30）
- AD2E598（688758 · semi_annual_report · 2024-06-30）

## Gate reading（observational only）

```text
per-session execution_gate (s1) = PASS_WITH_CAVEAT   # 50/50 ≥ 45/50
per-session execution_gate (s2) = PASS_WITH_CAVEAT   # 47/50 ≥ 45/50
combined 100-case threshold     = ≥90/100 → PASS_WITH_CAVEAT candidate (97 ≥ 90)
live_path_gate                  = READY_FOR_APPROVAL
```

- **不是 PASS** · **不是 verified** · **不是 production_ready**
- 正式 combined gate / commit 由 controller 裁定

## Artifacts

| 类 | 路径 |
|----|------|
| session1 archive | `outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1/reports/session1/` |
| session2 archive | `outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1/reports/session2/` |
| raw_metadata | `.../raw_metadata/AD2E501.json` … `AD2E600.json`（100 files） |
| session1 evidence | `outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1_live_session1_20260715.md` |
| session2 evidence | `outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1_live_session2_20260715.md` |
| this rollup | `outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1_live_session1_2_rollup_20260715.md` |

## Capability（observational）

**CAPABILITY_ADVANCED** — slice2 S1 100-case live metadata path 两场均已跑完；combined acceptable **97/100**（≥90 阈值候选）。**未 verified。**
