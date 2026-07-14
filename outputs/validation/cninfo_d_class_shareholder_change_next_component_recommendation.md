# CNINFO D 类 shareholder_change — Next-Component Recommendation

_生成时间：2026-07-13 · post equity_pledge commit **`85abad0`**

> **planning gate：** `d_class_shareholder_change_next_component_planning_gate = READY_FOR_APPROVAL`

---

## Primary Recommendation

**Component:** `shareholder_change`（股东增减持 · `shareholeder/detail`）

**One-line rationale:** equity_pledge first-slice 已收口并 commit（**`85abad0`** · `PASS_WITH_CAVEAT`）后，Era D 下一自然组件为 **P0 股东变动**；registry/schema 就绪、DLC006（000550）Phase1 tiny-live 先例、与全部已 closed slice 正交；须排除 301259 且 **不** 重开 known-event。

---

## Runner-Up

**Component:** `executive_shareholding`（高管持股变动）

**Rationale:** P0 · registry 就绪 · 但 DLC007 `needs_review_candidate` 与 DDS004 field-mapping 负担重叠；适合作为 shareholder_change 收口后的下一顺位。

---

## Rank Table

| Rank | Component | Risk | First-slice size |
|------|-----------|------|------------------|
| **1** | **shareholder_change** | medium | **5** |
| 2 | executive_shareholding | medium | 5 |
| 3 | abnormal_trading | high | deprioritize |
| 4 | shareholder_data | medium | deprioritize |
| 5 | fund_industry_allocation | low | deprioritize |
| — | equity_pledge | — | closed **`85abad0`** · NOT pushed |
| — | restricted_shares_unlock | — | closed **`aa087b5`** · NOT verified |
| — | block_trade | — | closed **`403472d`** · NOT verified |
| — | margin_trading | — | closed **`116f875`** |
| — | disclosure_schedule | — | closed **`d37ce0a`** |
| — | known_event | — | closed **`389cd9c`** |

---

## DLC006R / 301259 Policy

| 项 | 政策 |
|----|------|
| 301259 | **excluded** from primary first-slice universe |
| DLC006R | known-event track **closed** · **no reopen** |
| DLC006（000550） | usable as **distinct DSC** precedent · not DLC006R proxy |
| disclosure upgrade | **forbidden** |

---

## RSU / block_trade / equity_pledge Lessons Applied

- Universe 混排 `empty_but_valid` + `captured_normal_or_empty_but_valid`
- **禁止** sole `captured_normal_candidate` on sparse anchor（DBT002 教训）
- **避免** fragile sole `captured_normal_or_needs_review` without mix（DEP004 教训）
- `empty_but_valid` 为合法 acceptable 结果
- caveat ledger 预留 · **NOT verified**
- RSU / block_trade / equity_pledge **NOT verified** · **NOT pushed**

---

## Proposed First-Slice Parameters（sketch only）

| 项 | 值 |
|----|-----|
| case count | **5**（DSC001–DSC005） |
| output root | `outputs/validation/cninfo_d_class_shareholder_change_first_slice/` |
| flags | `--shareholder-change-first-slice` · `--approve-d-class-shareholder-change-first-slice` |
| endpoint | `data20/shareholeder/detail`（CNINFO spelling · do not fix） |
| query mode | `type=inc` + shared `tdate`（first-slice sketch） |
| proposed anchor | **2026-07-03**（registry default · offline only） |
| request cap | **≤ 20** |
| threshold | **≥ 3/5 acceptable** → `PASS_WITH_CAVEAT` |

**NOT APPROVED** · **无 runner** · **无 live**

---

## Human Approval Phrase（separate gate）

> **I approve D-class shareholder_change as the next Era D component.**

---

## Next Task

Human approve component choice → **shareholder_change first-slice approval package**（offline · universe + checklist · **无 CNINFO**）

---

## Red Lines

No CNINFO · No live · No closed-track expansion · No PDF/DB/MinIO/RAG/verified · No commit
