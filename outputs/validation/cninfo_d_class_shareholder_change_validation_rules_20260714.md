# CNINFO D 类 shareholder_change — First-Slice Validation Rules（Offline）

_生成时间：2026-07-14_

> **性质：** offline first-slice **acceptance rules checklist** only · **CNINFO calls = 0** · **无 live** · **无 runner** · **无 claim approved** · **无 commit** · **无 push**
>
> **边界：** 本清单用于 **未来** dry-run / live / closure 离线验收对照 · **不** 自行判定 PASS · **不** 升级 gate · **不** 标记 verified / production_ready
>
> **配套：** [sample_prep](cninfo_d_class_shareholder_change_sample_prep_20260714.md) · [offline_evidence_map CSV](cninfo_d_class_shareholder_change_offline_evidence_map_20260714.csv) · [event_model CSV](cninfo_d_class_shareholder_change_event_model_20260714.csv)

---

## 1. Delta vs Prior Artifacts

| 维度 | schema_prep / event_model | prep refresh checklist | **本包** |
|------|---------------------------|------------------------|----------|
| 粒度 | 字段映射 · taxonomy | planning item ready/blocked | **可执行验收规则 VR-001–VR-042** |
| 用途 | 建模参考 | 人工 Level-2 前清点 | **first-slice 切片验收**（offline 对照 synthetic / future live） |
| 通过判定 | 无 | 无 | 每条规则含 **pass 条件** · **fail 类型** · **blocked 条件** |

---

## 2. Current Gate（unchanged）

```text
d_class_shareholder_change_next_component_planning_gate = READY_FOR_APPROVAL
approval_queue_status = WAITING_APPROVAL
shareholder_change_first_slice_validation_gate = NOT_APPLICABLE (no runner/live yet)
```

**本包不创建或升级 execution gate。**

---

## 3. Acceptance Scope

| 项 | 值 |
|----|-----|
| universe | DSC001–DSC005（sketch · 见 universe draft CSV） |
| query mode | `type_inc` only · `type=inc` + `tdate=2026-07-03` |
| endpoint | `shareholeder/detail`（拼写 **shareholeder** 保留） |
| acceptable threshold（future live） | **≥ 3/5** cases acceptable → `PASS_WITH_CAVEAT` · **不是 bare PASS** |
| evidence layer | metadata / structured-table only · 无 PDF/OCR/DB/MinIO/RAG |

---

## 4. Rule Categories Overview

| 类别 | 规则 ID 范围 | 说明 |
|------|-------------|------|
| A — Universe & Query | VR-001 – VR-008 | 宇宙 · 锚点 · 请求预算 · 排除项 |
| B — Raw Retrieval | VR-009 – VR-014 | CNINFO 响应形态 · 公司过滤 · 空态语义 |
| C — Field Mapping | VR-015 – VR-024 | raw → d_company_event → payload |
| D — Envelope & Quality | VR-025 – VR-032 | event_status · quality_status · freeze v1 |
| E — Lineage | VR-033 – VR-037 | raw_record · hash · query_params · lineage_status |
| F — Evidence Boundary | VR-038 – VR-040 | disclosure 隔离 · 排除案例 |
| G — Governance | VR-041 – VR-042 | gate · 禁止升级 claim |

---

## 5. Validation Rules Checklist

### A — Universe & Query Contract

| ID | 规则 | Pass 条件 | Fail 类型 | 状态 |
|----|------|-----------|-----------|------|
| VR-001 | universe 恰好 **5** 行 · case_id **DSC001–DSC005** | 行数=5 · ID 连续无缺口 | `universe_shape_error` | draft |
| VR-002 | 全案 `component=shareholder_change` · `first_slice_include=yes` | 字段一致 | `universe_field_error` | draft |
| VR-003 | 全案共享 `anchor_tdate=2026-07-03` · `query_type=inc` | 单一锚点 · 无 per-case 漂移 | `anchor_drift` | draft |
| VR-004 | **688671** · **301259** 不在 primary universe | exclude_flags 含两项 · 无对应行 | `excluded_case_leak` | draft |
| VR-005 | DSC001 使用 **独立 case_id** · 引用 DLC006 公司但 **非** DLC006R 代理 | case_id=DSC001 · company=000550 · 无 DLC006R 标记 | `case_id_collision` | draft |
| VR-006 | per-case 请求预算 **≤ 4** · total cap **≤ 20** | 计划请求 ≤ 预算 | `budget_exceeded` | draft |
| VR-007 | first-slice **仅** `type=inc` · **禁止** `type=dec` | query 无 `dec` · registry R012 合规 | `invalid_query_type` | draft |
| VR-008 | `type_desc` / decrease 模式 **不** 在 first-slice 启用 | 无 desc 模式请求 | `scope_expansion` | blocked |

### B — Raw Retrieval Semantics

| ID | 规则 | Pass 条件 | Fail 类型 | 状态 |
|----|------|-----------|-----------|------|
| VR-009 | HTTP 200 · `data.records` 路径可解析 | 结构有效或合法空列表 | `http_or_structure_failure` | draft |
| VR-010 | 公司过滤：`SECCODE` == universe `company_code` | 输出行仅含目标公司 | `company_filter_leak` | draft |
| VR-011 | found：`record_count ≥ 1` 且每行含 registry 8 字段骨架 | SECCODE·VARYDATE·F002V·F004N 存在 | `incomplete_raw_row` | draft |
| VR-012 | empty_but_valid：`record_count=0` 为 **合法** 结果（DSC005 及 mix 案） | `event_status=empty_but_valid` · 非自动 failed | `empty_treated_as_failure` | draft |
| VR-013 | **禁止** sole `captured_normal_candidate` 绑定单一稀疏 anchor | expectation mix 含 empty 路径 · 无全局 forced captured | `fragile_anchor_binding` | draft |
| VR-014 | DSC004 允许 found + `needs_review` · **禁止** 单独 fragile mix | `captured_normal_or_needs_review` 与混排案共存 | `dep004_mix_missing` | draft |

### C — Field Mapping（raw → structured）

| ID | 规则 | Pass 条件 | Fail 类型 | 状态 |
|----|------|-----------|-----------|------|
| VR-015 | SECCODE → `company_code` | 值相等 | `mapping_mismatch` | draft |
| VR-016 | VARYDATE → `event_date` / `change_date` / `event_time` | 三处日期一致（normalize 后） | `date_inconsistency` | draft |
| VR-017 | F002V → `shareholder_name` / `actor_name` | 非空（found 时） | `missing_actor` | draft |
| VR-018 | F004N → `change_amount` · unit=shares | 数值映射 · unit 正确 | `amount_mapping_error` | draft |
| VR-019 | F005N → `change_ratio` · nullable_if_missing | 缺失时 nullable · 不伪造 | `ratio_forced_fill` | draft |
| VR-020 | query `type=inc` → `event_subtype=increase` · `change_type=inc` | 由 query 派生 · **非** 标题推断 | `subtype_inference_error` | draft |
| VR-021 | `event_type` 固定 `shareholder_change` | 无 executive_shareholding 混入 | `wrong_event_type` | draft |
| VR-022 | `event_id` = hash(source_id, query_mode, company_code, event_date, F002V) | 稳定可复现 | `event_id_unstable` | draft |
| VR-023 | F007V → `primary_price` 仅当存在时设置 | optional · yuan_per_share | `price_forced_fill` | draft |
| VR-024 | SECNAME / DECLAREDATE 映射 recommended 字段 | 缺失不导致 fail（除非 freeze 冲突） | `recommended_field_warning` | draft |

### D — Envelope & Quality Status

| ID | 规则 | Pass 条件 | Fail 类型 | 状态 |
|----|------|-----------|-----------|------|
| VR-025 | found → `event_status=captured` | 与 record_count 一致 | `status_semantic_error` | draft |
| VR-026 | zero rows 控制案 → `event_status=empty_but_valid` | DSC005 及合法 empty mix | `empty_status_wrong` | draft |
| VR-027 | empty_but_valid → **无** `shareholder_change` payload 键 | 不伪造 shareholder_name/change_amount | `empty_payload_forge` | draft |
| VR-028 | freeze v1 required：`company_code`·`shareholder_name`·`change_type`·`change_amount`·`change_date`·`quality_status` | found 时齐全 | `freeze_required_missing` | draft |
| VR-029 | 信封与 payload `quality_status` 一致 | 双处同值 | `quality_status_split` | draft |
| VR-030 | `quality_status=pass` 仅当映射 confidence 足够 · DSC004 可为 `needs_review` | 符合 case expectation | `quality_overclaim` | draft |
| VR-031 | acceptable 计数：found 或 legal empty 或 needs_review（按 expectation） | ≥3/5 acceptable | `below_acceptable_threshold` | draft |
| VR-032 | execution gate 最高 **`PASS_WITH_CAVEAT`** · **不是** bare PASS | 无 PASS/verified 宣称 | `gate_overclaim` | draft |

### E — Lineage & Provenance

| ID | 规则 | Pass 条件 | Fail 类型 | 状态 |
|----|------|-----------|-----------|------|
| VR-033 | captured 行 **必须** 含 `lineage.raw_record_json` 完整对象 | registry `raw_record_required=true` | `lineage_missing_raw` | draft |
| VR-034 | `lineage.raw_record_hash` 与 raw 对象稳定 hash 一致 | 可复算匹配 | `hash_mismatch` | draft |
| VR-035 | `lineage.query_mode=type_inc` · `query_params` 含 `type`+`tdate` | 与请求一致 | `query_lineage_drift` | draft |
| VR-036 | `lineage.registry_source_id=shareholder_change` | 固定值 | `wrong_source_id` | draft |
| VR-037 | `lineage_status=discovered`（Phase1）· **禁止** `linked` | 无 B-class event_document_link | `linked_premature` | blocked |

### F — Evidence Boundary

| ID | 规则 | Pass 条件 | Fail 类型 | 状态 |
|----|------|-----------|-----------|------|
| VR-038 | disclosure PDF / 人工复核 **不得** 填入 F002V/F004N 等 structured 字段 | 仅 captured pipeline raw | `disclosure_promotion` | blocked |
| VR-039 | `separate_disclosure_lineage_only` **不得** promote 为 `captured_normal` | 无跨层升级 | `lineage_promotion` | blocked |
| VR-040 | 301259 / DLC006R **永久排除** · known-event **不重开** | 无 rerun 痕迹 | `closed_track_reopen` | blocked |

### G — Governance & Safety

| ID | 规则 | Pass 条件 | Fail 类型 | 状态 |
|----|------|-----------|-----------|------|
| VR-041 | 验收时 `shareholder_change_component_approved` 状态与授权范围一致 | 未批准则不执行 live | `unauthorized_execution` | blocked |
| VR-042 | 无 verified · production_ready · testing_stable_sample claim | 报告与 gate 无禁用词 | `governance_violation` | blocked |

---

## 6. Per-Case Expected Behavior Matrix（acceptance reference）

| case_id | expected_behavior | VR 重点子集 | acceptable 当 |
|---------|-------------------|-------------|---------------|
| DSC001 | captured_normal_or_empty_but_valid | VR-012·013·025·026 | found captured **或** legal empty |
| DSC002 | captured_normal_or_empty_but_valid | VR-012·013·025·026 | 同上 |
| DSC003 | captured_normal_or_empty_but_valid | VR-012·013·025·026 | 同上 |
| DSC004 | captured_normal_or_needs_review | VR-014·030 | found + pass **或** found + needs_review **或** legal empty（记 caveat） |
| DSC005 | empty_but_valid | VR-012·026·027 | zero rows + empty_but_valid · 无 payload |

**DEP004 / DBT002 教训：** 不得因 DSC004 needs_review 或 DSC005 empty 单独判定整片 failed · 须用 VR-031 阈值 + caveat ledger。

---

## 7. Offline Execution Procedure（future · blocked）

```text
1. 加载 universe sketch CSV + Tier-1 synthetic fixtures（若已实现）
2. 对每条 VR-001–VR-042 记录 pass/fail/block + evidence_artifact_path
3. 生成 outcome ledger（参照 equity_pledge live_outcome_ledger 列）
4. 汇总 acceptable count · 提议 gate（仅 Controller 可落档）
5. CNINFO=0 阶段：仅对照 synthetic + schema lint
```

**本包不执行上述流程。**

---

## 8. Blocked Until Level-2 Approval

| 动作 | 阻断 |
|------|------|
| 对 live snapshot 运行 VR-009–VR-034 | 无 runner/live approval |
| VR-008 type_desc 验收 | first-slice 单 inc 政策 |
| VR-037 linked lineage | Phase1 不实现 |
| VR-038–040 disclosure/排除 | 政策红线 · 仅人工可变更 |
| gate 落档为 PASS_WITH_CAVEAT | Controller only |

---

## 9. Safety Zeros

| 项 | 本包 |
|----|------|
| CNINFO calls | **0** |
| live / runner | **no** |
| gate upgrade | **no** |
| commit / push | **no** |
| rules executed against live data | **no** |

---

## 10. Summary Block

```text
phase = shareholder_change_validation_rules_20260714
rule_count = 42 (VR-001 to VR-042)
categories = universe + retrieval + mapping + envelope + lineage + boundary + governance
acceptable_threshold = >=3/5 PASS_WITH_CAVEAT (future live only)
current_gate = READY_FOR_APPROVAL
cninfo_calls = 0
```
