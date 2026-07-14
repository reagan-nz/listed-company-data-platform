# CNINFO A 类 — Attribute Gap Ledger

_生成时间：2026-07-14_

> **offline analysis** · **CNINFO = 0** · **NOT verified** · **NOT production_ready** · **NOT APPROVED live**

---

## Mission Context

**A 类 mission objective v2：** 全市场上市公司基础信息覆盖（company profile · basic attributes · static company data）。

**与 company-code lineage 分离：** 本台账仅统计**属性维度**已知/未知状态；**486** effective company codes 不等于 attribute completeness 已达成。

**治理状态（引用）：** slice1 committed `4118974` · merge `71a83c1` · gate **`PASS_WITH_CAVEAT`** · post-integration **HOLD** · unresolved **6** retained（见 [coverage gap analysis](cninfo_a_class_mission_coverage_gap_analysis_20260714.md)）。

---

## Known vs Unknown — Attribute Dimensions

| 属性域 | 状态 | 证据摘要 |
|--------|------|----------|
| **company_code lineage（case 槽位）** | **known（partial）** | cumulative **486/500** effective · **14** unresolved side-track（scale-200 **8** + slice1 **6**） |
| **full-market universe 分母** | **unknown** | 全市场上市公司总数未冻结为正式分母 · 无法计算 mission 完成百分比 |
| **Phase1 freeze catalog — report_document required** | **partial** | [field catalog](cninfo_a_class_phase1_freeze_v1_field_catalog.csv) 已冻结 **13** 个 required 字段 · 未对 **486** effective cases 做 catalog completeness 评分 |
| **Phase1 freeze catalog — report_document recommended** | **partial** | catalog 含 org_id · company_name · adjunct_url 等 recommended · 填充率未聚合 |
| **report_period_snapshot 覆盖** | **partial** | 每 case 有 expected_period / report_type 规划 · 未产出跨 cohort 的 snapshot 填充矩阵 |
| **document_lineage 契约字段** | **partial** | Phase1 固定 storage_status=not_attempted · lineage 元数据在 live 产物中存在但未与 catalog 对账 |
| **matching_logic v2 检索属性** | **partial** | scale-200 + slice1 均用 v2 · unresolved **6** 中 **5** not_found · **1** network_error（见 [unresolved6 packaging](cninfo_a_class_unresolved6_offline_packaging_20260714.csv)） |
| **orgId 解析属性** | **partial** | slice1 unresolved 模式含 records=0 / orgId network_error · 未对 effective **486** 做 orgId 填充率统计 |
| **report_type × report_period 组合覆盖** | **partial** | slice1 universe 含 annual / quarterly / semi 混合 · 无按 report_type 分层的 attribute gap 表 |
| **company profile / static basic attributes** | **unknown** | mission objective v2 要求 company profile · Era D A-class 当前轨为 **report metadata discovery only** · 与 C-class F017V 等 static profile 字段无交叉评分 |
| **attribute catalog completeness score** | **unknown** | controller progress baseline · coverage gap analysis 均标 **UNKNOWN** |
| **PDF / download / parse 派生属性** | **known（out of scope）** | Phase1 catalog 将 download_time · file_hash 等标为 frozen_future · A-class Era D 明确 metadata-only |

---

## Gap vs Company-Code Lineage

| 指标 | company-code lineage | attribute completeness |
|------|---------------------|------------------------|
| 当前信号 | **486** effective codes | **未评分** |
| 分母 | staged ~500 case slots | Phase1 catalog + mission v2 static attributes（分母未冻结） |
| unresolved 影响 | **14** cases 不计入 effective | 6 案已有 failure_class · 属性缺失模式可离线审计 · 8 案 scale-200 side-track 未纳入本包 |
| mission 解读 | staged path **97.2%** | full-market attribute mission **不可宣称进展** |

---

## Missing Field Investigation Plan（offline only）

以下步骤**不调用 CNINFO** · **不 live** · **不修改 protected roots**。

### Phase A — Catalog 对账基线（优先）

| 步骤 | 动作 | 产出 |
|------|------|------|
| A1 | 从 [phase1 field catalog](cninfo_a_class_phase1_freeze_v1_field_catalog.csv) 导出 required / recommended / future 分组清单 | attribute_field_groups.csv（规划） |
| A2 | 对 scale-200 + slice1 **effective accepted ledgers** 做字段存在性抽样（读取已有 live report CSV · 不读 bulk raw_metadata 亦可先跑） | per-field presence rate draft |
| A3 | 将 **14** unresolved cases 的 failure_class 映射到 catalog 缺口类型（not_found → document_id null · network → retrieval_time only 等） | unresolved_attribute_pattern.csv（规划） |

### Phase B — Unresolved-6 属性审计（本包前置产物延伸）

| 步骤 | 动作 | 产出 |
|------|------|------|
| B1 | 沿用 [unresolved6 packaging](cninfo_a_class_unresolved6_offline_packaging_20260714.csv) · 对 **6** 案做 offline raw_metadata orgId / records / matching 审计 | triage notes（不 live retry） |
| B2 | 区分 not_found_or_matching_miss（**5**）vs network_or_empty_response（**1**）的属性可恢复性 | disposition 不变 · `live_needed=no` |

### Phase C — Mission v2 Static Attribute 边界

| 步骤 | 动作 | 产出 |
|------|------|------|
| C1 | 对照 [mission objective v2](../../plans/controller_mission_objective_v2.md) A-class 段落 · 明确 Era D metadata-only 与 company profile static 的分工 | static_vs_metadata_boundary.md（规划） |
| C2 | 引用 C-class [company_profile_text](cninfo_c_class_final_field_catalog.csv) 等字段 · 标记 A-track **not_in_scope** vs **future_cross_track** | cross_track_attribute_map draft |

### Phase D — 全市场分母与 slice2 衔接

| 步骤 | 动作 | 产出 |
|------|------|------|
| D1 | 冻结 non-BSE 候选池分母引用：[889 pool](../../lab/eval_companies_c_class_smoke_1000_non_bse_candidate.yaml) | denominator_reference row |
| D2 | 计算 A cumulative **486** codes ∩ 889 pool 的离线占比（**不等同** verified coverage） | pool_coverage_ratio draft |
| D3 | 与 [slice2 offline prep](cninfo_a_class_next_scale_slice2_offline_prep_20260714.md) 联动 · slice2 新 codes 纳入 attribute baseline 扩展计划 | slice2_attribute_baseline_hook |

---

## Blocked Investigation（需 live · 本 run 禁止）

| 动作 | 阻断原因 |
|------|----------|
| 对 unresolved 6 / scale-200 8 发起 CNINFO retry | post-integration **HOLD** · `live_needed=no` |
| 拉取 F10 / company basic profile endpoint | 无 A-class live 授权 · 非 Era D metadata 轨 |
| 宣称 attribute_coverage 百分比 | 分母与 scoring rubric 均未冻结 |

---

## Evidence Paths

| 文档 | 路径 |
|------|------|
| Coverage gap analysis | [cninfo_a_class_mission_coverage_gap_analysis_20260714.md](cninfo_a_class_mission_coverage_gap_analysis_20260714.md) |
| Unresolved-6 packaging | [cninfo_a_class_unresolved6_offline_packaging_20260714.csv](cninfo_a_class_unresolved6_offline_packaging_20260714.csv) |
| Phase1 field catalog | [cninfo_a_class_phase1_freeze_v1_field_catalog.csv](cninfo_a_class_phase1_freeze_v1_field_catalog.csv) |
| Cumulative lineage | [cninfo_a_class_erad_next_scale_slice1_cumulative_lineage_summary.md](cninfo_a_class_erad_next_scale_slice1_cumulative_lineage_summary.md) |
| Attribute gap skeleton | [cninfo_a_class_attribute_gap_skeleton_20260714.csv](cninfo_a_class_attribute_gap_skeleton_20260714.csv) |
| Slice2 prep | [cninfo_a_class_next_scale_slice2_offline_prep_20260714.md](cninfo_a_class_next_scale_slice2_offline_prep_20260714.md) |
| CURRENT_STATUS | [CURRENT_STATUS.md](../../CURRENT_STATUS.md) |
| PROJECT_CONTROL A | [PROJECT_CONTROL.md](../../PROJECT_CONTROL.md) §A-class |

---

## Gate

```text
attribute_gap_ledger_gate = READY_FOR_CONTROLLER_REVIEW
```

**CNINFO（本包）：0** · **live：NOT APPROVED** · **verified：NOT verified** · **production_ready：NOT production_ready**
