# CNINFO D 类 equity_pledge — Next-Component Planning

_生成时间：2026-07-10_

> **性质：** offline next-component planning only · **CNINFO calls = 0** · **无 live** · **无 runner** · **无 commit** · **不是 verified**

**Prior state：** restricted_shares_unlock first-slice committed **`aa087b5`** · gate **`PASS_WITH_CAVEAT`** · **NOT pushed**

**Planning gate：**

```text
d_class_equity_pledge_next_component_planning_gate = READY_FOR_APPROVAL
```

---

## 1. Why Plan Now

| 事件 | 状态 |
|------|------|
| restricted_shares_unlock first-slice | **closed + committed** · **`aa087b5`** · **5/5** sparse-day `empty_but_valid` · **NOT verified** · **NOT pushed** |
| block_trade first-slice | **closed** · **`403472d`** · **NOT verified** · **NOT pushed** |
| margin_trading / disclosure_schedule / known-event | **closed** · 不得重开 |

Era D D-line 已完成 **5** 个 first-slice 轨道（含 RSU）。下一组件选择基于 **v2 refresh runner-up**、RSU/block_trade **稀疏日教训**、以及 DLC005 tiny-live 先例重新确认。

**本任务：** 确认 primary · 写规划包 · 草拟 first-slice shape · **不** 实现 runner · **不** live。

---

## 2. Ranked Options（post RSU commit）

| Rank | Component | Status | Rationale |
|------|-----------|--------|-----------|
| **1** | **`equity_pledge`** | **primary** | P0 · registry/schema 就绪 · DLC005 `empty_but_valid` 先例 · 单 `tdate` 端点 · 实施成本低于 RSU multi-probe · orthogonality 高 |
| 2 | `shareholder_change` | runner-up | P0 · registry 就绪 · 须排除 301259 · DLC006R gap 文档负担高于 equity_pledge |
| 3 | `executive_shareholding` | alternate | DLC007 `needs_review` · 与 DDS004 field-mapping 负担重叠 |
| — | `restricted_shares_unlock` | **closed** · **`aa087b5`** | 不得重开 |
| — | `block_trade` | **closed** · **`403472d`** | 不得重开 · **NOT verified** |
| — | `margin_trading` | **closed** · **`116f875`** | 不得重开 |
| — | `disclosure_schedule` | **closed** · **`d37ce0a`** | 不得重开 |
| — | `known_event` | **closed** · **`389cd9c`** | 不得重开 · 不 rerun DLC003R/DLC006R |
| — | `abnormal_trading` | deferred | 市场级端点 · 无 tiny-live case |
| — | `shareholder_data` / `fund_industry_allocation` | deferred | P2 · 无 tiny-live 先例 |

**Recommend ONE primary：** **`equity_pledge`**

---

## 3. Lessons from RSU / block_trade Sparse-Day

| 教训 | equity_pledge 规划含义 |
|------|------------------------|
| 稀疏锚点全宇宙零行 | `empty_but_valid` 为 **合法 acceptable** 结果 · 不得视为 failure |
| block_trade DBT002 | **禁止** sole `captured_normal_candidate` 绑定可能稀疏的单一 anchor |
| RSU 5/5 empty_but_valid | universe 混排 `empty_but_valid` + `captured_normal_or_empty_but_valid` + 至多一例 `captured_normal_or_needs_review` |
| ≥3/5 acceptable | 执行 gate **`PASS_WITH_CAVEAT`** · **不是 bare PASS** |
| live_snapshots local-only | 沿用 commit boundary 政策 |
| RSU / block_trade | **NOT verified** · **NOT production_ready** |

---

## 4. Primary: `equity_pledge`

### 4.1 Rationale

| 项 | 评估 |
|----|------|
| prior evidence | DLC005（688981）Phase1 tiny-live **acceptable** · `empty_but_valid` |
| endpoint | `https://www.cninfo.com.cn/data20/equityPledge/list` · POST · query `tdate` |
| query mode | **`tdate_daily`**（单 tdate · 无 multi-probe 窗口） |
| schema | registry fields confirmed（SECCODE · F001V/F003V · F006N/F007N/F018N） |
| orthogonality | **高** — 股权质押 vs 解禁/大宗/融资融券/披露 无重叠 |
| implementation | 单请求/案可行 · per-case cap **≤ 4** · total **≤ 20** |
| risk | **低** — 单 tdate 端点 · 须排除 688671/301259 |

### 4.2 First-Slice Parameters（sketch only）

| 项 | 提案 |
|----|------|
| size | **5**（DEP001–DEP005） |
| output root | `outputs/validation/cninfo_d_class_equity_pledge_first_slice/` |
| mode flag | `--equity-pledge-first-slice`（**未来** · 本任务 **不实现**） |
| approval flag | `--approve-d-class-equity-pledge-first-slice`（**未来**） |
| proposed anchor `tdate` | **2026-07-03**（registry `default_params.tdate` · 离线文档化 · **非 CNINFO 探测**） |
| request cap | **≤ 20** total |
| threshold | **≥ 3/5 acceptable** → **`PASS_WITH_CAVEAT`** |

**NOT APPROVED** · **无 runner** · **无 live**

---

## 5. Runner-Up: `shareholder_change`

| 项 | 内容 |
|----|------|
| rank | **2** |
| why not primary now | DLC006 先例存在但 301259/DLC006R gap 文档负担；equity_pledge 证据链更干净（DLC005 only） |
| when | equity_pledge first-slice 收口后可再规划 |

---

## 6. Excludes

| 类别 | 项 |
|------|-----|
| Primary cases | **688671** · **301259** |
| Closed tracks | known-event · margin_trading · disclosure_schedule · block_trade · restricted_shares_unlock |
| This round | abnormal_trading · shareholder_data · fund_industry_allocation |

---

## 7. Closed Tracks（保持 unchanged）

| Track | Gate / Commit |
|-------|---------------|
| restricted_shares_unlock | **`PASS_WITH_CAVEAT`** · **`aa087b5`** · **NOT pushed** |
| block_trade | **`PASS_WITH_CAVEAT`** · **`403472d`** · **NOT verified** · **NOT pushed** |
| margin_trading | **`PASS_WITH_CAVEAT`** · **`116f875`** |
| disclosure_schedule | **`PASS_WITH_CAVEAT`** · **`d37ce0a`** |
| known-event | **`PASS_WITH_CAVEAT`** · **`389cd9c`** |

---

## 8. Artifacts

| 项 | 路径 |
|----|------|
| candidate matrix | [cninfo_d_class_equity_pledge_next_component_candidate_matrix.csv](../outputs/validation/cninfo_d_class_equity_pledge_next_component_candidate_matrix.csv) |
| recommendation | [cninfo_d_class_equity_pledge_next_component_recommendation.md](../outputs/validation/cninfo_d_class_equity_pledge_next_component_recommendation.md) |
| first-slice sketch | [cninfo_d_class_equity_pledge_first_slice_plan_draft.md](cninfo_d_class_equity_pledge_first_slice_plan_draft.md) |
| universe sketch | [cninfo_d_class_equity_pledge_first_slice_universe_draft_sketch.csv](../outputs/validation/cninfo_d_class_equity_pledge_first_slice_universe_draft_sketch.csv) |
| summary | [cninfo_d_class_equity_pledge_next_component_planning_summary.md](../outputs/validation/cninfo_d_class_equity_pledge_next_component_planning_summary.md) |
| next step | [cninfo_d_class_equity_pledge_next_component_next_step_recommendation.md](../outputs/validation/cninfo_d_class_equity_pledge_next_component_next_step_recommendation.md) |

---

## 9. Red Lines

No CNINFO · No live · No runner · No closed-track expansion · No PDF/DB/MinIO/RAG/verified · No commit · No push
