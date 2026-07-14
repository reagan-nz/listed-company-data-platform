# CNINFO D 类 shareholder_change — Next-Component Planning

_生成时间：2026-07-13_

> **性质：** offline next-component planning only · **CNINFO calls = 0** · **无 live** · **无 runner** · **无 commit** · **不是 verified**

**Prior state：** equity_pledge first-slice committed **`85abad0`** · gate **`PASS_WITH_CAVEAT`** · **NOT pushed**

**Planning gate：**

```text
d_class_shareholder_change_next_component_planning_gate = READY_FOR_APPROVAL
```

---

## 1. Why Plan Now

| 事件 | 状态 |
|------|------|
| equity_pledge first-slice | **closed + committed** · **`85abad0`** · **4/5** · DEP004 caveat · **NOT verified** · **NOT pushed** |
| restricted_shares_unlock | **closed** · **`aa087b5`** · **NOT pushed** |
| block_trade | **closed** · **`403472d`** · **NOT verified** · **NOT pushed** |
| margin_trading / disclosure_schedule / known-event | **closed** · 不得重开 |

Era D D-line 已完成 **6** 个 first-slice 轨道（含 equity_pledge）。equity_pledge 规划阶段已将 **`shareholder_change`** 标为 runner-up；commit **`85abad0`** 后自然晋升为 primary 候选。

**本任务：** 确认 primary · 写规划包 · 草拟 first-slice shape · **不** 实现 runner · **不** live。

---

## 2. Ranked Options（post equity_pledge commit）

| Rank | Component | Status | Rationale |
|------|-----------|--------|-----------|
| **1** | **`shareholder_change`** | **primary** | P0 · registry/schema 就绪 · DLC006（000550）Phase1 tiny-live 先例 · `shareholeder/detail` 单端点 · orthogonality 高 |
| 2 | `executive_shareholding` | runner-up | P0 · DLC007 `needs_review` · 与 DDS004 field-mapping 负担重叠 |
| 3 | `abnormal_trading` | deprioritize | 市场级端点 · 无 tiny-live company case |
| 4 | `shareholder_data` | deprioritize | P2 · periodic structure · 非 company_event 第一切片优先 |
| 5 | `fund_industry_allocation` | deprioritize | P2 · 基金行业 · 与公司事件正交性弱 |
| — | `equity_pledge` | **closed** · **`85abad0`** | 不得重开 · **NOT pushed** |
| — | `restricted_shares_unlock` | **closed** · **`aa087b5`** | 不得重开 · **NOT verified** |
| — | `block_trade` | **closed** · **`403472d`** | 不得重开 · **NOT verified** |
| — | `margin_trading` | **closed** · **`116f875`** | 不得重开 |
| — | `disclosure_schedule` | **closed** · **`d37ce0a`** | 不得重开 |
| — | `known_event` | **closed** · **`389cd9c`** | 不得重开 · 不 rerun DLC003R/DLC006R |

**Recommend ONE primary：** **`shareholder_change`**

---

## 3. Lessons from RSU / block_trade / equity_pledge Sparse-Day

| 教训 | shareholder_change 规划含义 |
|------|------------------------------|
| 稀疏锚点全宇宙零行 | `empty_but_valid` 为 **合法 acceptable** 结果 · 不得视为 failure |
| block_trade DBT002 | **禁止** sole `captured_normal_candidate` 绑定可能稀疏的单一 anchor |
| equity_pledge DEP004 | **避免** 单独 `captured_normal_or_needs_review` 在稀疏日上成为唯一 fragile label；混排 expectation mix |
| RSU 5/5 · equity_pledge 5/5 empty | universe 混排 `empty_but_valid` + `captured_normal_or_empty_but_valid` + 至多一例 `captured_normal_or_needs_review` |
| ≥3/5 acceptable | 执行 gate **`PASS_WITH_CAVEAT`** · **不是 bare PASS** |
| live_snapshots local-only | 沿用 commit boundary 政策 |
| prior tracks | **NOT verified** · **NOT production_ready** |

---

## 4. DLC006R / 301259 Baggage（explicit）

| 项 | 政策 |
|----|------|
| DLC006R（301259 艾布鲁） | known-event replacement track **closed** · **不得** 作为 first-slice 主案例 |
| 301259 | **永久排除** first-slice primary universe |
| DLC006（000550 江铃汽车） | Phase1 tiny-live 先例公司 · 可用 **独立 DSC case_id** · **不** 等同 DLC006R |
| known-event reopen | **禁止** · 不 rerun DLC003R/DLC006R |
| disclosure→captured_normal | **禁止** · DLC006R Option A+C 证据 **不** 升级为 structured capture |

---

## 5. Primary: `shareholder_change`

### 5.1 Rationale

| 项 | 评估 |
|----|------|
| prior evidence | DLC006（000550）Phase1 dry-run **`captured_normal`** 规划口径 · live 稀疏日 `empty_but_valid` 已校准 · endpoint 行为已验证 |
| endpoint | `https://www.cninfo.com.cn/data20/shareholeder/detail` · POST · **CNINFO 注册拼写 `shareholeder`（不修正）** |
| query mode | **`type_inc` / `type_desc`** + optional **`tdate`** · first-slice 建议单 `type` + 共享 `tdate` |
| schema | registry fields confirmed（SECCODE · F002V shareholder · F004N/F005N change amount/ratio） |
| orthogonality | **高** — 股东增减持 vs 质押/解禁/大宗/融资融券/披露 无重叠 |
| implementation | 单请求/案可行（`type=inc` + `tdate`）· per-case cap **≤ 4** · total **≤ 20** |
| risk | **medium** — `type` 模式选择 · 须排除 301259 · DLC006R 文档负担已隔离 |

### 5.2 First-Slice Parameters（sketch only）

| 项 | 提案 |
|----|------|
| size | **5**（DSC001–DSC005） |
| output root | `outputs/validation/cninfo_d_class_shareholder_change_first_slice/` |
| mode flag | `--shareholder-change-first-slice`（**未来** · 本任务 **不实现**） |
| approval flag | `--approve-d-class-shareholder-change-first-slice`（**未来**） |
| proposed anchor `tdate` | **2026-07-03**（registry `default_params.tdate` · 离线文档化 · **非 CNINFO 探测**） |
| default `type` | **`inc`**（first-slice 单模式 · 未来可扩展 desc） |
| request cap | **≤ 20** total |
| threshold | **≥ 3/5 acceptable** → **`PASS_WITH_CAVEAT`** |

**NOT APPROVED** · **无 runner** · **无 live**

---

## 6. Runner-Up: `executive_shareholding`

| 项 | 内容 |
|----|------|
| rank | **2** |
| why not primary now | DLC007 `needs_review_candidate` · field mapping medium confidence · 与 disclosure_schedule DDS004 caveat 模式重叠 |
| when | shareholder_change first-slice 收口后可再规划 |

---

## 7. Excludes

| 类别 | 项 |
|------|-----|
| Primary cases | **688671** · **301259** |
| Closed tracks | known-event · margin_trading · disclosure_schedule · block_trade · restricted_shares_unlock · equity_pledge |
| This round | abnormal_trading · shareholder_data · fund_industry_allocation |

---

## 8. Closed Tracks（保持 unchanged）

| Track | Gate / Commit |
|-------|---------------|
| equity_pledge | **`PASS_WITH_CAVEAT`** · **`85abad0`** · **NOT pushed** |
| restricted_shares_unlock | **`PASS_WITH_CAVEAT`** · **`aa087b5`** · **NOT pushed** |
| block_trade | **`PASS_WITH_CAVEAT`** · **`403472d`** · **NOT verified** · **NOT pushed** |
| margin_trading | **`PASS_WITH_CAVEAT`** · **`116f875`** |
| disclosure_schedule | **`PASS_WITH_CAVEAT`** · **`d37ce0a`** |
| known-event | **`PASS_WITH_CAVEAT`** · **`389cd9c`** |

---

## 9. Artifacts

| 项 | 路径 |
|----|------|
| candidate matrix | [cninfo_d_class_shareholder_change_next_component_candidate_matrix.csv](../outputs/validation/cninfo_d_class_shareholder_change_next_component_candidate_matrix.csv) |
| recommendation | [cninfo_d_class_shareholder_change_next_component_recommendation.md](../outputs/validation/cninfo_d_class_shareholder_change_next_component_recommendation.md) |
| first-slice sketch | [cninfo_d_class_shareholder_change_first_slice_plan_draft.md](cninfo_d_class_shareholder_change_first_slice_plan_draft.md) |
| universe sketch | [cninfo_d_class_shareholder_change_first_slice_universe_draft_sketch.csv](../outputs/validation/cninfo_d_class_shareholder_change_first_slice_universe_draft_sketch.csv) |
| summary | [cninfo_d_class_shareholder_change_next_component_planning_summary.md](../outputs/validation/cninfo_d_class_shareholder_change_next_component_planning_summary.md) |
| next step | [cninfo_d_class_shareholder_change_next_component_next_step_recommendation.md](../outputs/validation/cninfo_d_class_shareholder_change_next_component_next_step_recommendation.md) |

---

## 10. Red Lines

No CNINFO · No live · No runner · No closed-track expansion · No PDF/DB/MinIO/RAG/verified · No commit · No push
