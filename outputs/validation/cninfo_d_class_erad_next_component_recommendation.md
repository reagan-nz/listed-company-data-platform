# CNINFO D 类 Era D — Next-Component Recommendation

_生成时间：2026-07-10_

> **规划 gate：** `d_class_erad_next_component_planning_gate = READY_FOR_APPROVAL`

---

## Primary Recommendation

**Component:** `block_trade`（大宗交易 · `data20/ints/statistics`）

**One-line rationale:** 在 margin_trading 与 disclosure_schedule 均已 5/5 收口后，`block_trade` 具备 **最高 orthogonality**、**最低实施成本**（~1 CNINFO/公司）、Phase1 tiny-live **acceptable** 先例（DLC002），且 **不受** known-event track（688671/301259）污染。

---

## Runner-Up

**Component:** `restricted_shares_unlock`（限售股解禁 · `liftBan/detail`）

**Rationale:** P0 组件、Era D 广度价值高；但 anchor 窗口与 probe 复杂度高于 block_trade，且须严格排除 688671（DLC003R caveated evidence · track closed）。

---

## Proposed First-Slice Parameters

| 项 | 值 |
|----|-----|
| case count | **5**（DBT001–DBT005） |
| exclude | **688671** · **301259** |
| output root | `outputs/validation/cninfo_d_class_block_trade_first_slice/` |
| flags | `--block-trade-first-slice` · `--approve-d-class-block-trade-first-slice` |
| request cap | **≤ 20**（planned **5**） |
| execution threshold | **≥ 3/5 acceptable** → `PASS_WITH_CAVEAT` |

---

## Not Selected (This Round)

| 组件 | 原因 |
|------|------|
| margin_trading | closed @ `116f875` |
| disclosure_schedule | closed @ `d37ce0a` |
| shareholder_change | DLC006R gap baggage @ 301259 |
| executive_shareholding | needs_review / 002415 overlap |
| abnormal_trading | no tiny-live case; market-level endpoint |

---

## Closed Tracks (Unchanged)

| Track | Gate |
|-------|------|
| known-event | `PASS_WITH_CAVEAT` |
| margin_trading first-slice | `PASS_WITH_CAVEAT` |
| disclosure_schedule first-slice | `PASS_WITH_CAVEAT` |

---

## Next Task

**block_trade first-slice approval package**（offline · universe + checklist + command draft · **无 runner · 无 CNINFO**）

---

## Red Lines

No CNINFO · No live · No closed-track expansion · No PDF/DB/MinIO/RAG/verified · No commit
