# CNINFO D 类 fund_industry_allocation — Next-Component Planning

_生成时间：2026-07-15 · D-FM-10_

> **性质：** offline next-component planning · **CNINFO calls = 0** · **无 live** · **无 runner** · **无 commit** · **无 push** · **不是 verified** · **不是 production_ready**

**Prior state：** `shareholder_data` first-slice shared live-path **implemented**（D-FM-09 · offline mock · commit `0761c90`）· 真实 live **`NOT_APPROVED`** · `controller_execution_allowed=false` · standing D scope = full-market shareholder / capital

**Planning gate：**

```text
d_class_fund_industry_allocation_next_component_planning_gate = READY_FOR_APPROVAL
standing_scope_auth = full_market_shareholder_capital
level2_phrase_required = false
shareholder_data_live_gate = NOT_APPROVED
abnormal_trading_live_gate = NOT_APPROVED
```

**Explicit：** standing D scope 下 **不** IDLE 等待 Level-2 短语 · **不** 实现 runner/live · **不** 重开 DLC006R / 301259 · **不** 推进 shareholder_data / abnormal_trading 真实 live（本任务）

---

## 1. Why Plan Now

| 事件 | 状态 |
|------|------|
| shareholder_data | planning→fixtures→runner→shared live-path offline mock **DONE**（D-FM-06…09 · `0761c90`）· 真实 live 待 controller |
| abnormal_trading | live-path offline mock **DONE**（D-FM-05）· 真实 live **NOT_APPROVED** |
| executive_shareholding / shareholder_change / equity_pledge / RSU / block_trade / margin / disclosure / known-event | **closed** · 不得重开 |
| fund_industry_allocation | registry + schema + mapper + sample_raw 就绪 · Phase2 稳定性 19 行 / empty rdate 先例 · **无** first-slice · **无** runner |

Era D 在 shareholder_data shared live-path 收口至 offline mock 后，下一自然 **资本侧** 注册组件为 **`fund_industry_allocation`**（基金行业配置 · 行业聚合截面）。本组件 `company_code_available=false`，**不**进入 company event / company metric schema。

---

## 2. Ranked Options（post shareholder_data D-FM-09）

| Rank | Component | Status | Rationale |
|------|-----------|--------|-----------|
| **1** | **`fund_industry_allocation`** | **primary** | 唯一剩余已注册资本侧 source · registry/schema/mapper/sample_raw 就绪 · Phase2 19 行 + empty_but_valid 先例 · 与已 closed company-event slice 正交 |
| — | `shareholder_data` | live-path ready · live **NOT_APPROVED** | **不** 本任务重做 · 真实 live 仅 controller 批准后 |
| — | `abnormal_trading` | live-path ready · live **NOT_APPROVED** | **不** 本任务重做 · 真实 live 仅 controller 批准后 |
| — | closed tracks | closed | 不得重开 |
| — | `executive_shareholding_summary` | **not registered** | 未来 discovery · **out of scope** |

**Recommend ONE primary：** **`fund_industry_allocation`**

---

## 3. Primary: `fund_industry_allocation`

| 项 | 评估 |
|----|------|
| endpoint | `https://www.cninfo.com.cn/data20/fund/industry` · POST · query |
| records_path | `data.records` |
| query mode | **`default`**（无参）· 可选 **`rdate`**（`rdate=YYYYMMDD`） |
| company filter | **无** · `company_code_available=false` · 按 `industry_code`（F001V）识别行 |
| schema | `d_industry_aggregate` · 1 raw → **3** metric rows |
| mapper | `map_to_industry_aggregate` · `mapping_confidence=high` |
| prior evidence | Phase2 stability · `fia_default` / `fia_rdate_20260331` · **19** rows · `fia_rdate_20251231` · **0** rows empty_but_valid · sample_raw `C26` |
| risk | **low→managed** · 行业聚合体量小（~19）· first-slice 以 **≤3 shared probes**（default + rdate filled + rdate empty）控制 CNINFO |
| request model | prefer **≤ 3** CNINFO · offline industry-row filter · total cap **≤ 5** |
| threshold | **≥ 3/5 acceptable** → `PASS_WITH_CAVEAT` |

### First-Slice Parameters（sketch only · NOT APPROVED · no runner）

| 项 | 值 |
|----|-----|
| size | **5**（DFIA001–DFIA005） |
| output root | `outputs/validation/cninfo_d_class_fund_industry_allocation_first_slice/` |
| mode flag | `--fund-industry-allocation-first-slice`（**未来** · 本任务 **不实现**） |
| approval flag | `--approve-d-class-fund-industry-allocation-first-slice`（**未来** · live only） |
| anchor rdate | default 无参 · filled `20260331` · empty control `20251231` |
| request cap | total **≤ 5** · prefer **≤ 3** shared probes |

---

## 4. Excludes

| 类别 | 项 |
|------|-----|
| Schema | **禁止** 写入 `d_company_event` / `d_company_metric_periodic` |
| Primary cases | **688671** · **301259**（无 company 绑定；政策仍保留） |
| Closed tracks | known-event · margin · disclosure · block_trade · RSU · equity_pledge · shareholder_change · executive_shareholding reopen |
| In-flight | shareholder_data / abnormal_trading **真实 live**（须 controller；本包不触碰） |
| Forbidden | DLC006R reopen · PDF/DB/MinIO/RAG · verified · production_ready · commit/push（本任务） · A/B/C |

---

## 5. Red Lines

No CNINFO · No live · No runner · No closed-track expansion · No PDF/DB/MinIO/RAG/verified · No commit · No push · No DLC006R/301259 reopen · No A/B/C file touch · No Level-2 IDLE
