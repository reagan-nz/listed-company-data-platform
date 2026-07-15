# CNINFO D 类 abnormal_trading — Validation Rules（VR-001–VR-042）

_生成时间：2026-07-15 · D-FM-03 · offline draft_

> **性质：** first-slice VR checklist · **CNINFO = 0** · **不是 verified**

## A — Universe & Query（VR-001–VR-008）

| ID | 规则 |
|----|------|
| VR-001 | universe 恰好 **5** 行 · case_id **DAT001–DAT005** |
| VR-002 | component=`abnormal_trading` · first_slice_include=`yes` |
| VR-003 | 全案共享 `anchor_tdate=2026-07-03` · query `single_day_paged` |
| VR-004 | 永久排除 **688671** · **301259** |
| VR-005 | endpoint=`getMarketStatisticsData` · records_path=`marketList` |
| VR-006 | per-case request budget ≤ **1** · total ≤ **20** |
| VR-007 | params：sdate=edate=anchor · page=1 · rows=30 |
| VR-008 | first-slice **单模式** · 禁止 generic multi-probe |

## B — Raw Retrieval（VR-009–VR-014）

| ID | 规则 |
|----|------|
| VR-009 | 市场截面按 secCode 过滤目标公司 |
| VR-010 | empty marketList / 无匹配公司 → `empty_but_valid` 合法 |
| VR-011 | found 骨架：secCode · secName · tradeTime · type |
| VR-012 | expectation mix：empty_but_valid + captured_normal_or_empty_but_valid + 至多一例 needs_review |
| VR-013 | **禁止** sole `captured_normal_candidate` |
| VR-014 | DAT001 needs_review 可接受 · **不** forced pass |

## C — Field Mapping（VR-015–VR-024）

| ID | 规则 |
|----|------|
| VR-015 | company_code ← secCode |
| VR-016 | company_name ← secName |
| VR-017 | event_date ← tradeTime |
| VR-018 | event_subtype ← type（public_information_reason） |
| VR-019 | event_type=`abnormal_trading` |
| VR-020 | event_id = logical hash(source, mode, code, date, type) |
| VR-021 | buyTotal/sellTotal/buyPercent/sellPercent → raw_only |
| VR-022 | detail[] → **deferred** `d_event_party_detail` · 保留 raw_record_json |
| VR-023 | mapping_confidence=medium |
| VR-024 | 禁止把 detail[] 扁平进主 event 列 |

## D — Envelope & Quality（VR-025–VR-032）

| ID | 规则 |
|----|------|
| VR-025 | captured / empty_but_valid / needs_review 三分法 |
| VR-026 | empty_but_valid ⇒ record_count=0 · quality pass |
| VR-027 | DAT005 期望 empty_but_valid |
| VR-028 | freeze 字段：company_code · trade_date · public_information_reason · quality_status |
| VR-029 | quality_status 与 envelope 一致 |
| VR-030 | ≥3/5 acceptable → PASS_WITH_CAVEAT · **不是 bare PASS** |
| VR-031 | disclosure-only 升级 captured_normal **禁止** |
| VR-032 | PDF/OCR/extraction 禁止 |

## E — Lineage（VR-033–VR-037）

| ID | 规则 |
|----|------|
| VR-033 | raw_record_json 必填（found） |
| VR-034 | query_params 含 sdate/edate/page/rows |
| VR-035 | query_mode=`single_day_paged` |
| VR-036 | lineage_status ∈ {discovered, needs_review} · 禁止 linked |
| VR-037 | registry_source_id=`abnormal_trading` |

## F — Evidence Boundary（VR-038–VR-040）

| ID | 规则 |
|----|------|
| VR-038 | 不重开 executive_shareholding / shareholder_change / DLC006R |
| VR-039 | 不写 A/B/C 产物根 |
| VR-040 | exclude_flags 含 exclude_688671;exclude_301259 |

## G — Governance（VR-041–VR-042）

| ID | 规则 |
|----|------|
| VR-041 | standing D 授权 offline/S4 dry-run · live 另批 |
| VR-042 | 禁止 verified / production_ready / bare PASS / commit/push（本任务） |
