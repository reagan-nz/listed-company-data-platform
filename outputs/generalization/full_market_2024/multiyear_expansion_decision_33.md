# Multiyear expansion decision memo — Issue #33

_Generated: 2026-06-26 | Planning / documentation only — no extraction run_

## Closure decision

**#33 is closed** as a **decision memo**. This document records the recommended multiyear expansion strategy for human sign-off before any 2025 pilot execution. **Parent #23** (#24–#33) is **ready to close** after this memo and doc sync are committed.

---

## 1. Executive recommendation

**Proceed with 2025 first, via staged rollout — not parallel multiyear, not 2023/2022 backfill first.**

| Decision | Recommendation |
|---|---|
| Next year | **2025 annual reports first** |
| Universe | **Per-year universe** from CNINFO (not frozen 2024 list) |
| Rollout | **100-company stratified pilot → one-board pilot → full-market 2025 → backfill 2023/2022** |
| CNINFO | **Do not** launch full-market CNINFO immediately; pilot uses controlled download scope |
| 2024 outputs | **Do not overwrite** — separate `run_name` and output directories |
| Headline | **2024 non-fin 9.43/11 unchanged** until intentional full strict audit on that cohort |

**Rationale:** 2025 extends the live baseline forward with the same extraction stack validated on 2024; backfill years add historical depth but lower operational urgency and higher template drift risk. Staged rollout limits disk, CNINFO, and regression risk before committing to ~6k+ companies.

---

## 2. Current 2024 readiness

| Dimension | Status | Notes |
|---|---|---|
| Stage 3a quality follow-up | **PASS** (caveats) | See [stage3_quality_followup_summary.md](stage3_quality_followup_summary.md) |
| Non-fin strict headline | **9.43/11** | `run_name=full_market_2024_revenue_refresh`; **unchanged** through #32 |
| Financial cohort | **Separate headline** | bank/broker/insurer sub-schema; grading worksheet partial |
| Extraction pipeline | **Production-ready for industrial 11-field** | BSE/rnd/revenue improvements from #24–#26; #32c R&D helper |
| Residuals (non-blocking) | Documented | #31 under-tagging; #32 revenue pilot deferred; R&D partials |
| SQLite / CNINFO | **2024 imported** | 62,890 rows; no rerun required for this memo |
| Tooling | **Year-parameterizable with minor script work** | `make_full_market_yaml.py`, batch merge, strict audit — **not in #33 scope** |

**Readiness verdict:** 2024 baseline is **sufficient to start a 2025 pilot** after prerequisites (§5) and human checklist (§12) are satisfied. Full-market 2025 should wait until pilot gates pass.

---

## 3. Options compared

### 3.1 Option A — 2025 first (recommended)

| Pros | Cons |
|---|---|
| Aligns with “current year” database growth | 2025 reports may still be publishing (timing risk) |
| Reuses freshest extraction fixes from #24–#32 | New-year template drift unknown until pilot |
| Natural SQLite `report_year=2025` extension | Per-year universe rebuild required |
| Supervisor narrative: forward progress | Does not immediately fill historical gaps |

### 3.2 Option B — 2023/2022 backfill first

| Pros | Cons |
|---|---|
| Historical panel for research | Older PDF layouts / disclosure norms differ |
| Smaller “news” pressure vs latest year | Lower priority vs extending live baseline |
| Some companies delisted since 2022/2023 | Delisting / universe reconciliation harder |
| | Defers validation of 2025 pipeline |

### 3.3 Option C — Parallel multiyear (2025 + 2023 + 2022)

| Pros | Cons |
|---|---|
| Fastest historical coverage | 3× CNINFO load, disk, merge complexity |
| | Hard to attribute regressions across years |
| | Violates staged-risk policy from full_market_2024 |
| | No isolated pilot learning |

**Decision:** **Option A** with explicit backfill phase after full-market 2025 succeeds.

---

## 4. Recommended path

```
Phase 0  Prerequisites (#31 retag review, pilot YAML tooling sign-off)
    ↓
Phase 1  full_market_2025_pilot — 100-company stratified sample
    ↓  (validation gates §8)
Phase 2  full_market_2025_pilot_bse — one-board pilot (recommend BSE: smallest, strict history)
    ↓
Phase 3  full_market_2025 — full A-share 2025 universe, 5-board batch order
    ↓  (strict audit + summary; separate headline)
Phase 4  full_market_2023_backfill — per-year universe, same batch strategy
    ↓
Phase 5  full_market_2022_backfill — per-year universe, same batch strategy
```

**Parallel work (non-blocking for Phase 1):** revenue Tier4 pilot (#32b), R&D remaining partials — **do not** block 2025 pilot if scoped separately.

**Do not:** skip Phase 1–2; overwrite `outputs/generalization/full_market_2024/`; run full CNINFO for all years at once.

---

## 5. Prerequisites before expansion

| # | Prerequisite | Owner | Blocks |
|---|---|---|---|
| P1 | **Human sign-off** on this memo (§12 checklist) | Supervisor | Any CNINFO download |
| P2 | **#31 financial under-tagging review** — at minimum document retag decisions for `000402` / `600816` / `600318` and 8 financial-like revenue wrong | Human + dev | Financial 2025 strict headline credibility |
| P3 | **Year-parameterized run scripts** — `make_full_market_yaml.py --year 2025`, batch runner, merge, audit entrypoints (implementation issue, post-#33) | Dev | Phase 1+ |
| P4 | **Pilot universe YAML** — 100-co stratified sample (board × size × financial tag); seed from `sample_universe.py` pattern | Dev | Phase 1 |
| P5 | **Disk / CNINFO budget** — estimate ~6k PDFs × N years; confirm storage path under `outputs/generalization/` | Ops | Phase 2+ |
| P6 | **Evaluation method doc** — confirm 2025 metrics use same strict audit script version; record `run_name` in summary | Dev | Phase 3 headline |
| P7 | **2025 report availability** — confirm majority of A-share 2025 annual reports published on CNINFO | Human | Phase 3 timing |

**Soft prerequisites (deferrable):** revenue Tier4 production pilot; full R&D partial fix; financial worksheet 325-cell grading completion.

---

## 6. Pilot design

### 6.1 Phase 1 — 100-company stratified pilot

| Parameter | Value |
|---|---|
| `run_name` | `full_market_2025_pilot` |
| Size | **100** companies |
| Stratification | ~5 boards proportional; include ≥5 financial tagged; include ≥10 BSE; seed fixed for reproducibility |
| Fields | Full 11-field industrial + financial sub-schema where tagged |
| Success criteria | ok rate ≥90%; error=0; proxy within Δ±0.15 of eval1000_v2 reference; no blocker regressions on mandatory controls (002415, 000333, 600011 class) |
| Outputs | `outputs/generalization/full_market_2025_pilot/` |

### 6.2 Phase 2 — One-board pilot

| Parameter | Value |
|---|---|
| `run_name` | `full_market_2025_pilot_bse` (recommended) |
| Size | Full **BSE** 2025 universe (~580–650 cos, per-year list) |
| Rationale | Smallest board; BSE had most strict audit iteration (#24); fast feedback |
| Success criteria | ok rate comparable to 2024 BSE; strict audit runnable; merge + summary generated |
| Outputs | `outputs/generalization/full_market_2025_pilot_bse/` |

### 6.3 Phase 3 — Full-market 2025

| Parameter | Value |
|---|---|
| `run_name` | `full_market_2025` |
| Batch order | **bse → star → szse_main → chinext → sse_main** (same as 2024) |
| Universe | **Per-year** CNINFO A-share list for 2025 reporting season |
| Post-run | Hybrid strict audit + `full_market_2025_summary.md`; SQLite import `run_name=full_market_2025` |
| Scoped refresh | Follow 2024 pattern: extraction first; rnd/revenue refresh **only if** residuals warrant |

---

## 7. Run naming / output directory plan

| Phase | `run_name` | Output directory | SQLite `run_name` | Overwrites 2024? |
|---|---|---|---|---|
| 100-co pilot | `full_market_2025_pilot` | `outputs/generalization/full_market_2025_pilot/` | `full_market_2025_pilot` | **No** |
| Board pilot | `full_market_2025_pilot_bse` | `outputs/generalization/full_market_2025_pilot_bse/` | `full_market_2025_pilot_bse` | **No** |
| Full 2025 | `full_market_2025` | `outputs/generalization/full_market_2025/` | `full_market_2025` | **No** |
| 2023 backfill | `full_market_2023_backfill` | `outputs/generalization/full_market_2023_backfill/` | `full_market_2023_backfill` | **No** |
| 2022 backfill | `full_market_2022_backfill` | `outputs/generalization/full_market_2022_backfill/` | `full_market_2022_backfill` | **No** |

**Scoped refresh runs** (if needed later): append suffix — e.g. `full_market_2025_rnd_refresh`, `full_market_2025_revenue_refresh` — mirroring 2024 convention.

**YAML naming:** `lab/eval_companies_full_market_2025.yaml`, `lab/eval_companies_full_market_2025_pilot.yaml`, etc.

**Gitignore:** Same rules as 2024 — PDFs, per-company subdirs, `eval_results.json` gitignored; summary markdown committable.

---

## 8. Validation gates

| Gate | After | Required before next phase |
|---|---|---|
| **G1 Pilot extract** | Phase 1 | ok ≥90%, error=0, manual spot-check 10 companies |
| **G2 Pilot proxy** | Phase 1 | Non-fin proxy within agreed band vs eval1000_v2 |
| **G3 Board pilot** | Phase 2 | Full board merge OK; strict audit script runs without crash |
| **G4 Board strict** | Phase 2 | BSE strict ≥8.5/11 or documented template gap plan |
| **G5 Full extract** | Phase 3 | ok rate ≥2024 reference (93%±2%); error=0 |
| **G6 Full strict audit** | Phase 3 | Hybrid strict complete; **separate** `strict_audit_summary.md` under 2025 dir |
| **G7 SQLite import** | Phase 3 | Row count sanity vs ok × fields; FK clean |
| **G8 Headline publication** | Phase 3 | **Only after G6** — publish 2025 non-fin strict as **new headline**; do **not** retro-edit 2024 |
| **G9 Backfill** | Phase 4–5 | Each year passes G5–G7 independently |

**Cross-year comparison rule:** 2025 strict usable **cannot** be compared to 2024 **9.43/11** as “improvement” until same audit method version runs on both cohorts with documented rule parity.

---

## 9. Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| 2025 reports not fully published | Medium | Delays Phase 3 | Start Phase 1–2 early; monitor CNINFO |
| Template / layout drift in 2025 PDFs | Medium | Field regressions | 100-co pilot + board pilot before full |
| Per-year universe ≠ 2024 list | High | ok/no_announcement delta | Expected; document in summary |
| Disk exhaustion (multi-year PDFs) | Medium | Run failure | Board batch order; gitignore PDFs; backfill sequential |
| CNINFO rate limits / VPN issues | Medium | ChunkedEncodingError | Retry policy from eval1000 independent run |
| Financial mis-tags propagate | Medium | Wrong sub-schema eval | Complete #31 before financial 2025 headline |
| Mixing 2024/2025 metrics in reports | Medium | Misleading narrative | Separate `run_name`, separate summary files |
| Skipping pilot → full CNINFO | Low | High cost failure | Human gate P1; anti-claims §11 |

---

## 10. Deferred items (remain out of #33 / initial 2025 scope)

| Item | Issue | Notes |
|---|---|---|
| Revenue Tier4 + wrong-table production pilot | #32b follow-up | Harness signal only; defer until post-pilot or parallel scoped tranche |
| R&D remaining partial (72/104 P0 + full pop) | #32 defer | Does not block 2025 forward extraction |
| Revenue partial full methodology (~753) | #32 defer | Enumeration deferred |
| Financial wider extraction rollout | #30 defer | Audit framework done; grading pending |
| Full 2024 strict audit rerun after #32c | Policy defer | 9.43/11 unchanged |
| BrowserUser data source | Phase 4 ROADMAP | After multiyear baseline stable |
| `strict_audit_result` SQLite loader | Optional | Low priority |
| Parallel 2023+2022+2025 CNINFO | **Rejected** | See §3.3 |

---

## 11. Anti-claims

| Claim | Allowed? |
|---|---|
| #33 decision memo complete | **Yes** |
| Multiyear expansion executed | **No** — planning only |
| CNINFO rerun performed in #33 | **No** |
| Full manual validation of future years | **No** |
| 2025 metrics comparable to 2024 9.43/11 as delta | **No** — until same audit on both |
| Financial and non-fin metrics merged | **No** — separate headlines |
| 2024 headline updated by #33 | **No** — remains 9.43/11 |
| Parent #23 closed | **Yes** — after memo commit + human ack |
| #31 / revenue pilot blocked forever | **No** — parallel backlog |

---

## 12. Decision checklist (human sign-off)

- [ ] **A1** Approve **2025 first** (not 2023/2022 backfill first)
- [ ] **A2** Approve **per-year universe** (not frozen 2024 list for 2025 production)
- [ ] **A3** Approve **staged rollout**: 100-co → board → full → backfill
- [ ] **A4** Approve **run_name / directory** scheme (§7)
- [ ] **A5** Confirm **2024 outputs read-only** — no overwrite
- [ ] **A6** Confirm **#31 retag review** timing (before or parallel to Phase 1)
- [ ] **A7** Confirm **CNINFO budget** and disk for pilot + full 2025
- [ ] **A8** Confirm **2025 report season** readiness for Phase 3 target date
- [ ] **A9** Approve opening **implementation issue** for year-parameterized scripts (post-#33)
- [ ] **A10** Close **#33** and **#23** after memo commit

---

## 13. Safe-to-commit / do-not-commit list

### Safe to commit

- `outputs/generalization/full_market_2024/multiyear_expansion_decision_33.md` (this file)
- Doc sync: `CURRENT_STATUS.md`, `CHANGELOG.md`, `ROADMAP.md`, `stage3_quality_followup_summary.md`

### Do not commit (not produced by #33)

- Any `outputs/generalization/full_market_2025*/` directories
- PDFs, `eval_results.json`, `company_profile.json`
- SQLite DB changes
- New YAML universe files (until implementation phase)

---

## 14. GitHub #33 closing comment (中文)

```
#33 多年份扩展决策 — 已完成（决策备忘录）

结论：优先 2025，分阶段 rollout，2024 产出只读不覆盖。

推荐路径：
1. 100 家分层 pilot（full_market_2025_pilot）
2. 单板块 pilot（建议 BSE，full_market_2025_pilot_bse）
3. 全市场 2025（full_market_2025）
4. 再 backfill 2023 / 2022（full_market_2023_backfill、full_market_2022_backfill）

关键决策：
- 下一年份：2025 优先（非 2023/2022 先回填）
- Universe：按年重建 CNINFO 列表（非冻结 2024 名单）
- 不立即全量 CNINFO；不并行多年份
- run_name / 输出目录与 2024 分离
- 2024 non-fin strict 9.43/11 headline 不变

前置条件：本备忘录人工签核、#31 金融漏标 review、年份参数化脚本（后续 implementation issue）、磁盘/CNINFO 预算。

Defer：revenue Tier4 pilot、R&D partial、2024 full strict audit 重跑、BrowserUser。

未做：提取、CNINFO、refresh、strict audit、SQLite、YAML、代码修改。

产物：multiyear_expansion_decision_33.md
```

---

## Answers to decision questions (quick reference)

| # | Question | Answer |
|---|---|---|
| 1 | 2025 first or backfill 2023/2022? | **2025 first** |
| 2 | 2024 universe or per-year? | **Per-year universe** |
| 3 | Pilot, board, or full-market start? | **Staged: 100-co → board → full** |
| 4 | Prerequisites? | §5 — human sign-off, #31, tooling, disk, report season |
| 5 | Run naming? | §7 — `full_market_2025_pilot`, `_pilot_bse`, `full_market_2025`, `_2023_backfill`, `_2022_backfill` |
| 6 | Validation gates? | §8 — G1–G9 |
| 7 | Deferred? | §10 |
| 8 | Financial vs non-fin? | **Separate headlines**; financial sub-schema eval; never mix into 9.43/11 |
| 9 | What not to claim? | §11 |

---

## Parent #23 closing comment draft (中文)

```
#23 Stage 3 质量 follow-up 与多年份规划 — 可关单

子 issue 全部完成：
- #24 BSE strict audit-rule
- #25 rnd scoped refresh
- #26 revenue scoped refresh
- #27 金融 audit 框架
- #28 Stage 3a 汇总
- #30 金融 follow-up（#30a–#30g）
- #31 金融漏标候选已识别（retag 执行 defer 至 2025 前置）
- #32 revenue/R&D residual 当前范围关闭
- #33 多年份扩展决策备忘录

2024 基线状态：
- Stage 3a PASS（有保留项）
- non-fin strict usable 9.43/11（不变）
- 金融 cohort 单独 headline
- 2024 产出只读；后续 2025 分阶段扩展

后续工作（新 issue，非 #23 范围）：
- 2025 pilot 实施（人工签核 §12 后）
- #31 retag review
- revenue Tier4 / R&D partial backlog
- BrowserUser（ROADMAP Phase 4）

产物索引：stage3_quality_followup_summary.md、revenue_rnd_fix_32_final_summary.md、multiyear_expansion_decision_33.md
```
