# CNINFO D 类 shareholder_data — D-FM-14 Bounded Real Live

_生成时间：2026-07-15 · D-FM-14 · wall≈12s_

> **性质：** standing-scope bounded real live · **NOT verified** · **NOT production_ready** · **NOT bare PASS** · **无 commit** · **无 push**

## Task

| 项 | 值 |
|----|-----|
| task_id | **D-FM-14** |
| track | D · d-class-executor |
| phase | `shareholder_data_first_slice_bounded_real_live` |
| standing_scope | full-market shareholder / capital |
| controller_execution_allowed | **false**（仅阻 controller；standing capital 授权本任务 bounded live） |
| prefer taken | SD bounded real live（FIA caveats 另批；AT 次选） |
| commit/push | **禁止**（本任务） |

## Authorization Boundary

| 项 | 值 |
|----|-----|
| approve flag | `--approve-d-class-shareholder-data-first-slice` |
| Live CNINFO | **allowed**（standing capital scope · 本任务） |
| shared probes | **1**（`SHARED_RDATE` · `rdate=20260331`） |
| universe lock | DSD001–DSD005 · **未修改** |
| DLC006R / 301259 / 688671 | **未重开** |
| A/B/C | **未触碰** |
| FIA | **未重跑 live** · **未 mutate universe** |

Universe lock sha256（执行前后一致）:

```text
06633a0da42d5ddc669935b64942f4182611017d55907d7076528fc0993917b5
```

## Registry Note（no code change）

`shareholder_data` registry `params_location=query` · rdate override 正常发出 · **无需** FIA 式 `params_location=form` 强制覆盖。

## Command Executed

```bash
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --live \
  --shareholder-data-first-slice \
  --approve-d-class-shareholder-data-first-slice \
  --universe-csv outputs/validation/cninfo_d_class_shareholder_data_first_slice_universe_lock_20260715.csv \
  --output-root outputs/validation/cninfo_d_class_shareholder_data_first_slice
```

**exit code：** **0** · **wall ≈ 12s**

## Result

| 项 | 值 |
|----|-----|
| endpoint | `https://www.cninfo.com.cn/data20/shareholeder/data` |
| CNINFO calls（counted） | **1**（shared rdate 全市场截面） |
| acceptable | **5/5** |
| execution gate | **`PASS_WITH_CAVEAT`**（设计常量；≥3/5 不上调为 bare PASS） |
| live_gate | **NOT_APPROVED**（常量；本任务仅授权单次 live） |

### Per-case outcomes

| case_id | expected | retrieval_status | records | acceptable | failure_type |
|---------|----------|------------------|--------:|:----------:|--------------|
| DSD001 | captured_normal | found | 1 | yes | — |
| DSD002 | captured_normal_or_empty_but_valid | found | 1 | yes | — |
| DSD003 | captured_normal_or_empty_but_valid | found | 1 | yes | — |
| DSD004 | captured_normal_or_empty_but_valid | found | 1 | yes | — |
| DSD005 | empty_but_valid | empty_but_valid | 0 | yes | — |

### Caveats

1. **Gate 命名：** 即使 5/5 acceptable，execution_gate 仍为 `PASS_WITH_CAVEAT`（first-slice 设计；**不是** verified / production_ready / bare PASS）。
2. **DSD005：** 退市控制案在共享截面经 SECCODE 过滤后 0 行 · 与 `empty_but_valid` 期望一致。
3. **无** 额外 transport/HTTP/expectation 失败；本切片无 FIA 式 DFIA001/DFIA005 caveat。

## Artifacts

| artifact | path |
|----------|------|
| live report | `outputs/validation/cninfo_d_class_shareholder_data_first_slice/reports/d_class_shareholder_data_first_slice_live_report.csv` |
| quality report | `outputs/validation/cninfo_d_class_shareholder_data_first_slice/reports/d_class_shareholder_data_first_slice_quality_report.csv` |
| live summary | `outputs/validation/cninfo_d_class_shareholder_data_first_slice/reports/d_class_shareholder_data_first_slice_live_summary.md` |
| console log | `outputs/validation/cninfo_d_class_shareholder_data_first_slice/reports/live_dfm14_console_20260715.log` |
| live snapshots | `.../live_snapshots/DSD00{1-5}_shareholder_data.json`（on-disk · 可能 gitignored） |
| this evidence | `outputs/validation/cninfo_d_class_shareholder_data_dfm14_bounded_live_20260715.md` |

## Tests（pre-live offline）

| 套件 | 结果 |
|------|------|
| `lab/test_cninfo_d_class_shareholder_data_first_slice_runner.py` | **19/19 PASS** |
| `lab/test_cninfo_d_class_shareholder_data_fixtures.py` | **15/15 PASS** |
| `lab/test_cninfo_d_class_shareholder_data_offline_prep.py` | **6/6 PASS** |

## Gates

```text
d_class_shareholder_data_first_slice_approval_gate = STANDING_SCOPE_AUTHORIZED
d_class_shareholder_data_first_slice_runner_extension_gate = READY_FOR_APPROVAL
d_class_shareholder_data_first_slice_live_path_gate = READY_FOR_APPROVAL
d_class_shareholder_data_first_slice_live_gate = NOT_APPROVED
d_class_shareholder_data_first_slice_execution_gate = PASS_WITH_CAVEAT
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
| FIA reopen / re-live | **no** |
| commit / push | **no** |

## Next Step Recommendation

Primary：controller commit-boundary（D-FM-14 SD live 证据包）· executor **不** commit/push。

Secondary：abnormal_trading bounded live（DAT001–DAT005 · standing capital · CNINFO ≤5）· 或 FIA DFIA001/DFIA005 期望/锚点另批复核（**不** reopen DLC006R）。

## Status Block

```text
task_id = D-FM-14
phase = shareholder_data_first_slice_bounded_real_live
cninfo_calls = 1
live = EXECUTED_BOUNDED
execution_gate = PASS_WITH_CAVEAT
acceptable = 5/5
ready_for_commit = true
```
