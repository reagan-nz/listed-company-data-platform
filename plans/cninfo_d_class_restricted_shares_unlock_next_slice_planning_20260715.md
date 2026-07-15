# CNINFO D 类 restricted_shares_unlock（ES / 限售解禁）— Next-Slice Offline Planning

_生成时间：2026-07-15 · D-FM-45_

> **性质：** 限售解禁 next-slice **离线规划** · **CNINFO = 0** · **无 live** · **无 runner** · **无 commit** · **无 push** · **不是 verified** · **不是 production_ready**
>
> **prefer taken：** ES / `restricted_shares_unlock` next-slice offline planning（高于 shareholder_change · 高于 executive_shareholding · 高于任意 live）— D-FM-44 EP next-slice dry-run offline closure `PASS_OFFLINE` 已收口 · live 仍 `NOT_APPROVED`
>
> **命名：** ES = **限售解禁 / equity structure** = component `restricted_shares_unlock`（**不是** `executive_shareholding`）

**Prior state：**

| 项 | 状态 |
|----|------|
| EP next-slice S4 dry-run | D-FM-44 closure `PASS_OFFLINE` · planned_ok **5/5** · freeze ledger · **不得 mutate** · live `NOT_APPROVED` |
| EP / FIA / AT / SD first/next/further | frozen · **不得 mutate** |
| restricted_shares_unlock first-slice | closed · live **5/5** · `PASS_WITH_CAVEAT` · 公司级全空 on `2026-06-08` · **found-path 未 live 证明** |
| shareholder_change first-slice | closed · **4/5** · DSC004 caveat · DLC006R 文档负担 · **无** denser type=inc cite 包 |
| executive_shareholding first-slice | closed · **无** denser-window cite · ESS pause |
| ESS | DevTools pause · **不** H3/H4 |
| DLC006R / 301259 / 688671 | **未重开** |

**Planning gate：**

```text
d_class_restricted_shares_unlock_next_slice_planning_gate = READY_FOR_APPROVAL
d_class_es_shareholder_change_next_slice_readiness_rank_gate = PASS_OFFLINE
standing_scope_auth = shareholder_capital_fia_at_sd
level2_phrase_required = false
ep_next_slice_s4_dryrun_closure_gate = PASS_OFFLINE
ep_next_slice_live_gate = NOT_APPROVED
restricted_shares_unlock_first_slice_closure_gate = PASS_WITH_CAVEAT
restricted_shares_unlock_next_slice_live_gate = NOT_APPROVED
restricted_shares_unlock_next_slice_runner_gate = NOT_APPROVED
```

**Explicit：** standing D scope 下 **不** Level-2 IDLE · **不** mutate EP/FIA/AT/SD frozen roots · **不** H3/H4 · **不** reopen DLC006R · **不** RSU first-slice re-live · **不** flip live gates

---

## 1. Why Plan ES / Restricted Shares Unlock Next-Slice Now

| 事件 | 含义 |
|------|------|
| D-FM-44 | EP next-slice dry-run offline closure · secondary = ES / shareholder_change next-slice planning |
| RSU first-slice | sparse `2026-06-08` 5× company-level `empty_but_valid` · closure 明确 **deferred denser-day probe** |
| multidate offline cite | `tdate=2026-07-03` **9** 行 · `2026-07-06` **7** 行 · 结构稳定（**非** company-level live found） |
| Tier-0 sample | `fixtures/d_class/restricted_shares_unlock/sample_raw.json` · 字段结构 cite · SECCODE=`300992` · tdate=`2026-06-08`（结构 ≠ denser found） |
| shareholder_change | first-slice 已 closure · denser type=inc cite 弱 · DLC006R 负担 · 就绪度低于 ES/RSU |

**本任务：** 选定 primary · 写 next-slice 规划包 · **不** lock universe · **不** 实现 runner · **不** live。

---

## 2. Ranked Options（D-FM-45 readiness）

| Rank | 选项 | 就绪依据 | 本回合 |
|------|------|----------|--------|
| **1** | **`restricted_shares_unlock`（ES）next-slice offline planning** | first-slice closed+live 5/5 · denser-day offline cite · sample_raw 结构 · 无 DLC006R 负担 | **primary — 执行** |
| 2 | `shareholder_change` next-slice offline planning | first-slice closed 4/5 · DSC004 · DLC006R 负担 · type=inc denser cite 弱 | deferred |
| 3 | `executive_shareholding` next-slice offline planning | first-slice closed · 无 denser-window cite · ESS pause | deferred |
| — | EP / FIA / AT / SD bounded live | live NOT_APPROVED · controller_execution_allowed=false | **forbidden** |
| — | ESS H3/H4 · DLC006R · Level-2 IDLE | red lines | **forbidden** |

---

## 3. Universe Sketch（DRU101–DRU105 · draft_not_locked）

| case_id | code | market | expected_behavior | notes |
|---------|------|--------|-------------------|-------|
| DRU101 | 300992 | chinext | captured_normal_or_empty_but_valid | sample_raw 结构 cite |
| DRU102 | 000895 | szse_main | captured_normal_or_empty_but_valid | 蓝筹 |
| DRU103 | 600000 | sse_main | captured_normal_or_empty_but_valid | SSE 多样性 |
| DRU104 | 002415 | szse_main | captured_normal_or_empty_but_valid | **禁** sole needs_review |
| DRU105 | 601988 | sse_main | empty_but_valid | empty control |

- shared anchor：`2026-07-03` · `shared_probe_prefer=1` · total cap=`5`
- 禁止 sole found 锚：`2026-06-08`
- 永久排除：`688671` · `301259`
- endpoint：`liftBan/detail`

CSV：`outputs/validation/cninfo_d_class_restricted_shares_unlock_next_slice_universe_draft_sketch_20260715.csv`

---

## 4. Deliverables

1. Candidate matrix（ES vs shareholder_change readiness）
2. Universe sketch DRU101–105
3. VR-RSU-NS-001–042
4. Offline prep checklist
5. Recommendation + next-step + caveat ledger
6. Offline smoke test（frozen-root sha256 · CNINFO=0）

**不交付：** universe lock · Tier-1 fixtures · runner · dry-run · live · commit/push

---

## 5. Gates（本包）

```text
d_class_restricted_shares_unlock_next_slice_planning_gate = READY_FOR_APPROVAL
d_class_es_shareholder_change_next_slice_readiness_rank_gate = PASS_OFFLINE
d_class_restricted_shares_unlock_next_slice_live_gate = NOT_APPROVED
d_class_restricted_shares_unlock_next_slice_runner_gate = NOT_APPROVED
d_class_restricted_shares_unlock_next_slice_execution_gate = NOT_APPLICABLE
universe_lock_status = draft_not_locked
company_level_live_found_path_for_DRU101_105 = NOT_PROVEN
cninfo_calls = 0
ready_for_commit = true
```
