# CNINFO D 类 shareholder_data — Next-Component Planning

_生成时间：2026-07-15 · D-FM-06_

> **性质：** offline next-component planning · **CNINFO calls = 0** · **无 live** · **无 runner** · **无 commit** · **无 push** · **不是 verified** · **不是 production_ready**

**Prior state：** `abnormal_trading` first-slice live-path **implemented**（D-FM-05 · offline mock 4/5 `PASS_WITH_CAVEAT`）· 真实 live **`NOT_APPROVED`** · `controller_execution_allowed=false` · standing D scope = full-market shareholder / capital

**Planning gate：**

```text
d_class_shareholder_data_next_component_planning_gate = READY_FOR_APPROVAL
standing_scope_auth = full_market_shareholder_capital
level2_phrase_required = false
abnormal_trading_live_gate = NOT_APPROVED
```

**Explicit：** standing D scope 下 **不** IDLE 等待 Level-2 短语 · **不** 实现 runner/live · **不** 重开 DLC006R / 301259 · **不** 推进 abnormal_trading 真实 live（本任务）

---

## 1. Why Plan Now

| 事件 | 状态 |
|------|------|
| abnormal_trading | planning→fixtures→runner→live-path offline mock **DONE**（D-FM-03…05）· 真实 live 待 controller |
| executive_shareholding / shareholder_change / equity_pledge / RSU / block_trade / margin / disclosure / known-event | **closed** · 不得重开 |
| shareholder_data | registry + schema + mapper + sample_raw 就绪 · Phase2 稳定性 **5255** 行先例 · **无** first-slice · **无** runner |

Era D 在 abnormal_trading live-path 收口至 offline mock 后，下一自然 **资本/股东结构** 组件为 **`shareholder_data`**（股东人数/户均持股 · 报告期截面）。

---

## 2. Ranked Options（post abnormal_trading D-FM-05）

| Rank | Component | Status | Rationale |
|------|-----------|--------|-----------|
| **1** | **`shareholder_data`** | **primary** | P1 资本/股东结构 · registry/schema/mapper/sample_raw 就绪 · Phase2 稳定截面 · 与已 closed event slice 正交 |
| 2 | `fund_industry_allocation` | deprioritize | P2 · `company_code_available=false` · 行业聚合 |
| — | `abnormal_trading` | live-path ready · live **NOT_APPROVED** | **不** 本任务重做 · 真实 live 仅 controller 批准后 |
| — | closed tracks | closed | 不得重开 |

**Recommend ONE primary：** **`shareholder_data`**

---

## 3. Primary: `shareholder_data`

| 项 | 评估 |
|----|------|
| endpoint | `https://www.cninfo.com.cn/data20/shareholeder/data` · POST · query |
| records_path | `data.records` |
| query mode | **`rdate_report_period`** · `rdate=YYYYMMDD`（registry default `20260331`） |
| company filter | 全市场报告期截面后按 `SECCODE` 过滤目标公司 |
| schema | `d_company_metric_periodic` · 1 raw → **6** metric rows |
| mapper | `map_to_company_metric_periodic` · `mapping_confidence=high` |
| prior evidence | Phase2 stability · `sd_rdate_20260331` · **5255** rows · sample_raw `000001` 平安银行 |
| risk | **medium→managed** · 截面大体量 · first-slice 以 **1 shared rdate** + company filter 控制 CNINFO |
| request model | **prefer 1 shared CNINFO** for universe rdate · per-case filter offline · total cap **≤ 5**（prefer **1**） |
| threshold | **≥ 3/5 acceptable** → `PASS_WITH_CAVEAT` |

### First-Slice Parameters（sketch only · NOT APPROVED · no runner）

| 项 | 值 |
|----|-----|
| size | **5**（DSD001–DSD005） |
| output root | `outputs/validation/cninfo_d_class_shareholder_data_first_slice/` |
| mode flag | `--shareholder-data-first-slice`（**未来** · 本任务 **不实现**） |
| approval flag | `--approve-d-class-shareholder-data-first-slice`（**未来** · live only） |
| anchor rdate | **20260331**（registry default · Phase2 已验证截面） |
| request cap | total **≤ 5** · prefer **1** shared |

---

## 4. Excludes

| 类别 | 项 |
|------|-----|
| Primary cases | **688671** · **301259** |
| Closed tracks | known-event · margin · disclosure · block_trade · RSU · equity_pledge · shareholder_change · executive_shareholding reopen |
| In-flight | abnormal_trading **真实 live**（须 controller；本包不触碰） |
| Forbidden | DLC006R reopen · PDF/DB/MinIO/RAG · verified · production_ready · commit/push（本任务） · A/B/C |

---

## 5. Red Lines

No CNINFO · No live · No runner · No closed-track expansion · No PDF/DB/MinIO/RAG/verified · No commit · No push · No DLC006R/301259 reopen · No A/B/C file touch · No Level-2 IDLE
