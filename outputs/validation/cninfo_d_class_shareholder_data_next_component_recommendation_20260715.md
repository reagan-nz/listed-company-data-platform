# CNINFO D 类 shareholder_data — Next-Component Recommendation

_生成时间：2026-07-15 · post abnormal_trading D-FM-05 live-path offline mock · D-FM-06_

> **planning gate：** `d_class_shareholder_data_next_component_planning_gate = READY_FOR_APPROVAL`
>
> **standing_scope：** full-market shareholder / capital · **Level-2 phrase NOT required**
>
> **Explicit：** NOT verified · NOT production_ready · CNINFO = 0 · 无 runner · 无 live · 无 commit · 无 push

---

## Primary Recommendation

**Component:** `shareholder_data`（股东数据 · periodic · `data20/shareholeder/data`）

**One-line rationale:** abnormal_trading live-path 已 offline mock 收口（D-FM-05）且真实 live 仍 `NOT_APPROVED` 时，Era D 下一自然资本组件为报告期股东人数截面；registry/schema/mapper/sample_raw 与 Phase2 5255 行稳定性就绪；须排除 301259/688671 且 **不** 重开 known-event / DLC006R。

---

## Runner-Up

**Component:** `fund_industry_allocation`（基金行业配置 · deprioritize）

**Rationale:** `company_code_available=false` · 行业聚合 · 非公司级资本 first-slice 优先。

---

## Rank Table

| Rank | Component | Risk | First-slice size |
|------|-----------|------|------------------|
| **1** | **shareholder_data** | medium | **5** |
| 2 | fund_industry_allocation | low | deprioritize |
| — | abnormal_trading | high | inflight · live NOT_APPROVED · 不本任务扩展 |
| — | executive_shareholding | — | S5 PASS_WITH_CAVEAT · 不重开 |
| — | shareholder_change / equity_pledge / RSU / block_trade / margin / disclosure / known-event | — | closed · 不重开 |

---

## Standing Scope Auth

本组件处于 D standing scope（full-market shareholder / capital）。**不** IDLE 等待单独 Level-2 短语。first-slice **live** 仍须未来 `--approve-d-class-shareholder-data-first-slice` 且 `controller_execution_allowed`。

---

## Proposed First-Slice Parameters（sketch only）

| 项 | 值 |
|----|-----|
| case count | **5**（DSD001–DSD005） |
| output root | `outputs/validation/cninfo_d_class_shareholder_data_first_slice/` |
| flags | `--shareholder-data-first-slice` · `--approve-d-class-shareholder-data-first-slice`（**未来**） |
| endpoint | `data20/shareholeder/data` |
| query mode | `rdate_report_period` · `rdate=20260331` |
| request model | **1 shared rdate** + SECCODE filter · total cap **≤ 5**（prefer **1**） |
| threshold | **≥ 3/5 acceptable** → `PASS_WITH_CAVEAT` |

**NOT APPROVED** · **无 runner** · **无 live**

---

## Next Task

Standing-scope offline continue → **shareholder_data first-slice approval package**（universe lock + VR + Tier-1 fixtures · **无 CNINFO**）· **或** controller 批准后 abnormal_trading bounded live（独立任务）

---

## Red Lines

No CNINFO · No live · No runner · No closed-track expansion · No PDF/DB/MinIO/RAG/verified · No commit · No push · No DLC006R reopen · No Level-2 IDLE
