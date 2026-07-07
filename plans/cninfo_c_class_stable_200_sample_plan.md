# CNINFO C-Class Stable 200 Non-BSE Sample Plan（Era C Phase 4）

_生成时间：2026-07-07_

> **目的：** 在 [source status decision](cninfo_c_class_source_status_decision.md) 基础上，设计**清洗异常样本后**的 non-BSE **200 家**验证集，用于检验「C-class non-BSE 主宇宙是否稳定」。**本轮仅样本设计 + dry-run**；**非 verified**；**非 testing_stable_sample 升级**。

## 1. 背景

| 已完成验证 | 结论 |
|------------|------|
| 889 non-BSE live | 主路线 **CONDITIONAL YES**；fail 多来自样本质量 |
| 62 partial-fail retry | 困难样本验证 executive/share_capital partial-risk |
| 26 家 six_fail_hold | 6/6 全失败 · sample_quality_or_status_review |
| source status decision | dividend **proceed_testing**；top_float/share_capital **source_partial**；security **observe_only** |

**假设：** 剔除 six_fail_hold 与已知异常后，200 家分层样本应显著高于 889 全量的 pass/reachability 波动。

## 2. 母本与派生

| 项 | 路径 |
|----|------|
| 母本 | `lab/eval_companies_c_class_smoke_1000_non_bse_candidate.yaml`（**889**） |
| six_fail_hold | `lab/eval_companies_c_class_retry_889_six_fail_hold.yaml`（**26**） |
| 输出 | `lab/eval_companies_c_class_stable_200_non_bse.yaml`（**200**） |

## 3. 清洗规则

1. **排除** `six_fail_hold` **26 家**（主判定 6/6 全失败）
2. **排除** `abnormal_review` 显式代码（母本已剔除：600065 / 600978 / 000405）
3. **排除** 名称含「退市」/ delisted / terminated / 以「退」结尾（母本已剔除）
4. **排除** `board == bse`（母本已剔除）
5. **suspicious_duplicate_orgid：** 剔除 `000765`，保留 `001267`（汇绿生态）
6. ***ST 不自动剔除**，除非已在 six_fail_hold 或 abnormal_review
7. **分层抽样** toward 889 non-BSE board 比例

## 4. 分层目标与实际

| board | 889 占比 | 目标 | 实际 |
|-------|----------|------|------|
| sse_main | 292/889 ≈ 32.8% | **66** | **66** |
| szse_main | 239/889 ≈ 26.9% | **54** | **54** |
| chinext | 233/889 ≈ 26.2% | **52** | **52** |
| star | 125/889 ≈ 14.1% | **28** | **28** |
| **合计** | | **200** | **200** |

**抽样方法：** 按 `stock_code` 排序后各 board 取前 N（可复现、非随机）。

## 5. 排除统计

| 项 | 值 |
|----|-----|
| 母本 | 889 |
| 清洗后可选池 | **863** |
| 本轮排除 | **26**（均为 `six_fail_hold`） |
| 入样 | **200** |

## 6. Source 口径（live 时）

| 类型 | source |
|------|--------|
| 主判定（6） | basic · dividend · executive · share_capital · top_shareholders · top_float |
| observe_only | security |
| derived_no_separate_fetch | contact · business_scope · industry |
| source_partial | share_capital · top_float |

## 7. Dry-run

```bash
python lab/validate_cninfo_c_class_scale_smoke.py --dry-run \
  --sample-file lab/eval_companies_c_class_stable_200_non_bse.yaml
```

**预期：** companies=**200** · cases=**1400** · `DRY_RUN_ONLY`

**产出：**
- `outputs/validation/cninfo_c_class_stable_200_dryrun_report.csv`
- `outputs/validation/cninfo_c_class_stable_200_dryrun_summary.md`

## 8. Live 门槛（未执行）

| 项 | 要求 |
|----|------|
| 批准 | **人工批准后**再跑 `--live` |
| planned requests | **1400**（200 × 7） |
| 红线 | 无 YAML backfill 执行 · 无 DB · 无 verified |

## 9. 红线

- 本轮 **无 live** · **无 CNINFO** · **无 YAML 执行** · **无 DB**

## 10. 参考

- [source status decision](cninfo_c_class_source_status_decision.md)
- [889 diagnosis](../outputs/validation/cninfo_c_class_smoke_1000_non_bse_diagnosis.md)
- [62 retry live summary](../outputs/validation/cninfo_c_class_retry_889_partial_fail_live_summary.md)
- [universe split plan](cninfo_c_class_universe_split_and_sample_cleaning_plan.md)
