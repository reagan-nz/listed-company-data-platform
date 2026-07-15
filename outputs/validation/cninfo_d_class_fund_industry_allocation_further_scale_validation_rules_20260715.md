# CNINFO D 类 fund_industry_allocation — Further-Scale Validation Rules（VR-FS-001–VR-FS-042）

_生成时间：2026-07-15 · D-FM-38 · offline draft_

> **性质：** further-scale VR checklist · **CNINFO = 0** · **不是 verified** · **不覆盖** first-slice VR-001–042 · **不覆盖** next-slice VR-NS-001–042
>
> **范围：** DFIA201–DFIA205 · coarse A/B/\* · proven rdates only · 矩阵补全相对 DFIA101–105

## A — Universe & Query（VR-FS-001–VR-FS-008）

| ID | 规则 |
|----|------|
| VR-FS-001 | universe 恰好 **5** 行 · case_id **DFIA201–DFIA205**（与 DFIA001–005 / DFIA101–105 隔离） |
| VR-FS-002 | component=`fund_industry_allocation` · further_scale_include=`yes` · universe_lock_status=`locked` · approval_task_id=`D-FM-38` |
| VR-FS-003 | query 双模式：`default`（DFIA201）· `rdate`（DFIA202–DFIA205） |
| VR-FS-004 | 永久排除 **688671** · **301259** · exclude_flags 含 `no_company_code` · `exclude_company_event_schema` · `exclude_first_slice_C26_sole_anchor` · `exclude_mutate_next_slice_DFIA101_105` · `exclude_mutate_at_sd_next_slice_dryrun` |
| VR-FS-005 | endpoint=`data20/fund/industry` · records_path=`data.records` |
| VR-FS-006 | per-case budget ≤ **1** · total cap ≤ **5** · **prefer ≤3 shared probes**（default · rdate=20260331 · rdate=20251231） |
| VR-FS-007 | rdate 案：`rdate=YYYYMMDD` · default 案：无参 `{}` · 禁止 type/tdate 混用 · **禁止**未证新 rdate |
| VR-FS-008 | 行业聚合 · **禁止** 写入 `d_company_event` / `d_company_metric_periodic` |

## B — Raw Retrieval（VR-FS-009–VR-FS-014）

| ID | 规则 |
|----|------|
| VR-FS-009 | 全行业截面按 `industry_code`（F001V）离线过滤目标行业（A/B） |
| VR-FS-010 | empty records / 无匹配 F001V → `empty_but_valid` 合法 |
| VR-FS-011 | found 骨架：F001V · F002V · ENDDATE · F003N · F004N · F005N |
| VR-FS-012 | expectation mix：DFIA201/204/205=`captured_normal_or_empty_but_valid` · DFIA202/203=`captured_normal` |
| VR-FS-013 | **禁止** sole `captured_normal_candidate` 作为唯一成功标准 · **禁止** C26 作 further-scale 唯一 found 锚 |
| VR-FS-014 | industry_code ∈ {A, B, \*}（本包 coarse）· 粗粒度 live-observed · 不用细码 C26/C27 作唯一锚 |

## C — Field Mapping（VR-FS-015–VR-FS-024）

| ID | 规则 |
|----|------|
| VR-FS-015 | industry_code ← F001V |
| VR-FS-016 | industry_name ← F002V |
| VR-FS-017 | report_period ← ENDDATE（normalize date） |
| VR-FS-018 | F003N → fund_coverage_count |
| VR-FS-019 | F004N → industry_scale_100m_yuan |
| VR-FS-020 | F005N → net_asset_ratio_percent |
| VR-FS-021 | 1 raw → **3** metric rows · `d_industry_aggregate` · mapping_confidence=high |
| VR-FS-022 | **禁止** company_code 字段出现在 metric 行 |
| VR-FS-023 | cross-section 案（industry_code=`*`）评估截面非空 · 可用 sample 行映射 |
| VR-FS-024 | field_confidence=high（registry Tier-0） |

## D — Envelope & Quality（VR-FS-025–VR-FS-032）

| ID | 规则 |
|----|------|
| VR-FS-025 | captured / empty_but_valid / needs_review 三分法 |
| VR-FS-026 | empty_but_valid ⇒ metric_count=0 · quality pass |
| VR-FS-027 | DFIA201/204/205 期望 mixed · empty fixture 与 found fixture 双合法 |
| VR-FS-028 | freeze 字段：industry_code · report_period · metric_name · metric_value · quality_status |
| VR-FS-029 | quality_status 与 envelope 一致 |
| VR-FS-030 | ≥3/5 acceptable → PASS_WITH_CAVEAT · **不是 bare PASS** |
| VR-FS-031 | disclosure-only 升级 captured_normal **禁止** |
| VR-FS-032 | PDF/OCR/extraction 禁止 |

## E — Lineage（VR-FS-033–VR-FS-037）

| ID | 规则 |
|----|------|
| VR-FS-033 | raw_record_json 必填（found / captured） |
| VR-FS-034 | default：query_params=`{}` · rdate：query_params 含 rdate |
| VR-FS-035 | query_mode ∈ {default, rdate} |
| VR-FS-036 | lineage_status ∈ {discovered, needs_review} · 禁止 linked |
| VR-FS-037 | registry_source_id=`fund_industry_allocation` |

## F — Evidence Boundary（VR-FS-038–VR-FS-040）

| ID | 规则 |
|----|------|
| VR-FS-038 | 不重开 executive_shareholding / shareholder_change / equity_pledge / RSU / block_trade / margin / disclosure / known-event / DLC006R |
| VR-FS-039 | 不写 A/B/C 产物根 · **不** mutate FIA first/next-slice lock/live · **不** mutate AT/SD first/next-slice dry-run roots · **不** AT/SD live flip |
| VR-FS-040 | exclude_flags 含 exclude_688671;exclude_301259;no_company_code;exclude_company_event_schema;exclude_first_slice_C26_sole_anchor;exclude_mutate_next_slice_DFIA101_105;exclude_mutate_at_sd_next_slice_dryrun |

## G — Governance（VR-FS-041–VR-FS-042）

| ID | 规则 |
|----|------|
| VR-FS-041 | standing D 授权 offline lock/VR/fixtures · runner/S4/live 另批 · ESS H3/H4 禁止盲探 · controller_execution_allowed=false |
| VR-FS-042 | 禁止 verified / production_ready / bare PASS / commit/push（本任务） |
