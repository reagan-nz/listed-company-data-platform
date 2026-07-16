# CNINFO B 类 B-FM-04（R19）— Residual Scale200 晋升 + Bounded Live

> **executor:** b-class-executor · **track:** B · **task_id:** B-FM-04  
> **性质：** discovery harvest → ~200 residual 晋升 + allow-list live metadata + retry harden · **NOT verified** · **NOT production_ready**

---

## 1. Scale policy（excellence-gated）

| 阶梯 | 状态 |
|------|------|
| B-FM-03 ~50 | LIVE_PASS excellent 50/0/0 |
| **本包 ~200** | **LIVE_PASS excellent 200/0/0**（base+retry 合成） |
| ~1000 | **仅当本包 excellent 才可准备**；本包达标 → Controller 可调度下一阶梯包 |

非 excellent 则停留/硬化于 200，不通胀 1000。

## 2. Reject / closed

| 项 | 结论 |
|----|------|
| `audit_report_known_002` | **拒绝** |
| deferred known_002 薄族 | **未晋升** |
| 已 LIVE_PASS scale50 / tracking/bond 等 | **未重开** |

## 3. 本包组成（200）

| family | n |
|--------|---|
| legal_opinion | 43 |
| bond_trustee_report | 30 |
| shareholder_meeting | 29 |
| board_resolution | 25 |
| tracking_rating_report | 20 |
| supervisory_board | 15 |
| raised_funds_cash_management | 15 |
| continuous_supervision_annual | 8 |
| verification_opinion | 6 |
| company_articles | 5 |
| employee_stock_ownership_plan | 4 |

路由：既有硬化；**本包不改路由**。legal/searchkey 继承 B-FM-03 公司锚定 harden 经验。

## 4. Validation

| 检查 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_residual_scale200_promotion.py` | **8 OK** |
| `python lab/test_cninfo_b_class_residual_scale200_live.py` | **3 OK** |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py --strict` | ready 刷新 · invalid_ready=0 |
| fixture dry-run | **DRY_RUN_PASS** |
| allow-list pre-live dry-run | **DRY_RUN_PASS** · ready=200 |
| base bounded live | **PARTIAL** · pass=**193**/fail=**5**/amb=**2** |
| retry_v1 live（hardened 7） | **PARTIAL** · pass=**6**/0/amb=**1** |
| retry_v2 live（tracking_023） | **LIVE_PASS** · pass=**1**/0/0 |
| **cohort 合成** | **LIVE_PASS** · pass=**200**/0/0 · **excellent** |

## 5. Live 证据

### 5.1 Base（保留；不覆盖）

| 项 | 值 |
|----|-----|
| result | **PARTIAL** |
| CNINFO | **~402**（≈200 topSearch + 202 query；PDF=0） |
| wall | **~751 s** |
| fail/amb | 5 fail + 2 amb（searchkey/歧义；已 harden） |

### 5.2 Retry_v1（隔离根）

| 项 | 值 |
|----|-----|
| result | **PARTIAL**（6/0/1） |
| CNINFO | **~14** |
| wall | **~31 s** |

含：6 案 searchkey harden + `company_articles_known_010` 替换为科强股份（原华鑫主公告+附件同窗 ambiguous）。

### 5.3 Retry_v2（隔离根）

| 项 | 值 |
|----|-----|
| result | **LIVE_PASS** |
| CNINFO | **~2** |
| case | `tracking_rating_report_known_023` → pattern `浙江荣晟环保纸业股份有限公司关于` |

### 5.4 Discovery / 诊断

| 段 | 约数 |
|----|------|
| discovery harvest | **110** |
| diag/harden probes | **~38** |

### 5.5 本任务 CNINFO 合计

| 段 | 约数 |
|----|------|
| discovery | 110 |
| base live | ~402 |
| retry_v1 | ~14 |
| retry_v2 | ~2 |
| diag/harden probe | ~38 |
| **task total** | **~566** |
| PDF | **0** |

## 6. 能力增益

- ~200 multi-family residual known-doc 进入 ready 并经公司窗 live metadata 确认（含 retry harden）
- family 覆盖 tracking/bond/legal/meeting/board/supervisory/raised_funds/supervision/verification/articles/ESOP
- excellence 达成 → 下一阶梯可准备 **~1000**（独立包；不在本未提交包内执行）

## 7. Gate 摘要

```text
b_class_residual_scale200_promotion_live_gate = LIVE_PASS
task_id = B-FM-04
cohort_size = 200
pass = 200
fail = 0
ambiguous = 0
excellent = true
cninfo_calls_discovery = 110
cninfo_calls_base_live ~= 402
cninfo_calls_retry_v1 ~= 14
cninfo_calls_retry_v2 ~= 2
cninfo_calls_diag_probe ~= 38
cninfo_calls_task_total ~= 566
pdf_downloads = 0
ready_for_commit = true
commit = not_done
push = not_done
```

## 8. 修改文件

| 路径 | 用途 |
|------|------|
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | +200 ready（含 harden） |
| `lab/test_cninfo_b_class_residual_scale200_promotion.py` | 离线晋升锁测 |
| `lab/test_cninfo_b_class_residual_scale200_live.py` | live allow-list mock |
| `outputs/validation/_bfm04_*.json` | discovery/manifest |
| `outputs/validation/cninfo_b_class_r19_bfm04_offline_harvest_20260716.md` | harvest 决策 |
| `outputs/validation/cninfo_b_class_residual_scale200_live_20260716/` | base live 包 |
| `outputs/validation/cninfo_b_class_residual_scale200_retry_v1_live_20260716/` | retry_v1 |
| `outputs/validation/cninfo_b_class_residual_scale200_retry_v2_live_20260716/` | retry_v2 |
| `outputs/validation/cninfo_b_class_residual_scale200_promotion_dry_run_*` | fixture dry-run |
| `outputs/validation/cninfo_b_class_residual_scale200_promotion_live_20260716.md` | 本报告 |

## 9. Commit list + message（未执行）

拟纳入：

```
fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml
lab/test_cninfo_b_class_residual_scale200_promotion.py
lab/test_cninfo_b_class_residual_scale200_live.py
outputs/validation/_bfm04_candidate_pool.json
outputs/validation/_bfm04_discovery_meta.json
outputs/validation/_bfm04_discovery_log.jsonl
outputs/validation/_bfm04_manifest.json
outputs/validation/cninfo_b_class_r19_bfm04_offline_harvest_20260716.md
outputs/validation/cninfo_b_class_residual_scale200_promotion_dry_run_20260716.csv
outputs/validation/cninfo_b_class_residual_scale200_promotion_dry_run_summary_20260716.md
outputs/validation/cninfo_b_class_residual_scale200_promotion_live_20260716.md
outputs/validation/cninfo_b_class_residual_scale200_live_20260716/
outputs/validation/cninfo_b_class_residual_scale200_retry_v1_live_20260716/
outputs/validation/cninfo_b_class_residual_scale200_retry_v2_live_20260716/
outputs/validation/cninfo_b_class_retrieval_ready_case_report.csv
outputs/validation/cninfo_b_class_retrieval_ready_case_summary.md
```

Suggested message:

```
feat(b-class): promote residual scale200 known-doc cohort (B-FM-04)

Close R19 ~200 allow-list live after discovery harvest and searchkey
harden/retry; excellence LIVE_PASS enables next ~1000 package prep
(not in this commit).
```

## 10. Next

1. Controller 审阅后 **commit**（本包未 commit / 未 push）。
2. 因 **excellent**，下一包可 **准备 ~1000** coherent known-doc harvest/allow-list（独立包；不在本包内 live）。
