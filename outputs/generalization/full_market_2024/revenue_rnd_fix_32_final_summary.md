# Revenue + R&D residual fix #32 — final closure summary

_Generated: 2026-06-26 | Issue #32 closed for current scope_

## Closure decision

**#32 is closed** for its defined scope: read-only residual inventory, scoped P0 R&D fix (verified apply), and revenue strict-wrong dry-run diagnosis. Remaining revenue extraction work and broader R&D partials are **explicitly deferred** to future scoped pilots. **Non-fin strict usable headline remains 9.43/11** (post–#26 reference; not updated by #32).

---

## 1. Scope and boundary

| In scope (#32) | Out of scope (deferred) |
|---|---|
| Inventory of revenue + R&D residuals after #25/#26 | Full-market revenue or R&D refresh |
| Scoped P0 R&D apply (104 companies) | Full population R&D partial fix (~255) |
| Revenue strict-wrong dry-run classification (57 cells) | Revenue production apply |
| Documentation + harness artifacts | CNINFO re-download, SQLite import |
| Post-apply local verification (#32c-R5) | Global `strict_audit_summary.md` rerun |

**Financial cohort:** Separate sub-schema headline; 8 revenue wrong cells deferred to #31 tagging review.

---

## 2. What #32 completed

| Track | Deliverables | Outcome |
|---|---|---|
| **Inventory** | `revenue_rnd_residual_inventory_32.md`, `revenue_rnd_residual_candidates_32.csv` (513 rows) | Residuals classified; P0/P1/P2 split documented |
| **#32c R&D** | R2–R5 harnesses + production helper + scoped apply + verification | 32/104 P0 strict improved; 0 apply errors; verify PASS |
| **#32b Revenue** | `revenue_residual_fix_32b_dryrun.py` + summary + details CSV | 57/57 wrong cells classified; 17 harness improvements; 0 control regressions |

---

## 3. Inventory results (#32 baseline)

| Pool | Count | Notes |
|---|---:|---|
| Revenue strict wrong | **57** field-cells / **48** issuers | region 38 + segment 19 |
| Revenue partial (sub-pools only) | **186** in CSV | Full ~753 partial **not** enumerated |
| R&D partial | **255** | In CSV |
| R&D suspicious not_found | **15** | Table evidence in snippet |
| Non-fin headline (reference) | **9.43/11** | Unchanged through #32 |

---

## 4. #32c R&D — implementation and apply

| Phase | Key result |
|---|---|
| **R2** | Guarded `extract_rnd_situation_table_numeric()` + `merge_rnd_investment_with_guard()` in production |
| **R3** | Dry-run 104 P0 targets: 32 strict improvements, 0 regressions |
| **R4** | Apply: 104 targets, **32 updated**, 0 errors, 14 not_found→found, 0 found→not_found |
| **R5** | Post-apply verify **PASS**: 104/104 status match; 0 regressions; 002415 usable; 000333 partial |

**Scoped pool post-apply strict distribution:** usable=32, partial=71, not_found_unverified=1 (600238).

Mandatory recovered → usable: 600011, 600020, 688081, 600029, 600115, 600844.

---

## 5. #32b Revenue — dry-run classification

| Metric | Value |
|---|---:|
| Rows evaluated | **57/57** |
| Experimental harness improvements | **17** |
| Control revenue regressions | **0** |
| Production apply | **Deferred** |

### Root-cause distribution

| Root cause | Cells |
|---|---:|
| Tier3 stitched, still empty | 20 |
| Sales-mode bleed | 12 |
| Financial-like (defer #31) | 8 |
| Layout / data-row heuristic | 6 |
| Customer table as region | 6 |
| Empty / no stitch | 5 |

**Harness experiments:** Tier4 N+2..N+4 → 16 usable/partial; wrong-table ranking → 17 usable/partial. Production port requires human sign-off and scoped pilot.

---

## 6. Why headline 9.43/11 remains unchanged

1. **No full strict audit rerun** after #32c scoped apply or #32b dry-run.
2. **Scoped apply ≠ population metric** — 32 R&D profile updates do not recompute 5,621 × 11 non-fin cells.
3. **Revenue production fix not applied** — 57 strict-wrong cells remain in stored profiles for headline purposes.
4. **Intentional policy** — headline updates only after scheduled full strict audit, not per scoped tranche.

Reference headline source: `run_name=full_market_2024_revenue_refresh` / [strict_audit_summary.md](strict_audit_summary.md) (pre-#32).

---

## 7. Deferred revenue work

| Item | Priority | Notes |
|---|---|---|
| Tier4 multipage continuation (N+2..N+4) | P0 pilot | ~12 unique issuers after BSE dedupe; harness signal 16 cells |
| Wrong-table ranking | P1 pilot | Customer/supplier vs region/segment discrimination |
| Financial-like disclosures | P2 defer | 601066, 601668, 601611, 601216 → #31 |
| Full revenue partial methodology | P2 | ~753 partial population not fully enumerated |
| Sales-mode bleed trim | P1 | 12 cells; overlap with Tier4 on some codes |

---

## 8. Deferred R&D work

| Item | Notes |
|---|---|
| 72/104 P0 pool still partial | Profit-statement 研发费用 mis-capture majority |
| 000333 cumulative narrative | Stays partial by design; not forced usable |
| 301221 | Not in 104-code apply pool (P2 inventory) |
| ~255 full-population R&D partial | Only 32/104 scoped P0 improved |
| R&D P1 unit-scale / audit-rejects-合计 | 96 cells in inventory |

---

## 9. Anti-claims

| Claim | Allowed? |
|---|---|
| #32 closed for defined scope | **Yes** |
| Full market revenue/R&D fixed | **No** |
| Non-fin 9.43/11 updated by #32 | **No** |
| Full manual validation | **No** |
| CNINFO / SQLite rerun from #32 | **No** |
| Financial metrics in non-fin headline | **No** |
| Scoped apply = new population strict score | **No** |

---

## 10. Artifact index

| Artifact | Track |
|---|---|
| [revenue_rnd_residual_inventory_32.md](revenue_rnd_residual_inventory_32.md) | Inventory |
| [revenue_rnd_residual_candidates_32.csv](revenue_rnd_residual_candidates_32.csv) | Inventory |
| [rnd_residual_fix_32c_r2_summary.md](rnd_residual_fix_32c_r2_summary.md) | R&D |
| [rnd_residual_fix_32c_apply_summary.md](rnd_residual_fix_32c_apply_summary.md) | R&D apply |
| [rnd_residual_fix_32c_post_apply_verify.md](rnd_residual_fix_32c_post_apply_verify.md) | R&D verify |
| [revenue_residual_fix_32b_dryrun_summary.md](revenue_residual_fix_32b_dryrun_summary.md) | Revenue dry-run |
| **This file** | Closure |

---

## 11. Safe to commit

- `outputs/generalization/full_market_2024/revenue_rnd_fix_32_final_summary.md` (this file)
- All #32 inventory, harness, and summary markdown listed above
- `lab/revenue_residual_fix_32b_dryrun.py`, `lab/rnd_residual_fix_32c_*.py`, `lab/extract_annual_report.py` (R&D helper, if already committed)
- Doc sync: `CURRENT_STATUS.md`, `CHANGELOG.md`, `ROADMAP.md`, `docs/evaluation_method.md`

## 12. Do not commit

- Local `company_profile.json` / `eval_results.json` changes from #32c apply
- `rnd_refresh_changes_32c_apply.csv`, `.bak.rnd_refresh_*` backups
- `strict_audit_summary.md` (unchanged headline)
- Refresh CSVs, apply logs, YAML changes

---

## GitHub #32 closing comment (中文)

```
#32 revenue + R&D residual — 当前范围已关闭

已完成：
1. 盘点：revenue_rnd_residual_inventory_32.md + candidates_32.csv（513 行）
   - 收入 strict wrong 57（region 38 + segment 19）
   - 研发 partial 255 + 可疑 not_found 15
2. #32c R&D scoped P0：
   - 生产 guarded situation-table helper
   - apply 104 家 / 32 更新 / 0 errors / 14 not_found→found
   - 后验 PASS（104/104 一致，0 回归；002415 usable；000333 partial）
3. #32b 收入 dry-run：
   - 57/57 strict-wrong 已分类；harness 实验改善 17；control 回归 0
   - 生产 apply defer；建议后续 scoped Tier4 + wrong-table pilot

Headline：non-fin strict usable 9.43/11 **未更新**（无全局 strict audit 重跑；scoped apply ≠ 全人口指标）。

Defer：
- 收入 Tier4 / wrong-table ranking 生产试点
- 金融控股类 8 cell → #31
- 研发 72/104 partial、000333/301221、全人口 partial
- #33 多年份（单独决策）

未做：CNINFO、SQLite、全市场 refresh、全量人工验证。

产物：revenue_rnd_fix_32_final_summary.md
Do-not-commit：profile/eval apply 产物、refresh CSV（除非明确批准）
```
