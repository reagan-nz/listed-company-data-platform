# CNINFO D 类 restricted_shares_unlock（ES / 限售解禁）— Next-Slice Validation Rules（VR-RSU-NS-001–VR-RSU-NS-042）

_生成时间：2026-07-15 · D-FM-45_

> **性质：** next-slice VR checklist · **CNINFO = 0** · **不是 verified** · **不覆盖** first-slice VR / DRU001–005 证据
>
> **范围：** DRU101–DRU105 · shared denser-day cite `anchor_tdate=2026-07-03` · **禁** `2026-06-08` 作 found 唯一锚
>
> **命名：** ES = **限售解禁 / equity structure** = component `restricted_shares_unlock`（非 executive_shareholding）

## A — Universe & Query（VR-RSU-NS-001–VR-RSU-NS-008）

| ID | 规则 |
|----|------|
| VR-RSU-NS-001 | universe 恰好 **5** 行 · case_id **DRU101–DRU105**（与 DRU001–005 隔离） |
| VR-RSU-NS-002 | component=`restricted_shares_unlock` · next_slice_include=`yes` · universe_lock_status=`draft_not_locked`（本包）· 未来 lock 另批 |
| VR-RSU-NS-003 | 全案共享 `anchor_tdate=2026-07-03` · query `tdate_daily` · **禁止** `2026-06-08` 作 sole found 锚 |
| VR-RSU-NS-004 | 永久排除 **688671** · **301259** · exclude_flags 含 `exclude_sparse_day_20260608_sole_found_anchor` · `exclude_sole_needs_review` · `exclude_first_slice_DRU001_005_mutate` |
| VR-RSU-NS-005 | endpoint=`https://www.cninfo.com.cn/data20/liftBan/detail` · records_path=`data.records` |
| VR-RSU-NS-006 | per-case budget ≤ **1** · total cap ≤ **5** · **shared_probe_prefer=1**（同日截面一次 · 离线按 SECCODE 过滤） |
| VR-RSU-NS-007 | params：`tdate=2026-07-03` · method POST · query location |
| VR-RSU-NS-008 | next-slice **单模式** · 禁止把 first-slice DRU001–005 当 next-slice · 禁止 first-slice re-live |

## B — Raw Retrieval（VR-RSU-NS-009–VR-RSU-NS-014）

| ID | 规则 |
|----|------|
| VR-RSU-NS-009 | 截面按 SECCODE 过滤目标公司 |
| VR-RSU-NS-010 | empty records / 无匹配公司 → `empty_but_valid` 合法 |
| VR-RSU-NS-011 | found 骨架：SECCODE · SECNAME · DECLAREDATE · F003D · F004N · F005N · F008N |
| VR-RSU-NS-012 | expectation mix：DRU101–104=`captured_normal_or_empty_but_valid` · DRU105=`empty_but_valid` |
| VR-RSU-NS-013 | **禁止** sole `captured_normal_candidate` · **禁止** sole `captured_normal_or_needs_review` |
| VR-RSU-NS-014 | denser-day cite（multidate rows=9 on 2026-07-03）为市场截面密度 · **不**等于 company-level live found-path |

## C — Field Mapping（VR-RSU-NS-015–VR-RSU-NS-024）

| ID | 规则 |
|----|------|
| VR-RSU-NS-015 | company_code ← SECCODE |
| VR-RSU-NS-016 | company_name ← SECNAME |
| VR-RSU-NS-017 | announcement_date ← DECLAREDATE |
| VR-RSU-NS-018 | unlock_date / event_date ← F003D |
| VR-RSU-NS-019 | unlock_amount ← F004N · unlock_ratio ← F005N |
| VR-RSU-NS-020 | tradable_amount ← F008N |
| VR-RSU-NS-021 | event_type=`restricted_shares_unlock` · event_id = logical hash(source, mode, code, unlock_date, amounts) |
| VR-RSU-NS-022 | mapping_confidence=high（registry confirmed） |
| VR-RSU-NS-023 | sample_raw（300992 / tdate=2026-06-08）仅为字段结构 cite · **不**证明 denser-day company found |
| VR-RSU-NS-024 | 禁止把未确认 raw 列升为标准必填列 |

## D — Envelope & Quality（VR-RSU-NS-025–VR-RSU-NS-032）

| ID | 规则 |
|----|------|
| VR-RSU-NS-025 | captured / empty_but_valid / needs_review 三分法 |
| VR-RSU-NS-026 | empty_but_valid ⇒ record_count=0 · quality pass |
| VR-RSU-NS-027 | DRU105 期望 empty_but_valid · DRU101–104 mixed found/empty 双合法 |
| VR-RSU-NS-028 | freeze 字段：company_code · unlock_date · unlock_amount · unlock_ratio · quality_status |
| VR-RSU-NS-029 | quality_status 与 envelope 一致 |
| VR-RSU-NS-030 | ≥3/5 acceptable → PASS_WITH_CAVEAT · **不是 bare PASS** |
| VR-RSU-NS-031 | disclosure-only 升级 captured_normal **禁止** |
| VR-RSU-NS-032 | PDF/OCR/extraction 禁止 |

## E — Lineage（VR-RSU-NS-033–VR-RSU-NS-037）

| ID | 规则 |
|----|------|
| VR-RSU-NS-033 | raw_record_json 必填（found / captured） |
| VR-RSU-NS-034 | query_params 含 tdate · 且 tdate=`2026-07-03` |
| VR-RSU-NS-035 | query_mode=`tdate_daily` |
| VR-RSU-NS-036 | lineage_status ∈ {discovered, needs_review} · 禁止 linked |
| VR-RSU-NS-037 | registry_source_id=`restricted_shares_unlock` |

## F — Evidence Boundary（VR-RSU-NS-038–VR-RSU-NS-040）

| ID | 规则 |
|----|------|
| VR-RSU-NS-038 | 不重开 shareholder_change / EP / FIA / AT / SD / block_trade / margin / disclosure / known-event / DLC006R · **不** ESS H3/H4 |
| VR-RSU-NS-039 | 不写 A/B/C 产物根 · **不** mutate EP first/next dry-run · **不** mutate FIA first/next/further · **不** mutate AT/SD first/next · **不** mutate RSU first-slice |
| VR-RSU-NS-040 | exclude_flags 含 exclude_688671;exclude_301259;exclude_sparse_day_20260608_sole_found_anchor;exclude_sole_needs_review |

## G — Governance（VR-RSU-NS-041–VR-RSU-NS-042）

| ID | 规则 |
|----|------|
| VR-RSU-NS-041 | standing D 授权 offline planning/VR/sketch · runner/S4/live 另批 · ESS H3/H4 禁止盲探 · live_gate 本回合不翻转 |
| VR-RSU-NS-042 | 禁止 verified / production_ready / bare PASS / commit/push（本任务） |
