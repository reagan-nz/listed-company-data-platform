# CNINFO D 类 equity_pledge — Next-Component Recommendation

_生成时间：2026-07-10 · post RSU commit **`aa087b5`_

> **planning gate：** `d_class_equity_pledge_next_component_planning_gate = READY_FOR_APPROVAL`

---

## Primary Recommendation

**Component:** `equity_pledge`（股权质押 · `equityPledge/list`）

**One-line rationale:** RSU first-slice 已收口并 commit（**`aa087b5`** · `PASS_WITH_CAVEAT`）后，Era D 下一自然组件为 **P0 股权质押**；registry/schema 就绪、DLC005 tiny-live `empty_but_valid` 先例、单 `tdate` 端点实施成本低，且与全部已 closed slice 正交。

---

## Runner-Up

**Component:** `shareholder_change`（股东变动）

**Rationale:** P0 · registry 就绪 · 但须排除 301259 且 DLC006R gap 文档负担高于 equity_pledge；适合作为 equity_pledge 收口后的第四顺位组件。

---

## Rank Table

| Rank | Component | Risk | First-slice size |
|------|-----------|------|------------------|
| **1** | **equity_pledge** | low | **5** |
| 2 | shareholder_change | medium | 5 |
| 3 | executive_shareholding | medium | 5 |
| — | restricted_shares_unlock | — | closed **`aa087b5`** |
| — | block_trade | — | closed **`403472d`** · NOT verified |
| — | margin_trading | — | closed **`116f875`** |
| — | disclosure_schedule | — | closed **`d37ce0a`** |
| — | known_event | — | closed **`389cd9c`** |

---

## Excludes

| 类别 | 项 |
|------|-----|
| Primary cases | **688671** · **301259** |
| Closed tracks | known-event · margin_trading · disclosure_schedule · block_trade · restricted_shares_unlock |
| This round | abnormal_trading · shareholder_data · fund_industry_allocation |

---

## RSU / block_trade Lessons Applied

- Universe 混排 `empty_but_valid` + `captured_normal_or_empty_but_valid`
- 避免稀疏锚点上单一 `captured_normal_candidate`（DBT002 教训）
- `empty_but_valid` 为合法 acceptable 结果
- caveat ledger 预留 · **NOT verified**
- RSU / block_trade **NOT verified** · **NOT pushed**

---

## Proposed First-Slice Parameters（sketch only）

| 项 | 值 |
|----|-----|
| case count | **5**（DEP001–DEP005） |
| output root | `outputs/validation/cninfo_d_class_equity_pledge_first_slice/` |
| flags | `--equity-pledge-first-slice` · `--approve-d-class-equity-pledge-first-slice` |
| endpoint | `data20/equityPledge/list` |
| query mode | `tdate_daily` |
| proposed anchor | **2026-07-03**（registry default · offline only） |
| request cap | **≤ 20** |
| threshold | **≥ 3/5 acceptable** → `PASS_WITH_CAVEAT` |

**NOT APPROVED** · **无 runner** · **无 live**

---

## Human Approval Phrase（separate gate）

> **I approve D-class equity_pledge as the next Era D component.**

---

## Next Task

Human approve component choice → **equity_pledge first-slice approval package**（offline · universe + checklist · **无 CNINFO**）

---

## Red Lines

No CNINFO · No live · No closed-track expansion · No PDF/DB/MinIO/RAG/verified · No commit
