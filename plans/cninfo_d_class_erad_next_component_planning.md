# CNINFO D 类 Era D — Next-Component Planning

_生成时间：2026-07-10_

> **性质：** offline planning only · **无 CNINFO** · **无 live** · **无 runner 实现** · **无 commit** · **不是 verified**

**Era 状态：** D 类已完成 Era C finish-up；D 线 **进入 Era D**（本地多组件广度扩样）。

**规划 gate：**

```text
d_class_erad_next_component_planning_gate = READY_FOR_APPROVAL
```

---

## 1. Era D Goal for D-Line

在 **不接库、不写 verified、不下载 PDF** 的前提下，把 D 类从 Era C 的「单组件 first-slice 试点」扩展到 **多组件本地稳定抽取**：

| 目标 | 说明 |
|------|------|
| 广度 | ≥3 组件完成 first-slice 以上扩样（Era D 完整验收见 [eraD_execution_plan.md](eraD_execution_plan.md) §0.2） |
| 深度 | 每组件 first-slice **5-case** 起步；后续可扩至 ≥20 |
| 纪律 | 与 Era C 相同 gate 链：planning → dry-run → live-path → approve → live → closure → boundary → commit |
| 产物 | 隔离 `outputs/validation/cninfo_d_class_<component>_first_slice/` + live_snapshots + ledgers |
| 红线 | 无 DB/MinIO/RAG · 无 verified/production_ready · 不升级 disclosure-only → captured_normal |

**本任务仅选下一组件并写规划包**；不实现 runner、不 live、不扩已收口 slice。

---

## 2. Closed-Track Inventory（不得重开）

| Track | 状态 | Commit / 证据 | 本任务 |
|-------|------|---------------|--------|
| known-event replacement | **closed** · `PASS_WITH_CAVEAT` | `389cd9c` · DLC003R/DLC006R caveated | **不重开** · 不 rerun DLC003R/DLC006R |
| margin_trading first-slice | **closed** · `PASS_WITH_CAVEAT` | **`116f875`** · 5/5 acceptable | **不扩展** |
| disclosure_schedule first-slice | **closed** · `PASS_WITH_CAVEAT` | **`d37ce0a`** · 5/5 acceptable · DDS004 CAV-DDS-004 retained | **不扩展** |

**永久排除（first-slice 宇宙）：** **688671** · **301259**（known-event 主案例；不得作为下一组件 primary cases）。

---

## 3. Candidate Evaluation Criteria

| 维度 | 权重 | 说明 |
|------|------|------|
| prior tiny-live evidence | 高 | Phase1 tiny-live（DLC001–DLC007）与 ready-case benchmark（DC001–DC007） |
| endpoint stability | 高 | 单请求/公司、registry 已登记、Phase1 schema freeze 覆盖 |
| orthogonality | 高 | 与 margin_trading / disclosure_schedule 已收口 slice 不重复；不依赖 known-event 重开 |
| implementation cost | 中 | 可复用 `run_cninfo_d_class_tiny_live_validation.py` first-slice 模式 |
| request budget | 中 | first-slice 默认 ≤20 CNINFO（5-case × ~1 req） |
| Era D MVP 对齐 | 中 | P0 组件优先；支撑「再 1 组件」MVP（§0.3） |

---

## 4. Primary Recommendation: `block_trade`

### 4.1 Rationale

| 项 | 评估 |
|----|------|
| prior evidence | DLC002（601988）Phase1 tiny-live **acceptable** · `empty_but_valid`；DC002 ready-case **captured_pass**（fixture/synthetic 口径） |
| endpoint | `data20/ints/statistics` · **1 req/case** · `tdate` 日度查询 |
| orthogonality | **高** — 与 margin_trading / disclosure_schedule 无重叠 slice；known-event track **未**以 block_trade 为主轴 |
| implementation | 与 margin_trading first-slice 同型（company filter + date anchor） |
| risk | 低–中；稀疏日 `empty_but_valid` 为合法结果，需在 universe 中混排 captured + empty |

### 4.2 Proposed First-Slice

| 项 | 值 |
|----|-----|
| size | **5**（DBT001–DBT005） |
| exclude | **688671** · **301259** |
| endpoint family | `https://www.cninfo.com.cn/data20/ints/statistics` |
| query mode | `tdate_daily`（registry `block_trade/ints/statistics`） |
| request cap | **≤ 20**（planned **5**） |
| success threshold | **≥ 3/5 acceptable** → `d_class_block_trade_first_slice_execution_gate = PASS_WITH_CAVEAT` |
| positive control | DBT001 建议 `captured_normal_candidate`（活跃标的 · 非 known-event 排除码） |

### 4.3 Output Root Naming

```text
outputs/validation/cninfo_d_class_block_trade_first_slice/
```

### 4.4 Planned Flags Naming

| 用途 | 提案 |
|------|------|
| mode flag | `--block-trade-first-slice` |
| live approval | `--approve-d-class-block-trade-first-slice` |
| universe | `--universe-csv outputs/validation/cninfo_d_class_block_trade_first_slice_universe_draft.csv` |
| output root | `--output-root outputs/validation/cninfo_d_class_block_trade_first_slice/` |

### 4.5 Scope Limits

- metadata / structured-table only
- **无** PDF / OCR / extraction / DB / MinIO / RAG
- **无** verified / production_ready / testing_stable_sample 升级
- **无** disclosure→captured_normal 升级

---

## 5. Runner-Up: `restricted_shares_unlock`

| 项 | 评估 |
|----|------|
| prior evidence | DLC003（300009）tiny-live acceptable · `empty_but_valid`；DLC003R 有 caveated structured evidence（**track closed**） |
| endpoint | `liftBan/detail` · 可能需要 anchor 窗口 / 多 probe |
| orthogonality | 中 — 组件与 known-event **关联**但可新建宇宙；**必须**排除 688671 |
| implementation cost | **高于** block_trade（日期锚点、probe 计划） |
| 为何 runner-up | P0 优先级高、Era D 广度需要解禁日历；但复杂度和 known-event 文档负担使其实施排在 block_trade 之后 |

---

## 6. Deprioritized / Later

| 组件 | 原因 |
|------|------|
| shareholder_change | DLC006R 组件缺口已接受（301259）；fresh slice 可行但文档负担高 |
| executive_shareholding | DLC007 `needs_review`；与 DDS004（002415）field-mapping 负担重叠 |
| equity_pledge | 仅 tiny-live empty_but_valid 证据；可第三顺位 |
| abnormal_trading | 市场级统计端点；无 Phase1 tiny-live case；公司级 orthogonality 弱 |
| shareholder_data | P2 · registry 有 · 无 tiny-live 先例 |
| fund_industry_allocation | P2 · 基金行业配置 · 与公司事件 orthogonality 弱 |

---

## 7. Success Threshold Sketch

与 margin_trading / disclosure_schedule first-slice 对齐：

```text
acceptable_count >= 3  →  PASS_WITH_CAVEAT
acceptable_count < 3   →  FAIL_REVIEW_REQUIRED
```

- `empty_but_valid` 计 acceptable（若 expected_behavior 允许）
- `needs_review` 可 acceptable 但须 ledger caveat（参照 DDS004）
- **永不** bare PASS · **永不** verified

---

## 8. Next Step

**block_trade first-slice approval package**（offline）：

- universe draft（5-case · 排除 688671/301259）
- approval checklist · command draft · planning summary
- **无** runner 实现（下一任务）

---

## 9. References

- [eraD_execution_plan.md](eraD_execution_plan.md)
- [cninfo_d_class_source_registry_draft.yaml](../config/cninfo_d_class_source_registry_draft.yaml)
- [cninfo_d_class_readiness_matrix.csv](../outputs/validation/cninfo_d_class_readiness_matrix.csv)
- [cninfo_d_class_erad_next_component_candidate_matrix.csv](../outputs/validation/cninfo_d_class_erad_next_component_candidate_matrix.csv)
- margin_trading commit **`116f875`** · disclosure_schedule commit **`d37ce0a`**
