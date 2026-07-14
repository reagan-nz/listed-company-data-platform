# CNINFO D 类 shareholder_change — Tier-1 Fixture VR Validation（Offline）

_生成时间：2026-07-14_

> **性质：** offline Tier-1 synthetic fixture 验收 · **CNINFO calls = 0** · **无 live** · **无 runner** · **无 commit** · **无 push**
>
> **任务 ID：** D-GEN-20260714-07
>
> **边界：** 仅对照 Tier-1 fixtures vs VR-001–VR-042 · **不** 升级 execution gate · **不** 标记 verified / production_ready

---

## 1. Citations

| 引用 | 路径 | 角色 |
|------|------|------|
| approval package | [cninfo_d_class_shareholder_change_first_slice_approval_package_20260714.md](cninfo_d_class_shareholder_change_first_slice_approval_package_20260714.md) | AQ-D-SC 组件批准 · universe lock · Tier-1 路径 |
| validation rules | [cninfo_d_class_shareholder_change_validation_rules_20260714.md](cninfo_d_class_shareholder_change_validation_rules_20260714.md) | VR-001–VR-042 验收规则 |
| universe lock | [cninfo_d_class_shareholder_change_first_slice_universe_lock_20260714.csv](cninfo_d_class_shareholder_change_first_slice_universe_lock_20260714.csv) | DSC001–DSC005 锁定宇宙 |
| evidence map | [cninfo_d_class_shareholder_change_offline_evidence_map_20260714.csv](cninfo_d_class_shareholder_change_offline_evidence_map_20260714.csv) | raw 字段 → artifact pattern |
| sample prep | [cninfo_d_class_shareholder_change_sample_prep_20260714.md](cninfo_d_class_shareholder_change_sample_prep_20260714.md) | Tier-1 fixture 规格 |

---

## 2. Scope & Inputs

| 项 | 值 |
|----|-----|
| fixture root | `fixtures/d_class/shareholder_change_first_slice/` |
| fixture count | **8** JSON（DSC001–003 双态 found/empty · DSC004 needs_review · DSC005 empty_but_valid） |
| rule set | VR-001 – VR-042（42 条） |
| validation layer | Tier-1 synthetic envelope + lineage · **非** Tier-2 live snapshot |
| CNINFO calls | **0** |

---

## 3. Universe Lock Rollup（VR-001 – VR-008）

| VR | 规则 | 结果 | 证据 |
|----|------|------|------|
| VR-001 | universe 5 rows DSC001-DSC005 | **pass** | universe_lock CSV |
| VR-002 | component=shareholder_change first_slice_include=yes | **pass** | universe_lock CSV |
| VR-003 | anchor_tdate=2026-07-03 query_type=inc | **pass** | all fixtures query_params type=inc tdate=2026-07-03 |
| VR-004 | 688671/301259 excluded | **pass** | universe_lock CSV |
| VR-005 | DSC001 distinct case_id not DLC006R | **pass** | universe_lock CSV |
| VR-006 | per-case budget<=4 total<=20 | **pass** | universe_lock CSV |
| VR-007 | type=inc only | **pass** | all fixtures query_params type=inc tdate=2026-07-03 |
| VR-008 | type_desc not enabled (blocked) | **na** | blocked · first-slice inc-only policy |

---

## 4. Per-Fixture vs VR Matrix

### 4.1 `DSC001_empty.json`

| 项 | 值 |
|----|-----|
| case_id | DSC001 |
| scenario | empty_but_valid |
| company_code | 000550 |
| event_status | empty_but_valid |
| quality_status | pass |
| cninfo_called | False |

| VR | 规则 | 结果 | 备注 |
|----|------|------|------|
| VR-001 | universe 5 rows DSC001-DSC005 | **na** | universe_lock rollup §3 |
| VR-002 | component=shareholder_change first_slice_include=yes | **na** | universe_lock rollup §3 |
| VR-003 | anchor_tdate=2026-07-03 query_type=inc | **pass** |  |
| VR-004 | 688671/301259 excluded | **na** | universe_lock rollup §3 |
| VR-005 | DSC001 distinct case_id not DLC006R | **na** | universe_lock rollup §3 |
| VR-006 | per-case budget<=4 total<=20 | **na** | universe_lock rollup §3 |
| VR-007 | type=inc only | **pass** |  |
| VR-008 | type_desc not enabled (blocked) | **na** | blocked |
| VR-009 | HTTP 200 data.records | **na** | Tier-1 synthetic; no HTTP wrapper |
| VR-010 | SECCODE company filter | **na** |  |
| VR-011 | found 8-field skeleton | **na** |  |
| VR-012 | empty_but_valid legal | **pass** |  |
| VR-013 | no sole captured_normal_candidate | **pass** | portfolio dual-variant mix |
| VR-014 | DSC004 needs_review mix | **na** |  |
| VR-015 | SECCODE->company_code | **na** |  |
| VR-016 | VARYDATE date consistency | **na** |  |
| VR-017 | F002V->shareholder_name | **na** |  |
| VR-018 | F004N->change_amount | **na** |  |
| VR-019 | F005N nullable | **na** |  |
| VR-020 | inc->change_type=inc | **na** |  |
| VR-021 | event_type=shareholder_change | **na** |  |
| VR-022 | event_id stable | **na** |  |
| VR-023 | F007V optional price | **na** |  |
| VR-024 | SECNAME/DECLAREDATE recommended | **na** |  |
| VR-025 | found event_status=captured | **na** |  |
| VR-026 | empty event_status=empty_but_valid | **pass** |  |
| VR-027 | empty no payload forge | **pass** |  |
| VR-028 | freeze v1 required fields | **na** |  |
| VR-029 | quality_status envelope/payload match | **na** |  |
| VR-030 | quality_status expectation | **na** |  |
| VR-031 | acceptable>=3/5 | **pass** | 5/5 primary variants |
| VR-032 | no bare PASS gate claim | **pass** | no gate overclaim in fixture text |
| VR-033 | captured raw_record_json | **na** |  |
| VR-034 | raw_record_hash | **na** |  |
| VR-035 | query_mode type_inc params | **na** |  |
| VR-036 | registry_source_id | **na** |  |
| VR-037 | lineage_status=discovered (blocked linked) | **na** |  |
| VR-038 | no disclosure promotion (blocked) | **na** | blocked policy |
| VR-039 | no lineage promotion (blocked) | **na** | blocked policy |
| VR-040 | 301259/DLC006R exclusion | **pass** |  |
| VR-041 | component approval scope (blocked live) | **na** | blocked policy |
| VR-042 | no verified/production_ready claim (blocked) | **pass** |  |

**Fixture verdict:** **PASS** (10 pass / 32 na / 0 fail)

---

### 4.2 `DSC001_found.json`

| 项 | 值 |
|----|-----|
| case_id | DSC001 |
| scenario | captured |
| company_code | 000550 |
| event_status | captured |
| quality_status | pass |
| cninfo_called | False |

| VR | 规则 | 结果 | 备注 |
|----|------|------|------|
| VR-001 | universe 5 rows DSC001-DSC005 | **na** | universe_lock rollup §3 |
| VR-002 | component=shareholder_change first_slice_include=yes | **na** | universe_lock rollup §3 |
| VR-003 | anchor_tdate=2026-07-03 query_type=inc | **pass** |  |
| VR-004 | 688671/301259 excluded | **na** | universe_lock rollup §3 |
| VR-005 | DSC001 distinct case_id not DLC006R | **na** | universe_lock rollup §3 |
| VR-006 | per-case budget<=4 total<=20 | **na** | universe_lock rollup §3 |
| VR-007 | type=inc only | **pass** |  |
| VR-008 | type_desc not enabled (blocked) | **na** | blocked |
| VR-009 | HTTP 200 data.records | **na** | Tier-1 synthetic; no HTTP wrapper |
| VR-010 | SECCODE company filter | **pass** |  |
| VR-011 | found 8-field skeleton | **pass** |  |
| VR-012 | empty_but_valid legal | **na** |  |
| VR-013 | no sole captured_normal_candidate | **pass** | portfolio dual-variant mix |
| VR-014 | DSC004 needs_review mix | **na** |  |
| VR-015 | SECCODE->company_code | **pass** |  |
| VR-016 | VARYDATE date consistency | **pass** |  |
| VR-017 | F002V->shareholder_name | **pass** |  |
| VR-018 | F004N->change_amount | **pass** |  |
| VR-019 | F005N nullable | **pass** |  |
| VR-020 | inc->change_type=inc | **pass** |  |
| VR-021 | event_type=shareholder_change | **pass** |  |
| VR-022 | event_id stable | **pass** | synthetic fixture_id per DC005 convention |
| VR-023 | F007V optional price | **pass** | optional F007V; no forced primary_price in payload |
| VR-024 | SECNAME/DECLAREDATE recommended | **pass** |  |
| VR-025 | found event_status=captured | **pass** |  |
| VR-026 | empty event_status=empty_but_valid | **na** |  |
| VR-027 | empty no payload forge | **na** |  |
| VR-028 | freeze v1 required fields | **pass** |  |
| VR-029 | quality_status envelope/payload match | **pass** |  |
| VR-030 | quality_status expectation | **pass** |  |
| VR-031 | acceptable>=3/5 | **pass** | 5/5 primary variants |
| VR-032 | no bare PASS gate claim | **pass** | no gate overclaim in fixture text |
| VR-033 | captured raw_record_json | **pass** |  |
| VR-034 | raw_record_hash | **pass** | synthetic placeholder hash per Phase1 convention |
| VR-035 | query_mode type_inc params | **pass** |  |
| VR-036 | registry_source_id | **pass** |  |
| VR-037 | lineage_status=discovered (blocked linked) | **pass** |  |
| VR-038 | no disclosure promotion (blocked) | **na** | blocked policy |
| VR-039 | no lineage promotion (blocked) | **na** | blocked policy |
| VR-040 | 301259/DLC006R exclusion | **pass** |  |
| VR-041 | component approval scope (blocked live) | **na** | blocked policy |
| VR-042 | no verified/production_ready claim (blocked) | **pass** |  |

**Fixture verdict:** **PASS** (28 pass / 14 na / 0 fail)

---

### 4.3 `DSC002_empty.json`

| 项 | 值 |
|----|-----|
| case_id | DSC002 |
| scenario | empty_but_valid |
| company_code | 000895 |
| event_status | empty_but_valid |
| quality_status | pass |
| cninfo_called | False |

| VR | 规则 | 结果 | 备注 |
|----|------|------|------|
| VR-001 | universe 5 rows DSC001-DSC005 | **na** | universe_lock rollup §3 |
| VR-002 | component=shareholder_change first_slice_include=yes | **na** | universe_lock rollup §3 |
| VR-003 | anchor_tdate=2026-07-03 query_type=inc | **pass** |  |
| VR-004 | 688671/301259 excluded | **na** | universe_lock rollup §3 |
| VR-005 | DSC001 distinct case_id not DLC006R | **na** | universe_lock rollup §3 |
| VR-006 | per-case budget<=4 total<=20 | **na** | universe_lock rollup §3 |
| VR-007 | type=inc only | **pass** |  |
| VR-008 | type_desc not enabled (blocked) | **na** | blocked |
| VR-009 | HTTP 200 data.records | **na** | Tier-1 synthetic; no HTTP wrapper |
| VR-010 | SECCODE company filter | **na** |  |
| VR-011 | found 8-field skeleton | **na** |  |
| VR-012 | empty_but_valid legal | **pass** |  |
| VR-013 | no sole captured_normal_candidate | **pass** | portfolio dual-variant mix |
| VR-014 | DSC004 needs_review mix | **na** |  |
| VR-015 | SECCODE->company_code | **na** |  |
| VR-016 | VARYDATE date consistency | **na** |  |
| VR-017 | F002V->shareholder_name | **na** |  |
| VR-018 | F004N->change_amount | **na** |  |
| VR-019 | F005N nullable | **na** |  |
| VR-020 | inc->change_type=inc | **na** |  |
| VR-021 | event_type=shareholder_change | **na** |  |
| VR-022 | event_id stable | **na** |  |
| VR-023 | F007V optional price | **na** |  |
| VR-024 | SECNAME/DECLAREDATE recommended | **na** |  |
| VR-025 | found event_status=captured | **na** |  |
| VR-026 | empty event_status=empty_but_valid | **pass** |  |
| VR-027 | empty no payload forge | **pass** |  |
| VR-028 | freeze v1 required fields | **na** |  |
| VR-029 | quality_status envelope/payload match | **na** |  |
| VR-030 | quality_status expectation | **na** |  |
| VR-031 | acceptable>=3/5 | **pass** | 5/5 primary variants |
| VR-032 | no bare PASS gate claim | **pass** | no gate overclaim in fixture text |
| VR-033 | captured raw_record_json | **na** |  |
| VR-034 | raw_record_hash | **na** |  |
| VR-035 | query_mode type_inc params | **na** |  |
| VR-036 | registry_source_id | **na** |  |
| VR-037 | lineage_status=discovered (blocked linked) | **na** |  |
| VR-038 | no disclosure promotion (blocked) | **na** | blocked policy |
| VR-039 | no lineage promotion (blocked) | **na** | blocked policy |
| VR-040 | 301259/DLC006R exclusion | **pass** |  |
| VR-041 | component approval scope (blocked live) | **na** | blocked policy |
| VR-042 | no verified/production_ready claim (blocked) | **pass** |  |

**Fixture verdict:** **PASS** (10 pass / 32 na / 0 fail)

---

### 4.4 `DSC002_found.json`

| 项 | 值 |
|----|-----|
| case_id | DSC002 |
| scenario | captured |
| company_code | 000895 |
| event_status | captured |
| quality_status | pass |
| cninfo_called | False |

| VR | 规则 | 结果 | 备注 |
|----|------|------|------|
| VR-001 | universe 5 rows DSC001-DSC005 | **na** | universe_lock rollup §3 |
| VR-002 | component=shareholder_change first_slice_include=yes | **na** | universe_lock rollup §3 |
| VR-003 | anchor_tdate=2026-07-03 query_type=inc | **pass** |  |
| VR-004 | 688671/301259 excluded | **na** | universe_lock rollup §3 |
| VR-005 | DSC001 distinct case_id not DLC006R | **na** | universe_lock rollup §3 |
| VR-006 | per-case budget<=4 total<=20 | **na** | universe_lock rollup §3 |
| VR-007 | type=inc only | **pass** |  |
| VR-008 | type_desc not enabled (blocked) | **na** | blocked |
| VR-009 | HTTP 200 data.records | **na** | Tier-1 synthetic; no HTTP wrapper |
| VR-010 | SECCODE company filter | **pass** |  |
| VR-011 | found 8-field skeleton | **pass** |  |
| VR-012 | empty_but_valid legal | **na** |  |
| VR-013 | no sole captured_normal_candidate | **pass** | portfolio dual-variant mix |
| VR-014 | DSC004 needs_review mix | **na** |  |
| VR-015 | SECCODE->company_code | **pass** |  |
| VR-016 | VARYDATE date consistency | **pass** |  |
| VR-017 | F002V->shareholder_name | **pass** |  |
| VR-018 | F004N->change_amount | **pass** |  |
| VR-019 | F005N nullable | **pass** |  |
| VR-020 | inc->change_type=inc | **pass** |  |
| VR-021 | event_type=shareholder_change | **pass** |  |
| VR-022 | event_id stable | **pass** | synthetic fixture_id per DC005 convention |
| VR-023 | F007V optional price | **pass** | optional F007V; no forced primary_price in payload |
| VR-024 | SECNAME/DECLAREDATE recommended | **pass** |  |
| VR-025 | found event_status=captured | **pass** |  |
| VR-026 | empty event_status=empty_but_valid | **na** |  |
| VR-027 | empty no payload forge | **na** |  |
| VR-028 | freeze v1 required fields | **pass** |  |
| VR-029 | quality_status envelope/payload match | **pass** |  |
| VR-030 | quality_status expectation | **pass** |  |
| VR-031 | acceptable>=3/5 | **pass** | 5/5 primary variants |
| VR-032 | no bare PASS gate claim | **pass** | no gate overclaim in fixture text |
| VR-033 | captured raw_record_json | **pass** |  |
| VR-034 | raw_record_hash | **pass** | synthetic placeholder hash per Phase1 convention |
| VR-035 | query_mode type_inc params | **pass** |  |
| VR-036 | registry_source_id | **pass** |  |
| VR-037 | lineage_status=discovered (blocked linked) | **pass** |  |
| VR-038 | no disclosure promotion (blocked) | **na** | blocked policy |
| VR-039 | no lineage promotion (blocked) | **na** | blocked policy |
| VR-040 | 301259/DLC006R exclusion | **pass** |  |
| VR-041 | component approval scope (blocked live) | **na** | blocked policy |
| VR-042 | no verified/production_ready claim (blocked) | **pass** |  |

**Fixture verdict:** **PASS** (28 pass / 14 na / 0 fail)

---

### 4.5 `DSC003_empty.json`

| 项 | 值 |
|----|-----|
| case_id | DSC003 |
| scenario | empty_but_valid |
| company_code | 600000 |
| event_status | empty_but_valid |
| quality_status | pass |
| cninfo_called | False |

| VR | 规则 | 结果 | 备注 |
|----|------|------|------|
| VR-001 | universe 5 rows DSC001-DSC005 | **na** | universe_lock rollup §3 |
| VR-002 | component=shareholder_change first_slice_include=yes | **na** | universe_lock rollup §3 |
| VR-003 | anchor_tdate=2026-07-03 query_type=inc | **pass** |  |
| VR-004 | 688671/301259 excluded | **na** | universe_lock rollup §3 |
| VR-005 | DSC001 distinct case_id not DLC006R | **na** | universe_lock rollup §3 |
| VR-006 | per-case budget<=4 total<=20 | **na** | universe_lock rollup §3 |
| VR-007 | type=inc only | **pass** |  |
| VR-008 | type_desc not enabled (blocked) | **na** | blocked |
| VR-009 | HTTP 200 data.records | **na** | Tier-1 synthetic; no HTTP wrapper |
| VR-010 | SECCODE company filter | **na** |  |
| VR-011 | found 8-field skeleton | **na** |  |
| VR-012 | empty_but_valid legal | **pass** |  |
| VR-013 | no sole captured_normal_candidate | **pass** | portfolio dual-variant mix |
| VR-014 | DSC004 needs_review mix | **na** |  |
| VR-015 | SECCODE->company_code | **na** |  |
| VR-016 | VARYDATE date consistency | **na** |  |
| VR-017 | F002V->shareholder_name | **na** |  |
| VR-018 | F004N->change_amount | **na** |  |
| VR-019 | F005N nullable | **na** |  |
| VR-020 | inc->change_type=inc | **na** |  |
| VR-021 | event_type=shareholder_change | **na** |  |
| VR-022 | event_id stable | **na** |  |
| VR-023 | F007V optional price | **na** |  |
| VR-024 | SECNAME/DECLAREDATE recommended | **na** |  |
| VR-025 | found event_status=captured | **na** |  |
| VR-026 | empty event_status=empty_but_valid | **pass** |  |
| VR-027 | empty no payload forge | **pass** |  |
| VR-028 | freeze v1 required fields | **na** |  |
| VR-029 | quality_status envelope/payload match | **na** |  |
| VR-030 | quality_status expectation | **na** |  |
| VR-031 | acceptable>=3/5 | **pass** | 5/5 primary variants |
| VR-032 | no bare PASS gate claim | **pass** | no gate overclaim in fixture text |
| VR-033 | captured raw_record_json | **na** |  |
| VR-034 | raw_record_hash | **na** |  |
| VR-035 | query_mode type_inc params | **na** |  |
| VR-036 | registry_source_id | **na** |  |
| VR-037 | lineage_status=discovered (blocked linked) | **na** |  |
| VR-038 | no disclosure promotion (blocked) | **na** | blocked policy |
| VR-039 | no lineage promotion (blocked) | **na** | blocked policy |
| VR-040 | 301259/DLC006R exclusion | **pass** |  |
| VR-041 | component approval scope (blocked live) | **na** | blocked policy |
| VR-042 | no verified/production_ready claim (blocked) | **pass** |  |

**Fixture verdict:** **PASS** (10 pass / 32 na / 0 fail)

---

### 4.6 `DSC003_found.json`

| 项 | 值 |
|----|-----|
| case_id | DSC003 |
| scenario | captured |
| company_code | 600000 |
| event_status | captured |
| quality_status | pass |
| cninfo_called | False |

| VR | 规则 | 结果 | 备注 |
|----|------|------|------|
| VR-001 | universe 5 rows DSC001-DSC005 | **na** | universe_lock rollup §3 |
| VR-002 | component=shareholder_change first_slice_include=yes | **na** | universe_lock rollup §3 |
| VR-003 | anchor_tdate=2026-07-03 query_type=inc | **pass** |  |
| VR-004 | 688671/301259 excluded | **na** | universe_lock rollup §3 |
| VR-005 | DSC001 distinct case_id not DLC006R | **na** | universe_lock rollup §3 |
| VR-006 | per-case budget<=4 total<=20 | **na** | universe_lock rollup §3 |
| VR-007 | type=inc only | **pass** |  |
| VR-008 | type_desc not enabled (blocked) | **na** | blocked |
| VR-009 | HTTP 200 data.records | **na** | Tier-1 synthetic; no HTTP wrapper |
| VR-010 | SECCODE company filter | **pass** |  |
| VR-011 | found 8-field skeleton | **pass** |  |
| VR-012 | empty_but_valid legal | **na** |  |
| VR-013 | no sole captured_normal_candidate | **pass** | portfolio dual-variant mix |
| VR-014 | DSC004 needs_review mix | **na** |  |
| VR-015 | SECCODE->company_code | **pass** |  |
| VR-016 | VARYDATE date consistency | **pass** |  |
| VR-017 | F002V->shareholder_name | **pass** |  |
| VR-018 | F004N->change_amount | **pass** |  |
| VR-019 | F005N nullable | **pass** |  |
| VR-020 | inc->change_type=inc | **pass** |  |
| VR-021 | event_type=shareholder_change | **pass** |  |
| VR-022 | event_id stable | **pass** | synthetic fixture_id per DC005 convention |
| VR-023 | F007V optional price | **pass** | optional F007V; no forced primary_price in payload |
| VR-024 | SECNAME/DECLAREDATE recommended | **pass** |  |
| VR-025 | found event_status=captured | **pass** |  |
| VR-026 | empty event_status=empty_but_valid | **na** |  |
| VR-027 | empty no payload forge | **na** |  |
| VR-028 | freeze v1 required fields | **pass** |  |
| VR-029 | quality_status envelope/payload match | **pass** |  |
| VR-030 | quality_status expectation | **pass** |  |
| VR-031 | acceptable>=3/5 | **pass** | 5/5 primary variants |
| VR-032 | no bare PASS gate claim | **pass** | no gate overclaim in fixture text |
| VR-033 | captured raw_record_json | **pass** |  |
| VR-034 | raw_record_hash | **pass** | synthetic placeholder hash per Phase1 convention |
| VR-035 | query_mode type_inc params | **pass** |  |
| VR-036 | registry_source_id | **pass** |  |
| VR-037 | lineage_status=discovered (blocked linked) | **pass** |  |
| VR-038 | no disclosure promotion (blocked) | **na** | blocked policy |
| VR-039 | no lineage promotion (blocked) | **na** | blocked policy |
| VR-040 | 301259/DLC006R exclusion | **pass** |  |
| VR-041 | component approval scope (blocked live) | **na** | blocked policy |
| VR-042 | no verified/production_ready claim (blocked) | **pass** |  |

**Fixture verdict:** **PASS** (28 pass / 14 na / 0 fail)

---

### 4.7 `DSC004_needs_review_synthetic.json`

| 项 | 值 |
|----|-----|
| case_id | DSC004 |
| scenario | needs_review |
| company_code | 002415 |
| event_status | captured |
| quality_status | needs_review |
| cninfo_called | False |

| VR | 规则 | 结果 | 备注 |
|----|------|------|------|
| VR-001 | universe 5 rows DSC001-DSC005 | **na** | universe_lock rollup §3 |
| VR-002 | component=shareholder_change first_slice_include=yes | **na** | universe_lock rollup §3 |
| VR-003 | anchor_tdate=2026-07-03 query_type=inc | **pass** |  |
| VR-004 | 688671/301259 excluded | **na** | universe_lock rollup §3 |
| VR-005 | DSC001 distinct case_id not DLC006R | **na** | universe_lock rollup §3 |
| VR-006 | per-case budget<=4 total<=20 | **na** | universe_lock rollup §3 |
| VR-007 | type=inc only | **pass** |  |
| VR-008 | type_desc not enabled (blocked) | **na** | blocked |
| VR-009 | HTTP 200 data.records | **na** | Tier-1 synthetic; no HTTP wrapper |
| VR-010 | SECCODE company filter | **pass** |  |
| VR-011 | found 8-field skeleton | **pass** |  |
| VR-012 | empty_but_valid legal | **na** |  |
| VR-013 | no sole captured_normal_candidate | **pass** | portfolio dual-variant mix |
| VR-014 | DSC004 needs_review mix | **pass** | needs_review + mix |
| VR-015 | SECCODE->company_code | **pass** |  |
| VR-016 | VARYDATE date consistency | **pass** |  |
| VR-017 | F002V->shareholder_name | **pass** |  |
| VR-018 | F004N->change_amount | **pass** |  |
| VR-019 | F005N nullable | **pass** |  |
| VR-020 | inc->change_type=inc | **pass** |  |
| VR-021 | event_type=shareholder_change | **pass** |  |
| VR-022 | event_id stable | **pass** | synthetic fixture_id per DC005 convention |
| VR-023 | F007V optional price | **pass** | optional F007V; no forced primary_price in payload |
| VR-024 | SECNAME/DECLAREDATE recommended | **pass** |  |
| VR-025 | found event_status=captured | **pass** |  |
| VR-026 | empty event_status=empty_but_valid | **na** |  |
| VR-027 | empty no payload forge | **na** |  |
| VR-028 | freeze v1 required fields | **pass** |  |
| VR-029 | quality_status envelope/payload match | **pass** |  |
| VR-030 | quality_status expectation | **pass** |  |
| VR-031 | acceptable>=3/5 | **pass** | 5/5 primary variants |
| VR-032 | no bare PASS gate claim | **pass** | no gate overclaim in fixture text |
| VR-033 | captured raw_record_json | **pass** |  |
| VR-034 | raw_record_hash | **pass** | synthetic placeholder hash per Phase1 convention |
| VR-035 | query_mode type_inc params | **pass** |  |
| VR-036 | registry_source_id | **pass** |  |
| VR-037 | lineage_status=discovered (blocked linked) | **pass** |  |
| VR-038 | no disclosure promotion (blocked) | **na** | blocked policy |
| VR-039 | no lineage promotion (blocked) | **na** | blocked policy |
| VR-040 | 301259/DLC006R exclusion | **pass** |  |
| VR-041 | component approval scope (blocked live) | **na** | blocked policy |
| VR-042 | no verified/production_ready claim (blocked) | **pass** |  |

**Fixture verdict:** **PASS** (29 pass / 13 na / 0 fail)

---

### 4.8 `DSC005_empty_but_valid_synthetic.json`

| 项 | 值 |
|----|-----|
| case_id | DSC005 |
| scenario | empty_but_valid |
| company_code | 601988 |
| event_status | empty_but_valid |
| quality_status | pass |
| cninfo_called | False |

| VR | 规则 | 结果 | 备注 |
|----|------|------|------|
| VR-001 | universe 5 rows DSC001-DSC005 | **na** | universe_lock rollup §3 |
| VR-002 | component=shareholder_change first_slice_include=yes | **na** | universe_lock rollup §3 |
| VR-003 | anchor_tdate=2026-07-03 query_type=inc | **pass** |  |
| VR-004 | 688671/301259 excluded | **na** | universe_lock rollup §3 |
| VR-005 | DSC001 distinct case_id not DLC006R | **na** | universe_lock rollup §3 |
| VR-006 | per-case budget<=4 total<=20 | **na** | universe_lock rollup §3 |
| VR-007 | type=inc only | **pass** |  |
| VR-008 | type_desc not enabled (blocked) | **na** | blocked |
| VR-009 | HTTP 200 data.records | **na** | Tier-1 synthetic; no HTTP wrapper |
| VR-010 | SECCODE company filter | **na** |  |
| VR-011 | found 8-field skeleton | **na** |  |
| VR-012 | empty_but_valid legal | **pass** |  |
| VR-013 | no sole captured_normal_candidate | **pass** | portfolio dual-variant mix |
| VR-014 | DSC004 needs_review mix | **na** |  |
| VR-015 | SECCODE->company_code | **na** |  |
| VR-016 | VARYDATE date consistency | **na** |  |
| VR-017 | F002V->shareholder_name | **na** |  |
| VR-018 | F004N->change_amount | **na** |  |
| VR-019 | F005N nullable | **na** |  |
| VR-020 | inc->change_type=inc | **na** |  |
| VR-021 | event_type=shareholder_change | **na** |  |
| VR-022 | event_id stable | **na** |  |
| VR-023 | F007V optional price | **na** |  |
| VR-024 | SECNAME/DECLAREDATE recommended | **na** |  |
| VR-025 | found event_status=captured | **na** |  |
| VR-026 | empty event_status=empty_but_valid | **pass** |  |
| VR-027 | empty no payload forge | **pass** |  |
| VR-028 | freeze v1 required fields | **na** |  |
| VR-029 | quality_status envelope/payload match | **na** |  |
| VR-030 | quality_status expectation | **na** |  |
| VR-031 | acceptable>=3/5 | **pass** | 5/5 primary variants |
| VR-032 | no bare PASS gate claim | **pass** | no gate overclaim in fixture text |
| VR-033 | captured raw_record_json | **na** |  |
| VR-034 | raw_record_hash | **na** |  |
| VR-035 | query_mode type_inc params | **na** |  |
| VR-036 | registry_source_id | **na** |  |
| VR-037 | lineage_status=discovered (blocked linked) | **na** |  |
| VR-038 | no disclosure promotion (blocked) | **na** | blocked policy |
| VR-039 | no lineage promotion (blocked) | **na** | blocked policy |
| VR-040 | 301259/DLC006R exclusion | **pass** |  |
| VR-041 | component approval scope (blocked live) | **na** | blocked policy |
| VR-042 | no verified/production_ready claim (blocked) | **pass** |  |

**Fixture verdict:** **PASS** (10 pass / 32 na / 0 fail)

---

## 5. Portfolio Rollup

| 检查 | 结果 | 说明 |
|------|------|------|
| primary variant acceptable count (VR-031) | **pass** | 5/5 primary variants meet universe expected_behavior |
| dual-variant mix DSC001–003 + DSC005 control (VR-013) | **pass** | found+empty variants present; no sole captured_normal_candidate |
| DSC004 needs_review + mix (VR-014) | **pass** | needs_review synthetic coexists with empty variants |
| governance blocked rules VR-038–042 | **pass/na** | no disclosure promotion · no excluded codes · no forbidden claims in fixtures |

**Primary variant mapping（VR-031）：**

| case_id | primary fixture | expected_behavior | outcome |
|---------|-----------------|-------------------|---------|
| DSC001 | `DSC001_found.json` | captured_normal_or_empty_but_valid | captured / pass |
| DSC002 | `DSC002_found.json` | captured_normal_or_empty_but_valid | captured / pass |
| DSC003 | `DSC003_found.json` | captured_normal_or_empty_but_valid | captured / pass |
| DSC004 | `DSC004_needs_review_synthetic.json` | captured_normal_or_needs_review | captured / needs_review |
| DSC005 | `DSC005_empty_but_valid_synthetic.json` | empty_but_valid | empty_but_valid / pass |

---

## 6. Rule Group Summary

| rule_group | 名称 | fixtures all pass | universe row |
|------------|------|-------------------|--------------|
| A | Universe & Query | **pass** | pass |
| B | Raw Retrieval | **pass** | na |
| C | Field Mapping | **pass** | na |
| D | Envelope & Quality | **pass** | na |
| E | Lineage | **pass** | na |
| F | Evidence Boundary | **pass** | pass |
| G | Governance | **pass** | pass |

---

## 7. Caveats（non-fail）

| 项 | 说明 |
|----|------|
| VR-009 | Tier-1 synthetic 无 HTTP/`data.records` 包装层 · 标记 **na** · Tier-2 live 时再验 |
| VR-022 | offline synthetic 使用 `fixture_*` 描述性 event_id（对齐 DC005 Tier-0 惯例）· 非内容 hash |
| VR-034 | `raw_record_hash` 为 Phase1 占位符（`sha256:synthetic_*`）· 非对 raw JSON 的可复算 SHA256 |
| VR-008/037–041 | validation_rules 标记 **blocked** · 本验收记 **na** · 政策/治理层 |
| UTF-8 | 8 个 fixture 中文可读 · **无乱码** · **未修改** fixtures |

---

## 8. Overall Offline Gate

```text
task_id = D-GEN-20260714-07
phase = shareholder_change_fixture_vr_validation_20260714
fixture_count = 8
rule_count = 42 (VR-001 to VR-042)
cell_counts = pass:153 na:183 fail:0
fixture_verdicts = 8/8 PASS
universe_lock_vr_A = PASS
primary_acceptable_count = 5/5
shareholder_change_first_slice_fixture_vr_validation_gate = PASS_OFFLINE
shareholder_change_first_slice_live_gate = NOT_APPROVED (unchanged)
shareholder_change_first_slice_runner_gate = NOT_APPROVED (unchanged)
cninfo_calls = 0
fixtures_mutated = 0
verified = false
production_ready = false
```

**Overall offline gate: `PASS_OFFLINE`** — Tier-1 fixtures satisfy VR-001–VR-042 within offline synthetic scope; blocked rules recorded as na; live/runner remain separately gated.

---

## 9. Deliverables

| 文档 | 路径 |
|------|------|
| validation report | [cninfo_d_class_shareholder_change_fixture_vr_validation_20260714.md](cninfo_d_class_shareholder_change_fixture_vr_validation_20260714.md)（本文件） |
| rule group matrix CSV | [cninfo_d_class_shareholder_change_fixture_vr_matrix_20260714.csv](cninfo_d_class_shareholder_change_fixture_vr_matrix_20260714.csv) |

---

## 10. Safety Zeros

| 项 | 本包 |
|----|------|
| CNINFO calls | **0** |
| live / runner | **no** |
| fixture mutation | **no** |
| gate upgrade (live/runner) | **no** |
| commit / push | **no** |
