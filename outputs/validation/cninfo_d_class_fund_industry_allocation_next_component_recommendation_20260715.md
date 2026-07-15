# CNINFO D 类 fund_industry_allocation — Next-Component Recommendation

_生成时间：2026-07-15 · post shareholder_data D-FM-09 shared live-path offline mock · D-FM-10_

> **planning gate：** `d_class_fund_industry_allocation_next_component_planning_gate = READY_FOR_APPROVAL`
>
> **standing_scope：** full-market shareholder / capital · **Level-2 phrase NOT required**
>
> **Explicit：** NOT verified · NOT production_ready · CNINFO = 0 · 无 runner · 无 live · 无 commit · 无 push

---

## Primary Recommendation

**Component:** `fund_industry_allocation`（基金行业配置 · industry aggregate · `data20/fund/industry`）

**One-line rationale:** shareholder_data shared live-path 已 offline mock 收口（D-FM-09 · `0761c90`）且真实 live 仍 `NOT_APPROVED` / `controller_execution_allowed=false` 时，Era D 下一自然已注册资本组件为行业级基金配置截面；registry/schema/mapper/sample_raw 与 Phase2 19 行稳定性就绪；`company_code_available=false` · **禁止** 写入 company event/metric schema · **不** 重开 known-event / DLC006R。

---

## Runner-Up

**Component:** none in-registry

**Rationale:** shareholder_data / abnormal_trading 仅待 controller 批准后的 bounded real live；其余 company-event tracks 已 closed；`executive_shareholding_summary` 未注册。

---

## Rank Table

| Rank | Component | Risk | First-slice size |
|------|-----------|------|------------------|
| **1** | **fund_industry_allocation** | low | **5** |
| — | shareholder_data | medium | inflight · live NOT_APPROVED · 不本任务扩展 |
| — | abnormal_trading | high | inflight · live NOT_APPROVED · 不本任务扩展 |
| — | executive_shareholding / shareholder_change / equity_pledge / RSU / block_trade / margin / disclosure / known-event | — | closed · 不重开 |

---

## Standing Scope Auth

本组件处于 D standing scope（full-market shareholder / capital）。**不** IDLE 等待单独 Level-2 短语。first-slice **live** 仍须未来 `--approve-d-class-fund-industry-allocation-first-slice` 且 `controller_execution_allowed`。

---

## Proposed First-Slice Parameters（sketch only）

| 项 | 值 |
|----|-----|
| case count | **5**（DFIA001–DFIA005） |
| output root | `outputs/validation/cninfo_d_class_fund_industry_allocation_first_slice/` |
| flags | `--fund-industry-allocation-first-slice` · `--approve-d-class-fund-industry-allocation-first-slice`（**未来**） |
| endpoint | `data20/fund/industry` |
| query mode | `default` + optional `rdate` |
| request model | **≤3 shared probes**（default · rdate=20260331 · rdate=20251231）+ offline industry filter · total cap **≤ 5** |
| threshold | **≥ 3/5 acceptable** → `PASS_WITH_CAVEAT` |

**NOT APPROVED** · **无 runner** · **无 live**

---

## Next Task

Standing-scope offline continue → **fund_industry_allocation first-slice approval package**（universe lock + VR + Tier-1 fixtures · **无 CNINFO**）· **或** controller 批准后 shareholder_data / abnormal_trading bounded live（独立任务）

---

## Red Lines

No CNINFO · No live · No runner · No closed-track expansion · No PDF/DB/MinIO/RAG/verified · No commit · No push · No DLC006R reopen · No Level-2 IDLE
