# CNINFO C-Class Phase 3 Batch 500 Expansion Plan

_生成时间：2026-07-09_

> Phase 3 batch 500 **规划文档**。**无 CNINFO** · **无 live** · **无 harvest** · **无 snapshot build**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**前置 gate：** `phase2_smoke_closure_gate = PASS_WITH_CAVEAT` · `phase3_batch_planning_readiness_gate = READY_FOR_PLANNING`

---

# 1. Purpose

Phase 3 验证 C-class 能否从 Phase 2 smoke **200** 扩展到受控 batch **500**。

本轮 **不授权** 全市场（6124）扩源；仅设计第一个 **500** 家 batch 的选股、隔离、gate 与产物路径。

**Phase 3 证明目标：**

- matched_active 干净子集可支撑更大 batch 选股
- Phase 2 教训（delisted / inactive / 9240002）可编码为预筛规则
- output-root 隔离与 approval 流程可复用

**Phase 3 不证明：**

- 全市场稳定性
- BSE 覆盖
- verified / testing_stable_sample 升级

---

# 2. Candidate Pool

## 2.1 Primary pool（主 batch 选股池）

须同时满足：

| 字段 | 值 |
|------|-----|
| `reconciliation_classification` | `matched_active` |
| `refresh_action` | `full_market_active_candidate` |
| `harvest_support_status` | `candidate_supported` |
| `snapshot_support_status` | `not_built` |
| `requires_manual_review` | `false` |
| `board` | **≠** `bse` |

**Refreshed candidate 统计（2026-07-09）：**

- `matched_active` 总计：**4647**
- 满足 primary pool 过滤后：**4643**（剔除 **4** 家 BSE-in-matched_active）

## 2.2 Mandatory exclusions（主 batch 强制排除）

| 排除类别 | count | 说明 |
|----------|-------|------|
| `already_in_c_class` | **863** | Era C 863 已验证 universe |
| `matched_hold` | **26** | all6 hold 子集 |
| `matched_bse_supported_candidate` | **320** | BSE 支持候选 |
| `matched_bse_legacy_hold` | **242** | BSE legacy hold |
| `identity_conflict` | **10** | 身份冲突 |
| `needs_manual_review` | **16** | 需人工审查分类 |
| `not_found_in_cninfo` | **0** | 当前 refreshed CSV 无此分类 |
| `board = bse` | **4** | matched_active 内 BSE 行 |
| Phase 2 smoke 200 | **200** | 已 live harvest；不重复纳入 |
| Phase 2 all-direct-failure | **12** | 见 excluded caveat ledger |
| delisted / inactive caveat | **~318** | primary pool 内 `listing_status=delisted` 或名称含退/退市/*ST |

## 2.3 Phase 2 教训强化

**相对 Phase 2 smoke 200 的改进：**

1. **硬排除 `listing_status=delisted`** — Phase 2 有 **7** 家 delisted 进入 smoke 导致失败
2. **硬排除名称 caveat** — 含 `退` / `退市` / `*ST` 的行不进主 batch（**~161** 家 listed 但名称风险）
3. **排除 Phase 2 全部 200** — 含 **12** all-direct-failure 与 **188** 成功子集
4. **排除 excluded ledger 12 码** — 即使未来选股脚本误选也不纳入

## 2.4 Estimated eligible pool

Primary pool（**4643**）减去 Phase 2 200 与 inactive caveat 重叠后：

**~4145** 家 eligible for stratified selection → 取 **500**

详见 [candidate matrix](../outputs/validation/cninfo_c_class_phase3_batch_500_candidate_matrix.csv)。

---

# 3. Batch Size

**推荐：500 companies**

| 理由 | 说明 |
|------|------|
| 规模 | 足够验证 Phase 2 后的 scale-up（200 → 500） |
| 风险 | 小于全市场；失败可隔离在单 batch |
| 运维 | 3500 HTTP + QA 工作量可控 |
| 学习 | 可观察 delisted 预筛是否将 usable 率提升至 >94%（Phase 2: 188/200=94%） |

---

# 4. Sampling Strategy

## 4.1 分层维度

与 Phase 2 一致，stratified sampling by：

- `exchange`（SZSE / SSE）
- `board`（sse_main / szse_main / chinext / star）
- `listing_status`（仅 `listed`）
- `security_type`（含 `__MISSING__` bucket）
- `company_code_prefix`（000 / 002 / 300 / 600 / 688 / 603 / 601 / 301 / 605 / 001 / 003）

## 4.2 Phase 3 改进

| Phase 2 问题 | Phase 3 对策 |
|-------------|-------------|
| 7 delisted 进入 smoke | pre-filter `listing_status != delisted` |
| 5 ST/legacy 全失败 | pre-filter 名称 `退`/`退市`/`*ST` |
| 200 重复 harvest 风险 | 硬排除 Phase 2 200 codes |
| status CSV 遗留 | harvest QA 后强制 snapshot QA 校正 |

## 4.3 Selection script（未来）

复用/扩展 `lab/select_cninfo_c_class_phase2_smoke_universe.py` 模式：

- 新 seed（建议 `20260709` 或 batch-specific）
- 输入：eligible pool CSV slice
- 输出：`lab/eval_companies_c_class_phase3_batch_500_001.yaml`（**本轮不生成**）

---

# 5. Expected Harvest Scale

| 指标 | 计算 | 值 |
|------|------|-----|
| companies | batch size | **500** |
| live HTTP（direct） | 500 × 6 | **3000** |
| security observe-only | 500 × 1 | **500** |
| **total planned HTTP** | 500 × 7 | **3500** |
| derived normalized rows | 500 × 3 | **1500** |
| expected normalized max（direct） | 500 × 6 | **3000** |
| expected normalized total（含 derived） | ~500 × 10 | **~5000** |

**Snapshot 子集策略（沿用 Phase 2）：**

- harvest QA 后识别 all-direct-failure 公司
- snapshot build **仅 clean subset**；排除 all-direct-failure
- 预期 usable 率目标：**≥95%**（Phase 2 为 94% with delisted in pool）

---

# 6. Gates

Live 执行前须全部满足：

| # | Gate | 说明 |
|---|------|------|
| 1 | Batch 500 universe YAML generated | `eval_companies_c_class_phase3_batch_500_001.yaml` |
| 2 | Dry-run harvest **PASS** | expected case matrix + command checklist |
| 3 | Output-root isolation ready | `--output-root` / harvest runner extension 已验证 |
| 4 | No overlap with 863 active universe | 0 codes from `already_in_c_class` |
| 5 | No overlap with Phase 2 smoke 200 | 0 codes from phase2 smoke YAML |
| 6 | No all-direct-failure caveat codes | 0 codes from excluded ledger |
| 7 | No delisted rows in main batch | `listing_status=delisted` count = 0 |
| 8 | No BSE rows | board ≠ bse |
| 9 | No manual review rows | requires_manual_review = false |
| 10 | Explicit approval before live | `--approve-phase3-batch-500-harvest`（待实现） |

**Planning gate（本轮）：**

```
phase3_batch_500_planning_gate = DESIGN_COMPLETE
```

---

# 7. Future Output Roots

| 产物 | 路径 |
|------|------|
| universe YAML | `lab/eval_companies_c_class_phase3_batch_500_001.yaml` |
| selection matrix | `outputs/validation/cninfo_c_class_phase3_batch_500_001_selection_matrix.csv` |
| selection summary | `outputs/validation/cninfo_c_class_phase3_batch_500_001_selection_summary.md` |
| harvest root | `outputs/harvest/cninfo_c_class/phase3_batch_500_001/` |
| harvest dry-run report | `outputs/validation/cninfo_c_class_phase3_batch_500_001_harvest_dryrun_report.csv` |
| harvest dry-run summary | `outputs/validation/cninfo_c_class_phase3_batch_500_001_harvest_dryrun_summary.md` |
| live harvest QA | `outputs/validation/cninfo_c_class_phase3_batch_500_001_live_harvest_qa_summary.md` |
| snapshot root | `outputs/snapshot/cninfo_c_class/phase3_batch_500_001_success_subset/` |

**隔离红线：**

- **不写入** `outputs/harvest/cninfo_c_class/` 主轨（863 normalized）
- **不写入** `outputs/snapshot/cninfo_c_class/full/`
- **不修改** raw / normalized / field_inventory

---

# 8. References

- [Phase 2 closure review](cninfo_c_class_phase2_smoke_closure_review.md)
- [Phase 3 readiness summary](../outputs/validation/cninfo_c_class_phase3_batch_readiness_summary.md)
- [candidate matrix](../outputs/validation/cninfo_c_class_phase3_batch_500_candidate_matrix.csv)
- [output design](cninfo_c_class_phase3_batch_500_output_design.md)
- [execution checklist](cninfo_c_class_phase3_batch_500_execution_checklist.md)
- [planning summary](../outputs/validation/cninfo_c_class_phase3_batch_500_planning_summary.md)

## 红线确认

- 未请求 CNINFO · 未 live · 未 harvest · 未 snapshot
- 未生成 batch YAML（本轮）
- 未入库 / MinIO / RAG / registry / verified
