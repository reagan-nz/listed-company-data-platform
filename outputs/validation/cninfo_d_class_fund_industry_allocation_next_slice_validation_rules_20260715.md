# CNINFO D 类 fund_industry_allocation — Next-Slice Validation Rules（VR-NS-001–VR-NS-042）

_生成时间：2026-07-15 · D-FM-24 · offline draft_

> **性质：** next-slice VR checklist · **CNINFO = 0** · **不是 verified** · **不覆盖** first-slice VR-001–042
>
> **范围：** DFIA101–DFIA105 · coarse A/B/C/\* · proven rdates only

## A — Universe & Query（VR-NS-001–VR-NS-008）

| ID | 规则 |
|----|------|
| VR-NS-001 | universe 恰好 **5** 行 · case_id **DFIA101–DFIA105**（与 DFIA001–005 隔离） |
| VR-NS-002 | component=`fund_industry_allocation` · next_slice_include=`yes` · universe_lock_status=`locked` · approval_task_id=`D-FM-24` |
| VR-NS-003 | query 双模式：`default`（DFIA101–DFIA102）· `rdate`（DFIA103–DFIA105） |
| VR-NS-004 | 永久排除 **688671** · **301259** · exclude_flags 含 `no_company_code` · `exclude_company_event_schema` · `exclude_first_slice_C26_sole_anchor` |
| VR-NS-005 | endpoint=`data20/fund/industry` · records_path=`data.records` |
| VR-NS-006 | per-case budget ≤ **1** · total cap ≤ **5** · **prefer ≤3 shared probes**（default · rdate=20260331 · rdate=20251231） |
| VR-NS-007 | rdate 案：`rdate=YYYYMMDD` · default 案：无参 `{}` · 禁止 type/tdate 混用 · **禁止**未证新 rdate |
| VR-NS-008 | 行业聚合 · **禁止** 写入 `d_company_event` / `d_company_metric_periodic` |

## B — Raw Retrieval（VR-NS-009–VR-NS-014）

| ID | 规则 |
|----|------|
| VR-NS-009 | 全行业截面按 `industry_code`（F001V）离线过滤目标行业（A/B/C） |
| VR-NS-010 | empty records / 无匹配 F001V → `empty_but_valid` 合法 |
| VR-NS-011 | found 骨架：F001V · F002V · ENDDATE · F003N · F004N · F005N |
| VR-NS-012 | expectation mix：DFIA101/102/105=`captured_normal_or_empty_but_valid` · DFIA103/104=`captured_normal` |
| VR-NS-013 | **禁止** sole `captured_normal_candidate` 作为唯一成功标准 · **禁止** C26 作 next-slice 唯一 found 锚 |
| VR-NS-014 | industry_code ∈ {A, B, C, \*} · 粗粒度 live-observed · 不用细码 C26/C27 作唯一锚 |

## C — Field Mapping（VR-NS-015–VR-NS-024）

| ID | 规则 |
|----|------|
| VR-NS-015 | industry_code ← F001V |
| VR-NS-016 | industry_name ← F002V |
| VR-NS-017 | report_period ← ENDDATE（normalize date） |
| VR-NS-018 | F003N → fund_coverage_count |
| VR-NS-019 | F004N → industry_scale_100m_yuan |
| VR-NS-020 | F005N → net_asset_ratio_percent |
| VR-NS-021 | 1 raw → **3** metric rows · `d_industry_aggregate` · mapping_confidence=high |
| VR-NS-022 | **禁止** company_code 字段出现在 metric 行 |
| VR-NS-023 | cross-section 案（industry_code=`*`）评估截面非空 · 可用 sample 行映射 |
| VR-NS-024 | field_confidence=high（registry Tier-0） |

## D — Envelope & Quality（VR-NS-025–VR-NS-032）

| ID | 规则 |
|----|------|
| VR-NS-025 | captured / empty_but_valid / needs_review 三分法 |
| VR-NS-026 | empty_but_valid ⇒ metric_count=0 · quality pass |
| VR-NS-027 | DFIA105 期望 mixed · empty fixture 与 found fixture 双合法 |
| VR-NS-028 | freeze 字段：industry_code · report_period · metric_name · metric_value · quality_status |
| VR-NS-029 | quality_status 与 envelope 一致 |
| VR-NS-030 | ≥3/5 acceptable → PASS_WITH_CAVEAT · **不是 bare PASS** |
| VR-NS-031 | disclosure-only 升级 captured_normal **禁止** |
| VR-NS-032 | PDF/OCR/extraction 禁止 |

## E — Lineage（VR-NS-033–VR-NS-037）

| ID | 规则 |
|----|------|
| VR-NS-033 | raw_record_json 必填（found / captured） |
| VR-NS-034 | default：query_params=`{}` · rdate：query_params 含 rdate |
| VR-NS-035 | query_mode ∈ {default, rdate} |
| VR-NS-036 | lineage_status ∈ {discovered, needs_review} · 禁止 linked |
| VR-NS-037 | registry_source_id=`fund_industry_allocation` |

## F — Evidence Boundary（VR-NS-038–VR-NS-040）

| ID | 规则 |
|----|------|
| VR-NS-038 | 不重开 executive_shareholding / shareholder_change / equity_pledge / RSU / block_trade / margin / disclosure / known-event / DLC006R |
| VR-NS-039 | 不写 A/B/C 产物根 · **不** mutate first-slice FIA/ES/AT/SD live roots · **不** mutate first-slice universe lock |
| VR-NS-040 | exclude_flags 含 exclude_688671;exclude_301259;no_company_code;exclude_company_event_schema;exclude_first_slice_C26_sole_anchor |

## G — Governance（VR-NS-041–VR-NS-042）

| ID | 规则 |
|----|------|
| VR-NS-041 | standing D 授权 offline lock/VR/fixtures · runner/S4/live 另批 · ESS H3/H4 禁止盲探 |
| VR-NS-042 | 禁止 verified / production_ready / bare PASS / commit/push（本任务） |
