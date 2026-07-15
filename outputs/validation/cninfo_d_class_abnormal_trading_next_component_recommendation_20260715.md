# CNINFO D 类 abnormal_trading — Next-Component Recommendation

_生成时间：2026-07-15 · post executive_shareholding S5 **PASS_WITH_CAVEAT** · D-FM-03_

> **planning gate：** `d_class_abnormal_trading_next_component_planning_gate = READY_FOR_APPROVAL`
>
> **standing_scope：** full-market shareholder / capital · **Level-2 phrase NOT required**
>
> **Explicit：** NOT verified · NOT production_ready · CNINFO = 0 · 无 live · 无 commit · 无 push

---

## Primary Recommendation

**Component:** `abnormal_trading`（公开信息 / 异常交易 · `getMarketStatisticsData`）

**One-line rationale:** executive_shareholding S5 收口后，Era D 下一自然组件为市场异动；registry/schema/mapper/sample_raw 就绪；须排除 301259/688671 且 **不** 重开 known-event / DLC006R。

---

## Runner-Up

**Component:** `shareholder_data`（股东数据 · periodic）— deprioritize relative

---

## Standing Auth

本组件处于 D standing scope（full-market shareholder / capital）。**不** IDLE 等待单独 Level-2 短语。first-slice **live** 仍须 `--approve-d-class-abnormal-trading-first-slice` 且 `controller_execution_allowed`。

---

## Next Task（this package）

Offline first-slice package + Tier-1 fixtures + runner S4 dry-run path（**无 CNINFO** · **无 live**）
