# CNINFO D 类 executive_shareholding — Next-Slice Validation Rules（VR-ESH-NS-001–VR-ESH-NS-042）

_生成时间：2026-07-16 · D-FM-53 · lock 更新 D-FM-54_

> **性质：** next-slice VR checklist · **CNINFO = 0** · **不是 verified** · **不覆盖** first-slice VR / DES001–005 证据
>
> **范围：** DES101–DES105 · shared denser-mode cite `timeMark=threeMonth` + `varyType=b` · **禁** `timeMark=oneMonth`+`varyType=b` 作 found 唯一锚
>
> **命名：** ESH = 高管持股变动明细 = component `executive_shareholding` · endpoint **`leader/detail`** · **不是** summary H3/H4

## A — Universe & Query（VR-ESH-NS-001–VR-ESH-NS-008）

| ID | 规则 |
|----|------|
| VR-ESH-NS-001 | universe 恰好 **5** 行 · case_id **DES101–DES105**（与 DES001–005 隔离） |
| VR-ESH-NS-002 | component=`executive_shareholding` · next_slice_include=`yes` · universe_lock_status=`locked` · approval_task_id=`D-FM-54`（sketch 仍 `draft_not_locked` 作历史） |
| VR-ESH-NS-003 | 全案共享 `timeMark=threeMonth` · `varyType=b` · query_mode=`timeMark_threeMonth_varyType_b` · **禁止** `oneMonth`+`b` 作 sole found 锚 |
| VR-ESH-NS-004 | 永久排除 **688671** · **301259** · exclude_flags 含 `exclude_sparse_oneMonth_b_sole_found_anchor` · `exclude_sole_needs_review` · `exclude_first_slice_DES001_005_mutate` · `exclude_dlc006r` · `exclude_ess_h3_h4` |
| VR-ESH-NS-005 | endpoint=`https://www.cninfo.com.cn/data20/leader/detail` · records_path=`data.records` · **禁止** 当作 summary endpoint（≠ H4 reopen） |
| VR-ESH-NS-006 | per-case budget ≤ **1** · total cap ≤ **5** · **shared_probe_prefer=1**（同模式截面一次 · 离线按 SECCODE 过滤） |
| VR-ESH-NS-007 | params：`timeMark=threeMonth` · `varyType=b` · method POST · query location · **禁止** threeMonth/oneYear/s 作为本包外盲扩 |
| VR-ESH-NS-008 | next-slice **单模式 threeMonth+b** · 禁止把 first-slice DES001–005 当 next-slice · 禁止 first-slice re-live |

## B — Raw Retrieval（VR-ESH-NS-009–VR-ESH-NS-014）

| ID | 规则 |
|----|------|
| VR-ESH-NS-009 | 截面按 SECCODE 过滤目标公司 |
| VR-ESH-NS-010 | empty records / 无匹配公司 → `empty_but_valid` 合法 |
| VR-ESH-NS-011 | found 骨架：SECCODE · SECNAME · ENDDATE · HUMANNAME · F001V · F002V · F003V · F006N · F008N · F010V |
| VR-ESH-NS-012 | expectation mix：DES101–104=`captured_normal_or_empty_but_valid` · DES105=`empty_but_valid` |
| VR-ESH-NS-013 | **禁止** sole `captured_normal_candidate` · **禁止** sole `captured_normal_or_needs_review` |
| VR-ESH-NS-014 | denser-mode cite（priority2 threeMonth+b rows=1862）为市场截面密度 · **不**等于 company-level live found-path |

## C — Field Mapping（VR-ESH-NS-015–VR-ESH-NS-024）

| ID | 规则 |
|----|------|
| VR-ESH-NS-015 | company_code ← SECCODE |
| VR-ESH-NS-016 | company_name ← SECNAME |
| VR-ESH-NS-017 | shareholding_change_date / event_date ← ENDDATE |
| VR-ESH-NS-018 | executive_name ← HUMANNAME |
| VR-ESH-NS-019 | share_change_person ← F001V · executive_position ← F002V · relationship ← F003V |
| VR-ESH-NS-020 | changed_shares ← F006N · average_transaction_price ← F008N · change_reason ← F010V |
| VR-ESH-NS-021 | event_type=`executive_shareholding_change` · event_id = logical hash(source, mode, code, enddate, amounts) |
| VR-ESH-NS-022 | mapping_confidence=medium（registry confirmed · F005N uncertain 保留） |
| VR-ESH-NS-023 | DC006 / first-slice fixtures 仅为字段/envelope 结构 cite · **不**证明 denser-mode company found · DC006 ≠ company-level threeMonth found |
| VR-ESH-NS-024 | 禁止把未确认 raw 列（含 F005N）升为标准必填列 |

## D — Envelope & Quality（VR-ESH-NS-025–VR-ESH-NS-032）

| ID | 规则 |
|----|------|
| VR-ESH-NS-025 | captured / empty_but_valid / needs_review 三分法 |
| VR-ESH-NS-026 | empty_but_valid ⇒ record_count=0 · quality pass |
| VR-ESH-NS-027 | DES105 期望 empty_but_valid · DES101–104 mixed found/empty 双合法 |
| VR-ESH-NS-028 | freeze 字段：company_code · change_date · changed_shares · executive_name · quality_status |
| VR-ESH-NS-029 | quality_status 与 envelope 一致 |
| VR-ESH-NS-030 | ≥3/5 acceptable → PASS_WITH_CAVEAT · **不是 bare PASS** |
| VR-ESH-NS-031 | disclosure-only 升级 captured_normal **禁止** |
| VR-ESH-NS-032 | PDF/OCR/extraction 禁止 |

## E — Lineage（VR-ESH-NS-033–VR-ESH-NS-037）

| ID | 规则 |
|----|------|
| VR-ESH-NS-033 | raw_record_json 必填（found / captured） |
| VR-ESH-NS-034 | query_params 含 timeMark=`threeMonth` · varyType=`b` |
| VR-ESH-NS-035 | query_mode=`timeMark_threeMonth_varyType_b` |
| VR-ESH-NS-036 | lineage_status ∈ {discovered, needs_review} · 禁止 linked |
| VR-ESH-NS-037 | registry_source_id=`executive_shareholding` |

## F — Evidence Boundary（VR-ESH-NS-038–VR-ESH-NS-040）

| ID | 规则 |
|----|------|
| VR-ESH-NS-038 | 不重开 SC / RSU / EP / FIA / AT / SD / block_trade / margin / disclosure / known-event / DLC006R · **不** ESS H3/H4 |
| VR-ESH-NS-039 | 不写 A/B/C 产物根 · **不** mutate SC first/next dry-run · **不** mutate RSU first/next · **不** mutate EP first/next · **不** mutate FIA first/next/further · **不** mutate AT/SD first/next · **不** mutate ESH first-slice |
| VR-ESH-NS-040 | exclude_flags 含 exclude_688671;exclude_301259;exclude_sparse_oneMonth_b_sole_found_anchor;exclude_sole_needs_review;exclude_dlc006r;exclude_ess_h3_h4 |

## G — Governance（VR-ESH-NS-041–VR-ESH-NS-042）

| ID | 规则 |
|----|------|
| VR-ESH-NS-041 | standing D 授权 offline planning/VR/sketch · runner/S4/live 另批 · ESS H3/H4 禁止盲探 · live_gate 本回合不翻转 |
| VR-ESH-NS-042 | 禁止 verified / production_ready / bare PASS / commit/push（本任务） |
