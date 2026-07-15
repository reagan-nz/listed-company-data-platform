# CNINFO D 类 shareholder_data — Next-Slice Validation Rules（VR-NS-001–VR-NS-042）

_生成时间：2026-07-15 · D-FM-32 · offline draft_

> **性质：** next-slice VR checklist · **CNINFO = 0** · **不是 verified** · **不覆盖** first-slice VR-001–042
>
> **范围：** DSD101–DSD105 · multi-rdate `20260331` + `20251231` · **shared_probe_prefer=2**
>
> **与 first-slice 差异：** first-slice VR-008 仍禁止 multi-rdate；本 namespace **允许** 两共享 rdate（仅 next-slice）

## A — Universe & Query（VR-NS-001–VR-NS-008）

| ID | 规则 |
|----|------|
| VR-NS-001 | universe 恰好 **5** 行 · case_id **DSD101–DSD105**（与 DSD001–005 隔离） |
| VR-NS-002 | component=`shareholder_data` · next_slice_include=`yes` · universe_lock_status=`locked` · approval_task_id=`D-FM-32` |
| VR-NS-003 | rdate 集合仅为 `{20260331, 20251231}` · DSD101–103=`20260331` · DSD104–105=`20251231` · query `rdate_report_period` |
| VR-NS-004 | 永久排除 **688671** · **301259** · exclude_flags 含 `exclude_first_slice_mutate` · `allow_multi_rdate_next_slice_only` |
| VR-NS-005 | endpoint=`data20/shareholeder/data` · records_path=`data.records`（拼写 shareholeder 保留） |
| VR-NS-006 | per-case budget ≤ **1** · total cap ≤ **5** · **shared_probe_prefer=2**（两 rdate 各一次 · 离线按 SECCODE 过滤） |
| VR-NS-007 | params：`rdate` ∈ `{20260331, 20251231}` · 无 type/tdate 混用 · 无 AT denser-day 锚混入 |
| VR-NS-008 | next-slice **允许 multi-rdate**（仅本命名空间）· **禁止** 改写 first-slice VR-008 · **禁止** 把 DSD001–005 当 next-slice |

## B — Raw Retrieval（VR-NS-009–VR-NS-014）

| ID | 规则 |
|----|------|
| VR-NS-009 | 全市场报告期截面按 `SECCODE` 过滤目标公司 |
| VR-NS-010 | empty records / 无匹配 SECCODE → `empty_but_valid` 合法 |
| VR-NS-011 | found 骨架：SECCODE · SECNAME · ENDDATE · F001N–F006N |
| VR-NS-012 | expectation mix：DSD101=`captured_normal` · DSD102–104=`captured_normal_or_empty_but_valid` · DSD105=`empty_but_valid` |
| VR-NS-013 | **禁止** sole `captured_normal_candidate` · **禁止** sole `captured_normal_or_needs_review` |
| VR-NS-014 | `20251231` 为 unproven_rdate_mixed · **不**等于 live found-path · **不** claim DSD104/105 live-proven |

## C — Field Mapping（VR-NS-015–VR-NS-024）

| ID | 规则 |
|----|------|
| VR-NS-015 | company_code ← SECCODE |
| VR-NS-016 | company_name ← SECNAME |
| VR-NS-017 | report_period ← ENDDATE（normalize date） |
| VR-NS-018 | F001N → current_shareholder_count |
| VR-NS-019 | F002N → previous_shareholder_count |
| VR-NS-020 | F003N → shareholder_count_change_percent |
| VR-NS-021 | F004N → current_avg_shares_per_holder |
| VR-NS-022 | F005N → previous_avg_shares_per_holder |
| VR-NS-023 | F006N → avg_shares_per_holder_change_percent |
| VR-NS-024 | 1 raw → **6** metric rows · `d_company_metric_periodic` · mapping_confidence=high |

## D — Envelope & Quality（VR-NS-025–VR-NS-032）

| ID | 规则 |
|----|------|
| VR-NS-025 | captured / empty_but_valid / needs_review 三分法 |
| VR-NS-026 | empty_but_valid ⇒ metric_count=0 · quality pass |
| VR-NS-027 | DSD105 期望 empty_but_valid · DSD102–104 mixed found/empty fixtures 双合法 · DSD101 found-only |
| VR-NS-028 | freeze 字段：company_code · report_period · metric_count · quality_status |
| VR-NS-029 | quality_status 与 envelope 一致 |
| VR-NS-030 | ≥3/5 acceptable → PASS_WITH_CAVEAT · **不是 bare PASS** |
| VR-NS-031 | disclosure-only 升级 captured_normal **禁止** |
| VR-NS-032 | PDF/OCR/extraction 禁止 |

## E — Lineage（VR-NS-033–VR-NS-037）

| ID | 规则 |
|----|------|
| VR-NS-033 | raw_record_json 必填（found / captured） |
| VR-NS-034 | query_params 含 rdate · 且与 universe `anchor_rdate` 一致 |
| VR-NS-035 | query_mode=`rdate_report_period` |
| VR-NS-036 | lineage_status ∈ {discovered, needs_review} · 禁止 linked |
| VR-NS-037 | registry_source_id=`shareholder_data` |

## F — Evidence Boundary（VR-NS-038–VR-NS-040）

| ID | 规则 |
|----|------|
| VR-NS-038 | 不重开 executive_shareholding / shareholder_change / equity_pledge / RSU / block_trade / margin / disclosure / known-event / DLC006R |
| VR-NS-039 | 不写 A/B/C 产物根 · **不** mutate AT/SD first-slice lock/live roots · **不** mutate AT next-slice lock/live · **不** mutate FIA first/next-slice lock/live roots |
| VR-NS-040 | exclude_flags 含 exclude_688671;exclude_301259;exclude_first_slice_mutate |

## G — Governance（VR-NS-041–VR-NS-042）

| ID | 规则 |
|----|------|
| VR-NS-041 | standing D 授权 offline lock/VR/fixtures · runner/S4/live 另批 · ESS H3/H4 禁止盲探 · AT next-slice live 仍须另批 |
| VR-NS-042 | 禁止 verified / production_ready / bare PASS / commit/push（本任务） |
