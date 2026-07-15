# CNINFO D 类 shareholder_data — D-FM-09 Live-Path Offline Mock

_生成时间：2026-07-15 · D-FM-09_

> **性质：** shared live-path 实现 + offline mock 测试 · **CNINFO = 0** · **无真实 live** · **不是 verified**

## Scope

实现 `shareholder_data` first-slice **shared live path**（1 次 `rdate` 全市场截面 + 离线 SECCODE 过滤），仅以 **offline mock** 验证；`controller_execution_allowed=false`，**不**执行真实 CNINFO。

| 项 | 值 |
|----|-----|
| runner | `lab/run_cninfo_d_class_tiny_live_validation.py` |
| mode | `--shareholder-data-first-slice` + `--live` + `--approve-d-class-shareholder-data-first-slice` |
| endpoint | `data20/shareholeder/data` · records_path=`data.records` · `rdate_report_period` |
| shared model | **1** CNINFO · case_id=`SHARED_RDATE` · 按 SECCODE 拆 DSD001–DSD005 |
| acceptance | ≥3/5 → `PASS_WITH_CAVEAT`（不是 bare PASS） |
| mock scenario | 截面仅含非目标 SECCODE → 全案 empty · DSD001 mismatch · DSD002–005 acceptable → **4/5** |

## Implementation

- `execute_shareholder_data_first_slice_live`（替换 `live_not_implemented` stub）
- `assess_shareholder_data_first_slice_shared_case` · live snapshot writer
- request-cap：禁止非 SHARED 分摊请求 · shared ≤ planned_shared(1)
- live_report · quality_report · live_summary writers（含 shared_cninfo_requests）
- gates：`live_path_gate=READY_FOR_APPROVAL` · `live_gate=NOT_APPROVED`

**未改：** universe lock · Tier-1 fixtures · A/B/C · closed D tracks · DLC006R · abnormal_trading 真实 live

## Tests

| 套件 | 结果 |
|------|------|
| `lab/test_cninfo_d_class_shareholder_data_first_slice_runner.py` | **19/19 PASS** |
| `lab/test_cninfo_d_class_shareholder_data_fixtures.py` | **15/15 PASS** |

Mock live 断言：`requests.get` / `requests.post` **未调用**；`_cninfo_request` mock 恰好 1 次；产物写入临时 `cninfo_d_class_shareholder_data_first_slice` 根。

## Gates

```text
d_class_shareholder_data_first_slice_runner_extension_gate = READY_FOR_APPROVAL
d_class_shareholder_data_first_slice_live_path_gate = READY_FOR_APPROVAL
d_class_shareholder_data_first_slice_live_gate = NOT_APPROVED
```

**NOT verified** · **NOT production_ready** · **NOT bare PASS**

## Explicit Non-Claims

- 不 claim 真实 live 已跑通
- 不 reopen DLC006R / 301259 / 688671
- 不触碰 A/B/C 产物根
- 不 commit / push（executor）
- 真实 live 须 `controller_execution_allowed` + `--approve-d-class-shareholder-data-first-slice`

```text
task_id = D-FM-09
phase = shareholder_data_shared_live_path_offline_mock
ready_for_commit = true
cninfo_calls = 0
```
