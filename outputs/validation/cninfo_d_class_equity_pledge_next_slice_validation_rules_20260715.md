# CNINFO D 类 equity_pledge — Next-Slice Validation Rules（VR-EP-NS-001–VR-EP-NS-042）

_生成时间：2026-07-15 · D-FM-41 · offline draft_

> **性质：** next-slice VR checklist · **CNINFO = 0** · **不是 verified** · **不覆盖** first-slice VR / DEP001–005 证据
>
> **范围：** DEP101–DEP105 · shared denser-day cite `anchor_tdate=2026-07-02` · **禁** `2026-07-03` 作 found 唯一锚

## A — Universe & Query（VR-EP-NS-001–VR-EP-NS-008）

| ID | 规则 |
|----|------|
| VR-EP-NS-001 | universe 恰好 **5** 行 · case_id **DEP101–DEP105**（与 DEP001–005 隔离） |
| VR-EP-NS-002 | component=`equity_pledge` · next_slice_include=`yes` · universe_lock_status 未来=`locked`（本包 sketch=`draft_not_locked`） |
| VR-EP-NS-003 | 全案共享 `anchor_tdate=2026-07-02` · query `tdate_daily` · **禁止** `2026-07-03` 作 sole found 锚 |
| VR-EP-NS-004 | 永久排除 **688671** · **301259** · exclude_flags 含 `exclude_sparse_day_20260703_sole_found_anchor` · `exclude_sole_needs_review` · `exclude_first_slice_DEP001_005_mutate` |
| VR-EP-NS-005 | endpoint=`https://www.cninfo.com.cn/data20/equityPledge/list` · records_path=`data.records` |
| VR-EP-NS-006 | per-case budget ≤ **1** · total cap ≤ **5** · **shared_probe_prefer=1**（同日截面一次 · 离线按 SECCODE 过滤） |
| VR-EP-NS-007 | params：`tdate=2026-07-02` · method POST · query location |
| VR-EP-NS-008 | next-slice **单模式** · 禁止把 first-slice DEP001–005 当 next-slice · 禁止 first-slice re-live |

## B — Raw Retrieval（VR-EP-NS-009–VR-EP-NS-014）

| ID | 规则 |
|----|------|
| VR-EP-NS-009 | 截面按 SECCODE 过滤目标公司 |
| VR-EP-NS-010 | empty records / 无匹配公司 → `empty_but_valid` 合法 |
| VR-EP-NS-011 | found 骨架：SECCODE · SECNAME · DECLAREDATE · F001V · F003V · F006N · F007N · F018N |
| VR-EP-NS-012 | expectation mix：DEP101–104=`captured_normal_or_empty_but_valid` · DEP105=`empty_but_valid` |
| VR-EP-NS-013 | **禁止** sole `captured_normal_candidate` · **禁止** sole `captured_normal_or_needs_review` |
| VR-EP-NS-014 | denser-day cite（priority-2 rows=68）为市场截面密度 · **不**等于 company-level live found-path |

## C — Field Mapping（VR-EP-NS-015–VR-EP-NS-024）

| ID | 规则 |
|----|------|
| VR-EP-NS-015 | company_code ← SECCODE |
| VR-EP-NS-016 | company_name ← SECNAME |
| VR-EP-NS-017 | announcement_date / event_date ← DECLAREDATE |
| VR-EP-NS-018 | pledgor ← F001V · pledgee ← F003V |
| VR-EP-NS-019 | pledged_shares_10k_shares ← F006N · pledge_ratio_to_total_share_capital_percent ← F007N |
| VR-EP-NS-020 | cumulative_pledge_ratio_percent ← F018N · released_pledge_shares_10k_shares ← F012N |
| VR-EP-NS-021 | event_type=`equity_pledge` · event_id = logical hash(source, mode, code, date, pledgor, pledgee, shares) |
| VR-EP-NS-022 | F008V pledge_description_text → **raw_only**（UI 无独立列） |
| VR-EP-NS-023 | mapping_confidence=high（registry confirmed） |
| VR-EP-NS-024 | 禁止把 F008V 升为标准必填列 |

## D — Envelope & Quality（VR-EP-NS-025–VR-EP-NS-032）

| ID | 规则 |
|----|------|
| VR-EP-NS-025 | captured / empty_but_valid / needs_review 三分法 |
| VR-EP-NS-026 | empty_but_valid ⇒ record_count=0 · quality pass |
| VR-EP-NS-027 | DEP105 期望 empty_but_valid · DEP101–104 mixed found/empty 双合法 |
| VR-EP-NS-028 | freeze 字段：company_code · announcement_date · pledgor · pledged_shares · quality_status |
| VR-EP-NS-029 | quality_status 与 envelope 一致 |
| VR-EP-NS-030 | ≥3/5 acceptable → PASS_WITH_CAVEAT · **不是 bare PASS** |
| VR-EP-NS-031 | disclosure-only 升级 captured_normal **禁止** |
| VR-EP-NS-032 | PDF/OCR/extraction 禁止 |

## E — Lineage（VR-EP-NS-033–VR-EP-NS-037）

| ID | 规则 |
|----|------|
| VR-EP-NS-033 | raw_record_json 必填（found / captured） |
| VR-EP-NS-034 | query_params 含 tdate · 且 tdate=`2026-07-02` |
| VR-EP-NS-035 | query_mode=`tdate_daily` |
| VR-EP-NS-036 | lineage_status ∈ {discovered, needs_review} · 禁止 linked |
| VR-EP-NS-037 | registry_source_id=`equity_pledge` |

## F — Evidence Boundary（VR-EP-NS-038–VR-EP-NS-040）

| ID | 规则 |
|----|------|
| VR-EP-NS-038 | 不重开 ES / shareholder_change / RSU / block_trade / margin / disclosure / known-event / DLC006R |
| VR-EP-NS-039 | 不写 A/B/C 产物根 · **不** mutate FIA first/next/further-scale dry-run · **不** mutate AT/SD first/next dry-run · **不** mutate EP first-slice |
| VR-EP-NS-040 | exclude_flags 含 exclude_688671;exclude_301259;exclude_sparse_day_20260703_sole_found_anchor;exclude_sole_needs_review |

## G — Governance（VR-EP-NS-041–VR-EP-NS-042）

| ID | 规则 |
|----|------|
| VR-EP-NS-041 | standing D 授权 offline planning/VR/sketch · runner/S4/live 另批 · ESS H3/H4 禁止盲探 · live_gate 本回合不翻转 |
| VR-EP-NS-042 | 禁止 verified / production_ready / bare PASS / commit/push（本任务） |
