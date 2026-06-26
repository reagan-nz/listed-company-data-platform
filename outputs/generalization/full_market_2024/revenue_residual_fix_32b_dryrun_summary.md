# Revenue residual fix #32b dry-run summary

_Generated: 2026-06-26 | Read-only diagnosis; no profile writes_

## Verdict: **PASS**

## 1. Scope and guardrails

- **Universe:** 57 revenue strict-wrong field-cells (48 issuers) from `#32` inventory
- **Fields:** `revenue_by_region` (38) + `revenue_by_segment` (19)
- **Mode:** Read-only harness experiments; no apply, no full refresh, no CNINFO/SQLite
- **Non-fin headline 9.43/11:** unchanged; no `strict_audit_summary.md` update
- **R&D extraction:** not touched
- **Financial-like rows (8 cells):** marked defer to #31 — not forced fix

## 2. Files changed

- `lab/revenue_residual_fix_32b_dryrun.py` (new)
- `outputs/generalization/full_market_2024/revenue_residual_fix_32b_dryrun_summary.md` (this file)
- `outputs/generalization/full_market_2024/revenue_residual_fix_32b_dryrun_details.csv` (optional detail)

## 3. Rows evaluated

| Metric | Value |
|---|---:|
| Field-cells evaluated | **57** |
| Unique issuers (BSE mirrors grouped) | **48** |
| BSE mirror pairs in pool | **20** groups |
| Experimental improvements (any harness path) | **17** |
| Control revenue regressions | **0** |

## 4. Root-cause distribution (inventory + harness classification)

### Inventory root_cause

| Root cause | Cells |
|---|---:|
| `tier3_stitched_still_empty_multipage` | 20 |
| `wrong_table_sales_mode_bleed` | 12 |
| `financial_like_holding_disclosure` | 8 |
| `rows_present_fail_data_row_heuristic` | 6 |
| `wrong_table_customer_captured_as_region` | 6 |
| `empty_table_no_stitch` | 5 |

### Harness classification

| Classification | Cells |
|---|---:|
| tier4_multipage_candidate | 31 |
| financial_like_defer | 8 |
| sales_mode_bleed | 6 |
| wrong_sibling_table | 6 |
| layout_numeric_format | 3 |
| empty_table_no_stitch | 2 |
| wrong_table_ranking_candidate | 1 |

## 5. Experimental Tier4 multipage (N+2..N+4)

- Rows where Tier4 experiment yields usable/partial: **16**
| Code | Field | Stored → Tier4 |
|---|---|---|
| 000011 | revenue_by_region | wrong → **usable** |
| 002783 | revenue_by_region | wrong → **usable** |
| 300435 | revenue_by_region | wrong → **usable** |
| 301382 | revenue_by_region | wrong → **usable** |
| 301551 | revenue_by_region | wrong → **usable** |
| 601952 | revenue_by_region | wrong → **usable** |
| 603037 | revenue_by_region | wrong → **partial** |
| 603421 | revenue_by_region | wrong → **usable** |
| 605090 | revenue_by_region | wrong → **usable** |
| 688509 | revenue_by_region | wrong → **usable** |

## 6. Experimental wrong-table ranking

- Rows where ranked re-scan yields usable/partial: **17**
| Code | Field | Stored → Ranked |
|---|---|---|
| 000972 | revenue_by_region | wrong → **usable** |
| 000011 | revenue_by_region | wrong → **usable** |
| 002783 | revenue_by_region | wrong → **usable** |
| 300435 | revenue_by_region | wrong → **partial** |
| 301382 | revenue_by_region | wrong → **usable** |
| 301551 | revenue_by_region | wrong → **usable** |
| 601952 | revenue_by_region | wrong → **usable** |
| 603037 | revenue_by_region | wrong → **partial** |
| 603421 | revenue_by_region | wrong → **usable** |
| 605090 | revenue_by_region | wrong → **usable** |

## 7. Single-row audit relaxation estimate

- Rows that could become **partial** (not usable) under 境内/境外 relaxation: **0**
- Production audit **not changed** in this task; count only.

## 8. P0/P1/P2 decision table

| Decision | Cells |
|---|---:|
| P0 Tier4 | 19 |
| P1 Tier4 | 12 |
| P2 defer (#31) | 8 |
| P1 wrong-table ranking | 7 |
| P1 trim/ranking | 6 |
| P1 layout/heuristic | 3 |
| P1 manual PDF review | 2 |

- **Fixable now (P0/P1 extraction or ranking pilot):** ~44 cells
- **Deferred (#31 / manual / no safe fix):** ~13 cells

## 9. Recommendation

1. **defer production apply; scoped Tier4 + wrong-table pilot after human sign-off**
2. **Close #32:** yes — #32 can close with revenue/R&D residuals explicitly deferred.
3. Next engineering (not this task): port Tier4 N+2..N+4 stitch + wrong-table ranking into harness-validated scoped pilot (~12 unique Tier4 issuers after BSE dedupe).
4. Do **not** update non-fin **9.43/11** headline until intentional scoped apply + strict audit rerun.

> **Caveat:** Some Tier4 hits overlap sales-mode-bleed inventory rows (e.g. 000011) — require PDF spot-check before production port.

## 10. Safe to commit

- `lab/revenue_residual_fix_32b_dryrun.py`
- `outputs/generalization/full_market_2024/revenue_residual_fix_32b_dryrun_summary.md`
- `outputs/generalization/full_market_2024/revenue_residual_fix_32b_dryrun_details.csv`

## 11. Do not commit

- Profiles, eval_results, strict_audit_summary.md, refresh CSVs, YAML

## GitHub #32b comment (中文)

```
#32b revenue residual dry-run 完成（只读诊断）

结论：**PASS** — 57/57 strict-wrong 收入 cell 已分类；control 回归 0。
- region wrong 38 + segment wrong 19
- Tier4 实验改善：16；wrong-table ranking 改善：17
- 金融控股类 8 cell → defer #31；BSE 83/92 镜像已分组
- 建议：**defer 生产 apply**；#32 可关单并将 revenue 剩余项 defer 到后续 scoped pilot（Tier4 + wrong-table ranking）
未改 production extraction/audit；未更新 9.43/11 headline。
```

