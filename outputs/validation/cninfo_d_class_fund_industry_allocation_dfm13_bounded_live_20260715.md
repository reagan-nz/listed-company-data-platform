# CNINFO D 类 fund_industry_allocation — D-FM-13 Bounded Real Live

_生成时间：2026-07-15 · D-FM-13 · wall≈15s（成功 live）· 另含 attempt-1 超时预跑_

> **性质：** standing-scope bounded real live · **NOT verified** · **NOT production_ready** · **NOT bare PASS** · **无 commit** · **无 push**

## Task

| 项 | 值 |
|----|-----|
| task_id | **D-FM-13** |
| track | D · d-class-executor |
| phase | `fund_industry_allocation_first_slice_bounded_real_live` |
| standing_scope | full-market shareholder / capital |
| controller_execution_allowed | **false**（仅阻 controller；executor 本任务已跑 bounded live） |
| prefer taken | FIA bounded real live（live-path offline mock 已在 D-FM-12） |
| commit/push | **禁止**（本任务） |

## Authorization Boundary

| 项 | 值 |
|----|-----|
| approve flag | `--approve-d-class-fund-industry-allocation-first-slice` |
| Live CNINFO | **allowed**（standing capital scope · 本任务） |
| shared probes | ≤ **3**（default · rdate_20260331 · rdate_20251231） |
| universe lock | DFIA001–DFIA005 · **未修改** |
| DLC006R / 301259 / 688671 | **未重开** |
| A/B/C | **未触碰** |

Universe lock sha256（执行前后一致）:

```text
048799c7279f3c2ce0d3392a5404ef8f3e0e9532ed59d7bdaa7b31b910f3e8ee
```

## Code Fix（pre-live）

Registry `params_location=none` 会使 `_cninfo_request` **静默丢弃** rdate override。D-FM-13 在 `execute_fund_industry_allocation_first_slice_live` 内将 `params_location` 强制为 `form`，保证共享探针参数真正发出。

- `lab/run_cninfo_d_class_tiny_live_validation.py` — form override
- `lab/test_cninfo_d_class_fund_industry_allocation_first_slice_runner.py` — mock 断言 `params_location=form`

## Command Executed（attempt-2 · evidence）

```bash
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --live \
  --fund-industry-allocation-first-slice \
  --approve-d-class-fund-industry-allocation-first-slice \
  --universe-csv outputs/validation/cninfo_d_class_fund_industry_allocation_first_slice_universe_lock_20260715.csv \
  --output-root outputs/validation/cninfo_d_class_fund_industry_allocation_first_slice
```

**exit code：** **0** · **wall ≈ 15s**

## Result

| 项 | 值 |
|----|-----|
| endpoint | `https://www.cninfo.com.cn/data20/fund/industry` |
| CNINFO calls（counted） | **2**（default + rdate_20260331 成功；rdate_20251231 Read timeout · 未计入 stats） |
| acceptable | **3/5** |
| execution gate | **`PASS_WITH_CAVEAT`** |
| live_gate | **NOT_APPROVED**（常量；本任务仅授权单次 live） |

### Per-case outcomes

| case_id | expected | retrieval_status | records | acceptable | failure_type |
|---------|----------|------------------|--------:|:----------:|--------------|
| DFIA001 | captured_normal | empty_but_valid | 0 | no | expectation_mismatch（default 截面无 C26） |
| DFIA002 | captured_normal | found | 16 | yes | — |
| DFIA003 | captured_normal | found | 19 | yes | — |
| DFIA004 | captured_normal_or_empty_but_valid | empty_but_valid | 0 | yes | — |
| DFIA005 | empty_but_valid | http_error | 0 | no | transport_or_http_error（rdate_20251231 timeout） |

### Caveats

1. **DFIA001**：default 最新截面（ENDDATE=2026-06-30 · 16 行）经 F001V=C26 过滤后 0 行 → 合法 empty，但与 `captured_normal` 期望不一致。
2. **DFIA005**：第三共享探针 `rdate=20251231` Read timeout(10s)；stats 仅计成功 HTTP，故 `cninfo_calls=2`。
3. **attempt-1**（修复前）：3 探针均 timeout · counted=0 · `FAIL_REVIEW_REQUIRED`（预跑，非本证据主结果）。

## Artifacts

| artifact | path |
|----------|------|
| live report | `outputs/validation/cninfo_d_class_fund_industry_allocation_first_slice/reports/d_class_fund_industry_allocation_first_slice_live_report.csv` |
| quality report | `outputs/validation/cninfo_d_class_fund_industry_allocation_first_slice/reports/d_class_fund_industry_allocation_first_slice_quality_report.csv` |
| live summary | `outputs/validation/cninfo_d_class_fund_industry_allocation_first_slice/reports/d_class_fund_industry_allocation_first_slice_live_summary.md` |
| console log | `outputs/validation/cninfo_d_class_fund_industry_allocation_first_slice/reports/live_dfm13_console_20260715.log` |
| live snapshots | `.../live_snapshots/DFIA00{1-5}_fund_industry_allocation.json`（on-disk · 可能 gitignored） |
| this evidence | `outputs/validation/cninfo_d_class_fund_industry_allocation_dfm13_bounded_live_20260715.md` |

## Tests

| 套件 | 结果 |
|------|------|
| `lab/test_cninfo_d_class_fund_industry_allocation_first_slice_runner.py` | **15/15 PASS** |
| `lab/test_cninfo_d_class_fund_industry_allocation_fixtures.py` | **15/15 PASS** |
| `lab/test_cninfo_d_class_fund_industry_allocation_offline_prep.py` | **6/6 PASS** |

## Gates

```text
d_class_fund_industry_allocation_first_slice_approval_gate = STANDING_SCOPE_AUTHORIZED
d_class_fund_industry_allocation_first_slice_runner_extension_gate = READY_FOR_APPROVAL
d_class_fund_industry_allocation_first_slice_live_path_gate = READY_FOR_APPROVAL
d_class_fund_industry_allocation_first_slice_live_gate = NOT_APPROVED
d_class_fund_industry_allocation_first_slice_execution_gate = PASS_WITH_CAVEAT
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
| commit / push | **no** |

## Next Step Recommendation

Primary：controller commit-boundary（D-FM-13 form 修复 + live 证据 · executor **不** commit/push）。

Secondary：shareholder_data / abnormal_trading bounded live（standing capital）· 或 FIA DFIA001/DFIA005 期望/锚点另批复核（**不** reopen DLC006R）。

## Status Block

```text
task_id = D-FM-13
phase = fund_industry_allocation_first_slice_bounded_real_live
cninfo_calls = 2
live = EXECUTED_BOUNDED
execution_gate = PASS_WITH_CAVEAT
acceptable = 3/5
ready_for_commit = true
```
