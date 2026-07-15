# CNINFO D 类 fund_industry_allocation — D-FM-18 DFIA005 Single-Probe Bounded Retry

_生成时间：2026-07-15 · D-FM-18 · wall≈2.8s_

> **性质：** standing-scope DFIA005 单探针 bounded retry · **CNINFO=1** · **不** mutate universe lock · **不** commit/push · **NOT verified** · **NOT production_ready** · **NOT bare PASS**

## Task

| 项 | 值 |
|----|-----|
| task_id | **D-FM-18** |
| track | D · d-class-executor |
| phase | `fund_industry_allocation_dfia005_single_probe_bounded_retry` |
| standing_scope | full-market shareholder / capital |
| controller_execution_allowed | **false**（仅阻 controller；standing capital 授权本任务单探针） |
| prefer taken | (1) DFIA005 single-probe CNINFO≤1（高于 next capital offline discovery） |
| commit/push | **禁止**（本任务） |

## Authorization Boundary

| 项 | 值 |
|----|-----|
| approve flag | `--approve-d-class-fund-industry-allocation-first-slice` |
| Live CNINFO | **allowed** · **硬上限 1** · 仅 `rdate=20251231` |
| universe lock | DFIA001–DFIA005 · **未修改** |
| DFIA001–DFIA004 | **未重探** |
| DLC006R / 301259 / 688671 | **未重开** |
| A/B/C | **未触碰** |
| Level-2 IDLE | **否** |

Universe lock sha256（执行前后一致）:

```text
d74f965618c8125445cdad9ba0605d33f0897cb1c59b85deef4370813f976a55
```

## Command Executed

```bash
python lab/run_cninfo_d_class_fund_industry_allocation_dfia005_single_probe.py \
  --live \
  --approve-d-class-fund-industry-allocation-first-slice
```

**exit code：** **0** · **wall ≈ 2.77s** · **CNINFO = 1**

## Result

| 项 | 值 |
|----|-----|
| endpoint | `https://www.cninfo.com.cn/data20/fund/industry` |
| probe | `rdate_20251231` · params `{rdate: 20251231}` · `params_location=form` |
| http_status | **200** |
| retrieval_status | **found** |
| records | **19** |
| expected_behavior | `empty_but_valid`（lock **未改**） |
| runner acceptable | **yes**（宽 `found` 路径；与 D-FM-16 已记行为一致） |
| caveat | **`empty_control_anchor_stale`** |
| transport | **cleared**（D-FM-13 Read timeout **不再复现**） |

### Caveat 解读

1. **运输 caveat 清除：** D-FM-13 第三共享探针 `rdate=20251231` Read timeout(10s) 在本单探针下 **HTTP 200 / 2.8s** 成功。
2. **空控锚点过期：** Phase2 / lock 将 `rdate=20251231` 作 empty control；本探针返回 **19** 行（ENDDATE=2025-12-31），与 `empty_but_valid` 期望漂移。
3. **不** 在本任务 mutate lock / 不改 VR / 不无界重跑 FIA 5-case live。

### Counterfactual after D-FM-17 + D-FM-18

| case | expected | live status | acceptable |
|------|----------|-------------|:----------:|
| DFIA001 | captured_normal_or_empty_but_valid | empty_but_valid (D-FM-13) | yes* |
| DFIA002 | captured_normal | found | yes |
| DFIA003 | captured_normal | found | yes |
| DFIA004 | captured_normal_or_empty_but_valid | empty_but_valid | yes |
| DFIA005 | empty_but_valid | found(19) · transport cleared | yes† |

\* D-FM-17 lock amend 反事实。  
† runner 宽 found；探针层 caveat=`empty_control_anchor_stale`。

## Artifacts

| artifact | path |
|----------|------|
| probe script | `lab/run_cninfo_d_class_fund_industry_allocation_dfia005_single_probe.py` |
| unit test | `lab/test_cninfo_d_class_fund_industry_allocation_dfia005_single_probe.py` |
| live report | `outputs/validation/cninfo_d_class_fund_industry_allocation_dfia005_single_probe/reports/dfia005_single_probe_live_report.csv` |
| live summary | `outputs/validation/cninfo_d_class_fund_industry_allocation_dfia005_single_probe/reports/dfia005_single_probe_live_summary.md` |
| live snapshot | `outputs/validation/cninfo_d_class_fund_industry_allocation_dfia005_single_probe/live_snapshots/DFIA005_fund_industry_allocation.json` |
| console log | `outputs/validation/cninfo_d_class_fund_industry_allocation_dfia005_single_probe/reports/live_dfm18_console_20260715.log` |
| matrix | `outputs/validation/cninfo_d_class_fund_industry_allocation_dfm18_dfia005_single_probe_matrix_20260715.csv` |
| this evidence | `outputs/validation/cninfo_d_class_fund_industry_allocation_dfm18_dfia005_single_probe_20260715.md` |

## Tests

| 套件 | 结果 |
|------|------|
| `lab/test_cninfo_d_class_fund_industry_allocation_dfia005_single_probe.py` | **5/5 PASS**（mock · CNINFO=0） |

## Gates

```text
d_class_fund_industry_allocation_first_slice_approval_gate = STANDING_SCOPE_AUTHORIZED
d_class_fund_industry_allocation_dfia005_single_probe_gate = PASS_WITH_CAVEAT
d_class_fund_industry_allocation_first_slice_live_gate = NOT_APPROVED
d_class_fund_industry_allocation_first_slice_execution_gate = PASS_WITH_CAVEAT
caveat = empty_control_anchor_stale
transport_cleared = true
universe_lock_mutated = false
```

**NOT verified** · **NOT production_ready** · **NOT bare PASS**

## Allow-list / Safety

| 项 | 状态 |
|----|------|
| A/B/C tracks | **未触碰** |
| DLC006R / 301259 / 688671 | **未重开** |
| Level-2 IDLE | **否** |
| PDF/OCR/DB/MinIO/RAG | **no** |
| universe lock mutate | **no** |
| first-slice 5-case live overwrite | **no**（独立 output dir） |
| commit / push | **no** |

## Next Step Recommendation

Primary：controller commit-boundary（D-FM-18 单探针脚本 + 证据 · executor **不** commit/push）。

Secondary（另批）：

1. DFIA005 lock/expectation amend（`captured_normal_or_empty_but_valid`）或另选 empty rdate 空控 · **CNINFO=0** 离线包
2. next capital discovery offline（如 `executive_shareholding_summary`）· **CNINFO=0**
3. **不** 无界重跑 FIA / SD / AT live · **不** Level-2 IDLE · **不** reopen DLC006R

## Status Block

```text
task_id = D-FM-18
phase = fund_industry_allocation_dfia005_single_probe_bounded_retry
cninfo_calls = 1
live = EXECUTED_BOUNDED_SINGLE_PROBE
probe_gate = PASS_WITH_CAVEAT
caveat = empty_control_anchor_stale
transport_cleared = true
universe_lock_mutated = false
ready_for_commit = true
```
