# R&D residual fix #32c-R4 scoped P0 apply summary

_Generated: 2026-06-26 | Post-apply report only; no re-run of apply or refresh_

## Executive summary

Scoped P0 `rnd_investment` refresh was **successfully applied** to **104 companies** using the guarded situation-table production path from #32c-R2. Apply completed with **0 errors**, **32 profile updates**, **14 not_found→found** recoveries, and **0 found→not_found** regressions. Post-apply harness re-run shows `improved=0` — an **expected metric artifact** because stored profiles already reflect the applied improvements.

**This was scoped P0 only, not a full R&D rollout.**

---

## 1. Scope

| Item | Detail |
|---|---|
| Field | `rnd_investment` only |
| Pool | 104 deduplicated P0 companies from `revenue_rnd_residual_candidates_32.csv` |
| Root causes | 62×利润表研发费用 mis-capture; 27×费用化/合计 anchor collision; 15×suspicious not_found with table evidence |
| Extraction | #32c-R2 guarded path: `extract_rnd_situation_table_numeric()` + `merge_rnd_investment_with_guard()` |
| Out of scope | Full market R&D; revenue; financial audit; CNINFO re-download; SQLite import; YAML changes; non-fin 9.43/11 headline update |

---

## 2. Apply command and result

```bash
cd listed_company_data_collector
python lab/refresh_rnd_full_market.py --apply --codes <104 P0 codes> \
  --changes-csv outputs/generalization/full_market_2024/rnd_refresh_changes_32c_apply.csv
```

**Apply output:**

```
[rnd_refresh] APPLIED complete
  targets: 104
  updated: 32
  unchanged: 72
  errors: 0
  not_found_to_found: 14
  found_to_not_found: 0
  status_changes: 32
  batch_files_updated: 2
  changes_csv: outputs/generalization/full_market_2024/rnd_refresh_changes_32c_apply.csv
```

- **Profiles modified:** 32 `company_profile.json` files updated; 72 unchanged.
- **Eval batch files modified:** 2 board-level `eval_results.json` files updated (rnd field counts only).
- **Backups created:** `company_profile.json.bak.rnd_refresh_20260624` and `eval_results.json.bak.rnd_refresh_20260624` where writes occurred.

---

## 3. Dry-run baseline recap (#32c-R3, pre-apply)

Before apply, #32c-R3 dry-run against stored profiles predicted:

| Gate | Pre-apply dry-run |
|---|---:|
| P0 companies | 104 |
| Strict improvements | **32** |
| Regressions | **0** |
| P0 improved | **32** |
| Mandatory improved | **7/8** |
| Control regressions | **0** |
| Verdict | **PASS** → approve scoped apply |

Strict transitions predicted:

| Transition | Count |
|---|---:|
| not_found_unverified → usable | 14 |
| partial → usable | 18 |
| partial → partial | 71 |
| Regressions | 0 |

Apply outcome (**32 updated**, **14 not_found→found**, **18 found→found** with value/anchor change) matches the dry-run prediction.

---

## 4. Apply metrics

From `rnd_refresh_changes_32c_apply.csv`:

| Metric | Value |
|---|---:|
| Targets processed | 104 |
| Rows changed (`changed=True`) | **32** |
| Unchanged | 72 |
| Errors | **0** |
| Status: `not_found → found` | **14** |
| Status: `found → found` (value/anchor upgrade) | **18** |
| Status: `found → not_found` | **0** |
| All 32 changes used situation-table anchor | 32/32 `(situation_table)` |

---

## 5. Post-apply check interpretation

Post-apply re-run of `lab/rnd_residual_fix_32c_r3_dryrun.py`:

```
pool=104 evaluated=104 improved=0 regressed=0 mandatory_improved=1/8 verdict=FAIL
```

**This FAIL is not an apply failure.** The harness compares fresh extraction vs **current stored profile**. After apply, profiles already contain the improved values, so:

- `improved=0` — baseline equals stored; no delta to measure
- `mandatory_improved=1/8` — only **301221** (not in apply pool) still shows improvement potential; the other 7 mandatory codes are already at target in stored profiles

**Valid post-apply checks (all pass):**

| Check | Result |
|---|---|
| Apply errors | **0** |
| Updated profiles | **32** (matches dry-run) |
| not_found_to_found | **14** |
| found_to_not_found | **0** |
| Post-apply regressions | **0** |
| 002415 control | usable → usable |
| Mandatory P0 recoveries in apply pool | usable where expected |
| 000333 | partial → partial (cumulative narrative; not forced) |

---

## 6. Mandatory examples

| Code | Name | In apply pool | Pre-apply strict | Post-apply strict | Apply action |
|---|---|---|---|---|---|
| 600011 | 华能国际 | yes | partial | **usable** | Applied: 研发费用 → 研发投入合计 (situation_table) |
| 600020 | 中原高速 | yes | partial | **usable** | Applied |
| 688081 | 兴图新科 | yes | not_found_unverified | **usable** | Applied: not_found → found |
| 600029 | 南方航空 | yes | not_found_unverified | **usable** | Applied |
| 600115 | 中国东航 | yes | not_found_unverified | **usable** | Applied |
| 600844 | 金煤科技 | yes | not_found_unverified | **usable** | Applied |
| 000333 | 美的集团 | no | partial | **partial** | Not in pool; correctly unresolved |
| 301221 | 光庭信息 | no (P2) | partial | partial in profile; extract→usable | Not applied; optional follow-up |

Post-apply harness (stored vs fresh): 600011–600844 show **usable → usable**; 301221 shows **partial → usable** (latent improvement, not applied); 000333 **partial → partial**.

---

## 7. Regression check

| Category | Result |
|---|---|
| P0 pool strict regressions (post-apply) | **0** |
| found → not_found | **0** |
| usable → partial/wrong/not_found | **0** |
| Control 002415 | usable → usable |
| Controls 300750, 600519, 601012, 688111 | all usable → usable |
| Non-R&D fields touched | **No** (refresh tool updates rnd_investment only) |

---

## 8. Remaining limitations

- **72/104 P0 rows unchanged** — mostly 利润表研发费用 cases where situation-table did not beat baseline under strict guard; still partial under strict audit.
- **Not a full R&D residual fix** — P1 pool, narrative partials (000333), and non-P0 cases untouched.
- **301221** improves under fresh extraction but was outside the 104-code apply list (CSV priority P2).
- **No CNINFO rerun** — used cached PDFs only.
- **No SQLite import** — local profile/eval updates only.
- **No strict_audit_summary.md update** — headline non-fin **9.43/11** unchanged.
- **No full manual validation** — automated apply + spot-check only.

---

## 9. Do-not-commit generated files

Do **not** commit unless explicitly approved:

- `outputs/generalization/**/company_profile.json` (32 modified + backups)
- `outputs/generalization/**/eval_results.json` (2 board files modified + backups)
- `outputs/generalization/full_market_2024/rnd_refresh_changes_32c_apply.csv`
- `outputs/generalization/**/.bak.rnd_refresh_20260624` backup files
- Apply/refresh terminal logs

---

## 10. Safe-to-commit list

- `outputs/generalization/full_market_2024/rnd_residual_fix_32c_apply_summary.md` (this file)
- Previously committed: `lab/extract_annual_report.py`, `lab/rnd_residual_fix_32c_dryrun.py`, `lab/rnd_residual_fix_32c_r3_dryrun.py`, R2/R3 summary markdown

---

## 11. Rollback reference

If rollback is needed:

```bash
# Per modified company — restore from backup
cp outputs/generalization/<board>/<code>/company_profile.json.bak.rnd_refresh_20260624 \
   outputs/generalization/<board>/<code>/company_profile.json

# Per modified board eval
cp outputs/generalization/<board>/eval_results.json.bak.rnd_refresh_20260624 \
   outputs/generalization/<board>/eval_results.json
```

---

## GitHub #32c apply comment (中文)

```
#32c-R4 已完成 scoped P0 rnd_investment apply（104 家，非全市场 R&D rollout）。

Apply 结果：
- targets: 104
- updated: 32
- unchanged: 72
- errors: 0
- not_found→found: 14
- found→not_found: 0
- batch eval 更新: 2 个 board

与 #32c-R3 dry-run 预测一致（32 条 strict 改善、0 回归）。Apply 后重跑 harness 显示 improved=0 / verdict=FAIL 属于预期指标 artifact（profile 已写入改善结果，stored vs fresh 无 delta），不代表 apply 失败。

Mandatory 样例：
- 600011/600020/688081/600029/600115/600844：已恢复 usable
- 000333：保持 partial（累计披露 narrative，未强制 usable）
- 301221：不在 104 家 apply 池（P2），profile 仍为 partial，但 fresh extract 可达 usable

控制样例 002415：usable→usable，无回归。

未做：CNINFO 重跑、SQLite import、strict_audit_summary 更新、non-fin 9.43/11 headline 更新。

72/104 仍为 partial（主要是利润表研发费用 mis-capture 未命中 situation-table 或 guard 保留 baseline），属已知剩余项。

产物：`rnd_residual_fix_32c_apply_summary.md`
Do-not-commit：profile/eval 变更、rnd_refresh_changes_32c_apply.csv、backup 文件（除非明确批准）。
```
