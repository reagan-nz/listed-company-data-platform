# CNINFO C-Class Registry Candidate Refresh Planning Summary

_生成时间：2026-07-08_

> Phase 1 registry candidate refresh 规划摘要。**仅规划** · **execution not started** · **无 refreshed CSV**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

---

# Current State

| 项 | 状态 |
|----|------|
| Phase 0 reconciliation | **完成** · 6124 行 · gate **PASS_WITH_CAVEAT** |
| registry candidate draft | **6124** 行 |
| identity decision ledger | **267** 条 |
| Phase 1 refresh planning | **完成（本轮）** |
| refreshed candidate CSV | **未生成** |
| registry implementation | **deferred** |

---

# Main Result

**6124 candidates can be assigned refresh actions.**

| classification | count | refresh_action |
|----------------|-------|----------------|
| matched_active | 4647 | full_market_active_candidate |
| already_in_c_class | 863 | preserve_high_confidence |
| matched_hold | 26 | preserve_hold |
| matched_bse_supported_candidate | 320 | bse_supported_candidate |
| matched_bse_legacy_hold | 242 | preserve_legacy_hold |
| identity_conflict | 10 | conflict_review_required |
| needs_manual_review | 16 | manual_review_required |
| not_found_in_cninfo | 0 | exclude_unresolved |

**扩展池粗估（可进入未来 smoke）：** matched_active **4647** + BSE 920 **320** = **4967**（扣除 conflict/manual 后须 manifest 过滤）

---

# Blockers

| # | Blocker | count | 阻塞范围 |
|---|---------|-------|----------|
| 1 | **identity_conflict** | 10 | 自动扩展池 |
| 2 | **needs_manual_review** | 16 | 自动扩展池 |
| 3 | **BSE legacy** | 242 | 主 harvest gate |
| 4 | **registry implementation** | — | Layer 2 入库（不阻塞 refresh 脚本） |

**非阻塞：** hold 26（已侧轨）· already_in_c_class 863（已完成）

---

# Refresh Design Summary

| 维度 | 设计 |
|------|------|
| base 字段 | 24 registry 字段保留 |
| 扩展字段 | reconciliation_classification · refresh_action · refresh_confidence · requires_manual_review · lineage_note |
| confidence | high(863) · medium(hold/BSE) · low(active) · review(conflict/manual) |
| 未来脚本 | `lab/refresh_cninfo_c_class_company_registry_candidate.py` |
| 安全 | default dry-run · `--write` 才 emit |

---

# Gate

**`registry_candidate_refresh_planning_gate = DESIGN_COMPLETE`**

| 项 | 值 |
|----|-----|
| planning | **complete** |
| refresh script | **not implemented** |
| refreshed CSV | **not generated** |
| harvest/snapshot expansion | **not started** |

---

# 产物索引

| 文档 | 路径 |
|------|------|
| Refresh plan | [cninfo_c_class_registry_candidate_refresh_plan.md](../../plans/cninfo_c_class_registry_candidate_refresh_plan.md) |
| Action matrix | [cninfo_c_class_registry_candidate_refresh_action_matrix.csv](cninfo_c_class_registry_candidate_refresh_action_matrix.csv) |
| Execution plan | [cninfo_c_class_registry_candidate_refresh_execution_plan.md](../../plans/cninfo_c_class_registry_candidate_refresh_execution_plan.md) |
| Phase 0 result | [cninfo_c_class_full_market_universe_reconciliation_result.csv](cninfo_c_class_full_market_universe_reconciliation_result.csv) |

---

# Recommended Next Task

**Implement Phase 1 refresh script dry-run** (`lab/refresh_cninfo_c_class_company_registry_candidate.py`)

（非 harvest · 非 refreshed CSV 写入除非 `--write` 批准 · 非 registry implementation）

---

# 红线确认

本轮 **未执行：**

- refreshed candidate 生成
- CNINFO / live / harvest / snapshot
- registry implementation / DB
- identity merge
- raw / normalized / field_inventory 修改
- verified / testing_stable_sample
