# CNINFO D 类 executive_shareholding — First-Slice Validation Rules（Offline）

_生成时间：2026-07-15_

> **性质：** offline first-slice **acceptance rules checklist** · 自 Run 15 stub **promote** · **CNINFO calls = 0** · **无 live** · **无 runner** · **无 claim approved** · **无 commit** · **无 push**
>
> **任务 ID：** D-R16-01
>
> **边界：** 本清单用于 **未来** dry-run / live / closure 离线验收对照 · **不** 自行判定 PASS · **不** 升级 gate · **不** 标记 verified / production_ready
>
> **配套：** [sample_prep](cninfo_d_class_executive_shareholding_sample_prep_20260715.md) · [universe lock](cninfo_d_class_executive_shareholding_first_slice_universe_lock_20260715.csv) · [approval package](cninfo_d_class_executive_shareholding_first_slice_approval_package_20260715.md)

---

## 1. Delta vs Run 15 Stub

| 维度 | Run 15 stub（ESH-STUB-01） | **本包（D-R16-01）** |
|------|---------------------------|----------------------|
| 粒度 | prep checklist 一句 stub | **可执行验收规则 VR-001–VR-042** |
| 状态 | `stub_only` · full VR deferred | **full checklist promoted** · 仍为 offline draft |
| 用途 | 规划清点 | first-slice 切片验收（offline 对照 Tier-0 / future Tier-1 / future live） |

---

## 2. Current Gate（unchanged）

```text
d_class_executive_shareholding_next_component_planning_gate = READY_FOR_APPROVAL
executive_shareholding_component_approved = false
executive_shareholding_first_slice_validation_gate = NOT_APPLICABLE (no runner/live yet)
```

**本包不创建或升级 execution / component gate。** `READY_FOR_APPROVAL` ≠ approved。

---

## 3. Acceptance Scope

| 项 | 值 |
|----|-----|
| universe | DES001–DES005（**locked** · 见 universe lock CSV） |
| query mode | `timeMark=oneMonth` + `varyType=b` only（first-slice 单模式） |
| endpoint | `https://www.cninfo.com.cn/data20/leader/detail` |
| acceptable threshold（future live） | **≥ 3/5** cases acceptable → `PASS_WITH_CAVEAT` · **不是 bare PASS** |
| evidence layer | metadata / structured-table only · 无 PDF/OCR/DB/MinIO/RAG |
| Tier-0 cite only | **DC006**（synthetic） · **DLC007**（calibrated needs_review） |

---

## 4. Rule Categories Overview

| 类别 | 规则 ID 范围 | 说明 |
|------|-------------|------|
| A — Universe & Query | VR-001 – VR-008 | 宇宙 · 锚点 · 请求预算 · 排除项 |
| B — Raw Retrieval | VR-009 – VR-014 | CNINFO 响应形态 · 公司过滤 · 空态语义 |
| C — Field Mapping | VR-015 – VR-024 | raw → d_company_event → executive_shareholding payload |
| D — Envelope & Quality | VR-025 – VR-032 | event_status · quality_status · freeze v1 |
| E — Lineage | VR-033 – VR-037 | raw_record · hash · query_params · lineage_status |
| F — Evidence Boundary | VR-038 – VR-040 | disclosure 隔离 · 排除案例 · 不重开 closed tracks |
| G — Governance | VR-041 – VR-042 | gate · 禁止升级 claim |

---

## 5. Validation Rules Checklist

### A — Universe & Query Contract

| ID | 规则 | Pass 条件 | Fail 类型 | 状态 |
|----|------|-----------|-----------|------|
| VR-001 | universe 恰好 **5** 行 · case_id **DES001–DES005** | 行数=5 · ID 连续无缺口 | `universe_shape_error` | draft |
| VR-002 | 全案 `component=executive_shareholding` · `first_slice_include=yes` | 字段一致 | `universe_field_error` | draft |
| VR-003 | 全案共享 `time_mark=oneMonth` · `vary_type=b` | 单一查询契约 · 无 per-case 漂移 | `anchor_drift` | draft |
| VR-004 | **688671** · **301259** 不在 primary universe | exclude_flags 含两项 · 无对应行 | `excluded_case_leak` | draft |
| VR-005 | DES001 使用 **独立 case_id** · 引用 DLC007 公司但 **非** DDS004 代理 · **非** forced pass | case_id=DES001 · company=002415 · 无 DDS004/DLC006R 标记 | `case_id_collision` | draft |
| VR-006 | per-case 请求预算 **≤ 4** · total cap **≤ 20** | 计划请求 ≤ 预算 | `budget_exceeded` | draft |
| VR-007 | first-slice **仅** `timeMark=oneMonth` + `varyType=b` · **禁止** 多 timeMark 探测 | query 无 threeMonth/oneYear/s 扩展 | `invalid_query_mode` | draft |
| VR-008 | `varyType=s` / 其他 timeMark 组合 **不** 在 first-slice 启用 | 无非默认模式请求 | `scope_expansion` | blocked |

### B — Raw Retrieval Semantics

| ID | 规则 | Pass 条件 | Fail 类型 | 状态 |
|----|------|-----------|-----------|------|
| VR-009 | HTTP 200 · `data.records` 路径可解析 | 结构有效或合法空列表 | `http_or_structure_failure` | draft |
| VR-010 | 公司过滤：`SECCODE` == universe `company_code` | 输出行仅含目标公司 | `company_filter_leak` | draft |
| VR-011 | found：`record_count ≥ 1` 且每行含 registry 核心字段骨架 | SECCODE·ENDDATE·HUMANNAME·F006N 存在 | `incomplete_raw_row` | draft |
| VR-012 | empty_but_valid：`record_count=0` 为 **合法** 结果（DES005 及 mix 案） | `event_status=empty_but_valid` · 非自动 failed | `empty_treated_as_failure` | draft |
| VR-013 | **禁止** sole `captured_normal_candidate` 绑定单一可能稀疏 window | expectation mix 含 empty 路径 · 无全局 forced captured | `fragile_anchor_binding` | draft |
| VR-014 | DES001 允许 found + `needs_review` · **禁止** 单独 fragile mix | `captured_normal_or_needs_review` 与混排案共存 | `dep004_mix_missing` | draft |

### C — Field Mapping（raw → structured）

| ID | 规则 | Pass 条件 | Fail 类型 | 状态 |
|----|------|-----------|-----------|------|
| VR-015 | SECCODE → `company_code` | 值相等 | `mapping_mismatch` | draft |
| VR-016 | ENDDATE → `event_date` / `change_date` / `event_time` | 三处日期一致（normalize 后） | `date_inconsistency` | draft |
| VR-017 | HUMANNAME → `executive_name` | 非空（found 时） | `missing_executive` | draft |
| VR-018 | F006N → `change_amount` · unit=shares | 数值映射 · unit 正确 | `amount_mapping_error` | draft |
| VR-019 | F002V → `position` · nullable_if_missing / medium confidence | 缺失或歧义时允许 needs_review · 不伪造 | `position_forced_fill` | draft |
| VR-020 | query `varyType=b` → `change_type` 由 query/mode 派生 · **非** 标题推断 | 与 registry `event_subtype_mode` 一致 | `subtype_inference_error` | draft |
| VR-021 | `event_type` 固定 `executive_shareholding`（freeze）/ `executive_shareholding_change`（registry mapping）语义一致 | 无 shareholder_change 混入 | `wrong_event_type` | draft |
| VR-022 | `event_id` = hash(source_id, query_mode, company_code, event_date, HUMANNAME) | 稳定可复现 | `event_id_unstable` | draft |
| VR-023 | F005N / F008N → amount/price 仅当存在且 confidence 足够 | optional · uncertain F005N 不得 forced fill | `amount_price_forced_fill` | draft |
| VR-024 | SECNAME / F001V / F003V / F010V 映射 recommended 字段 | 缺失不导致 fail（除非 freeze 冲突） | `recommended_field_warning` | draft |

### D — Envelope & Quality Status

| ID | 规则 | Pass 条件 | Fail 类型 | 状态 |
|----|------|-----------|-----------|------|
| VR-025 | found → `event_status=captured` | 与 record_count 一致 | `status_semantic_error` | draft |
| VR-026 | zero rows 控制案 → `event_status=empty_but_valid` | DES005 及合法 empty mix | `empty_status_wrong` | draft |
| VR-027 | empty_but_valid → **无** `executive_shareholding` payload 键 | 不伪造 executive_name/change_amount | `empty_payload_forge` | draft |
| VR-028 | freeze v1 required：`company_code`·`executive_name`·`change_type`·`change_amount`·`change_date`·`quality_status` | found 时齐全 | `freeze_required_missing` | draft |
| VR-029 | 信封与 payload `quality_status` 一致 | 双处同值 | `quality_status_split` | draft |
| VR-030 | `quality_status=pass` 仅当映射 confidence 足够 · DES001 可为 `needs_review`（DLC007 先例） | 符合 case expectation · **不** forced pass | `quality_overclaim` | draft |
| VR-031 | acceptable 计数：found 或 legal empty 或 needs_review（按 expectation） | ≥3/5 acceptable | `below_acceptable_threshold` | draft |
| VR-032 | execution gate 最高 **`PASS_WITH_CAVEAT`** · **不是** bare PASS | 无 PASS/verified 宣称 | `gate_overclaim` | draft |

### E — Lineage & Provenance

| ID | 规则 | Pass 条件 | Fail 类型 | 状态 |
|----|------|-----------|-----------|------|
| VR-033 | captured 行 **必须** 含 `lineage.raw_record_json` 完整对象 | registry `raw_record_required=true` | `lineage_missing_raw` | draft |
| VR-034 | `lineage.raw_record_hash` 与 raw 对象稳定 hash 一致 | 可复算匹配 | `hash_mismatch` | draft |
| VR-035 | `lineage.query_mode` 反映 timeMark/varyType · `query_params` 含 `timeMark`+`varyType` | 与请求一致 | `query_lineage_drift` | draft |
| VR-036 | `lineage.registry_source_id=executive_shareholding` | 固定值 | `wrong_source_id` | draft |
| VR-037 | `lineage_status=discovered` 或 `needs_review`（Phase1）· **禁止** `linked` | 无 B-class event_document_link | `linked_premature` | blocked |

### F — Evidence Boundary

| ID | 规则 | Pass 条件 | Fail 类型 | 状态 |
|----|------|-----------|-----------|------|
| VR-038 | disclosure PDF / 人工复核 **不得** 填入 HUMANNAME/F006N 等 structured 字段 | 仅 captured pipeline raw | `disclosure_promotion` | blocked |
| VR-039 | `separate_disclosure_lineage_only` **不得** promote 为 `captured_normal` | 无跨层升级 | `lineage_promotion` | blocked |
| VR-040 | 301259 / DLC006R / shareholder_change DSC 轨 **永久排除或不得重开** · known-event **不重开** | 无 rerun 痕迹 | `closed_track_reopen` | blocked |

### G — Governance & Safety

| ID | 规则 | Pass 条件 | Fail 类型 | 状态 |
|----|------|-----------|-----------|------|
| VR-041 | 验收时 `executive_shareholding_component_approved` 状态与授权范围一致 | 未批准则不执行 live | `unauthorized_execution` | blocked |
| VR-042 | 无 verified · production_ready · testing_stable_sample claim | 报告与 gate 无禁用词 | `governance_violation` | blocked |

---

## 6. Per-Case Expected Behavior Matrix（acceptance reference）

| case_id | expected_behavior | VR 重点子集 | acceptable 当 |
|---------|-------------------|-------------|---------------|
| DES001 | captured_normal_or_needs_review | VR-014·030 · DLC007 先例 | found + pass **或** found + needs_review **或** legal empty（记 caveat） |
| DES002 | captured_normal_or_empty_but_valid | VR-012·013·025·026 | found captured **或** legal empty |
| DES003 | captured_normal_or_empty_but_valid | VR-012·013·025·026 | 同上 |
| DES004 | captured_normal_or_empty_but_valid | VR-012·013·025·026 | 同上 |
| DES005 | empty_but_valid | VR-012·026·027 | zero rows + empty_but_valid · 无 payload |

**DEP004 / DBT002 / DSC004 / DDS004 教训：** 不得因 DES001 needs_review 或 DES005 empty 单独判定整片 failed · 须用 VR-031 阈值 + caveat ledger · **禁止** DES001 forced pass。

---

## 7. Offline Execution Procedure（future · blocked）

```text
1. 加载 universe lock CSV + Tier-0（DC006/DLC007 cite）+ Tier-1 synthetic（若已实现）
2. 对每条 VR-001–VR-042 记录 pass/fail/block + evidence_artifact_path
3. 生成 outcome ledger（参照 prior first-slice live_outcome_ledger 列）
4. 汇总 acceptable count · 提议 gate（仅 Controller 可落档）
5. CNINFO=0 阶段：仅对照 synthetic + schema lint
```

**本包不执行上述流程。**

---

## 8. Blocked Until Component / Later Approvals

| 动作 | 阻断 |
|------|------|
| 对 live snapshot 运行 VR-009–VR-034 | 无 runner/live approval · `component_approved=false` |
| VR-008 非默认 timeMark/varyType 验收 | first-slice 单模式政策 |
| VR-037 linked lineage | Phase1 不实现 |
| VR-038–040 disclosure/排除 | 政策红线 · 仅人工可变更 |
| gate 落档为 PASS_WITH_CAVEAT | Controller only |

---

## 9. Safety Zeros

| 项 | 本包 |
|----|------|
| CNINFO calls | **0** |
| live / runner | **no** |
| gate upgrade | **no**（保持 `READY_FOR_APPROVAL`） |
| commit / push | **no** |
| rules executed against live data | **no** |
| component_approved | **false** |

---

## 10. Summary Block

```text
task_id = D-R16-01
phase = executive_shareholding_validation_rules_20260715
rule_count = 42 (VR-001 to VR-042)
categories = universe + retrieval + mapping + envelope + lineage + boundary + governance
acceptable_threshold = >=3/5 PASS_WITH_CAVEAT (future live only)
current_gate = READY_FOR_APPROVAL
component_approved = false
cninfo_calls = 0
verified = false
production_ready = false
```
