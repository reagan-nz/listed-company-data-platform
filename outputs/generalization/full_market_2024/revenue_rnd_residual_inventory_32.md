# Revenue + R&D Residual Inventory #32

_Generated: 2026-06-25 | Issue #32 — read-only residual inventory_

## 1. Scope and guardrails

- **Task:** Read-only inventory of remaining non-financial `revenue_by_region`, `revenue_by_segment`, and `rnd_investment` residuals after #25 (R&D scoped refresh) and #26 (revenue Tier 2/3 scoped refresh).
- **Universe:** 5,621 non-financial companies with `status=ok` in `full_market_2024`.
- **Baseline headline (unchanged):** non-fin strict usable **9.43 / 11** — reference until an intentional re-audit is run.
- **Inputs (read-only):**
  - [strict_audit_summary.md](strict_audit_summary.md)
  - [revenue_refresh_summary.md](revenue_refresh_summary.md)
  - [rnd_refresh_summary.md](rnd_refresh_summary.md)
  - [stage3_quality_followup_summary.md](stage3_quality_followup_summary.md)
  - Stored `company_profile.json` + `eval_results.json`
  - [lab/strict_audit_full_market.py](../../lab/strict_audit_full_market.py) (re-run in memory only)
- **Not done:** Code changes, extraction, refresh, apply, merge, SQLite, CNINFO, profile/eval writes, #32a–#32d implementation.
- **Financial cohort:** Excluded from this inventory except where a non-fin company overlaps #31 under-tag review (`601066`, `601668`, etc.).

## 2. Current baseline from #25/#26/#28

| Metric | Post-#25 (R&D) | Post-#26 (revenue) | Notes |
|---|---:|---:|---|
| Non-fin strict usable | 9.38 / 11 | **9.43 / 11** | Population-consistent trajectory |
| `revenue_by_region` strict wrong | 258 → **38** | #26 Tier 2/3 stitch |
| `revenue_by_segment` strict wrong | 109 → **19** | 297 wrong→usable, 0 regressions |
| `revenue_by_region` strict partial | 469 → **480** | Largely unchanged by design |
| `revenue_by_segment` strict partial | 271 → **273** | Largely unchanged by design |
| `rnd_investment` found rate | 67.9% → **94.2%** | BSE 22.8% → 99.2% |
| `rnd_investment` strict wrong | 0 | No post-#25 wrong cells |
| `rnd_investment` strict partial | **255** | Quality, not absence |
| `rnd_investment` not_found_unverified | 1,791 → **280** | Residual absence pool |

**#26 partial population note:** Revenue refresh achieved **0 partial→usable** by design. Residual partial cells (753 field-cells / 648 companies) are not enumerated in the CSV; only selected sub-pools are included.

## 3. Revenue residual inventory

### 3.1 Strict wrong — all 57 field-cells (48 unique companies)

| Field | Strict wrong |
|---|---:|
| `revenue_by_region` | 38 |
| `revenue_by_segment` | 19 |
| **Total** | **57** |

All 57 fail `revenue_table_plausible()` in strict audit (`fails revenue_table_plausible`).

### 3.2 Root-cause taxonomy (wrong)

| Root cause | Cells | Priority | Fix type |
|---|---:|---|---|
| `tier3_stitched_still_empty_multipage` | 20 | **P0** | Extraction Tier 4 (N+2 / multi-page beyond Tier 3) |
| `wrong_table_sales_mode_bleed` | 12 | P1 | Extraction Tier 4 / table ranking |
| `wrong_table_customer_captured_as_region` | 6 | P1 | Extraction Tier 4 / sibling-table fix |
| `rows_present_fail_data_row_heuristic` | 6 | P1 | Extraction or audit after PDF review |
| `empty_table_no_stitch` | 5 | P1 | Manual PDF review / true absence |
| `financial_like_holding_disclosure` | 8 | **P2 defer** | #31 under-tag / N/A for industrial schema |

### 3.3 P0 revenue wrong — Tier 4 multipage candidates (20 cells)

Tier 3 (`stitched=True`) ran but **0 strict data rows** remain. Extend `_stitch_revenue_table_continuation` beyond N+1.

| Code | Name | Field | Notes |
|---|---|---|---|
| `000972` | *ST中基 | region | stitched, 0 data rows |
| `300128` | 锦富技术 | segment | stitched, 0 data rows |
| `300729` | 乐歌股份 | segment | stitched, 0 data rows |
| `831039` / `920039` | 国义招标 | region | BSE dual listing |
| `831832` / `920932` | 科达自控 | region | BSE dual listing |
| `832175` / `920175` | 东方碳素 | region | BSE dual listing |
| `836957` / `920957` | 汉维科技 | region | BSE dual listing |
| `839719` / `920719` | 宁新新材 | region | BSE dual listing |
| `872392` / `920392` | 佳合科技 | region | BSE dual listing |
| `873339` / `920339` | 恒太照明 | segment | BSE dual listing |
| `873593` / `920593` | 鼎智科技 | region | BSE dual listing |
| `920116` | 星图测控 | segment | BSE |

**Unique companies (non-duplicate codes):** ~12 issuers (10 BSE pairs + 3 non-BSE).

### 3.4 P1 revenue wrong — selected examples

**Wrong customer table captured as region (6 cells):**

| Code | Name | Field |
|---|---|---|
| `833075` / `920075` | 柏星龙 | region |
| `832885` / `920885` | 星辰科技 | region |
| `839725` / `920725` | 惠丰钻石 | segment |

Evidence shows customer names (e.g. 贵州茅台文化旅游, 客户1) under a 分地区 header — table selection bug, not continuation.

**Sales-mode / sibling bleed (12 cells):** `000011`, `002783`, `300117`, `300435`, `301190`, `301382`, `301551`, `603280`, `600132`, `600398`, `600598`, `603132` (mixed with empty-table on some).

**Empty table / layout (11 cells):** `600132`, `600398`, `603037`, `603421`, `688509` (empty); `601952`, `603132`, `603919`, `605090` (raw rows fail heuristic).

### 3.5 P2 defer — financial-like holdings (8 cells)

| Code | Name | Fields | Notes |
|---|---|---|---|
| `601066` | 中信建投 | region + segment | Broker; #31 under-tag candidate |
| `601668` | 中国建筑 | region + segment | Construction conglomerate |
| `601611` | 中国核建 | region + segment | Engineering/holding |
| `601216` | 君正集团 | region + segment | Chemical + finance mix |

Do not fix under non-fin industrial schema until #31 human review.

### 3.6 Revenue partial — selected sub-pools only (186 cells in CSV)

Full population: **753 partial field-cells / 648 companies** — **not enumerated**.

| Sub-pool | Cells in CSV | Strict reason | Proposed fix |
|---|---:|---|---|
| `single_row_domestic_foreign` | **122** | `single data row only` + 境内/境外 label | **Audit-only** (P1): accept valid 1-row region |
| `status_partial_multi_row` | **64** | `status=partial` + ≥2 data rows | Manual PDF review (P1) |

Remaining ~567 partial cells (other single-row, low-content partial) are documented statistically only.

## 4. R&D residual inventory

### 4.1 Strict wrong

**0 cells** — post-#25 P2.1 resolved prior regressions; no usable→wrong risk documented.

### 4.2 Strict partial — all 255 companies (in CSV)

| Root cause | Count | Priority | Fix type |
|---|---:|---|---|
| `profit_statement_研发费用_not_rnd_table` | 62 | **P0** | Extraction P2.2: prefer 研发投入情况表 over 利润表 snippet |
| `expensed_vs_total_anchor_collision` | 27 | **P0** | Extraction P2.2: prefer 研发投入合计 / sum expensed+capitalized |
| `unit_scale_below_strict_floor` | 54 | P1 | Unit-aware parse (万元/亿元) or audit floor |
| `audit_rejects_heji_label` | 42 | P1 | Audit-only: 合计 label handling |
| `narrative_or_mixed_unit_partial` | 44 | P2 | Manual review (e.g. `000333`, `301221`) |
| `other_partial` | 26 | P2 | Manual review |

**Exemplar partial cases (from prior summaries):**

| Code | Name | Issue |
|---|---|---|
| `600011` | 华能国际 | partial — 利润表 `研发费用` 16.58亿, not 万元-table 合计 |
| `600020` | 中原高速 | partial — 利润表 500,000 vs 万元-table 192.43 费用化 |
| `301221` | 光庭信息 | partial — narrative `研发投入合计 7,021.75 万元` |
| `000333` | 美的集团 | partial — cumulative `160 亿元` narrative |

### 4.3 not_found_unverified — suspicious misses (15 in CSV)

Full population: **280 not_found** (129 explicit N/A, ~151 true non-disclosure). Only rows with **numeric table evidence in snippet** are included.

| Code | Name | Evidence hint |
|---|---|---|
| `688081` | 兴图新科 | `研发投入合计 40,751,381.81` |
| `600029` | 南方航空 | 费用化/合计 万元-table |
| `600115` | 中国东航 | 费用化/合计 万元-table |
| `600844` | 金煤科技 | 费用化/合计 万元-table |
| `600097` | 开创国际 | 万元-table evidence |
| `600113` | 浙江东日 | 万元-table evidence |
| `600125` | 铁龙物流 | 万元-table evidence |
| `600238` | *ST椰岛 | 万元-table evidence |
| `600362` | 江西铜业 | 万元-table evidence |
| `600798` | 宁波海运 | 万元-table evidence |
| `600826` | 兰生股份 | 万元-table evidence |
| `601727` | 上海电气 | 万元-table evidence |
| `601865` | 福莱特 | 万元-table evidence |
| `601898` | 中煤能源 | 万元-table evidence |
| `688429` | 时创能源 | 万元-table evidence |

## 5. Root-cause taxonomy (summary)

### Revenue

| Category | Examples | Likely fix |
|---|---|---|
| Extraction bug — multipage | Tier 3 stitched, still empty | Tier 4 N+2 scan |
| Extraction bug — wrong table | 柏星龙 customer-as-region | Table ranking / stop-row |
| Extraction bug — sales-mode bleed | 深物业A, 南方路机 | Tier 2 extension or ranking |
| Strict-audit harsh | 122 single-row 境内/境外 partial | Audit-only relaxation |
| True absence | Empty tables after PDF review | Document only |
| Financial/industrial tagging | 601066, 601668 | Defer to #31 |

### R&D

| Category | Examples | Likely fix |
|---|---|---|
| Anchor collision — 费用化 vs 合计 | 厦门象屿, 亨通光电 | P2.2 anchor priority |
| Profit-statement capture | 华能国际, 600020 | P2.2 prefer R&D section table |
| Unit scale | 54 partial <10万元 floor | Unit parse or audit |
| Audit rejects 合计 | 42 partial | Audit rule review |
| Narrative / cumulative | 美的集团, 光庭信息 | Manual review / defer |
| True N/A | 280 − 15 suspicious | Document only |

## 6. Priority fix candidates

### P0 — safe high-confidence scoped fixes (human sign-off before code)

**Revenue (20 wrong cells / ~12 issuers):**
- Tier 4 multipage: codes in §3.3
- Pilot dry-run on `000972`, `300128`, `300729` before BSE batch

**R&D (89 partial + 15 not_found = 104 CSV rows):** — **#32c scoped apply verified (2026-06-26)** — 32/104 strict improved in P0 pool; 72 still partial/unresolved; see Appendix B

### P1 — targeted PDF review first

**Revenue (29 wrong + 186 partial sub-pool):**
- 6 customer-table mis-captures (柏星龙, 星辰科技, 惠丰钻石)
- 12 sales-mode bleed cases
- 122 single-row domestic/foreign partial → audit-only proposal

**R&D (96 partial):**
- 54 unit-scale below floor
- 42 audit-rejects-合计

### P2 — defer / ambiguous

- 8 financial-like revenue wrong (`601066`, `601668`, `601611`, `601216`)
- 44 narrative R&D partial + 26 other partial
- ~265 true not_found (non-suspicious)

### P3 — documentation only

- Full 753 revenue partial population (stats only)
- ~129 R&D explicit N/A disclosures

## 7. Proposed implementation split (plan only — not executed)

| Sub-issue | Scope | Touch (future) |
|---|---|---|
| **#32 (this task)** | Read-only inventory | 2 output files |
| **#32a** | Revenue diagnosis + audit-only single-row proposal | `strict_audit_full_market.py` |
| **#32b** | Revenue Tier 4 extraction | `extract_annual_report.py`, `refresh_revenue_full_market.py` |
| **#32c** | R&D anchor/unit + not_found recovery | `extract_annual_report.py`, `refresh_rnd_full_market.py` | **Scoped P0 apply verified** (104 targets, 32 updated) — not full rollout |
| **#32d** | Dry-run validation harness | New dry-run script (pattern: `financial_audit_fix_30f_dryrun.py`) |

**Recommended order:** #32 inventory → human P0 sign-off → #32c (lower regression risk) + #32b in parallel → #32d → scoped apply.

## 8. Validation plan (for future #32a–d)

| Fix type | Dry-run scope | Pass gates |
|---|---|---|
| Revenue Tier 4 | P0 codes → expand | 0 usable→wrong; P0 wrong→usable; #26 controls unchanged |
| Wrong-table ranking | 柏星龙 + 3 pilots | PDF spot-check + 0 regressions |
| R&D anchor/unit | 89 P0 partial + 15 misses | 0 found→not_found; `600011`/`600020` improve; `301221`/`000333` unchanged |
| Audit-only single-row | 20-code sample from 122 | 0 multi-row control regressions |

**Global gates:** No profile writes until dry-run passes; no CNINFO; no full-market refresh until pilot passes; exclude `financial: true` from non-fin fixes; do not update 9.43/11 headline until intentional re-audit.

## 9. Deferred items

- Full 753 revenue partial enumeration
- Financial-like revenue wrong until #31 YAML review
- Narrative R&D (`000333`, `301221`) — no safe auto-fix
- Bulk 280 R&D not_found (non-suspicious) — document as true absence
- `risk_factors` strict wrong (221 cells) — out of #32 scope
- BSE board gap (8.82/11) — monitor only

## 10. Safe-to-commit / do-not-commit list

### Safe to commit (this task only)

- `outputs/generalization/full_market_2024/revenue_rnd_residual_inventory_32.md`
- `outputs/generalization/full_market_2024/revenue_rnd_residual_candidates_32.csv`

### Do not commit from this task

- Code, YAML, profiles, `eval_results.json`, audit summaries, refresh CSVs/logs, SQLite

## 11. GitHub #32 progress comment (中文)

---

**#32 收入 + 研发残留盘点 — 只读完成**

**范围：** 非金融 ok 样本 5621 家；在 #25 R&D refresh、#26 revenue Tier2/3 refresh 之后，盘点 `revenue_by_region` / `revenue_by_segment` / `rnd_investment` 残留。

**基线（不变）：** 非金融 strict usable **9.43/11**；金融指标单独统计，不混入 headline。

**交付：**
- `revenue_rnd_residual_inventory_32.md`
- `revenue_rnd_residual_candidates_32.csv`（**513 行**）

**CSV 构成：**
- 收入 strict wrong：**57**（region 38 + segment 19）
- 收入 partial 精选子池：**186**（122 单行境内/境外 + 64 status=partial 多行；**未**枚举全部 753 partial）
- 研发 partial：**255**
- 研发 not_found 可疑：**15**（证据中有数值表但未 found）

**收入 wrong 主因：** Tier3 缝合后仍空表 20、销售模式串表 12、客户表误捕为分地区 6、金融控股类 8（defer #31）。

**研发残留：** strict wrong **0**；partial 255（利润表研发费用误捕 62、费用化/合计锚点冲突 27）；not_found 可疑 15。

**P0 建议（需人工确认后再做 #32b/#32c）：** 收入 Tier4 多页 ~12 issuer；研发锚点/单位 + 15 个 not_found 恢复。

**建议：** 以盘点 + 人工复核门禁关闭 #32；**暂不**启动 #32a–#32d 实现。

**未改动：** 代码 / profile / eval / refresh / SQLite / CNINFO / 无 commit

---

## Appendix: CSV row counts

| Pool | Rows |
|---|---:|
| Revenue strict wrong | 57 |
| Revenue partial sub-pool | 186 |
| R&D partial | 255 |
| R&D not_found suspicious | 15 |
| **Total** | **513** |

---

## Appendix B: #32c status (#32c-R2–R5, 2026-06-26)

**Scope:** Scoped P0 `rnd_investment` fix only — **not** full R&D rollout; **not** global strict audit headline update.

| Phase | Result |
|---|---|
| **R2** | Production guarded helper in `extract_annual_report.py`; dry-run 207 rows — 117 improved, 0 regressed, mandatory 7/8 |
| **R3** | P0 dry-run 104 targets — 32 strict improvements, 0 regressions; apply recommended |
| **R4** | Scoped apply — 104 targets, **32 updated**, 0 errors, 14 not_found→found, 0 found→not_found |
| **R5** | Post-apply verification **PASS** — 104/104 profile status matches apply CSV; 0 regressions |

### P0 R&D pool status (post-apply, scoped pool only)

| Bucket | Pre-#32c (inventory) | Post-#32c apply |
|---|---|---|
| P0 pool size | 104 companies | 104 processed |
| Strict improved (scoped) | 32 predicted | **32 applied** |
| Still partial / unresolved | 72 predicted | **71 partial + 1 not_found_unverified** (600238) |
| Mandatory recovered → usable | 600011, 600020, 688081, 600029, 600115, 600844 | **Verified usable** |
| Deferred narrative | 000333, 301221 | 000333 **partial**; 301221 **not in apply pool** (P2) |

### Unresolved buckets (unchanged scope)

- **Revenue:** 57 strict-wrong — still **#32b** candidate
- **R&D P1:** 96 partial (unit-scale, audit-rejects-合计) — not in scoped P0 apply
- **R&D P2:** narrative partial (000333, 301221) — manual review
- **Full population R&D partial (~255 pre-apply inventory):** only 32/104 P0 scoped cells improved; **non-fin 9.43/11 headline unchanged**

### Artifacts

- [rnd_residual_fix_32c_r2_summary.md](rnd_residual_fix_32c_r2_summary.md)
- [rnd_residual_fix_32c_r3_summary.md](rnd_residual_fix_32c_r3_summary.md)
- [rnd_residual_fix_32c_apply_summary.md](rnd_residual_fix_32c_apply_summary.md)
- [rnd_residual_fix_32c_post_apply_verify.md](rnd_residual_fix_32c_post_apply_verify.md)

**Do not commit:** local `company_profile.json` / `eval_results.json` apply outputs; `rnd_refresh_changes_32c_apply.csv` unless explicitly approved.

---

## Appendix C: #32 final status (2026-06-26)

**#32 closed** for current scope. See [revenue_rnd_fix_32_final_summary.md](revenue_rnd_fix_32_final_summary.md).

| Track | Status |
|---|---|
| **Inventory** | Done — 513-row CSV; 57 revenue wrong + R&D partial/not_found pools |
| **#32c R&D** | Done — scoped P0 apply verified (32/104 strict improved); headline unchanged |
| **#32b Revenue** | Done (dry-run) — 57/57 classified; **production apply deferred** |

**Deferred:** revenue Tier4 pilot, wrong-table ranking, financial-like → #31, full revenue partial methodology, remaining R&D partials.

Detail: [revenue_rnd_residual_candidates_32.csv](revenue_rnd_residual_candidates_32.csv)
