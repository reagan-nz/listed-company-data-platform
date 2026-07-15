# CNINFO D 类 shareholder_data — Validation Rules（VR-001–VR-042）

_生成时间：2026-07-15 · D-FM-07 · offline draft_

> **性质：** first-slice VR checklist · **CNINFO = 0** · **不是 verified**

## A — Universe & Query（VR-001–VR-008）

| ID | 规则 |
|----|------|
| VR-001 | universe 恰好 **5** 行 · case_id **DSD001–DSD005** |
| VR-002 | component=`shareholder_data` · first_slice_include=`yes` |
| VR-003 | 全案共享 `anchor_rdate=20260331` · query `rdate_report_period` |
| VR-004 | 永久排除 **688671** · **301259** |
| VR-005 | endpoint=`data20/shareholeder/data` · records_path=`data.records`（拼写 shareholeder 保留） |
| VR-006 | per-case budget ≤ **1** · total cap ≤ **5** · **prefer 1 shared rdate** 请求 |
| VR-007 | params：`rdate=20260331` · 无 type/tdate 混用 |
| VR-008 | first-slice **单模式** · 禁止 multi-rdate probe |

## B — Raw Retrieval（VR-009–VR-014）

| ID | 规则 |
|----|------|
| VR-009 | 全市场报告期截面按 `SECCODE` 过滤目标公司 |
| VR-010 | empty records / 无匹配 SECCODE → `empty_but_valid` 合法 |
| VR-011 | found 骨架：SECCODE · SECNAME · ENDDATE · F001N–F006N |
| VR-012 | expectation mix：empty_but_valid + captured_normal_or_empty_but_valid + 至多一例 needs_review |
| VR-013 | **禁止** sole `captured_normal_candidate` 作为唯一成功标准 |
| VR-014 | DSD005 期望 empty_but_valid · **不** forced pass |

## C — Field Mapping（VR-015–VR-024）

| ID | 规则 |
|----|------|
| VR-015 | company_code ← SECCODE |
| VR-016 | company_name ← SECNAME |
| VR-017 | report_period ← ENDDATE（normalize date） |
| VR-018 | F001N → current_shareholder_count |
| VR-019 | F002N → previous_shareholder_count |
| VR-020 | F003N → shareholder_count_change_percent |
| VR-021 | F004N → current_avg_shares_per_holder |
| VR-022 | F005N → previous_avg_shares_per_holder |
| VR-023 | F006N → avg_shares_per_holder_change_percent |
| VR-024 | 1 raw → **6** metric rows · `d_company_metric_periodic` · mapping_confidence=high |

## D — Envelope & Quality（VR-025–VR-032）

| ID | 规则 |
|----|------|
| VR-025 | captured / empty_but_valid / needs_review 三分法 |
| VR-026 | empty_but_valid ⇒ metric_count=0 · quality pass |
| VR-027 | DSD005 期望 empty_but_valid |
| VR-028 | freeze 字段：company_code · report_period · metric_name · metric_value · quality_status |
| VR-029 | quality_status 与 envelope 一致 |
| VR-030 | ≥3/5 acceptable → PASS_WITH_CAVEAT · **不是 bare PASS** |
| VR-031 | disclosure-only 升级 captured_normal **禁止** |
| VR-032 | PDF/OCR/extraction 禁止 |

## E — Lineage（VR-033–VR-037）

| ID | 规则 |
|----|------|
| VR-033 | raw_record_json 必填（found） |
| VR-034 | query_params 含 rdate |
| VR-035 | query_mode=`rdate_report_period` |
| VR-036 | lineage_status ∈ {discovered, needs_review} · 禁止 linked |
| VR-037 | registry_source_id=`shareholder_data` |

## F — Evidence Boundary（VR-038–VR-040）

| ID | 规则 |
|----|------|
| VR-038 | 不重开 executive_shareholding / shareholder_change / equity_pledge / RSU / block_trade / margin / disclosure / known-event / DLC006R |
| VR-039 | 不写 A/B/C 产物根 · 不推进 abnormal_trading 真实 live（本包） |
| VR-040 | exclude_flags 含 exclude_688671;exclude_301259 |

## G — Governance（VR-041–VR-042）

| ID | 规则 |
|----|------|
| VR-041 | standing D 授权 offline lock/VR/fixtures · runner/S4/live 另批 |
| VR-042 | 禁止 verified / production_ready / bare PASS / commit/push（本任务） |
