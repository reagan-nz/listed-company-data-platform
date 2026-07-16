# A-FM-02 — Finish listing-aware S22 + excellence gate（AD2E1601–1650）

_生成时间：2026-07-16 · track A · executor a-class-executor · task_id A-FM-02 · R19 excellence-gated scale_

> **standing_scope：** metadata / listing-aware scale cohorts  
> **CNINFO live（本 turn）：** **107**（main reconstructed 97 + retry1 7 + retry2 3）· **未 mutate S1–S21 live 主根** · **无 commit/push**  
> **Prior：** S21 49/50（~98%）`PASS_WITH_CAVEAT` · excellent enough to scale；S22 +50 已在途（dry-run 完成 · live 中断于 41/50）→ 本包先 coherent 收口 S22

## 1. Task

| 项 | 值 |
|----|-----|
| task_id | **A-FM-02** |
| track | A |
| executor | a-class-executor |
| R19 ladder | ~50 → ~200 → ~1000 · **仅当当前步 EXCELLENT 才升梯** |
| 目标 | 收口 S22（resume + isolated retry + combined）→ 判定 excellence → 若 ≥95% 则下一包跳 ~200 新孤立根 |
| 保护 | **禁止** mutate S1–S21 live 主根 |

## 2. Excellence definition（human clarified）

```text
A excellent = acceptable >= 95%（例：>=48/50）
          + failures understood
          + isolated retry done
若非 excellent：同尺度 harden，禁止通胀
若 excellent：下一包跳到 ladder 下一档
```

## 3. S22 flight recovery

发现：`.../s22/raw_metadata` 已有 AD2E1601–1641（41）· 无完整 live report · 无活跃 python 进程（中断）。

| 步骤 | 结果 |
|------|------|
| resume `--case-range AD2E1642:AD2E1650` | **9/9** found/pass · CNINFO=**18** |
| first-pass（50 raw 重建） | **47/50** · not_found=3 |
| not_found | AD2E1604 · AD2E1605 · AD2E1633 |

## 4. not_found classification + isolated retry

| case_id | code | prior_class（main） | retry | recovered |
|---------|------|-------------------|-------|-----------|
| AD2E1604 | 600754 | proxy_503 / cninfo=0 → v2 后 records=12 last_err=ok | retry + v2 仍 not_found | **no** |
| AD2E1605 | 600756 | network_timeout / cninfo=0 | found/pass | **yes** |
| AD2E1633 | 688048 | matching_v2_empty_window（records=20 last_err=ok） | 仍 not_found | **no** |

孤立根：

- `.../s22/retry_not_found_1604_1605_1633/`
- `.../s22/retry_not_found_1604_v2/`（仅 1604；仍 matching 空窗，非单纯 SSL）

**诚实分类：** 残差 AD2E1604 / AD2E1633 均为 `matching_v2_empty_window_with_orgid_resolved`（orgid 已解析；非 listing_date 后置）。

## 5. Verified metrics

| 指标 | 值 |
|------|-----|
| universe size | **50**（AD2E1601–1650） |
| prefix counts | 600=25 · 688=25（max=25） |
| reject ledger | **1486** |
| dry-run planned_ok | **50/50** · CNINFO=**0**（prior in-flight） |
| live first-pass | **47/50** acceptable |
| isolated retry recovery | **1**/3（AD2E1605） |
| **combined** | **48/50 = 96.0%** |
| CNINFO calls（本 turn 合计） | **107** |
| orgid_fallback | hits 记于 raw；本包无新增 miss 膨胀 |
| network_timeout（残差） | 已理解；1605 恢复；1604 转 matching 空窗 |
| execution gate（combined） | `PASS_WITH_CAVEAT` |
| **excellence** | **YES**（≥48/50 · failures understood · retry done） |
| S1–S21 live 主根 mutated | **no**（mtime vs `_tmp_s22_prior_live_mtime_snap.json`） |

## 6. Tests

| 步骤 | 结果 |
|------|------|
| `test_cninfo_a_class_erad_listing_aware_s22_runner.py` | **5/5 OK** |

## 7. Files

### Created / updated（本包）
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s22/`（resume live + full reconstructed live report + retry 子根）
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s22_not_found_retry_universe_20260716.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s22_not_found_precheck_20260716.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s22_fm02_recovery_ledger_20260716.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s22_fm02_combined_live_report_20260716.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s22_fm02_combined_live_quality_report_20260716.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s22_fm02_20260716.md`（本报告）

### Prior in-flight（已存在 · 本包收口）
- `lab/test_cninfo_a_class_erad_listing_aware_s22_runner.py`
- `lab/cninfo_a_class_listing_aware_cohort_builder.py`（S22）
- `lab/run_cninfo_a_class_phase2_metadata_expansion.py`（S22）
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s22_plus50_universe_20260716.csv`
- `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s22_reject_ledger_20260716.csv`

### Not touched（保护）
- 封闭 S1 **live** 主报告
- listing-aware S2–S21 **live** 主报告
- B/C/D · commit/push

## 8. Allow-list（ready_for_commit）

Track-A only（排除 console log · 排除 gitignored `raw_metadata/` · 排除 B/C/D）：

1. `lab/cninfo_a_class_listing_aware_cohort_builder.py`
2. `lab/run_cninfo_a_class_phase2_metadata_expansion.py`
3. `lab/test_cninfo_a_class_erad_listing_aware_s22_runner.py`
4. `lab/test_cninfo_a_class_listing_aware_cohort_builder.py`
5. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s22_plus50_universe_20260716.csv`
6. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s22_reject_ledger_20260716.csv`
7. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s22/`（整根；排除 `raw_metadata/` · `*console*`）
8. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s22_not_found_retry_universe_20260716.csv`
9. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s22_not_found_precheck_20260716.csv`
10. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s22_fm02_recovery_ledger_20260716.csv`
11. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s22_fm02_combined_live_report_20260716.csv`
12. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s22_fm02_combined_live_quality_report_20260716.csv`
13. `outputs/validation/cninfo_a_class_erad_next_scale_listing_aware_s22_fm02_20260716.md`

## 9. Gate

```text
a_class_fm02_listing_aware_s22_first_pass_gate = PASS_WITH_CAVEAT   # 47/50
a_class_fm02_s22_not_found_retry_gate = PASS_WITH_CAVEAT            # 1/3 recovered
a_class_fm02_combined_s22_plus_retry_gate = PASS_WITH_CAVEAT        # 48/50
a_class_fm02_excellence = YES                                       # 96% >= 95%
cninfo_calls = 107
s1_s21_live_main_roots_mutated = no
ready_for_commit = yes
commit = not_done
push = not_done
```

## 10. Next ladder step（excellence → scale）

```text
S22 EXCELLENT → 禁止继续无尽 +50
下一包 = listing-aware ~200（AD2E1651–AD2E1850）NEW isolated root S23
勿 mutate S1–S22 live 主根；无 B/C/D；无 commit/push（除非 Controller）
```
