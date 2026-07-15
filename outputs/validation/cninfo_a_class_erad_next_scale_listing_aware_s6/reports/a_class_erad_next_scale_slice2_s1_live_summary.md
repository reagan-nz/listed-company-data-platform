# CNINFO A 类 Era D Listing-aware S6 — Live 执行摘要（merged）

_生成时间：2026-07-15 12:26:04 UTC_

> **性质：** listing-aware S6 live metadata validation · **无 PDF** · **不是 verified**
> **合并：** session_full50（含 18×network_timeout）+ retry AD2E801–810 + retry AD2E819–826

| 项 | 值 |
|----|-----|
| cases | 50（AD2E801–850） |
| executed | 50 |
| acceptable | 50 |
| retrieval found | 50 |
| first-pass CNINFO | 71 |
| retry CNINFO | 40（22+18） |
| CNINFO total（本 turn） | 111 |
| per-row cninfo_request_count sum（merged） | 108 |
| orgid_fallback（final merged） | hits 见各案 notes · retry 批 hits=0 |
| execution gate | `PASS_WITH_CAVEAT` |
| acceptance threshold | ≥45/50 → PASS_WITH_CAVEAT |
| output isolation | `/Users/zhao/Desktop/97/实操/数据收集测试/listed_company_data_collector/outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s6` |
| closed S1–S5 live roots mutated | **no** |

## Gates

```text
a_class_erad_next_scale_slice2_s1_live_path_gate = READY_FOR_APPROVAL
a_class_erad_next_scale_slice2_s1_execution_gate = PASS_WITH_CAVEAT
```

## Retry note

- First pass: 32/50 acceptable · 18× `network_timeout`（cninfo_request_count=0）→ `FAIL_REVIEW_REQUIRED`
- Isolated retry under S6 sub-roots recovered **18/18** found/pass
- Merged canonical reports overwrite first-pass not_found rows with retry PASS rows

**不是 PASS** · **不是 verified** · **不是 production_ready**
