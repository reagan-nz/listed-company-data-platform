# CNINFO D 类 fund_industry_allocation — D-FM-17 DFIA001 Lock Amend（Offline）

_生成时间：2026-07-15 · D-FM-17 · wall≈短（纯离线）_

> **性质：** DFIA001 `expected_behavior` lock amend + VR/planned/dryrun/test 同步 · **CNINFO = 0** · **无 live** · **无 commit/push**
>
> **NOT verified** · **NOT production_ready** · **NOT bare PASS**

## Task

| 项 | 值 |
|----|-----|
| task_id | **D-FM-17** |
| track | D · d-class-executor |
| phase | `fund_industry_allocation_dfia001_lock_amend_offline` |
| standing_scope | full-market shareholder / capital |
| controller_execution_allowed | **false** |
| prefer taken | (1) DFIA001 lock amend offline + fixture/VR sync（高于 DFIA005 probe / next capital discovery） |
| commit/push | **禁止** |

## Authorization Boundary

| 项 | 值 |
|----|-----|
| CNINFO live | **0**（本任务） |
| universe lock mutate | **yes · 仅 DFIA001 expected_behavior** |
| FIA / SD / AT re-live | **no** |
| DFIA005 lock / anchor | **未改**（保持 rdate=20251231 / empty_but_valid） |
| DLC006R / 301259 / 688671 | **未重开** |
| A/B/C | **未触碰** |
| Level-2 IDLE | **否** |

## Amend

| 字段 | 旧 | 新 |
|------|----|----|
| DFIA001.expected_behavior | `captured_normal` | `captured_normal_or_empty_but_valid` |
| DFIA001.industry_code | C26 | **KEEP** |
| DFIA001.query_mode | default | **KEEP** |
| DFIA001.approval_task_id | D-FM-11 | **KEEP**（notes 标注 D-FM-17） |
| DFIA002–DFIA005 | — | **未改** |
| draft sketch | captured_normal | **只读历史 · 未改** |

Universe lock sha256（amend 后）:

```text
d74f965618c8125445cdad9ba0605d33f0897cb1c59b85deef4370813f976a55
```

依据：D-FM-16 `expectation_too_strict` · 对齐 DFIA004 mixed policy · Tier-0 sample_raw 非 rolling-default C26 保证。

## Fixture / VR Sync

| 项 | 动作 |
|----|------|
| Tier-1 `DFIA001_found.json` | **保留**（captured 路径在新期望下仍合法） |
| 新增 empty fixture | **否**（最小必要；empty 路径由 lock + runner 规则覆盖） |
| VR-012 注释 | 已追加 D-FM-17 amend 说明 |
| approval package 表 | DFIA001 行已更新 |
| planned snapshot / dry-run | 已同步 `captured_normal_or_empty_but_valid` |

## Offline Counterfactual（D-FM-13 live · CNINFO=0）

对既有 live_report 摘要调用 `is_fund_industry_allocation_first_slice_acceptable`：

| case_id | lock expected（新） | live retrieval | acceptable |
|---------|-------------------|----------------|:----------:|
| DFIA001 | captured_normal_or_empty_but_valid | empty_but_valid | **yes** |
| DFIA002 | captured_normal | found | yes |
| DFIA003 | captured_normal | found | yes |
| DFIA004 | captured_normal_or_empty_but_valid | empty_but_valid | yes |
| DFIA005 | empty_but_valid | http_error | **no**（transport） |

```text
counterfactual_acceptable = 4/5
execution_gate_counterfactual = PASS_WITH_CAVEAT
dfia005_caveat = transport_or_http_error（未本任务修复）
```

## Explicit Non-Actions

- **不** 无界重跑 FIA live · **不** re-live SD/AT
- **不** DFIA005 单探针 live（另批）
- **不** reopen DLC006R / 301259 / 688671
- **不** Level-2 IDLE · **不** 触碰 A/B/C
- **不** 改 runner 判定逻辑（仅 sync 单测期望）
- **不** 本任务 commit / push
- **不** 改 draft sketch

## Artifacts

| artifact | path |
|----------|------|
| this report | `outputs/validation/cninfo_d_class_fund_industry_allocation_dfm17_dfia001_lock_amend_20260715.md` |
| matrix | `outputs/validation/cninfo_d_class_fund_industry_allocation_dfm17_dfia001_lock_amend_matrix_20260715.csv` |
| universe lock | `outputs/validation/cninfo_d_class_fund_industry_allocation_first_slice_universe_lock_20260715.csv` |
| next-step | `outputs/validation/cninfo_d_class_fund_industry_allocation_first_slice_next_step_recommendation_20260715.md` |

## Tests

| 套件 | 结果 |
|------|------|
| `lab/test_cninfo_d_class_fund_industry_allocation_first_slice_runner.py` | **15/15 PASS** |
| `lab/test_cninfo_d_class_fund_industry_allocation_fixtures.py` | **15/15 PASS** |
| `lab/test_cninfo_d_class_fund_industry_allocation_offline_prep.py` | **6/6 PASS** |
| dry-run regenerate | **PASS** · CNINFO=0 · planned_shared=3 |
| aggregate | **36 ran · OK** · CNINFO=0 |

## Gates

```text
d_class_fund_industry_allocation_first_slice_approval_gate = STANDING_SCOPE_AUTHORIZED
d_class_fund_industry_allocation_first_slice_runner_extension_gate = READY_FOR_APPROVAL
d_class_fund_industry_allocation_first_slice_live_path_gate = READY_FOR_APPROVAL
d_class_fund_industry_allocation_first_slice_live_gate = NOT_APPROVED
d_class_fund_industry_allocation_first_slice_execution_gate = PASS_WITH_CAVEAT
d_class_fund_industry_allocation_dfm16_expectation_anchor_review_gate = PASS_OFFLINE
d_class_fund_industry_allocation_dfm17_dfia001_lock_amend_gate = PASS_OFFLINE
```

## Next Step Recommendation

Primary：controller commit-boundary（D-FM-17 DFIA001 lock amend 包）· executor **不** commit/push。

Secondary（另批 · 择一）：

1. **DFIA005** 授权下单探针 bounded retry（仅 `rdate=20251231` · CNINFO≤1）
2. next capital **discovery** offline planning（禁 Level-2 IDLE · 禁 re-live SD/AT）

## Status Block

```text
task_id = D-FM-17
phase = fund_industry_allocation_dfia001_lock_amend_offline
cninfo_calls = 0
live = NOT_RUN
universe_lock_mutated = true
mutate_scope = DFIA001.expected_behavior_only
dfia001_expected = captured_normal_or_empty_but_valid
dfia005_lock = unchanged
counterfactual_acceptable = 4/5
amend_gate = PASS_OFFLINE
ready_for_commit = true
```
