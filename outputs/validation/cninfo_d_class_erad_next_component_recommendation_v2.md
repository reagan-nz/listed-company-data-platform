# CNINFO D 类 Era D — Next-Component Recommendation v2

_生成时间：2026-07-10 · post block_trade commit **`403472d`_

> **refresh gate：** `d_class_erad_next_component_planning_refresh_gate = READY_FOR_APPROVAL`

---

## Primary Recommendation

**Component:** `restricted_shares_unlock`（限售股解禁 · `liftBan/detail`）

**One-line rationale:** block_trade first-slice 已收口（**`403472d`** · `PASS_WITH_CAVEAT`）后，Era D 下一自然组件为 **P0 解禁日历**；registry/schema 就绪、DLC003 tiny-live 先例、orthogonality 高，且与已 closed 的 margin_trading / disclosure_schedule / block_trade 无重叠。

---

## Runner-Up

**Component:** `equity_pledge`（股权质押）

**Rationale:** P0 · DLC005 `empty_but_valid` 先例 · 单 tdate 端点 · 实施成本低于解禁 multi-probe；适合作为 restricted_shares_unlock 收口后的第三组件。

---

## Rank Table

| Rank | Component | Risk | First-slice size |
|------|-----------|------|------------------|
| **1** | **restricted_shares_unlock** | medium | **5** |
| 2 | equity_pledge | low | 5 |
| 3 | shareholder_change | medium | 5 |
| 4 | executive_shareholding | medium | 5 |
| — | block_trade | — | closed **`403472d`** |
| — | margin_trading | — | closed **`116f875`** |
| — | disclosure_schedule | — | closed **`d37ce0a`** |

---

## Excludes

| 类别 | 项 |
|------|-----|
| Primary cases | **688671** · **301259** |
| Closed tracks | known-event · margin_trading · disclosure_schedule · block_trade first-slice |
| This round | abnormal_trading · shareholder_data · fund_industry_allocation |

---

## block_trade Lessons Applied

- Universe 混排 `empty_but_valid` + `captured_normal_or_empty_but_valid`
- 避免稀疏锚点上单一 `captured_normal_candidate`（DBT002 教训）
- `empty_but_valid` 为合法 acceptable 结果
- caveat ledger 预留 · **NOT verified**

---

## Proposed First-Slice Parameters（sketch only）

| 项 | 值 |
|----|-----|
| case count | **5**（DRU001–DRU005） |
| output root | `outputs/validation/cninfo_d_class_restricted_shares_unlock_first_slice/` |
| flags | `--restricted-shares-unlock-first-slice` · `--approve-d-class-restricted-shares-unlock-first-slice` |
| request cap | **≤ 20** |
| threshold | **≥ 3/5 acceptable** → `PASS_WITH_CAVEAT` |

**NOT APPROVED** · **无 runner** · **无 live**

---

## Next Task

Human approve next-component choice → **restricted_shares_unlock first-slice approval package**（offline · universe + checklist · **无 CNINFO**）

---

## Red Lines

No CNINFO · No live · No closed-track expansion · No PDF/DB/MinIO/RAG/verified · No commit
