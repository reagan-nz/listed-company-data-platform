# CNINFO D 类 AT/SD — Next-Slice Scale Hardening Planning

_生成时间：2026-07-15 · D-FM-28_

> **性质：** abnormal_trading / shareholder_data **next-slice / scale** 离线规划 · **CNINFO = 0** · **无 live** · **无 runner** · **无 commit** · **无 push** · **不是 verified** · **不是 production_ready**
>
> **prefer taken：** AT/SD scale hardening offline（高于 FIA further-scale · 高于 next capital ESS · 高于 ESS H3/H4）— D-FM-27 FIA next-slice closure 已 commit

**Prior state：**

| 项 | 状态 |
|----|------|
| FIA next-slice | D-FM-27 closure `PASS_WITH_CAVEAT` · unified 5/5 · **committed** · **不得 mutate** |
| FIA first-slice | frozen · **不得 mutate** |
| AT first-slice | D-FM-15 live **4/5** · `PASS_WITH_CAVEAT` · lock **frozen** · found-path **未** live 证明 |
| SD first-slice | D-FM-14 live **5/5** · `PASS_WITH_CAVEAT` · lock **frozen** · **单 rdate** |
| ESS | DevTools pause · **不** H3/H4 |
| DLC006R / 301259 / 688671 | **未重开** |

**Planning gate：**

```text
d_class_at_sd_next_slice_scale_planning_gate = READY_FOR_APPROVAL
d_class_abnormal_trading_next_slice_scale_planning_gate = READY_FOR_APPROVAL
d_class_shareholder_data_next_slice_scale_planning_gate = READY_FOR_APPROVAL
standing_scope_auth = full_market_shareholder_capital
level2_phrase_required = false
fia_next_slice_closure_gate = PASS_WITH_CAVEAT
at_first_slice_execution_gate = PASS_WITH_CAVEAT
sd_first_slice_execution_gate = PASS_WITH_CAVEAT
at_sd_first_slice_live_gate = NOT_APPROVED
```

**Explicit：** standing D scope 下 **不** Level-2 IDLE · **不** mutate AT/SD/FIA first-slice 或 FIA next-slice live roots · **不** H3/H4 · **不** reopen DLC006R · **不** AT/SD/FIA re-live

---

## 1. Why Scale Plan Now

| 事件 | 含义 |
|------|------|
| D-FM-27 | FIA next-slice 正式收口并 commit · post-closure secondary = AT/SD scale offline |
| D-FM-15 AT live | 稀疏日 `2026-07-03` 全案 company-level empty · DAT001 `expectation_mismatch` · **found-path 从未 live 证明** |
| D-FM-14 SD live | shared rdate=`20260331` 5/5 · VR-008 禁 multi-rdate · 自然扩展为 **第二报告期** |
| Tier-1 fixtures | AT found / multi_type 离线已有；live 未触及 |

Era D 在 FIA next-slice 收口后，下一自然资本扩展是 **AT found-path / denser-day sketch** + **SD multi-rdate sketch**（仍 **not locked** · **no runner**）。

---

## 2. Ranked Options（D-FM-28）

| Rank | 选项 | 本回合 |
|------|------|--------|
| **1** | **AT/SD next-slice scale hardening offline** | **primary — 执行** |
| 2 | FIA further-scale planning offline | deferred — next-slice 刚 closure；禁无界 live |
| 3 | next capital / ESS DevTools | paused_pending_devtools · **不**盲探 |
| — | ESS H3/H4 blind probe | **禁止** |
| — | AT/SD/FIA first-slice 或 FIA next-slice re-live | **禁止** |
| — | Level-2 IDLE | **禁止** |

**Within-package prefer：** AT 优先（found-path 缺口）· SD 次之（multi-rdate）。

---

## 3. AT Scale Design Principles（from D-FM-15）

| 原则 | 依据 | next-slice 应用 |
|------|------|-----------------|
| 弃用稀疏日作唯一 found 锚 | D-FM-15：`2026-07-03` 5× empty | **禁止**把 `2026-07-03` 锁为 found 唯一锚 |
| denser-day cite 门禁 | 尚无 live-proven non-empty company hit | sketch `anchor_tdate=PENDING_DENSE_DAY_CITE` · **lock 前**须另批 cite |
| 混合期望 | DAT001 sole needs_review 失败 | 默认 `captured_normal_or_empty_but_valid` · **禁** sole needs_review |
| shared day probe | first-slice 5× CNINFO | prefer **1** shared tdate（未来 runner）· total cap ≤5 |
| found 结构 | Tier-1 DAT002–004 found / multi_type | 离线结构可复用；**不** claim live found |
| detail[] | VR-022/024 deferred | **仍 deferred** · 非本 sketch |
| first-slice 冻结 | D-FM-15 | **不**改 lock · **不**改 live_report · **不**刷 DAT001 |

### AT Draft Cases（DAT101–DAT105 · NOT locked）

| case_id | company_code | company_name | market | anchor_tdate | expected_behavior | evidence cite |
|---------|--------------|--------------|--------|--------------|-------------------|---------------|
| DAT101 | 000895 | 双汇发展 | szse_main | PENDING_DENSE_DAY_CITE | captured_normal_or_empty_but_valid | D-FM-15 empty on sparse day · Tier-1 DAT002_found |
| DAT102 | 600000 | 浦发银行 | sse_main | PENDING_DENSE_DAY_CITE | captured_normal_or_empty_but_valid | board diversity · Tier-1 DAT003_found |
| DAT103 | 002415 | 海康威视 | szse_main | PENDING_DENSE_DAY_CITE | captured_normal_or_empty_but_valid | Tier-1 DAT004_multi_type_found |
| DAT104 | 000001 | 平安银行 | szse_main | PENDING_DENSE_DAY_CITE | captured_normal_or_empty_but_valid | code diversify vs AT first-slice |
| DAT105 | 601988 | 中国银行 | sse_main | PENDING_DENSE_DAY_CITE | empty_but_valid | empty control retained |

**Explicit non-includes：** mutate DAT001–005 · re-live first-slice · `detail[]` ETL · 688671/301259 · sole `captured_normal_or_needs_review` on unproven day。

---

## 4. SD Scale Design Principles（from D-FM-14）

| 原则 | 依据 | next-slice 应用 |
|------|------|-----------------|
| 保留已证 rdate | D-FM-14 `20260331` shared=1 · 5/5 | DSD101–103 复用 |
| 第二 rdate 扩展 | VR-008 仅限 first-slice | DSD104–105 用 `20251231` · **mixed**（SD 端点未 live 证） |
| shared probes ≤2 | SD shared 模式已证 | prefer **2**：`20260331` · `20251231` |
| 空控保留 | DSD005 | DSD105 empty_but_valid |
| 代码适度分散 | 与 AT 重叠蓝筹 | 引入 600519（sketch only） |
| first-slice 冻结 | D-FM-14 | **不**改 lock · **不** re-live |

### SD Draft Cases（DSD101–DSD105 · NOT locked）

| case_id | company_code | company_name | market | anchor_rdate | expected_behavior | evidence cite |
|---------|--------------|--------------|--------|--------------|-------------------|---------------|
| DSD101 | 000001 | 平安银行 | szse_main | 20260331 | captured_normal | D-FM-14 DSD001 found=1 |
| DSD102 | 000895 | 双汇发展 | szse_main | 20260331 | captured_normal_or_empty_but_valid | D-FM-14 DSD002 found=1 |
| DSD103 | 600519 | 贵州茅台 | sse_main | 20260331 | captured_normal_or_empty_but_valid | diversify · shared rdate |
| DSD104 | 002415 | 海康威视 | szse_main | 20251231 | captured_normal_or_empty_but_valid | multi-rdate scale · unproven_rdate_mixed |
| DSD105 | 000004 | 国华退 | szse_main | 20251231 | empty_but_valid | empty control on second rdate |

**Explicit non-includes：** mutate DSD001–005 · first-slice multi-rdate 改 VR · 无界 re-live。

---

## 5. Shared Parameters（sketch only · NOT locked · no runner）

| 项 | AT | SD |
|----|----|----|
| case namespace | **DAT101–DAT105** | **DSD101–DSD105** |
| endpoint | `getMarketStatisticsData`（不变） | `data20/shareholeder/data`（不变） |
| output root（未来） | `.../cninfo_d_class_abnormal_trading_next_slice/` | `.../cninfo_d_class_shareholder_data_next_slice/` |
| mode flag（未来） | `--abnormal-trading-next-slice`（**不实现**） | `--shareholder-data-next-slice`（**不实现**） |
| shared probes | prefer **1** denser tdate | prefer **2** rdates |
| total CNINFO cap（未来 live） | **≤5** · prefer **1** | **≤5** · prefer **2** |
| threshold（未来） | ≥3/5 → `PASS_WITH_CAVEAT` | ≥3/5 → `PASS_WITH_CAVEAT` |
| universe status | **draft_not_locked** | **draft_not_locked** |

---

## 6. Excludes / Frozen

| 类别 | 项 |
|------|-----|
| AT first-slice freeze | universe lock · live_report · live_snapshots · DAT001–005 |
| SD first-slice freeze | universe lock · live_report · live_snapshots · DSD001–005 |
| FIA freeze | first-slice + next-slice live roots / locks（D-FM-27） |
| Codes | **688671** · **301259** · DLC006R |
| ESS | **不** H3/H4 |
| Forbidden | PDF/DB/MinIO/RAG · verified · production_ready · bare PASS · commit/push · A/B/C · Level-2 IDLE |

---

## 7. Red Lines

No CNINFO · No live · No runner · No first-slice mutate · No FIA next-slice mutate · No ESS H3/H4 · No DLC006R · No A/B/C · No Level-2 IDLE · No commit · No push · No verified
