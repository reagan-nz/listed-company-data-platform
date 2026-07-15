# CNINFO D 类 abnormal_trading — D-FM-15 Bounded Real Live

_生成时间：2026-07-15 · D-FM-15 · wall≈8s_

> **性质：** standing-scope bounded real live · **NOT verified** · **NOT production_ready** · **NOT bare PASS** · **无 commit** · **无 push**

## Task

| 项 | 值 |
|----|-----|
| task_id | **D-FM-15** |
| track | D · d-class-executor |
| phase | `abnormal_trading_first_slice_bounded_real_live` |
| standing_scope | full-market shareholder / capital |
| controller_execution_allowed | **false**（仅阻 controller；standing capital 授权本任务 bounded live） |
| prefer taken | AT bounded real live（DAT001–DAT005；FIA caveat / next capital 次选） |
| commit/push | **禁止**（本任务） |

## Authorization Boundary

| 项 | 值 |
|----|-----|
| approve flag | `--approve-d-class-abnormal-trading-first-slice` |
| Live CNINFO | **allowed**（standing capital scope · 本任务） |
| per-case / total | ≤1 / ≤20 · planned **5** · counted **5** |
| universe lock | DAT001–DAT005 · **未修改** |
| DLC006R / 301259 / 688671 | **未重开** |
| A/B/C | **未触碰** |
| FIA / shareholder_data | **未重跑 live** · **未 mutate universe** |

Universe lock sha256（执行前后一致）:

```text
d197b9618dc86c89d2a034addb75c37999baaf58e7455ab8626facd3f02adac2
```

## Command Executed

```bash
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --live \
  --abnormal-trading-first-slice \
  --approve-d-class-abnormal-trading-first-slice \
  --universe-csv outputs/validation/cninfo_d_class_abnormal_trading_first_slice_universe_lock_20260715.csv \
  --output-root outputs/validation/cninfo_d_class_abnormal_trading_first_slice
```

**exit code：** **0** · **wall ≈ 8s**

## Result

| 项 | 值 |
|----|-----|
| endpoint | `https://www.cninfo.com.cn/data/statis/getMarketStatisticsData` |
| query mode | **single_day_paged** · sdate=edate=**2026-07-03** |
| records_path | `marketList`（公司过滤） |
| CNINFO calls（counted） | **5**（1 per case） |
| acceptable | **4/5** |
| execution gate | **`PASS_WITH_CAVEAT`**（≥3/5；不上调为 bare PASS） |
| live_gate | **NOT_APPROVED**（常量；本任务仅授权单次 live） |

### Per-case outcomes

| case_id | expected | retrieval_status | records | acceptable | failure_type |
|---------|----------|------------------|--------:|:----------:|--------------|
| DAT001 | captured_normal_or_needs_review | empty_but_valid | 0 | no | expectation_mismatch |
| DAT002 | captured_normal_or_empty_but_valid | empty_but_valid | 0 | yes | — |
| DAT003 | captured_normal_or_empty_but_valid | empty_but_valid | 0 | yes | — |
| DAT004 | captured_normal_or_empty_but_valid | empty_but_valid | 0 | yes | — |
| DAT005 | empty_but_valid | empty_but_valid | 0 | yes | — |

### Caveats

1. **DAT001：** Tier-0 cite 案期望 `captured_normal_or_needs_review`，但 anchor `2026-07-03` 经 marketList 公司过滤后 0 行 → 合法 `empty_but_valid`，与期望不匹配（`expectation_mismatch`）。与 D-FM-05 offline mock 稀疏日情景一致。
2. **DAT002–DAT004：** 稀疏日 company-level empty 在 `captured_normal_or_empty_but_valid` 下可接受。
3. **DAT005：** empty control 与期望一致。
4. **Gate 命名：** 即使达阈值，execution_gate 仍为 `PASS_WITH_CAVEAT`（first-slice 设计；**不是** verified / production_ready / bare PASS）。
5. **无** transport/HTTP 失败（5/5 HTTP 200）。

## Artifacts

| artifact | path |
|----------|------|
| live report | `outputs/validation/cninfo_d_class_abnormal_trading_first_slice/reports/d_class_abnormal_trading_first_slice_live_report.csv` |
| quality report | `outputs/validation/cninfo_d_class_abnormal_trading_first_slice/reports/d_class_abnormal_trading_first_slice_quality_report.csv` |
| live summary | `outputs/validation/cninfo_d_class_abnormal_trading_first_slice/reports/d_class_abnormal_trading_first_slice_live_summary.md` |
| console log | `outputs/validation/cninfo_d_class_abnormal_trading_first_slice/reports/live_dfm15_console_20260715.log` |
| live snapshots | `.../live_snapshots/DAT00{1-5}_abnormal_trading.json`（on-disk · 可能 gitignored） |
| this evidence | `outputs/validation/cninfo_d_class_abnormal_trading_dfm15_bounded_live_20260715.md` |

## Tests（pre-live offline）

| 套件 | 结果 |
|------|------|
| `lab/test_cninfo_d_class_abnormal_trading_first_slice_runner.py` | **18/18 PASS** |
| `lab/test_cninfo_d_class_abnormal_trading_fixtures.py` | **15/15 PASS** |

## Gates

```text
d_class_abnormal_trading_first_slice_approval_gate = STANDING_SCOPE_AUTHORIZED
d_class_abnormal_trading_first_slice_runner_extension_gate = READY_FOR_APPROVAL
d_class_abnormal_trading_first_slice_live_path_gate = READY_FOR_APPROVAL
d_class_abnormal_trading_first_slice_live_gate = NOT_APPROVED
d_class_abnormal_trading_first_slice_execution_gate = PASS_WITH_CAVEAT
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
| FIA / SD reopen / re-live | **no** |
| commit / push | **no** |

## Next Step Recommendation

Primary：controller commit-boundary（D-FM-15 AT live 证据包）· executor **不** commit/push。

Secondary：FIA DFIA001/DFIA005 期望/锚点另批复核（**不** reopen DLC006R · **不**无界重跑 FIA live）· 或 next capital offline planning。

## Status Block

```text
task_id = D-FM-15
phase = abnormal_trading_first_slice_bounded_real_live
cninfo_calls = 5
live = EXECUTED_BOUNDED
execution_gate = PASS_WITH_CAVEAT
acceptable = 4/5
ready_for_commit = true
```
