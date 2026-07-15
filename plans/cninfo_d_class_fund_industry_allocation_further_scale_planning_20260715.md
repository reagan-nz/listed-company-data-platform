# CNINFO D 类 fund_industry_allocation — Further-Scale Offline Planning

_生成时间：2026-07-15 · D-FM-37_

> **性质：** FIA next-slice 收口后的 **further-scale** 离线规划 · **CNINFO = 0** · **无 live** · **无 runner** · **无 commit** · **无 push** · **不是 verified** · **不是 production_ready**
>
> **prefer taken：** FIA further-scale offline planning（高于 equity pledge / ES / shareholder_change next-slice planning）— D-FM-36 AT+SD readiness 已 commit；controller_execution_allowed=false · 禁 AT/SD live flip

**Prior state：**

| 项 | 状态 |
|----|------|
| FIA first-slice | D-FM-20 closure `PASS_WITH_CAVEAT` · lock **frozen** |
| FIA next-slice | D-FM-27 closure `PASS_WITH_CAVEAT` · unified live 5/5 · lock **frozen** |
| AT/SD next-slice | D-FM-34/35 dry-run closure + D-FM-36 readiness `PASS_OFFLINE` · live **NOT_APPROVED** |
| ESS endpoint | D-FM-22 `FAIL_REVIEW_REQUIRED` · **不**盲探 H3/H4 |
| controller_execution_allowed | **false** |

**Planning gate：**

```text
d_class_fund_industry_allocation_further_scale_planning_gate = READY_FOR_APPROVAL
standing_scope_auth = full_market_shareholder_capital
level2_phrase_required = false
first_slice_closure_gate = PASS_WITH_CAVEAT
next_slice_closure_gate = PASS_WITH_CAVEAT
first_slice_live_gate = NOT_APPROVED
next_slice_live_gate = NOT_APPROVED
ess_endpoint_probe_gate = FAIL_REVIEW_REQUIRED
ess_endpoint_status = unconfirmed_probe_failed
controller_execution_allowed = false
at_sd_live_flip = forbidden
```

**Explicit：** standing D scope 下 **不** Level-2 IDLE · **不** mutate first/next-slice FIA lock/live · **不** mutate AT/SD first/next dry-run roots · **不** H3/H4 盲探 · **不** reopen DLC006R · **不** AT/SD live flip

---

## 1. Why Further-Scale Plan Now

| 事件 | 含义 |
|------|------|
| D-FM-27 | next-slice 正式收口 · post-closure secondary 含 FIA next-scale planning |
| D-FM-26 live | 证明 coarse A/B/C + `*` · rdate `20260331`/`20251231` shared-probe 路径 5/5 |
| D-FM-36 | AT+SD dual-track readiness `PASS_OFFLINE` · live 仍 NOT_APPROVED · prefer #1 = FIA further-scale |
| CAV-FIA-NS-001 | next-slice 仅 5 案；full-market 覆盖 **不** claim；further-scale 需新命名空间 |
| AT/SD live | controller_execution_allowed=false · **禁止**本回合翻转 |

Era D 在 FIA next-slice 收口后，下一自然扩展是 **同 endpoint、已证 rdate × 粗粒度行业矩阵补全**（仍 **not locked** · **no runner** · **禁 mutate closed roots**）。

---

## 2. Ranked Options（D-FM-37）

| Rank | 选项 | 本回合 |
|------|------|--------|
| **1** | **FIA further-scale offline planning** | **primary — 执行** |
| 2 | Equity pledge / ES / shareholder_change next-slice offline planning | deferred — FIA 已证路径扩展价值更高 |
| — | AT/SD next-slice bounded live | **禁止** — controller_execution_allowed=false |
| — | ESS H3/H4 blind probe | **禁止** |
| — | FIA first/next-slice live reopen / mutate | **禁止** |
| — | Level-2 IDLE | **禁止** |
| — | DLC006R reopen | **禁止** |

---

## 3. Further-Scale Design Principles（from next-slice evidence）

| 原则 | 依据 | further-scale 应用 |
|------|------|---------------------|
| 粗粒度 F001V only | D-FM-26 sample 仅 A/B/C | **不**引入未证细码 / 未证字母作唯一 found 锚 |
| 矩阵补全 | next-slice：default=A/C；20260331=`*`/B；20251231=C | 补 **default=B** · **20260331=A** · **20251231=`*`/A/B** |
| shared probes ≤3 | VR / next-slice | 复用 default · `20260331` · `20251231`（**无新未证 rdate**） |
| 命名空间隔离 | CAV-FIA-NS-001 | **DFIA201–205** · 不覆盖 DFIA001–005 / DFIA101–105 |
| closed roots 冻结 | D-FM-20/27/34/35/36 | **不**改 first/next lock · live_report · dry-run 根 |
| schema 边界 | company_code_available=false | 仅 `d_industry_aggregate` |

---

## 4. Further-Scale Parameters（sketch only · NOT locked · no runner）

| 项 | 值 |
|----|-----|
| case_id | **DFIA201–DFIA205**（与 first/next-slice 隔离） |
| size | **5** |
| component | `fund_industry_allocation` |
| endpoint | `https://www.cninfo.com.cn/data20/fund/industry`（不变） |
| output root（未来） | `outputs/validation/cninfo_d_class_fund_industry_allocation_further_scale/` |
| mode flag（未来） | `--fund-industry-allocation-further-scale`（**本任务不实现**） |
| approval flag（未来） | `--approve-d-class-fund-industry-allocation-further-scale`（**本任务不实现**） |
| shared probes | prefer **≤3**：default · rdate=`20260331` · rdate=`20251231` |
| total CNINFO cap（未来 live） | **≤5** · prefer **≤3** |
| threshold（未来） | **≥3/5 acceptable** → `PASS_WITH_CAVEAT`（禁 bare PASS） |
| universe status | **draft sketch only** · **not locked** |

### Draft Cases

| case_id | industry_code | industry_name | query_mode | anchor_rdate | expected_behavior | scale_delta_vs_next_slice |
|---------|---------------|---------------|------------|--------------|-------------------|---------------------------|
| DFIA201 | B | 采矿业 | default | | captured_normal_or_empty_but_valid | next-slice default 缺 B |
| DFIA202 | A | 农、林、牧、渔业 | rdate | 20260331 | captured_normal | next-slice 20260331 缺 A 过滤 |
| DFIA203 | * | 全行业截面_rdate_20251231 | rdate | 20251231 | captured_normal | next-slice `*` 仅 20260331 |
| DFIA204 | A | 农、林、牧、渔业 | rdate | 20251231 | captured_normal_or_empty_but_valid | next-slice 20251231 缺 A |
| DFIA205 | B | 采矿业 | rdate | 20251231 | captured_normal_or_empty_but_valid | next-slice 20251231 缺 B |

**Explicit non-includes：** C26 / 未证细码 · 新未证 rdate（如 20250331）· company_code · H3/H4 ESS · AT/SD live · mutate DFIA101–105.

---

## 5. Excludes / Frozen

| 类别 | 项 |
|------|-----|
| FIA freeze | first-slice lock/live · next-slice lock/live · DFIA001–005 · DFIA101–105 |
| AT/SD freeze | first-slice · next-slice dry-run roots · universe locks（只读 attestation） |
| Schema | **禁止** `d_company_event` / `d_company_metric_periodic` |
| Codes | **688671** · **301259** · DLC006R |
| Closed tracks | ES detail · shareholder_change · equity_pledge · RSU · block_trade · margin · disclosure · known-event（本包不重开） |
| ESS | **不** H3/H4 盲探 · endpoint 仍 unconfirmed |
| Forbidden | PDF/DB/MinIO/RAG · verified · production_ready · bare PASS · commit/push · A/B/C · AT/SD live flip |

---

## 6. Red Lines

No CNINFO · No live · No runner · No FIA first/next mutate · No AT/SD dry-run mutate · No AT/SD live flip · No ESS H3/H4 · No DLC006R · No A/B/C · No Level-2 IDLE · No commit · No push · No verified
