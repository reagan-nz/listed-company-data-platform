# CNINFO D 类 Era D — Next-Component Planning Refresh

_生成时间：2026-07-10_

> **性质：** offline planning refresh only · **CNINFO calls = 0** · **无 live** · **无 runner** · **无 commit** · **不是 verified**

**Prior planning gate（保持）：** `d_class_erad_next_component_planning_gate = READY_FOR_APPROVAL`

**Refresh gate：**

```text
d_class_erad_next_component_planning_refresh_gate = READY_FOR_APPROVAL
```

---

## 1. Why Refresh Now

| 事件 | 状态 |
|------|------|
| block_trade first-slice | **closed** · commit **`403472d`** · gate **`PASS_WITH_CAVEAT`** · **NOT pushed** |
| margin_trading first-slice | **closed** · commit **`116f875`** |
| disclosure_schedule first-slice | **closed** · commit **`d37ce0a`** |
| known-event replacement | **closed** · `PASS_WITH_CAVEAT` · commit **`389cd9c`** |

Era D D-line 已完成 **4** 个 first-slice 轨道（含 block_trade）。下一组件选择需基于 **block_trade 稀疏日教训** 重新排序，而非重复 v1 推荐。

**本任务：** 选下一组件 + 写规划包 v2 · **不** 实现 runner · **不** live · **不** 扩已收口 slice。

---

## 2. block_trade Lessons（输入约束）

| 教训 | 规划含义 |
|------|----------|
| 稀疏日全宇宙 `empty_but_valid` | anchor `tdate` 不得假设有行；universe 应混排 `empty_but_valid` 与 `captured_normal_or_empty_but_valid` |
| DBT002 `expectation_mismatch_on_sparse_day` | **禁止** 将唯一 `captured_normal_candidate` 案例绑定稀疏锚点；DLC002-style control 保留 `empty_but_valid` |
| 4/5 acceptable 仍 `PASS_WITH_CAVEAT` | 阈值 **≥3/5** 仍适用；caveat ledger 必须预留 |
| live_snapshots local-only | 下一组件沿用 commit boundary 政策 |

**block_trade 不是 verified** · **不是 production_ready**。

---

## 3. Closed-Track Inventory（不得重开）

| Track | Gate / Commit | 本任务 |
|-------|---------------|--------|
| known-event | `PASS_WITH_CAVEAT` · **`389cd9c`** | **不重开** · 不 rerun DLC003R/DLC006R |
| margin_trading first-slice | `PASS_WITH_CAVEAT` · **`116f875`** | **不扩展** |
| disclosure_schedule first-slice | `PASS_WITH_CAVEAT` · **`d37ce0a`** | **不扩展** |
| block_trade first-slice | `PASS_WITH_CAVEAT` · **`403472d`** | **不扩展** |

**永久排除（first-slice 宇宙）：** **688671** · **301259**

---

## 4. Candidate Re-Evaluation（post block_trade）

| Rank | Component | Why now / why not |
|------|-----------|-------------------|
| **1** | **`restricted_shares_unlock`** | P0 · registry + table_sources 就绪 · DLC003 tiny-live `empty_but_valid` · orthogonality 高（解禁日历 vs 大宗/融资融券/披露）· runner 已有 multi-probe 骨架 · Era D 广度下一自然步 |
| **2** | `equity_pledge` | P0 · DLC005 先例 · 单 tdate 端点 · 实施成本低于解禁 · 但 Era D 广度上解禁日历优先于股权质押 |
| **3** | `shareholder_change` | DLC006 先例 · 须排除 301259 · DLC006R gap 文档负担 |
| **4** | `executive_shareholding` | DLC007 `needs_review` · 与 DDS004 field-mapping 负担重叠 |
| — | `block_trade` | **done** · commit **`403472d`** |
| — | `margin_trading` / `disclosure_schedule` | **closed** |
| — | `abnormal_trading` | 市场级端点 · 无 tiny-live case · 公司级 first-slice 弱 |
| — | `shareholder_data` / `fund_industry_allocation` | P2 · 无 tiny-live 先例 |

---

## 5. Primary Recommendation: `restricted_shares_unlock`

### 5.1 Rationale

| 项 | 评估 |
|----|------|
| prior evidence | DLC003（300009）Phase1 tiny-live **acceptable** · `empty_but_valid` |
| endpoint | `https://www.cninfo.com.cn/data20/liftBan/detail` · POST · query `tdate` |
| schema | registry fields confirmed（SECCODE · F003D unlock date · F004N/F005N/F008N） |
| orthogonality | **高** — 与已收口 slice 无重叠；解禁日历语义独立 |
| implementation | runner 已支持 `restricted_shares_unlock` multi-probe；需新建 first-slice mode 隔离层 |
| risk | **中** — anchor 窗口 / 多 probe · **必须**排除 688671（DLC003R caveated · track closed） |
| block_trade lesson | universe 混排 empty + flexible captured；避免单案例 `captured_normal_candidate` on sparse anchor |

### 5.2 Proposed First-Slice Sketch

见 [cninfo_d_class_restricted_shares_unlock_first_slice_plan_draft.md](cninfo_d_class_restricted_shares_unlock_first_slice_plan_draft.md)。

| 项 | 提案 |
|----|------|
| size | **5**（DRU001–DRU005） |
| output root | `outputs/validation/cninfo_d_class_restricted_shares_unlock_first_slice/` |
| mode flag | `--restricted-shares-unlock-first-slice` |
| approval flag | `--approve-d-class-restricted-shares-unlock-first-slice` |
| request cap | **≤ 20**（multi-probe 需 per-case budget 设计） |
| threshold | **≥ 3/5 acceptable** → `PASS_WITH_CAVEAT` |

**NOT APPROVED** · **无 runner** · **无 live**

---

## 6. Runner-Up: `equity_pledge`

| 项 | 评估 |
|----|------|
| prior evidence | DLC005 tiny-live `empty_but_valid` acceptable |
| endpoint | 单 tdate · 实施成本 **低于** restricted_shares_unlock |
| 为何 runner-up | P0 价值高但解禁日历对 Era D 广度更关键；可在 restricted_shares_unlock 收口后作为第三组件 |

---

## 7. Deprioritized

| 组件 | 原因 |
|------|------|
| shareholder_change | 301259 gap baggage · DLC006R track closed |
| executive_shareholding | needs_review · 002415/DDS004 overlap |
| abnormal_trading | 无 tiny-live · 市场级 |
| shareholder_data / fund_industry_allocation | P2 · 无先例 |

---

## 8. Success Threshold（继承）

```text
acceptable_count >= 3  →  PASS_WITH_CAVEAT
acceptable_count < 3   →  FAIL_REVIEW_REQUIRED
```

**永不** bare PASS · **永不** verified · **永不** production_ready

---

## 9. Next Step

Human approve next-component choice → **restricted_shares_unlock first-slice approval package**（universe + checklist + command draft · **仍无 live**）

---

## 10. References

- [block_trade commit status](../outputs/validation/cninfo_d_class_block_trade_first_slice_commit_status.md)
- [candidate matrix v2](../outputs/validation/cninfo_d_class_erad_next_component_candidate_matrix_v2.csv)
- [recommendation v2](../outputs/validation/cninfo_d_class_erad_next_component_recommendation_v2.md)
- [prior planning v1](cninfo_d_class_erad_next_component_planning.md)
- [registry draft](../config/cninfo_d_class_source_registry_draft.yaml)
