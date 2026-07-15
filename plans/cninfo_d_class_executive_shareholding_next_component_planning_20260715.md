# CNINFO D 类 executive_shareholding — Next-Component Planning

_生成时间：2026-07-15_

> **性质：** offline next-component planning only · **CNINFO calls = 0** · **无 live** · **无 runner** · **无 commit** · **无 push** · **不是 verified** · **不是 production_ready** · **不是 approved**

**Prior state：** `shareholder_change` first-slice **`COMMITTED_COMPLETE`** · closure/execution gate **`PASS_WITH_CAVEAT`** · closure commit **`17bc0fe`** · commit-boundary note **`ca608c1`** · **NOT pushed** · **NOT verified**

**Planning gate：**

```text
d_class_executive_shareholding_next_component_planning_gate = READY_FOR_APPROVAL
```

**Explicit：** `READY_FOR_APPROVAL` ≠ **approved** · 本包 **不** 实现 runner · **不** CNINFO live · **不** 重开 DLC006R / 301259

---

## 1. Why Plan Now

| 事件 | 状态 |
|------|------|
| shareholder_change first-slice | **COMMITTED_COMPLETE** · **`17bc0fe`** · 4/5 acceptable · DSC004 caveat retained · **NOT verified** · **NOT pushed** |
| equity_pledge | **closed** · **`85abad0`** · **NOT pushed** |
| restricted_shares_unlock | **closed** · **`aa087b5`** · **NOT pushed** |
| block_trade | **closed** · **`403472d`** · **NOT verified** · **NOT pushed** |
| margin_trading / disclosure_schedule / known-event | **closed** · 不得重开 |

Era D D-line 已完成 **7** 个 first-slice 轨道（含 shareholder_change）。shareholder_change 规划阶段已将 **`executive_shareholding`** 标为 runner-up；`COMMITTED_COMPLETE` 后自然晋升为 **primary** 候选。

**本任务：** 确认 primary · 写规划包 · 草拟 first-slice shape · **不** 实现 runner · **不** live。

---

## 2. Ranked Options（post shareholder_change COMMITTED_COMPLETE）

| Rank | Component | Status | Rationale |
|------|-----------|--------|-----------|
| **1** | **`executive_shareholding`** | **primary** | P0 · registry/schema freeze 就绪 · DLC007（002415）Phase1 tiny-live 先例 · `leader/detail` 单端点 · 与已 closed slice 正交 |
| 2 | `abnormal_trading` | deprioritize | 市场级端点 · 无 tiny-live company case · first-slice fit 弱 |
| 3 | `shareholder_data` | deprioritize | P2 · periodic structure · 非 company_event 第一切片优先 |
| 4 | `fund_industry_allocation` | deprioritize | P2 · 基金行业 · 与公司事件正交性弱 |
| — | `shareholder_change` | **COMMITTED_COMPLETE** · **`17bc0fe`** | 不得重开 · **NOT verified** · **NOT pushed** |
| — | `equity_pledge` | **closed** · **`85abad0`** | 不得重开 · **NOT pushed** |
| — | `restricted_shares_unlock` | **closed** · **`aa087b5`** | 不得重开 · **NOT verified** |
| — | `block_trade` | **closed** · **`403472d`** | 不得重开 · **NOT verified** |
| — | `margin_trading` | **closed** · **`116f875`** | 不得重开 |
| — | `disclosure_schedule` | **closed** · **`d37ce0a`** | 不得重开 · DDS004 caveat retained |
| — | `known_event` | **closed** · **`389cd9c`** | 不得重开 · 不 rerun DLC003R/DLC006R |

**Recommend ONE primary：** **`executive_shareholding`**

---

## 3. Lessons from Prior Sparse-Day / Caveat Tracks

| 教训 | executive_shareholding 规划含义 |
|------|--------------------------------|
| 稀疏锚点全宇宙零行 | `empty_but_valid` 为 **合法 acceptable** 结果 · 不得视为 failure |
| block_trade DBT002 | **禁止** sole `captured_normal_candidate` 绑定可能稀疏的单一 anchor |
| equity_pledge DEP004 / shareholder_change DSC004 | **避免** 单独 fragile `captured_normal_or_needs_review` 成为唯一硬期望；混排 expectation mix |
| RSU 5/5 · equity_pledge / shareholder_change sparse | universe 混排 `empty_but_valid` + `captured_normal_or_empty_but_valid` + 至多一例 `captured_normal_or_needs_review` |
| ≥3/5 acceptable | 执行 gate **`PASS_WITH_CAVEAT`** · **不是 bare PASS** |
| DDS004（002415）field-mapping | DLC007 同公司同映射负担 · first-slice **可** 用独立 **DES** case_id · **不** 等同 DDS004 · **不** forced pass |
| live_snapshots local-only | 沿用 commit boundary 政策 |
| prior tracks | **NOT verified** · **NOT production_ready** |

---

## 4. DLC006R / 301259 / DLC007 Policy（explicit）

| 项 | 政策 |
|----|------|
| DLC006R（301259 艾布鲁） | known-event replacement track **closed** · **不得** 作为 first-slice 主案例 · **不得** 重开 |
| 301259 | **永久排除** first-slice primary universe |
| 688671 | **永久排除** first-slice primary universe（DLC003R） |
| DLC007（002415 海康威视） | Phase1 tiny-live **`needs_review_candidate`** 先例 · 可用 **独立 DES case_id** · **不** 等同 DDS004 · **不** forced pass |
| known-event reopen | **禁止** · 不 rerun DLC003R/DLC006R |
| disclosure→captured_normal | **禁止** |

---

## 5. Primary: `executive_shareholding`

### 5.1 Rationale

| 项 | 评估 |
|----|------|
| prior evidence | DLC007（002415）Phase1 tiny-live **found · needs_review**（2 rows · position/amount medium confidence）· DC006 synthetic `captured_normal` 模板 |
| endpoint | `https://www.cninfo.com.cn/data20/leader/detail` · POST · query params |
| query mode | **`timeMark` / `varyType`** · registry default **`oneMonth` + `b`** · stability tested：oneMonth/b · threeMonth/b · oneMonth/s |
| schema | Phase1 freeze v1 · ready_case **DC006** · `mapping_confidence=medium` · 通用 event 列不足须保留 `raw_record_json` |
| orthogonality | **高** — 高管持股变动 vs 股东增减持/质押/解禁/大宗/融资融券/披露 无 first-slice 重叠 |
| implementation | first-slice 建议 **单模式** `timeMark=oneMonth` + `varyType=b` · per-case **≤ 1–3** probe · total **≤ 20** |
| risk | **medium** — varyType 语义 UI 待确认 · F005N uncertain · position/amount medium confidence · 与 DDS004 映射模式重叠但组件正交 |

### 5.2 First-Slice Parameters（sketch only · NOT APPROVED）

| 项 | 提案 |
|----|------|
| size | **5**（DES001–DES005） |
| output root | `outputs/validation/cninfo_d_class_executive_shareholding_first_slice/` |
| mode flag | `--executive-shareholding-first-slice`（**未来** · 本任务 **不实现**） |
| approval flag | `--approve-d-class-executive-shareholding-first-slice`（**未来**） |
| proposed query | **`timeMark=oneMonth`** · **`varyType=b`**（registry `default_params` · 离线文档化 · **非 CNINFO 探测**） |
| optional probe note | tiny-live 曾用 threeMonth/oneYear 多探测；first-slice **优先单模式**，多探测仅在后续 runner design 批准后 |
| request cap | **≤ 20** total |
| threshold | **≥ 3/5 acceptable** → **`PASS_WITH_CAVEAT`** |

**NOT APPROVED** · **无 runner** · **无 live** · **NOT verified** · **NOT production_ready**

### 5.3 Field / Mapping Caveats（planning awareness）

| 项 | 说明 |
|----|------|
| confirmed core | SECCODE · SECNAME · ENDDATE · HUMANNAME · F001V · F002V · F003V · F006N · F008N · F010V |
| raw_only / not_visible | DECLAREDATE · F004N · F007N · F009N · F011V |
| uncertain | **F005N**（transaction_amount_candidate） |
| needs_review trigger（runner 既有逻辑，只读引用） | F001V≠F002V 或 F004N/F005N/F006N 全空 → `needs_review` |
| summary tab | **不是** 本 source · 未来 `executive_shareholding_summary` · **本 first-slice 不做** |

---

## 6. Runner-Up（after executive_shareholding）

| 项 | 内容 |
|----|------|
| rank | **2**（deprioritized relative to primary） |
| component | `abnormal_trading`（或后续再评 `shareholder_data`） |
| why not primary now | 市场级端点 / 无 company tiny-live · 或 P2 periodic · 不适合紧接 shareholder_change 后的 company_event 广度 |
| when | executive_shareholding first-slice 收口后再规划 |

---

## 7. Excludes

| 类别 | 项 |
|------|-----|
| Primary cases | **688671** · **301259** |
| Closed tracks | known-event · margin_trading · disclosure_schedule · block_trade · restricted_shares_unlock · equity_pledge · **shareholder_change** |
| This round | abnormal_trading · shareholder_data · fund_industry_allocation · executive_shareholding_summary |
| Forbidden reopen | DLC003R · **DLC006R** · denser-day without separate approval |

---

## 8. Closed Tracks（保持 unchanged）

| Track | Gate / Commit |
|-------|---------------|
| shareholder_change | **`PASS_WITH_CAVEAT`** · **`COMMITTED_COMPLETE`** · **`17bc0fe`** · **NOT verified** · **NOT pushed** |
| equity_pledge | **`PASS_WITH_CAVEAT`** · **`85abad0`** · **NOT pushed** |
| restricted_shares_unlock | **`PASS_WITH_CAVEAT`** · **`aa087b5`** · **NOT pushed** |
| block_trade | **`PASS_WITH_CAVEAT`** · **`403472d`** · **NOT verified** · **NOT pushed** |
| margin_trading | **`PASS_WITH_CAVEAT`** · **`116f875`** |
| disclosure_schedule | **`PASS_WITH_CAVEAT`** · **`d37ce0a`** · DDS004 retained |
| known-event | **`PASS_WITH_CAVEAT`** · **`389cd9c`** |

---

## 9. Artifacts

| 项 | 路径 |
|----|------|
| planning（本文件） | [cninfo_d_class_executive_shareholding_next_component_planning_20260715.md](cninfo_d_class_executive_shareholding_next_component_planning_20260715.md) |
| candidate matrix | [cninfo_d_class_executive_shareholding_next_component_candidate_matrix_20260715.csv](../outputs/validation/cninfo_d_class_executive_shareholding_next_component_candidate_matrix_20260715.csv) |
| recommendation | [cninfo_d_class_executive_shareholding_next_component_recommendation_20260715.md](../outputs/validation/cninfo_d_class_executive_shareholding_next_component_recommendation_20260715.md) |
| planning summary | [cninfo_d_class_executive_shareholding_next_component_planning_summary_20260715.md](../outputs/validation/cninfo_d_class_executive_shareholding_next_component_planning_summary_20260715.md) |
| universe sketch | [cninfo_d_class_executive_shareholding_first_slice_universe_draft_sketch_20260715.csv](../outputs/validation/cninfo_d_class_executive_shareholding_first_slice_universe_draft_sketch_20260715.csv) |
| VR checklist stub | [cninfo_d_class_executive_shareholding_offline_prep_checklist_stub_20260715.csv](../outputs/validation/cninfo_d_class_executive_shareholding_offline_prep_checklist_stub_20260715.csv) |
| next step | [cninfo_d_class_executive_shareholding_next_component_next_step_recommendation_20260715.md](../outputs/validation/cninfo_d_class_executive_shareholding_next_component_next_step_recommendation_20260715.md) |

---

## 10. Red Lines

No CNINFO · No live · No runner · No closed-track expansion · No PDF/DB/MinIO/RAG/verified · No commit · No push · No DLC006R/301259 reopen · No A/B/C file touch
