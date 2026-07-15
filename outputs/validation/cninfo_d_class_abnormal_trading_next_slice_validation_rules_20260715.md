# CNINFO D 类 abnormal_trading — Next-Slice Validation Rules（VR-NS-001–VR-NS-042）

_生成时间：2026-07-15 · D-FM-30 · offline draft_

> **性质：** next-slice VR checklist · **CNINFO = 0** · **不是 verified** · **不覆盖** first-slice VR-001–042
>
> **范围：** DAT101–DAT105 · shared denser-day cite `anchor_tdate=2026-07-02` · **禁** `2026-07-03` 作 found 唯一锚

## A — Universe & Query（VR-NS-001–VR-NS-008）

| ID | 规则 |
|----|------|
| VR-NS-001 | universe 恰好 **5** 行 · case_id **DAT101–DAT105**（与 DAT001–005 隔离） |
| VR-NS-002 | component=`abnormal_trading` · next_slice_include=`yes` · universe_lock_status=`locked` · approval_task_id=`D-FM-30` |
| VR-NS-003 | 全案共享 `anchor_tdate=2026-07-02` · query `single_day_paged` · **禁止** `2026-07-03` 作 sole found 锚 |
| VR-NS-004 | 永久排除 **688671** · **301259** · exclude_flags 含 `exclude_sparse_day_20260703_sole_found_anchor` · `exclude_sole_needs_review` · `detail_nested_deferred` |
| VR-NS-005 | endpoint=`getMarketStatisticsData` · records_path=`marketList` |
| VR-NS-006 | per-case budget ≤ **1** · total cap ≤ **5** · **shared_probe_prefer=1**（同日 marketList 一次 · 离线按 secCode 过滤） |
| VR-NS-007 | params：sdate=edate=`2026-07-02` · page=1 · rows=30 |
| VR-NS-008 | next-slice **单模式** · 禁止 generic multi-day probe · 禁止把 first-slice DAT001–005 当 next-slice |

## B — Raw Retrieval（VR-NS-009–VR-NS-014）

| ID | 规则 |
|----|------|
| VR-NS-009 | 市场截面按 secCode 过滤目标公司 |
| VR-NS-010 | empty marketList / 无匹配公司 → `empty_but_valid` 合法 |
| VR-NS-011 | found 骨架：secCode · secName · tradeTime · type |
| VR-NS-012 | expectation mix：DAT101–104=`captured_normal_or_empty_but_valid` · DAT105=`empty_but_valid` |
| VR-NS-013 | **禁止** sole `captured_normal_candidate` · **禁止** sole `captured_normal_or_needs_review` |
| VR-NS-014 | denser-day cite 为市场截面密度 · **不**等于 company-level live found-path |

## C — Field Mapping（VR-NS-015–VR-NS-024）

| ID | 规则 |
|----|------|
| VR-NS-015 | company_code ← secCode |
| VR-NS-016 | company_name ← secName |
| VR-NS-017 | event_date / trade_date ← tradeTime |
| VR-NS-018 | event_subtype ← type（public_information_reason） |
| VR-NS-019 | event_type=`abnormal_trading` |
| VR-NS-020 | event_id = logical hash(source, mode, code, date, type) |
| VR-NS-021 | buyTotal/sellTotal/buyPercent/sellPercent → raw_only |
| VR-NS-022 | detail[] → **deferred** `d_event_party_detail` · 保留 raw_record_json |
| VR-NS-023 | mapping_confidence=medium |
| VR-NS-024 | 禁止把 detail[] 扁平进主 event 列 |

## D — Envelope & Quality（VR-NS-025–VR-NS-032）

| ID | 规则 |
|----|------|
| VR-NS-025 | captured / empty_but_valid / needs_review 三分法 |
| VR-NS-026 | empty_but_valid ⇒ record_count=0 · quality pass |
| VR-NS-027 | DAT105 期望 empty_but_valid · DAT101–104 mixed found/empty fixtures 双合法 |
| VR-NS-028 | freeze 字段：company_code · trade_date · public_information_reason · quality_status |
| VR-NS-029 | quality_status 与 envelope 一致 |
| VR-NS-030 | ≥3/5 acceptable → PASS_WITH_CAVEAT · **不是 bare PASS** |
| VR-NS-031 | disclosure-only 升级 captured_normal **禁止** |
| VR-NS-032 | PDF/OCR/extraction 禁止 |

## E — Lineage（VR-NS-033–VR-NS-037）

| ID | 规则 |
|----|------|
| VR-NS-033 | raw_record_json 必填（found / captured） |
| VR-NS-034 | query_params 含 sdate/edate/page/rows · 且 sdate=edate=`2026-07-02` |
| VR-NS-035 | query_mode=`single_day_paged` |
| VR-NS-036 | lineage_status ∈ {discovered, needs_review} · 禁止 linked |
| VR-NS-037 | registry_source_id=`abnormal_trading` |

## F — Evidence Boundary（VR-NS-038–VR-NS-040）

| ID | 规则 |
|----|------|
| VR-NS-038 | 不重开 executive_shareholding / shareholder_change / equity_pledge / RSU / block_trade / margin / disclosure / known-event / DLC006R |
| VR-NS-039 | 不写 A/B/C 产物根 · **不** mutate AT/SD first-slice lock/live roots · **不** mutate FIA first/next-slice lock/live roots |
| VR-NS-040 | exclude_flags 含 exclude_688671;exclude_301259;exclude_sparse_day_20260703_sole_found_anchor;exclude_sole_needs_review |

## G — Governance（VR-NS-041–VR-NS-042）

| ID | 规则 |
|----|------|
| VR-NS-041 | standing D 授权 offline lock/VR/fixtures · runner/S4/live 另批 · ESS H3/H4 禁止盲探 |
| VR-NS-042 | 禁止 verified / production_ready / bare PASS / commit/push（本任务） |
