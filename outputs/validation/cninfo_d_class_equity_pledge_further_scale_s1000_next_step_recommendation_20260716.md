# EP Further-Scale S1000 Next-Step Recommendation

Task: D-FM-13  
Gate: `d_class_equity_pledge_further_scale_s1000_execution_gate = PASS_WITH_CAVEAT`  
Excellence: **YES** (1000/1000, fail/http=0)

## Recommendation

**Component switch** to next shareholder/capital component first rung:

1. Preferred: **restricted_shares_unlock (RSU) ~50** denser bounded live on a NEW isolated root
2. Alternate: **fund_industry_allocation (FIA) ~50** denser bounded live on a NEW isolated root

Do **not** further-scale EP beyond s1000. Do **not** inflate SC / ESH / AT.

## Rationale

- EP ladder s50/s200/s1000 all excellence-gated PASS_WITH_CAVEAT
- s1000 residual found density is thin (133 found + 867 honest empty pad) — further EP scale adds little capability signal
- Standing D mission next value is a new component first rung (~50)

## Commit boundary (Controller-owned)

Executor did **not** commit/push. Suggested commit message when Controller lands:

```
feat(d-class): EP further-scale ~1000 denser multi-day live (DEP501-1500)
```

Suggested paths (track-owned):

- `lab/run_cninfo_d_class_equity_pledge_further_scale_s1000.py`
- `lab/test_cninfo_d_class_equity_pledge_further_scale_s1000_runner.py`
- `outputs/validation/cninfo_d_class_equity_pledge_further_scale_s1000/**`
- `outputs/validation/cninfo_d_class_equity_pledge_further_scale_s1000_*.csv|json|md`
- `outputs/validation/cninfo_d_class_equity_pledge_dfm13_further_scale_s1000_live_20260716.md`
