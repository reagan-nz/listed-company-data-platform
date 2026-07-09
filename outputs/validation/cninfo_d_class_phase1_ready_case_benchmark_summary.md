# CNINFO D 类 Phase 1 Ready-case Benchmark 摘要

_生成时间：2026-07-09 06:37:32 UTC_

> **性质：** 离线 fixture benchmark；**无 CNINFO**；**无 live**；**无 harvest**。

## Counts

| 指标 | 值 |
|------|-----|
| Total cases | 7 |
| Passed | 7 |
| Failed | 0 |
| Schema version | d_class_phase1_freeze_v1 |
| CNINFO calls | **0** |

## Component Coverage

- Components exercised: **6** — block_trade, equity_pledge, executive_shareholding, margin_trading, restricted_shares_unlock, shareholder_change
- Scenarios: empty_but_valid (**2/2** pass) · captured_normal · needs_review (**1/1** pass)

## Quality Policy Coverage

- `empty_but_valid`: DC001 margin_trading · DC004 equity_pledge — retrieval=`empty_but_valid`, quality=`pass`
- `captured` + `pass`: DC002–DC006 — retrieval=`found`, required fields from freeze v1 catalog
- `needs_review`: DC007 — captured row with mapping ambiguity; quality/lineage=`needs_review`
- Removed fields (`verified_flag`, `testing_stable_sample_flag`): absent
- Future fields (`buyer`, `seller`, `pledge_status`): not populated

## Case Results

| case_id | component | scenario | expected_status | actual_status | retrieval_status | quality_status | lineage_status | passed |
|---------|-----------|----------|-----------------|---------------|------------------|----------------|----------------|--------|
| DC001 | margin_trading | empty_but_valid | empty_but_valid_pass | empty_but_valid_pass | empty_but_valid | pass | discovered | yes |
| DC002 | block_trade | captured_normal | captured_pass | captured_pass | found | pass | discovered | yes |
| DC003 | restricted_shares_unlock | captured_normal | captured_pass | captured_pass | found | pass | discovered | yes |
| DC004 | equity_pledge | empty_but_valid | empty_but_valid_pass | empty_but_valid_pass | empty_but_valid | pass | discovered | yes |
| DC005 | shareholder_change | captured_normal | captured_pass | captured_pass | found | pass | discovered | yes |
| DC006 | executive_shareholding | captured_normal | captured_pass | captured_pass | found | pass | discovered | yes |
| DC007 | equity_pledge | needs_review | needs_review_accepted | needs_review_accepted | found | needs_review | needs_review | yes |

## empty_but_valid Behavior

- **DC001** (margin_trading): retrieval=`empty_but_valid` · quality=`pass` · passed=**yes**
- **DC004** (equity_pledge): retrieval=`empty_but_valid` · quality=`pass` · passed=**yes**

## needs_review Behavior

- **DC007** (equity_pledge): quality=`needs_review` · lineage=`needs_review` · passed=**yes**

## Gate

```text
d_class_ready_case_benchmark_gate = READY_FOR_REVIEW
```

**不是 PASS** · **不是 live_ready** · **不是 verified**.

## Parallel Safety

- C-class status: **`SNAPSHOT_GENERATED_QA_REVIEW`**（不变）
- A-class / B-class outputs: **unchanged**
- CNINFO calls: **0**
- testing_stable_sample: **not upgraded**

