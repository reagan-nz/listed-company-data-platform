# CNINFO D 类 fund_industry_allocation — Validation Rules（VR-001–VR-042）

_生成时间：2026-07-15 · D-FM-11 · offline draft_

> **性质：** first-slice VR checklist · **CNINFO = 0** · **不是 verified**

## A — Universe & Query（VR-001–VR-008）

| ID | 规则 |
|----|------|
| VR-001 | universe 恰好 **5** 行 · case_id **DFIA001–DFIA005** |
| VR-002 | component=`fund_industry_allocation` · first_slice_include=`yes` · universe_lock_status=`locked` |
| VR-003 | query 双模式：`default`（DFIA001–DFIA002）· `rdate`（DFIA003–DFIA005） |
| VR-004 | 永久排除 **688671** · **301259** · exclude_flags 含 `no_company_code` · `exclude_company_event_schema` |
| VR-005 | endpoint=`data20/fund/industry` · records_path=`data.records` |
| VR-006 | per-case budget ≤ **1** · total cap ≤ **5** · **prefer ≤3 shared probes**（default · rdate=20260331 · rdate=20251231） |
| VR-007 | rdate 案：`rdate=YYYYMMDD` · default 案：无参 `{}` · 禁止 type/tdate 混用 |
| VR-008 | 行业聚合 · **禁止** 写入 `d_company_event` / `d_company_metric_periodic` |

## B — Raw Retrieval（VR-009–VR-014）

| ID | 规则 |
|----|------|
| VR-009 | 全行业截面按 `industry_code`（F001V）离线过滤目标行业 |
| VR-010 | empty records / 无匹配 F001V → `empty_but_valid` 合法 |
| VR-011 | found 骨架：F001V · F002V · ENDDATE · F003N · F004N · F005N |
| VR-012 | expectation mix：empty_but_valid + captured_normal_or_empty_but_valid + captured_normal · 至多一例 needs_review |
| VR-013 | **禁止** sole `captured_normal_candidate` 作为唯一成功标准 |
| VR-014 | DFIA005 期望 empty_but_valid · **不** forced pass |

> **D-FM-17 amend（VR-012 注释）：** DFIA001 `expected_behavior` 由 `captured_normal` → `captured_normal_or_empty_but_valid`（对齐 DFIA004 · 保持 C26/default）。mix 仍含 DFIA002/DFIA003 `captured_normal` + DFIA005 `empty_but_valid` · VR-012 成立。DFIA005 锚点/期望 **未** 改。

## C — Field Mapping（VR-015–VR-024）

| ID | 规则 |
|----|------|
| VR-015 | industry_code ← F001V |
| VR-016 | industry_name ← F002V |
| VR-017 | report_period ← ENDDATE（normalize date） |
| VR-018 | F003N → fund_coverage_count |
| VR-019 | F004N → industry_scale_100m_yuan |
| VR-020 | F005N → net_asset_ratio_percent |
| VR-021 | 1 raw → **3** metric rows · `d_industry_aggregate` · mapping_confidence=high |
| VR-022 | **禁止** company_code 字段出现在 metric 行 |
| VR-023 | cross-section 案（industry_code=`*`）评估截面非空 · 可用 sample 行映射 |
| VR-024 | field_confidence=high（registry Tier-0） |

## D — Envelope & Quality（VR-025–VR-032）

| ID | 规则 |
|----|------|
| VR-025 | captured / empty_but_valid / needs_review 三分法 |
| VR-026 | empty_but_valid ⇒ metric_count=0 · quality pass |
| VR-027 | DFIA005 期望 empty_but_valid |
| VR-028 | freeze 字段：industry_code · report_period · metric_name · metric_value · quality_status |
| VR-029 | quality_status 与 envelope 一致 |
| VR-030 | ≥3/5 acceptable → PASS_WITH_CAVEAT · **不是 bare PASS** |
| VR-031 | disclosure-only 升级 captured_normal **禁止** |
| VR-032 | PDF/OCR/extraction 禁止 |

## E — Lineage（VR-033–VR-037）

| ID | 规则 |
|----|------|
| VR-033 | raw_record_json 必填（found / captured） |
| VR-034 | default：query_params=`{}` · rdate：query_params 含 rdate |
| VR-035 | query_mode ∈ {default, rdate} |
| VR-036 | lineage_status ∈ {discovered, needs_review} · 禁止 linked |
| VR-037 | registry_source_id=`fund_industry_allocation` |

## F — Evidence Boundary（VR-038–VR-040）

| ID | 规则 |
|----|------|
| VR-038 | 不重开 executive_shareholding / shareholder_change / equity_pledge / RSU / block_trade / margin / disclosure / known-event / DLC006R |
| VR-039 | 不写 A/B/C 产物根 · 本包 **不** 推进 shareholder_data / abnormal_trading 真实 live |
| VR-040 | exclude_flags 含 exclude_688671;exclude_301259;no_company_code;exclude_company_event_schema |

## G — Governance（VR-041–VR-042）

| ID | 规则 |
|----|------|
| VR-041 | standing D 授权 offline lock/VR/fixtures · runner/S4/live 另批 |
| VR-042 | 禁止 verified / production_ready / bare PASS / commit/push（本任务） |
