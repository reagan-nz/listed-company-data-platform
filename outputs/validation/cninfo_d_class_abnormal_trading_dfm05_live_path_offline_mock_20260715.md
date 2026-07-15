# CNINFO D 类 abnormal_trading — D-FM-05 Live-Path Offline Mock

_生成时间：2026-07-15 · D-FM-05_

> **性质：** live-path 实现 + offline mock 测试 · **CNINFO = 0** · **无真实 live** · **不是 verified**

## Scope

实现 `abnormal_trading` first-slice **live path**（对标 shareholder_change / executive_shareholding），仅以 **offline mock** 验证；`controller_execution_allowed=false`，**不**执行真实 CNINFO。

| 项 | 值 |
|----|-----|
| runner | `lab/run_cninfo_d_class_tiny_live_validation.py` |
| mode | `--abnormal-trading-first-slice` + `--live` + `--approve-d-class-abnormal-trading-first-slice` |
| endpoint | `getMarketStatisticsData` · records_path=`marketList` · single_day_paged |
| acceptance | ≥3/5 → `PASS_WITH_CAVEAT`（不是 bare PASS） |
| mock scenario | 全案 empty sparse-day → DAT001 mismatch · DAT002–005 acceptable → **4/5** |

## Implementation

- `execute_abnormal_trading_first_slice_live`（替换 `live_not_implemented` stub）
- acceptable / failure_type / request-cap / execution-gate helpers
- live_report · quality_report · live_summary writers
- LIVE/QUALITY report column schemas

**未改：** universe lock · Tier-1 fixtures · S4 dry-run path · A/B/C · closed D tracks · DLC006R

## Tests

| 套件 | 结果 |
|------|------|
| `lab/test_cninfo_d_class_abnormal_trading_first_slice_runner.py` | **18/18 PASS** |
| `lab/test_cninfo_d_class_abnormal_trading_fixtures.py` | **15/15 PASS** |

Mock live 断言：`requests.get` / `requests.post` **未调用**；产物写入临时 `cninfo_d_class_abnormal_trading_first_slice` 根。

## Gates

```text
d_class_abnormal_trading_fixture_vr_gate = PASS_OFFLINE
d_class_abnormal_trading_first_slice_runner_extension_gate = READY_FOR_APPROVAL
d_class_abnormal_trading_first_slice_live_path_gate = READY_FOR_APPROVAL
d_class_abnormal_trading_first_slice_live_gate = NOT_APPROVED
```

**NOT verified** · **NOT production_ready** · **NOT bare PASS**

## Explicit Non-Claims

- 不 claim 真实 live 已跑通
- 不 reopen DLC006R / 301259 / 688671
- 不触碰 A/B/C 产物根
- 不 commit / push（executor）
- 真实 live 须 `controller_execution_allowed` + `--approve-d-class-abnormal-trading-first-slice`

```text
task_id = D-FM-05
phase = abnormal_trading_live_path_offline_mock
ready_for_commit = true
cninfo_calls = 0
```
