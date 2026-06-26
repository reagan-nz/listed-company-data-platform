# R&D residual fix #32c-R5 post-apply verification

_Generated: 2026-06-26 | Read-only audit of current profiles vs apply CSV_

## Verdict: **PASS**

## 1. Scope

- Verify **104** scoped P0 `rnd_investment` apply targets after #32c-R4 apply
- Read current `company_profile.json` only; no re-extraction, no refresh, no apply
- Field scope: `rnd_investment` only; no revenue or non-R&D fields
- Not a full R&D rollout; not a global strict audit headline update

## 2. Inputs

- `outputs/generalization/full_market_2024/rnd_refresh_changes_32c_apply.csv`
- `outputs/generalization/full_market_2024/revenue_rnd_residual_candidates_32.csv` (inventory strict labels)
- Current `company_profile.json` per target code
- `lab/strict_audit_full_market.py` → `strict_audit_field()`

## 3. Apply recap

| Metric | Value |
|---|---:|
| Targets | 104 |
| Updated (apply CSV) | 32 |
| Unchanged | 72 |
| Apply errors | 0 |
| not_found → found | 14 |
| found → not_found | 0 |

## 4. Current profile verification summary

| Check | Result |
|---|---|
| Targets loaded | **104** |
| Profile/field read errors | **0** |
| Current status matches apply `after_status` | **104/104** |
| Apply CSV consistency (status + anchor) | **104/104** |
| found → not_found regressions | **0** |
| Strict regressions vs inventory | **0** |
| Apply changed rows (CSV) | **32** |
| Apply unchanged rows (CSV) | **72** |

## 5. Strict label distribution (current profiles, 104 targets)

| Strict label | Count |
|---|---:|
| usable | 32 |
| partial | 71 |
| not_found_unverified | 1 |

**Current extraction status:**

- `found`: 103
- `not_found`: 1

## 6. Mandatory examples

| Code | In apply pool | Inventory strict | Apply before→after | Current strict | Current status | Gate |
|---|---|---|---|---|---|---|
| 600011 | yes | partial | found→found | **usable** | found | PASS (usable) |
| 600020 | yes | partial | found→found | **usable** | found | PASS (usable) |
| 688081 | yes | not_found_unverified | not_found→found | **usable** | found | PASS (usable) |
| 600029 | yes | not_found_unverified | not_found→found | **usable** | found | PASS (usable) |
| 600115 | yes | not_found_unverified | not_found→found | **usable** | found | PASS (usable) |
| 600844 | yes | not_found_unverified | not_found→found | **usable** | found | PASS (usable) |
| 000333 | no | partial | —→— | **partial** | partial | PASS (partial, not forced usable) |
| 301221 | no | partial | —→— | **partial** | partial | N/A (not in apply pool) — current partial |

## 7. Regression table

_None — no regressions detected._

## 8. Control check (002415)

| Code | Current strict | Current status | Usable OK |
|---|---|---|---|
| 002415 | **usable** | found | yes |

## 9. Differences vs dry-run expectations

- #32c-R3 dry-run predicted **32** strict improvements and **0** regressions before apply.
- Apply updated **32** profiles; post-apply profile state matches apply CSV `after_*` columns.
- Post-apply harness `improved=0` is expected: stored profiles already equal fresh extraction for applied rows.
- **72/104** unchanged in apply — current strict remains partial for most 利润表研发费用 cases.

## 10. Remaining limitations

- **72/104** P0 targets unchanged — situation-table did not beat baseline under guard
- **000333** cumulative narrative remains **partial** — not forced usable (correct)
- **301221** not in 104-code apply pool (P2 in inventory) — profile may still be partial
- No CNINFO rerun, SQLite import, or **non-fin 9.43/11** headline update
- Not a claim of full R&D residual fix or full manual validation

## Safe to commit

- `lab/rnd_residual_fix_32c_post_apply_verify.py`
- `outputs/generalization/full_market_2024/rnd_residual_fix_32c_post_apply_verify.md`
- `outputs/generalization/full_market_2024/rnd_residual_fix_32c_post_apply_verify.csv` (optional)

## Do not commit

- `company_profile.json`, `eval_results.json`, backups
- `rnd_refresh_changes_32c_apply.csv` (unless explicitly approved)
- `strict_audit_summary.md`

## GitHub #32c post-apply verification comment (中文)

```
#32c-R5 已完成 scoped P0 rnd_investment apply 后验（只读 profile 审计）。

结论：**PASS**
- 104 家目标均已读取当前 profile
- profile 读错：0
- 当前 status 与 apply CSV after_status 一致：104/104
- found→not_found 回归：0
- strict 回归（相对 #32 inventory）：0
- 当前 strict 分布：usable=32 partial=71 not_found*=1

Mandatory：600011/600020/688081/600029/600115/600844 当前均为 usable；000333 保持 partial；301221 不在 apply 池。
控制样例 002415：usable 保持。

说明：apply 后 harness improved=0 属预期（profile 已写入改善值）。本报告直接读 profile，不依赖 harness delta。
未更新 non-fin 9.43/11 headline；非全市场 R&D rollout。
```

