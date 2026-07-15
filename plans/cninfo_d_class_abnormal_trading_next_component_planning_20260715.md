# CNINFO D 类 abnormal_trading — Next-Component Planning

_生成时间：2026-07-15_

> **性质：** offline next-component planning · **CNINFO calls = 0** · **无 live** · **无 commit** · **无 push** · **不是 verified** · **不是 production_ready**

**Prior state：** `executive_shareholding` first-slice **S5 offline closure `PASS_WITH_CAVEAT`**（D-FM-02）· Controller committing · standing D scope = full-market shareholder / capital

**Planning gate：**

```text
d_class_abnormal_trading_next_component_planning_gate = READY_FOR_APPROVAL
standing_scope_auth = full_market_shareholder_capital
level2_phrase_required = false
```

**Explicit：** standing D scope 下 **不** IDLE 等待 Level-2 短语 · **不** 实现 live · **不** 重开 DLC006R / 301259

---

## 1. Why Plan Now

| 事件 | 状态 |
|------|------|
| executive_shareholding | S5 closure **PASS_WITH_CAVEAT** · D-FM-02 · Controller committing |
| shareholder_change / equity_pledge / RSU / block_trade / margin / disclosure / known-event | **closed** · 不得重开 |
| abnormal_trading | registry + schema + mapper + sample_raw 就绪 · **无** first-slice · **无** tiny-live company case |

Era D 下一自然资本/市场组件为 **`abnormal_trading`**（市场异动 · `getMarketStatisticsData` / `marketList`）。

---

## 2. Ranked Options（post executive_shareholding S5）

| Rank | Component | Status | Rationale |
|------|-----------|--------|-----------|
| **1** | **`abnormal_trading`** | **primary** | P1 资本/市场 · registry/schema/mapper 就绪 · sample_raw Tier0 · 与已 closed slice 正交 |
| 2 | `shareholder_data` | deprioritize | P2 periodic · metric_periodic · 非本轮 |
| 3 | `fund_industry_allocation` | deprioritize | P2 基金行业 · company_code_available=false |
| — | `executive_shareholding` | S5 **PASS_WITH_CAVEAT** | 不得重开 first-slice · Controller commit |
| — | closed tracks | closed | 不得重开 |

**Recommend ONE primary：** **`abnormal_trading`**

---

## 3. Primary: `abnormal_trading`

| 项 | 评估 |
|----|------|
| endpoint | `https://www.cninfo.com.cn/data/statis/getMarketStatisticsData` · POST · query |
| records_path | `marketList` |
| query mode | **`single_day_paged`** · `sdate=edate=2026-07-03` · page=1 · rows=30 |
| company filter | 市场日截面后按 `secCode` 过滤目标公司（company_code_available=true） |
| schema | `d_company_event` · optional future `d_event_party_detail`（detail[] **deferred**） |
| mapper | `_map_abnormal_trading` · mapping_confidence=medium |
| risk | **high→managed** · 市场级端点 · 无 Phase1 tiny-live company case · first-slice 以 expectation mix + empty_but_valid 控制稀疏日 |
| request cap | per-case **≤ 1** · total **≤ 20** · planned **5** |
| threshold | **≥ 3/5 acceptable** → `PASS_WITH_CAVEAT` |

### First-Slice Parameters（locked in D-FM-03 package）

| 项 | 值 |
|----|-----|
| size | **5**（DAT001–DAT005） |
| output root | `outputs/validation/cninfo_d_class_abnormal_trading_first_slice/` |
| mode flag | `--abnormal-trading-first-slice` |
| approval flag | `--approve-d-class-abnormal-trading-first-slice`（live only · 本任务不 live） |
| anchor | **2026-07-03** |

---

## 4. Excludes

| 类别 | 项 |
|------|-----|
| Primary cases | **688671** · **301259** |
| Closed tracks | known-event · margin · disclosure · block_trade · RSU · equity_pledge · shareholder_change · executive_shareholding reopen |
| Forbidden | DLC006R reopen · PDF/DB/MinIO/RAG · verified · production_ready · commit/push（本任务） |

---

## 5. Red Lines

No CNINFO · No live · No closed-track expansion · No PDF/DB/MinIO/RAG/verified · No commit · No push · No DLC006R/301259 reopen · No A/B/C file touch
