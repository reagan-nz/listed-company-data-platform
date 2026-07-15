# CNINFO D 类 equity_pledge — Next-Slice Offline Planning

_生成时间：2026-07-15 · D-FM-41_

> **性质：** 股权质押 next-slice **离线规划** · **CNINFO = 0** · **无 live** · **无 runner** · **无 commit** · **无 push** · **不是 verified** · **不是 production_ready**
>
> **prefer taken：** equity_pledge next-slice offline planning（高于 ES / shareholder_change next-slice · 高于 FIA further-scale live · 高于 ESS H3/H4）— D-FM-40 FIA further-scale dry-run offline closure `PASS_OFFLINE` 已收口 · live 仍 `NOT_APPROVED`

**Prior state：**

| 项 | 状态 |
|----|------|
| FIA further-scale S4 dry-run | D-FM-40 closure `PASS_OFFLINE` · planned_ok **5/5** · freeze ledger · **不得 mutate** · live `NOT_APPROVED` |
| FIA first / next-slice | frozen · **不得 mutate** |
| AT / SD first / next-slice dry-run | frozen · **不得 mutate** · live `NOT_APPROVED` |
| equity_pledge first-slice | closed · live **4/5** · `PASS_WITH_CAVEAT` · DEP004 caveat · sparse `2026-07-03` 全空 · **found-path 未 live 证明** |
| executive_shareholding first-slice | closed · **无** next-slice 规划包 |
| shareholder_change first-slice | closed · **无** next-slice 规划包 · **不** reopen DLC006R |
| ESS | DevTools pause · **不** H3/H4 |
| DLC006R / 301259 / 688671 | **未重开** |

**Planning gate：**

```text
d_class_equity_pledge_next_slice_planning_gate = READY_FOR_APPROVAL
d_class_equity_pledge_es_shareholder_change_readiness_rank_gate = PASS_OFFLINE
standing_scope_auth = shareholder_capital_fia_at_sd
level2_phrase_required = false
fia_further_scale_s4_dryrun_closure_gate = PASS_OFFLINE
fia_further_scale_live_gate = NOT_APPROVED
equity_pledge_first_slice_closure_gate = PASS_WITH_CAVEAT
equity_pledge_next_slice_live_gate = NOT_APPROVED
equity_pledge_next_slice_runner_gate = NOT_APPROVED
```

**Explicit：** standing D scope 下 **不** Level-2 IDLE · **不** mutate FIA/AT/SD frozen roots · **不** H3/H4 · **不** reopen DLC006R · **不** equity_pledge first-slice re-live · **不** flip live gates

---

## 1. Why Plan Equity Pledge Next-Slice Now

| 事件 | 含义 |
|------|------|
| D-FM-40 | FIA further-scale dry-run offline closure · secondary = equity pledge / ES / shareholder_change next-slice planning |
| equity_pledge first-slice | sparse `2026-07-03` 5× `empty_but_valid` · DEP004 expectation mismatch · closure 明确 **deferred denser-day probe** |
| priority-2 offline cite | `tdate=2026-07-02` **68** 行 · `2026-07-01` **82** 行 · 结构稳定（**非** company-level live found） |
| Tier-0 sample | `fixtures/d_class/equity_pledge/sample_raw.json` · `tdate=2026-07-02` · SECCODE=`000001` 结构 cite |
| ES / shareholder_change | first-slice 已 closure · **尚无** next-slice planning 包 · 就绪度低于 equity_pledge |

**本任务：** 选定 primary · 写 next-slice 规划包 · **不** lock universe · **不** 实现 runner · **不** live。

---

## 2. Ranked Options（D-FM-41 readiness）

| Rank | 选项 | 就绪依据 | 本回合 |
|------|------|----------|--------|
| **1** | **`equity_pledge` next-slice offline planning** | first-slice closed+live · denser-day offline cite · sample_raw · deferred probe 文档齐全 | **primary — 执行** |
| 2 | `executive_shareholding` next-slice offline planning | first-slice closed · **无** denser-window cite 包 · ESS summary 仍 pause | deferred |
| 3 | `shareholder_change` next-slice offline planning | first-slice closed · DLC006R 文档负担 · **无** next-slice sketch | deferred |
| — | FIA further-scale / AT / SD bounded live | live_gate=`NOT_APPROVED` · `controller_execution_allowed=false` | **禁止本回合** |
| — | ESS H3/H4 blind probe | pause · FAIL_REVIEW_REQUIRED | **禁止** |
| — | reopen DLC006R / mutate frozen FIA·AT·SD roots | red line | **禁止** |

**Recommend ONE primary：** **`equity_pledge` next-slice**

---

## 3. Design Principles（from first-slice + sparse-day lessons）

| 原则 | 依据 | next-slice 应用 |
|------|------|-----------------|
| 弃用稀疏日作唯一 found 锚 | first-slice `2026-07-03` 5× empty | **禁止**把 `2026-07-03` 锁为 found 唯一锚 |
| denser-day offline cite | priority-2 `2026-07-02`=68 · sample_raw | sketch `anchor_tdate=2026-07-02` · **仍 draft_not_locked** |
| 混合期望 | DEP004 sole needs_review 失败 | 默认 `captured_normal_or_empty_but_valid` · **禁** sole needs_review |
| shared day probe | first-slice 5× per-case CNINFO | prefer **1** shared tdate · total cap ≤5 |
| found 结构 | sample_raw + priority-2 字段 10 列 | 离线结构可复用；**不** claim company-level live found |
| first-slice 冻结 | DEP001–005 live/dry-run | **不**改 universe_draft · **不**改 live_report · **不**刷 DEP004 |
| 永久排除 | DLC003R/DLC006R | **688671** · **301259** |

### Draft Cases（DEP101–DEP105 · NOT locked）

| case_id | company_code | company_name | market | anchor_tdate | expected_behavior | evidence cite |
|---------|--------------|--------------|--------|--------------|-------------------|---------------|
| DEP101 | 000001 | 平安银行 | szse_main | 2026-07-02 | captured_normal_or_empty_but_valid | sample_raw SECCODE=000001 · priority2 denser day |
| DEP102 | 000895 | 双汇发展 | szse_main | 2026-07-02 | captured_normal_or_empty_but_valid | first-slice DEP002 sparse empty · board diversify |
| DEP103 | 600000 | 浦发银行 | sse_main | 2026-07-02 | captured_normal_or_empty_but_valid | SSE 金融 diversify |
| DEP104 | 002415 | 海康威视 | szse_main | 2026-07-02 | captured_normal_or_empty_but_valid | DEP004 retarget · **禁** sole needs_review |
| DEP105 | 601988 | 中国银行 | sse_main | 2026-07-02 | empty_but_valid | empty control retained |

**Explicit non-includes：** mutate DEP001–005 · re-live first-slice · sole `captured_normal_or_needs_review` · 688671/301259 · FIA/AT/SD root mutate · live / runner 本回合。

---

## 4. Shared Parameters（sketch only · NOT locked · no runner）

| 项 | 提案 |
|----|------|
| size | **5**（DEP101–DEP105） |
| output root（未来） | `outputs/validation/cninfo_d_class_equity_pledge_next_slice/` |
| mode flag（未来） | `--equity-pledge-next-slice` |
| approval flag（未来） | `--approve-d-class-equity-pledge-next-slice` |
| endpoint | `https://www.cninfo.com.cn/data20/equityPledge/list` |
| query mode | **`tdate_daily`** |
| proposed anchor `tdate` | **2026-07-02**（offline denser cite · **非** CNINFO 新探测） |
| forbidden sole found anchor | **2026-07-03** |
| request model | prefer **1** shared probe · total cap **≤ 5** · per-case ≤ 1 |
| success criteria (future live) | **≥ 3/5** acceptable → `PASS_WITH_CAVEAT` |
| universe lock | **not locked**（本包仅 sketch） |

**NOT APPROVED** · **无 runner** · **无 live** · company-level live found-path for DEP101–105 = **NOT_PROVEN**

---

## 5. Closed / Frozen Tracks（保持 unchanged）

| Track | 政策 |
|-------|------|
| FIA further-scale dry-run root + freeze ledger | **frozen_read_only** |
| FIA first / next-slice locks | **frozen** |
| AT / SD first / next-slice locks + dry-run roots | **frozen** |
| equity_pledge first-slice DEP001–005 | **frozen** · 不 re-live |
| executive_shareholding / shareholder_change first-slice | **不**本回合扩展 |
| RSU / block_trade / margin / disclosure / known-event | **closed** · 不重开 |
| ESS H3/H4 · DLC006R | **禁止** |

---

## 6. Artifacts

| 项 | 路径 |
|----|------|
| planning plan | 本文件 |
| candidate matrix | `outputs/validation/cninfo_d_class_equity_pledge_es_shareholder_change_next_slice_candidate_matrix_20260715.csv` |
| universe sketch | `outputs/validation/cninfo_d_class_equity_pledge_next_slice_universe_draft_sketch_20260715.csv` |
| validation rules | `outputs/validation/cninfo_d_class_equity_pledge_next_slice_validation_rules_20260715.md` |
| offline prep checklist | `outputs/validation/cninfo_d_class_equity_pledge_next_slice_offline_prep_checklist_20260715.csv` |
| recommendation | `outputs/validation/cninfo_d_class_equity_pledge_next_slice_recommendation_20260715.md` |
| planning summary | `outputs/validation/cninfo_d_class_equity_pledge_next_slice_planning_summary_20260715.md` |
| next step | `outputs/validation/cninfo_d_class_equity_pledge_next_slice_next_step_recommendation_20260715.md` |
| caveat ledger | `outputs/validation/cninfo_d_class_equity_pledge_next_slice_final_caveat_ledger.csv` |
| task wall | `outputs/validation/cninfo_d_class_equity_pledge_dfm41_next_slice_planning_20260715.md` |
| offline test | `lab/test_cninfo_d_class_equity_pledge_next_slice_planning_offline.py` |

---

## 7. Red Lines

No CNINFO · No live · No runner · No live-gate flip · No closed-track reopen · No FIA/AT/SD/EP first-slice mutate · No PDF/DB/MinIO/RAG/verified · No commit · No push · No ESS H3/H4 · No DLC006R
