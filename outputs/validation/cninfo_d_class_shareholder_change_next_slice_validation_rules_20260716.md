# CNINFO D 类 shareholder_change — Next-Slice Validation Rules（VR-SC-NS-001–VR-SC-NS-042）

_生成时间：2026-07-16 · D-FM-49 · D-FM-50 lock 更新_

> **性质：** next-slice VR checklist · **CNINFO = 0** · **不是 verified** · **不覆盖** first-slice VR / DSC001–005 证据
>
> **范围：** DSC101–DSC105 · shared denser-mode cite `type=desc` + `anchor_tdate=2026-07-03` · **禁** `type=inc`+`2026-07-03` 作 found 唯一锚
>
> **命名：** SC = 股东增减持 = component `shareholder_change` · endpoint 拼写 **shareholeder**（不修正）
>
> **D-FM-50：** universe_lock_status 晋升为 `locked` · `approval_task_id=D-FM-50` · sketch 仍为只读 `draft_not_locked` 历史

## A — Universe & Query（VR-SC-NS-001–VR-SC-NS-008）

| ID | 规则 |
|----|------|
| VR-SC-NS-001 | universe 恰好 **5** 行 · case_id **DSC101–DSC105**（与 DSC001–005 隔离） |
| VR-SC-NS-002 | component=`shareholder_change` · next_slice_include=`yes` · universe_lock_status=`locked` · approval_task_id=`D-FM-50` |
| VR-SC-NS-003 | 全案共享 `query_type=desc` · `anchor_tdate=2026-07-03` · query_mode=`type_desc_tdate_daily` · **禁止** `type=inc`+`2026-07-03` 作 sole found 锚 |
| VR-SC-NS-004 | 永久排除 **688671** · **301259** · exclude_flags 含 `exclude_sparse_inc_20260703_sole_found_anchor` · `exclude_sole_needs_review` · `exclude_first_slice_DSC001_005_mutate` · `exclude_dlc006r` |
| VR-SC-NS-005 | endpoint=`https://www.cninfo.com.cn/data20/shareholeder/detail` · records_path=`data.records` · 拼写 **shareholeder** 不修正 |
| VR-SC-NS-006 | per-case budget ≤ **1** · total cap ≤ **5** · **shared_probe_prefer=1**（同日同模式截面一次 · 离线按 SECCODE 过滤） |
| VR-SC-NS-007 | params：`type=desc` · `tdate=2026-07-03` · method POST · query location · **禁止** `type=dec` |
| VR-SC-NS-008 | next-slice **单模式 desc** · 禁止把 first-slice DSC001–005 当 next-slice · 禁止 first-slice re-live |

## B — Raw Retrieval（VR-SC-NS-009–VR-SC-NS-014）

| ID | 规则 |
|----|------|
| VR-SC-NS-009 | 截面按 SECCODE 过滤目标公司 |
| VR-SC-NS-010 | empty records / 无匹配公司 → `empty_but_valid` 合法 |
| VR-SC-NS-011 | found 骨架：SECCODE · SECNAME · DECLAREDATE · VARYDATE · F002V · F004N · F005N · F007V |
| VR-SC-NS-012 | expectation mix：DSC101–104=`captured_normal_or_empty_but_valid` · DSC105=`empty_but_valid` |
| VR-SC-NS-013 | **禁止** sole `captured_normal_candidate` · **禁止** sole `captured_normal_or_needs_review` |
| VR-SC-NS-014 | denser-mode cite（priority2 type=desc rows=16 on 2026-07-03）为市场截面密度 · **不**等于 company-level live found-path |

## C — Field Mapping（VR-SC-NS-015–VR-SC-NS-024）

| ID | 规则 |
|----|------|
| VR-SC-NS-015 | company_code ← SECCODE |
| VR-SC-NS-016 | company_name ← SECNAME |
| VR-SC-NS-017 | announcement_date ← DECLAREDATE |
| VR-SC-NS-018 | share_change_date / event_date ← VARYDATE |
| VR-SC-NS-019 | shareholder_name ← F002V |
| VR-SC-NS-020 | share_change_amount ← F004N · share_change_ratio ← F005N · share_change_price ← F007V |
| VR-SC-NS-021 | event_type=`shareholder_change` · change_type=`desc` · event_id = logical hash(source, mode, code, varydate, amounts) |
| VR-SC-NS-022 | mapping_confidence=high（registry confirmed · desc/inc 同 8-field 骨架） |
| VR-SC-NS-023 | DC005 / first-slice fixtures 仅为字段/envelope 结构 cite · **不**证明 denser-mode company found · DC005 change_type=inc ≠ next-slice desc |
| VR-SC-NS-024 | 禁止把未确认 raw 列升为标准必填列 |

## D — Envelope & Quality（VR-SC-NS-025–VR-SC-NS-032）

| ID | 规则 |
|----|------|
| VR-SC-NS-025 | captured / empty_but_valid / needs_review 三分法 |
| VR-SC-NS-026 | empty_but_valid ⇒ record_count=0 · quality pass |
| VR-SC-NS-027 | DSC105 期望 empty_but_valid · DSC101–104 mixed found/empty 双合法 |
| VR-SC-NS-028 | freeze 字段：company_code · change_date · change_amount · change_ratio · change_type · quality_status |
| VR-SC-NS-029 | quality_status 与 envelope 一致 |
| VR-SC-NS-030 | ≥3/5 acceptable → PASS_WITH_CAVEAT · **不是 bare PASS** |
| VR-SC-NS-031 | disclosure-only 升级 captured_normal **禁止** |
| VR-SC-NS-032 | PDF/OCR/extraction 禁止 |

## E — Lineage（VR-SC-NS-033–VR-SC-NS-037）

| ID | 规则 |
|----|------|
| VR-SC-NS-033 | raw_record_json 必填（found / captured） |
| VR-SC-NS-034 | query_params 含 type=desc · tdate=`2026-07-03` |
| VR-SC-NS-035 | query_mode=`type_desc_tdate_daily` |
| VR-SC-NS-036 | lineage_status ∈ {discovered, needs_review} · 禁止 linked |
| VR-SC-NS-037 | registry_source_id=`shareholder_change` |

## F — Evidence Boundary（VR-SC-NS-038–VR-SC-NS-040）

| ID | 规则 |
|----|------|
| VR-SC-NS-038 | 不重开 RSU / EP / FIA / AT / SD / block_trade / margin / disclosure / known-event / DLC006R · **不** ESS H3/H4 |
| VR-SC-NS-039 | 不写 A/B/C 产物根 · **不** mutate RSU first/next dry-run · **不** mutate EP first/next · **不** mutate FIA first/next/further · **不** mutate AT/SD first/next · **不** mutate SC first-slice |
| VR-SC-NS-040 | exclude_flags 含 exclude_688671;exclude_301259;exclude_sparse_inc_20260703_sole_found_anchor;exclude_sole_needs_review;exclude_dlc006r |

## G — Governance（VR-SC-NS-041–VR-SC-NS-042）

| ID | 规则 |
|----|------|
| VR-SC-NS-041 | standing D 授权 offline planning/VR/sketch · runner/S4/live 另批 · ESS H3/H4 禁止盲探 · live_gate 本回合不翻转 |
| VR-SC-NS-042 | 禁止 verified / production_ready / bare PASS / commit/push（本任务） |
