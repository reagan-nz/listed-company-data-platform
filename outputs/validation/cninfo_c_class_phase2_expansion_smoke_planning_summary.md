# CNINFO C-Class Phase 2 Expansion Smoke Planning Summary

_生成时间：2026-07-08_

> Phase 2 expansion smoke 规划摘要。**仅规划** · **execution not started** · **无 smoke YAML**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

---

# Candidate Pool

| 项 | 值 |
|----|-----|
| **eligible classification** | matched_active |
| **eligible count** | **4647** |
| **筛选条件** | full_market_active_candidate · candidate_supported · not_built · manual=false |

### 主池分布（4647）

| 维度 | 分布 |
|------|------|
| exchange | SZSE 2612 · SSE 2031 · BSE 4（smoke 排除） |
| board | sse_main 1544 · szse_main 1406 · chinext 1206 · star 487 · bse 4 |
| listing_status | listed 4492 · delisted 155 |

---

# Recommended Smoke Size

| 推荐 | 值 |
|------|-----|
| **Option A** | 100 |
| **Option B（推荐）** | **200** |

**理由：** 与 stable 200 经验对齐 · 分层覆盖足够 · 风险可控 · HTTP **1400** cases

---

# Excluded Rows

| classification | count | 原因 |
|----------------|-------|------|
| already_in_c_class | 863 | 863 已完成 |
| matched_hold | 26 | hold 侧轨 |
| matched_bse_supported_candidate | 320 | BSE 920 独立 gate |
| matched_bse_legacy_hold | 242 | legacy 侧轨 |
| identity_conflict | 10 | 冲突双行 |
| needs_manual_review | 16 | 人工队列 |
| not_found_in_cninfo | 0 | 未解析 |

**合计排除：1477**（不含主池内 BSE board 4 行附加过滤）

---

# Sampling Strategy

- 分层：exchange · board · listing_status · security_type（缺失则回退）
- 回退：company_code 前缀 · source 分布 · 固定 seed
- non-BSE smoke：排除 board=bse

---

# Gate

**`phase2_expansion_smoke_planning_gate = DESIGN_COMPLETE`**

| 项 | 状态 |
|----|------|
| planning | **complete** |
| smoke YAML | **not generated** |
| harvest / snapshot | **not started** |
| registry implementation | **deferred** |

---

# Execution Status

**Execution not started.**

---

# 产物索引

| 文档 | 路径 |
|------|------|
| Smoke plan | [cninfo_c_class_phase2_expansion_smoke_plan.md](../../plans/cninfo_c_class_phase2_expansion_smoke_plan.md) |
| Candidate matrix | [cninfo_c_class_phase2_expansion_smoke_candidate_matrix.csv](cninfo_c_class_phase2_expansion_smoke_candidate_matrix.csv) |
| Output design | [cninfo_c_class_phase2_smoke_universe_output_design.md](../../plans/cninfo_c_class_phase2_smoke_universe_output_design.md) |
| Execution checklist | [cninfo_c_class_phase2_expansion_smoke_execution_checklist.md](../../plans/cninfo_c_class_phase2_expansion_smoke_execution_checklist.md) |
| Refreshed candidate | [cninfo_c_class_company_registry_candidate_refreshed.csv](cninfo_c_class_company_registry_candidate_refreshed.csv) |

---

# Recommended Next Task

**Build Phase 2 smoke universe selection script dry-run** (`lab/build_cninfo_c_class_phase2_smoke_universe.py`)

（生成 selection matrix + summary · **可选** `--write` YAML · **非 harvest**）

---

# 红线确认

本轮 **未执行：**

- smoke YAML 生成
- CNINFO / live / harvest / snapshot
- production registry / DB
- identity merge
- raw / normalized / field_inventory 修改
- verified / testing_stable_sample
