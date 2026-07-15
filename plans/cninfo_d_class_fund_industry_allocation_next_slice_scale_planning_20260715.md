# CNINFO D 类 fund_industry_allocation — Next-Slice Scale Planning

_生成时间：2026-07-15 · D-FM-23_

> **性质：** FIA first-slice 收口后的 **next-slice / scale** 离线规划 · **CNINFO = 0** · **无 live** · **无 runner** · **无 commit** · **无 push** · **不是 verified** · **不是 production_ready**
>
> **prefer taken：** FIA scale / next-slice offline（高于 AT/SD scale hardening · 高于 ESS H3/H4 盲探）

**Prior state：**

| 项 | 状态 |
|----|------|
| FIA first-slice | D-FM-20 closure `PASS_WITH_CAVEAT` · counterfactual **5/5** · lock **frozen** |
| first-slice live root | D-FM-13 + D-FM-18 layered evidence · **不得 mutate** |
| ESS endpoint | D-FM-22 `FAIL_REVIEW_REQUIRED` · H1/H2=404 · **不**盲探 H3/H4 |
| AT / SD first-slice | closed live evidence · **不**本任务 re-live / scale live |

**Planning gate：**

```text
d_class_fund_industry_allocation_next_slice_scale_planning_gate = READY_FOR_APPROVAL
standing_scope_auth = full_market_shareholder_capital
level2_phrase_required = false
first_slice_closure_gate = PASS_WITH_CAVEAT
first_slice_live_gate = NOT_APPROVED
ess_endpoint_probe_gate = FAIL_REVIEW_REQUIRED
ess_endpoint_status = unconfirmed_probe_failed
```

**Explicit：** standing D scope 下 **不** Level-2 IDLE · **不** mutate first-slice lock/live · **不** H3/H4 盲探 · **不** reopen DLC006R · **不** AT/SD/ES/FIA first-slice live 重跑

---

## 1. Why Scale Plan Now

| 事件 | 含义 |
|------|------|
| D-FM-20 | first-slice 正式收口 · post-closure secondary = FIA scale offline |
| D-FM-13/18 live | 证明 `data20/fund/industry` shared-probe 路径；截面 F001V 为粗粒度 **A/B/C…** |
| C26 caveat | first-slice C26 过滤常 empty（CAV-FIA-003）· scale **不得**再以细码作唯一 found 锚 |
| D-FM-22 ESS | endpoint unconfirmed · DevTools 路径待人工 · **不**烧 CNINFO 猜 H3/H4 |
| AT/SD | first-slice 已有证据 · 本回合 scale hardening 价值低于 FIA next-slice 规划 |

Era D 在 FIA first-slice 收口后，下一自然资本扩展是 **同 endpoint、粗粒度行业 + 已证 rdate 的 next-slice sketch**（仍 **not locked** · **no runner**）。

---

## 2. Ranked Options（D-FM-23）

| Rank | 选项 | 本回合 |
|------|------|--------|
| **1** | **FIA next-slice / scale offline planning** | **primary — 执行** |
| 2 | AT/SD scale hardening offline | deferred — first-slice 已收口；无新证据缺口 |
| 3 | ESS DevTools pause package | hold note only — D-FM-22 已证伪 H1/H2；人工 DevTools 未到 |
| — | ESS H3/H4 blind probe | **禁止** |
| — | FIA/AT/SD/ES first-slice live reopen | **禁止** |
| — | Level-2 IDLE | **禁止** |

---

## 3. Scale Design Principles（from first-slice evidence）

| 原则 | 依据 | next-slice 应用 |
|------|------|-----------------|
| 粗粒度 F001V | D-FM-13 DFIA002/003 sample：`A`/`B`/`C` | DFIA101–104 用 A/B/C，**不用** C26 作唯一 found 锚 |
| 混合期望 | D-FM-17/19 | 行业过滤案默认 `captured_normal_or_empty_but_valid` |
| shared probes ≤3 | VR-006 / first-slice | 复用 default · `20260331` · `20251231` |
| 截面案保留 | DFIA002/003 found | 保留 `*` cross-section 非空评估 |
| 空控过期 | D-FM-18：`20251231` found=19 | 不再标 empty_control；改为 mixed found/empty |
| schema 边界 | company_code_available=false | 仅 `d_industry_aggregate` |
| first-slice 冻结 | D-FM-20 | **不**改 lock · **不**改 live_report · **不**改 VR-001 五案 |

---

## 4. Next-Slice Parameters（sketch only · NOT locked · no runner）

| 项 | 值 |
|----|-----|
| case_id | **DFIA101–DFIA105**（与 first-slice DFIA001–005 隔离） |
| size | **5** |
| component | `fund_industry_allocation` |
| endpoint | `https://www.cninfo.com.cn/data20/fund/industry`（不变） |
| output root（未来） | `outputs/validation/cninfo_d_class_fund_industry_allocation_next_slice/` |
| mode flag（未来） | `--fund-industry-allocation-next-slice`（**本任务不实现**） |
| approval flag（未来） | `--approve-d-class-fund-industry-allocation-next-slice`（**本任务不实现**） |
| shared probes | prefer **≤3**：default · rdate=`20260331` · rdate=`20251231` |
| total CNINFO cap（未来 live） | **≤5** · prefer **≤3** |
| threshold（未来） | **≥3/5 acceptable** → `PASS_WITH_CAVEAT`（禁 bare PASS） |
| universe status | **draft sketch only** · **not locked** |

### Draft Cases

| case_id | industry_code | industry_name | query_mode | anchor_rdate | expected_behavior | evidence cite |
|---------|---------------|---------------|------------|--------------|-------------------|---------------|
| DFIA101 | A | 农、林、牧、渔业 | default | | captured_normal_or_empty_but_valid | D-FM-13 DFIA002 sample F001V=A |
| DFIA102 | C | 制造业 | default | | captured_normal_or_empty_but_valid | D-FM-13 DFIA002 sample F001V=C |
| DFIA103 | * | 全行业截面_rdate_20260331 | rdate | 20260331 | captured_normal | D-FM-13 DFIA003 found=19 |
| DFIA104 | B | 采矿业 | rdate | 20260331 | captured_normal | D-FM-13 DFIA003 sample F001V=B |
| DFIA105 | C | 制造业 | rdate | 20251231 | captured_normal_or_empty_but_valid | D-FM-18 found=19 · sample F001V=C |

**Explicit non-includes：** C26（first-slice caveat）· 新未证 rdate（如 20250331）· company_code · H3/H4 ESS。

---

## 5. Excludes / Frozen

| 类别 | 项 |
|------|-----|
| First-slice freeze | universe lock · live_report · live_snapshots · DFIA001–005 · VR-001 五案 |
| Schema | **禁止** `d_company_event` / `d_company_metric_periodic` |
| Codes | **688671** · **301259** · DLC006R |
| Closed tracks | ES detail · shareholder_change · equity_pledge · RSU · block_trade · margin · disclosure · known-event |
| Sibling live | AT / SD / FIA first-slice **不** re-live |
| ESS | **不** H3/H4 盲探 · endpoint 仍 unconfirmed |
| Forbidden | PDF/DB/MinIO/RAG · verified · production_ready · bare PASS · commit/push · A/B/C |

---

## 6. Red Lines

No CNINFO · No live · No runner · No first-slice mutate · No ESS H3/H4 · No DLC006R · No A/B/C · No Level-2 IDLE · No commit · No push · No verified
