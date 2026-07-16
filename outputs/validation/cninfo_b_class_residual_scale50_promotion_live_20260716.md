# CNINFO B 类 B-FM-03（R19）— Residual Scale50 晋升 + Bounded Live

> **executor:** b-class-executor · **track:** B · **task_id:** B-FM-03  
> **性质：** offline harvest → ~50 residual 晋升 + allow-list live metadata + retry_v1 硬化 · **NOT verified** · **NOT production_ready**  
> **不造** validation_design §7 FP · **不**重开 B-FM-01/02 及更早 LIVE_PASS · **拒绝** `audit_report_known_002`

---

## 1. Scale policy（excellence-gated）

| 阶梯 | 本包 |
|------|------|
| 5–10 → **50** → 200 → 1000 | 先验 B-FM-01（3）/ B-FM-02（8）LIVE_PASS → 本包 **~50** |
| B excellent | LIVE_PASS · fail=0 · ambiguous=0 |
| 非 excellent | 停在 ~50 硬化/retry · **不**跳 200 |

---

## 2. 5-horizon / 组成

| # | horizon | 结论 |
|---|---------|------|
| 1–4 | deferred known_002 四族 | **推迟** — 仍薄 |
| 5 | `audit_report_known_002` | **拒绝** — 年报陷阱 |
| 6 | ~50 coherent residual | **执行** — 单根 allow-list |

| family | n |
|--------|---|
| bond_trustee_report | 10（含 spotlight 精测/润禾/奥飞/金田 + 公司债余量） |
| tracking_rating_report | 2（中天精装/润达医疗「跟踪评级结果的公告」） |
| legal_opinion | 16 |
| shareholder_meeting | 12 |
| board_resolution | 5 |
| raised_funds_cash_management | 4 |
| continuous_supervision_annual | 1 |
| **合计** | **50** |

路由：既有硬化；**本包不改路由**。

---

## 3. Validation

| 检查 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_residual_scale50_promotion.py` | **8 OK** |
| `python lab/test_cninfo_b_class_residual_scale50_live.py` | **3 OK** |
| `python lab/select_cninfo_b_class_retrieval_ready_cases.py --strict` | ready=**153** · invalid_ready=**0** · **PASS** |
| fixture dry-run | **DRY_RUN_PASS** · ready=153 |
| allow-list pre-live dry-run | **DRY_RUN_PASS** · ready=50 |
| base bounded live | **PARTIAL** · pass=**48**/fail=**2**/amb=0 |
| retry_v1 live（hardened 2） | **LIVE_PASS** · pass=**2**/0/0 |
| **cohort 合成** | **LIVE_PASS** · pass=**50**/0/0 · **excellent** |

---

## 4. Live 证据

### 4.1 Base（保留；不覆盖）

| 项 | 值 |
|----|-----|
| result | **PARTIAL** |
| CNINFO | **~100**（50×(topSearch+query)；PDF=0） |
| wall | **~234 s** |
| fail | `legal_opinion_known_019`, `legal_opinion_known_021`（律所全称 searchkey → 0 条） |

### 4.2 Retry_v1（隔离根）

| 项 | 值 |
|----|-----|
| result | **LIVE_PASS** |
| CNINFO | **4**（2×(topSearch+query)；PDF=0） |
| wall | **~12 s** |

| case_id | matched | date | result |
|---------|---------|------|--------|
| `legal_opinion_known_019` | 北京市安理律师事务所关于中粮糖业控股股份有限公司2024年年度股东大会的法律意见书 | 2025-06-19 | **pass** |
| `legal_opinion_known_021` | 北京金诚同达（深圳）律师事务所关于深圳市杰普特光电股份有限公司2024年度差异化分红事项的法律意见书 | 2025-06-16 | **pass** |

硬化：title_pattern 改为公司锚定可区分串（仍为 harvest 子串；全局 ready pattern 互斥）。

### 4.3 诊断探针（非 package 证据）

失败根因确认另耗约 **~29** CNINFO 探测调用（多 keyword/date 组合）；不计入 LIVE_PASS 判定分子，计入本任务合计。

### 4.4 本任务 CNINFO 合计

| 段 | 约数 |
|----|------|
| base live | ~100 |
| retry_v1 | 4 |
| diag probe | ~29 |
| **task total** | **~133** |
| PDF | **0** |

---

## 5. 能力增益

- ~50 residual known-doc 进入 ready 并经公司窗 live metadata 确认（含 retry 硬化）
- ready 计数刷新为 **153**；deferred known_002 仍薄；`audit_report_known_002` 仍拒
- excellence 达成 → 下一阶梯可准备 **~200** coherent known-doc live（**本包不执行 ~200**）

---

## 6. Gate 摘要

```text
b_class_residual_scale50_promotion_live_gate = LIVE_PASS
task_id = B-FM-03
cohort_size = 50
pass = 50
fail = 0
ambiguous = 0
excellent = true
cninfo_calls_base_live ~= 100
cninfo_calls_retry_v1 = 4
cninfo_calls_diag_probe ~= 29
cninfo_calls_task_total ~= 133
pdf_downloads = 0
ready_for_commit = true
commit = not_done
push = not_done
```

---

## 7. 修改文件

| 路径 | 作用 |
|------|------|
| `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` | +50 residual ready；019/021 searchkey 硬化 |
| `lab/test_cninfo_b_class_residual_scale50_promotion.py` | 离线晋升锁测 |
| `lab/test_cninfo_b_class_residual_scale50_live.py` | live allow-list mock |
| `outputs/validation/cninfo_b_class_r19_bfm03_offline_harvest_20260716.md` | offline harvest 决策 |
| `outputs/validation/_bfm03_manifest.json` / `_bfm03_candidate_pool.json` | 本包 manifest / 候选池 |
| `outputs/validation/cninfo_b_class_residual_scale50_live_20260716/` | base live 包（PARTIAL 保留） |
| `outputs/validation/cninfo_b_class_residual_scale50_retry_v1_live_20260716/` | retry_v1 live 包 |
| `outputs/validation/cninfo_b_class_residual_scale50_promotion_dry_run_*_20260716.*` | fixture dry-run |
| `outputs/validation/cninfo_b_class_retrieval_ready_case_*` | ready=153 刷新 |
| `outputs/validation/cninfo_b_class_residual_scale50_promotion_live_20260716.md` | 本报告 |

---

## 8. Commit path（显式；executor 不执行 commit）

```text
fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml
lab/test_cninfo_b_class_residual_scale50_promotion.py
lab/test_cninfo_b_class_residual_scale50_live.py
outputs/validation/cninfo_b_class_r19_bfm03_offline_harvest_20260716.md
outputs/validation/_bfm03_manifest.json
outputs/validation/_bfm03_candidate_pool.json
outputs/validation/cninfo_b_class_residual_scale50_live_20260716/
outputs/validation/cninfo_b_class_residual_scale50_retry_v1_live_20260716/
outputs/validation/cninfo_b_class_residual_scale50_promotion_dry_run_20260716.csv
outputs/validation/cninfo_b_class_residual_scale50_promotion_dry_run_summary_20260716.md
outputs/validation/cninfo_b_class_residual_scale50_promotion_live_20260716.md
outputs/validation/cninfo_b_class_retrieval_ready_case_report.csv
outputs/validation/cninfo_b_class_retrieval_ready_case_summary.md
```

Suggested message:

```text
feat(b-class): promote residual scale50 known-doc cohort (B-FM-03)

Close R19 ~50 allow-list live after searchkey harden/retry on two legal_opinion
cases; excellence LIVE_PASS enables next ~200 package prep (not in this commit).
```

---

## 9. Next B candidate

1. **Controller commit** 本包（executor 不 commit/push）。
2. 因 **excellent**，下一包可 **准备 ~200** coherent known-doc harvest/allow-list（独立包；不在本未提交包内 live）。
3. deferred known_002 仍薄则继续推迟；**勿**晋升 `audit_report_known_002`。
4. **勿**重开本包及更早 LIVE_PASS。
