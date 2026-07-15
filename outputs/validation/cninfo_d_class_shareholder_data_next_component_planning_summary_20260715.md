# CNINFO D 类 shareholder_data — Next-Component Planning Summary

_生成时间：2026-07-15 · D-FM-06_

> **性质：** offline planning 摘要 · **CNINFO calls = 0** · **无 live** · **无 runner** · **无 commit** · **无 push**
>
> **Explicit：** NOT verified · NOT production_ready · NOT approved for live

---

## 1. Planning Result

Post abnormal_trading **D-FM-05** live-path offline mock（4/5 `PASS_WITH_CAVEAT` · real live `NOT_APPROVED`）, Era D next-component planning confirms:

| 项 | 值 |
|----|-----|
| **primary** | **`shareholder_data`** |
| **runner-up** | **`fund_industry_allocation`**（deprioritize） |
| planning gate | **`d_class_shareholder_data_next_component_planning_gate = READY_FOR_APPROVAL`** |
| standing_scope | full-market shareholder / capital · Level-2 **NOT** required |
| first-slice size | **5**（DSD001–DSD005 sketch） |
| success threshold | **≥ 3/5 acceptable** → `PASS_WITH_CAVEAT` |

---

## 2. Prior Evidence

| 项 | 内容 |
|----|------|
| Tier-0 sample | `fixtures/d_class/shareholder_data/sample_raw.json` · 000001 平安银行 |
| mapper | `map_to_company_metric_periodic` · 1 raw → 6 metrics |
| schema | `schemas/d_class/d_company_metric_periodic.schema.json` · prior schema validation **PASS** |
| Phase2 stability | `sd_rdate_20260331` · **5255** rows · `testing_stable_sample` |
| endpoint | `data20/shareholeder/data?rdate=YYYYMMDD` · `records_path=data.records` |

---

## 3. DLC006R / 301259

| 项 | 政策 |
|----|------|
| 301259 / 688671 | **excluded** from primary universe |
| DLC006R | known-event **closed** · **no reopen** |

---

## 4. Request Model Note

全市场报告期截面：first-slice **prefer 1 shared rdate request**，再按 `SECCODE` 过滤 DSD001–DSD005。避免 5× 重复全市场拉取。

---

## 5. Closed / In-flight Tracks（unchanged）

| Track | Status |
|-------|--------|
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
task_id = D-FM-06
phase = shareholder_data_next_component_offline_planning
ready_for_commit = true
cninfo_calls = 0
```
