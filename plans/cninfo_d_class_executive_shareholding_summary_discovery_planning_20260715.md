# CNINFO D 类 executive_shareholding_summary — Offline Discovery Planning

_生成时间：2026-07-15 · D-FM-21_

> **性质：** next capital component offline discovery · **CNINFO calls = 0** · **无 live** · **无 runner** · **无 commit** · **无 push** · **不是 verified** · **不是 production_ready**

**Prior state：** `fund_industry_allocation` first-slice offline closure **PASS_WITH_CAVEAT**（D-FM-20 · counterfactual 5/5 · commit `4566f40`）· `controller_execution_allowed=false` · standing D scope = full-market shareholder / capital

**Discovery planning gate：**

```text
d_class_executive_shareholding_summary_discovery_planning_gate = READY_FOR_APPROVAL
standing_scope_auth = full_market_shareholder_capital
level2_phrase_required = false
endpoint_status = unconfirmed
registry_status = not_registered
fia_first_slice_closure_gate = PASS_WITH_CAVEAT
```

**Explicit：** standing D scope 下 **不** IDLE 等待 Level-2 短语 · **不** 实现 runner/live · **不** 重开 DLC006R / 301259 · **不** 重开 closed FIA first-slice live roots · **不** 重开 executive_shareholding first-slice · **不** AT/SD re-live / scale live

---

## 1. Why Discover Now

| 事件 | 状态 |
|------|------|
| fund_industry_allocation | first-slice closure **PASS_WITH_CAVEAT**（D-FM-20）· 正式收口完成 |
| shareholder_data / abnormal_trading | first-slice live 已完成 · **不**本任务 scale hardening live |
| executive_shareholding（明细） | first-slice **closed** · endpoint `leader/detail` · **不**重开 |
| executive_shareholding_summary | **未注册** · 仅有 UI tab 线索 · Phase2 **未**抓到独立 Network endpoint |
| FIA scale / next-slice | 可选但低于未注册 capital discovery 优先级（本回合） |

Era D 在 FIA first-slice 离线收口后，下一自然资本侧动作是 **未注册组件 discovery**：页面「高管持股变动汇总」tab，候选 `source_id=executive_shareholding_summary`。本任务只做离线 discovery planning，**不**做 endpoint live probe。

---

## 2. Ranked Options（post FIA D-FM-20 closure）

| Rank | Component / Action | Status | Rationale |
|------|--------------------|--------|-----------|
| **1** | **`executive_shareholding_summary` discovery** | **primary** | 唯一明确 deferred 的未注册 capital 组件 · UI tab 已文档化 · 与 closed ES detail 正交 |
| 2 | FIA scale / next-slice offline | deferred | first-slice 已 closure；scale 另批 · 本回合低于 discovery |
| — | AT / SD scale hardening | excluded | first-slice 已 live；禁无界 re-live · 非本 discovery 包 |
| — | closed tracks | excluded | ES detail / SC / EP / RSU / BT / MT / DS / known-event / DLC006R **不重开** |
| — | FIA first-slice live roots | frozen | D-FM-13 / D-FM-18 产物 **不 mutate** |

**Recommend ONE primary：** **`executive_shareholding_summary` offline discovery**

---

## 3. Primary: `executive_shareholding_summary`

| 项 | 评估 |
|----|------|
| UI page | `https://www.cninfo.com.cn/new/commonUrl?url=data/person-stock-data-tables` · tab **高管持股变动汇总** |
| sibling source | `executive_shareholding` · `POST .../data20/leader/detail` · **closed first-slice** · 不得混用 |
| endpoint status | **unconfirmed** · Phase2 仅 UI 表头 · **无** Network capture |
| endpoint hypotheses | 见 §3.1 · **均未验证** |
| company_code | **likely yes**（UI「证券代码」） |
| schema hypothesis | company-level **summary / aggregate event or metric** · **不是** per-executive detail · **不是** `d_industry_aggregate` |
| mapper | **未实现** · 本任务不写 |
| sample_raw | **无** · 须 endpoint 确认后另批 |
| prior evidence | field semantics priority2 §5.2 UI 表头 · registry ES notes「Summary tab not this source」 |
| risk | **medium** · endpoint 未确认 · 字段 raw 名未知 · 可能与 detail 同参或不同参 |
| request model（未来 probe） | prefer **≤ 2** CNINFO 有界探针 · total cap **≤ 3** · **本任务 = 0** |

### 3.1 Endpoint Hypotheses（offline only · NOT probed）

| Rank | Candidate URL | Confidence | Rationale |
|------|---------------|------------|-----------|
| H1 | `https://www.cninfo.com.cn/data20/leader/summary` | **low–medium** | 与 `leader/detail` 命名对称；最自然拆分 |
| H2 | `https://www.cninfo.com.cn/data20/leader/statistics` | low | 汇总语义常见命名 |
| H3 | `https://www.cninfo.com.cn/data20/leader/total` | low | 合计语义猜测 |
| H4 | 同 `leader/detail` 另参 | low | 若 tab 仅前端聚合则无独立 API；须 DevTools 证伪 |

**本任务不调用以上任一 URL。**

### 3.2 UI Field Sketch（from prior offline docs · not raw-confirmed）

| ui_label | standard_candidate | company_code | notes |
|----------|--------------------|:------------:|-------|
| 变动统计区间 | `change_stat_period` | n/a | 可能对应 timeMark / 起止区间 |
| 证券代码 | `company_code` | yes | 支持 company-level |
| 证券简称 | `company_name` | yes | |
| 变动类型 | `change_type` | n/a | 可能对应 varyType 语义 |
| 高管持股变动数量合计(万股) | `executive_share_change_total_wan` | n/a | 合计字段 · 非明细 F006N |

**raw field 名（SECCODE / F00xN 等）未知** — 须 endpoint probe 后对照。

### 3.3 First-Slice Parameters（sketch only · NOT APPROVED · no runner）

| 项 | 值 |
|----|-----|
| size | **5**（DESS001–DESS005 · **sketch only**） |
| output root（未来） | `outputs/validation/cninfo_d_class_executive_shareholding_summary_first_slice/` |
| mode flag | `--executive-shareholding-summary-first-slice`（**未来** · 本任务 **不实现**） |
| approval flag | `--approve-d-class-executive-shareholding-summary-first-slice`（**未来**） |
| prerequisite | bounded endpoint probe **PASS** + registry draft + sample_raw |
| request cap（未来 first-slice） | total **≤ 5** · prefer shared probes |
| threshold（未来） | **≥ 3/5 acceptable** → `PASS_WITH_CAVEAT` |

**NOT APPROVED** · **无 runner** · **无 live** · **NOT verified** · **NOT production_ready**

---

## 4. Excludes

| 类别 | 项 |
|------|-----|
| Primary cases | **688671** · **301259**（政策保留） |
| Closed tracks | known-event · margin · disclosure · block_trade · RSU · equity_pledge · shareholder_change · **executive_shareholding reopen** |
| Frozen live roots | FIA D-FM-13 / D-FM-18 live 产物 · ES / AT / SD first-slice live 根 |
| Forbidden | DLC006R reopen · PDF/DB/MinIO/RAG · verified · production_ready · commit/push（本任务） · A/B/C · Level-2 IDLE |

---

## 5. Red Lines

No CNINFO · No live · No runner · No registry freeze as verified · No closed-track expansion · No FIA live-root mutate · No PDF/DB/MinIO/RAG/verified · No commit · No push · No DLC006R/301259 reopen · No A/B/C file touch · No Level-2 IDLE
