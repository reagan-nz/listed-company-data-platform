# CNINFO D 类 fund_industry_allocation — Next-Component Planning Summary

_生成时间：2026-07-15 · D-FM-10_

> **性质：** offline planning 摘要 · **CNINFO calls = 0** · **无 live** · **无 runner** · **无 commit** · **无 push**
>
> **Explicit：** NOT verified · NOT production_ready · NOT approved for live

---

## 1. Planning Result

Post shareholder_data **D-FM-09** shared live-path offline mock（commit `0761c90` · real live `NOT_APPROVED` · `controller_execution_allowed=false`）, Era D next-component planning confirms:

| 项 | 值 |
|----|-----|
| **primary** | **`fund_industry_allocation`** |
| **runner-up** | **none in-registry**（live 待 controller） |
| planning gate | **`d_class_fund_industry_allocation_next_component_planning_gate = READY_FOR_APPROVAL`** |
| standing_scope | full-market shareholder / capital · Level-2 **NOT** required |
| first-slice size | **5**（DFIA001–DFIA005 sketch） |
| success threshold | **≥ 3/5 acceptable** → `PASS_WITH_CAVEAT` |

---

## 2. Prior Evidence

| 项 | 内容 |
|----|------|
| Tier-0 sample | `fixtures/d_class/fund_industry_allocation/sample_raw.json` · industry `C26` |
| mapper | `map_to_industry_aggregate` · 1 raw → 3 metrics |
| schema | `schemas/d_class/d_industry_aggregate.schema.json` |
| Phase2 stability | `fia_default` / `fia_rdate_20260331` · **19** rows · `fia_rdate_20251231` · **0** rows empty_but_valid |
| endpoint | `data20/fund/industry` · `records_path=data.records` · `company_code_available=false` |

---

## 3. DLC006R / 301259

| 项 | 政策 |
|----|------|
| 301259 / 688671 | **excluded**（无 company 绑定；政策保留） |
| DLC006R | known-event **closed** · **no reopen** |
| company schemas | **禁止** 写入 `d_company_event` / `d_company_metric_periodic` |

---

## 4. Request Model Note

行业聚合截面体量小（~19 行）：first-slice **prefer ≤3 shared probes**（default · rdate filled · rdate empty），再按 `industry_code` 离线过滤 DFIA 案例。避免重复无意义全表拉取。

---

## 5. Closed / In-flight Tracks（unchanged）

| Track | Status |
|-------|--------|
| shareholder_data | live-path ready · live **NOT_APPROVED** · 不本任务扩展 |
| abnormal_trading | live-path ready · live **NOT_APPROVED** · 不本任务扩展 |
| executive_shareholding / shareholder_change / equity_pledge / RSU / block_trade / margin / disclosure / known-event | **closed** · 不重开 |

---

## 6. Safety

| 项 | 本回合 |
|----|--------|
| CNINFO | **0** |
| live / runner | **none** |
| commit / push | **no** |
| verified / production_ready | **no** |
| A/B/C files | **untouched** |

```text
task_id = D-FM-10
phase = fund_industry_allocation_next_component_offline_planning
ready_for_commit = true
cninfo_calls = 0
```
