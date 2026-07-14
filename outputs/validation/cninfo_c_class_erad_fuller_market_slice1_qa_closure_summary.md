# CNINFO C 类 Era D — Fuller-Market Slice1 QA Closure Summary

_生成时间：2026-07-13 · offline status-ledger rebuild · CNINFO=0_

> **offline only** · **no live** · **no snapshot** · **no commit/push** · **approved_for_snapshot_rebuild=false**

---

## Task

Offline rebuild/reconcile `company_harvest_status.csv` for `fuller_market_slice1_200` from disk evidence + universe draft, and produce bounded QA closure package.

---

## Source Root Verified

| 项 | 值 |
|----|-----|
| **output root** | `outputs/harvest/cninfo_c_class/fuller_market_slice1_200/` |
| **universe** | `outputs/validation/cninfo_c_class_erad_fuller_market_slice1_universe_draft.csv` |
| **expected universe** | **200**（CE1E001–CE1E200） |
| **disk unique companies** | **200**（normalized 文件名并集） |
| **unmatched disk vs universe** | **0** |
| **duplicates** | **0** |

---

## Pre-rebuild Ledger Diagnosis

| 项 | 值 |
|----|-----|
| previous status-ledger rows | **100** |
| diagnosis | **incomplete/stale**（Session 2 覆盖写入 Session 1 · 仅保留后 100 家） |
| universe rows missing from old ledger | **100** |
| old classification (of 100) | complete 93 · partial 7 |

---

## Classification Rule（documented）

从 `normalized/<source_type>/*` 统计每家公司出现的源目录数（共 10）：

| 条件 | harvest_status |
|------|----------------|
| **normalized sources ≥ 10** | **complete** |
| **1 ≤ sources ≤ 9** | **partial** |
| **sources = 0** | **missing** |

`sources_http_success` / `sources_failed` 由 `raw/` 下 7 个 HTTP 源的 `retrieval_status` 离线重算（不调用 CNINFO）。

**注：** 文件存在（含 0 字节 `dividend_history.jsonl`）计入 sources_present，与 harvest runner「HTTP 无 fail → complete」一致。offline resume-audit 对 0 字节 dividend 另标 `needs_review`（见下）。

---

## Post-rebuild Counts

| 指标 | 值 |
|------|-----|
| rebuilt status-ledger rows | **200** |
| **complete** | **193** |
| **partial** | **7** |
| **missing** | **0** |
| duplicate | **0** |
| unmatched | **0** |

Backup: `company_harvest_status.csv.bak_pre_offline_rebuild_20260713T100619Z`

### Offline resume-audit（post-rebuild · CNINFO=0）

| resume_state | count |
|--------------|-------|
| complete | **190** |
| partial | **7** |
| needs_review | **3** |

命令：`python3 lab/run_cninfo_c_class_harvest_resume_audit.py --dry-run --harvest-root outputs/harvest/cninfo_c_class/fuller_market_slice1_200/ --universe-yaml lab/eval_companies_c_class_fuller_market_slice1_200.yaml --output-root outputs/validation/cninfo_c_class_erad_fuller_market_slice1_qa_closure_audit/`

---

## Exact Caveat Case IDs（10）

### A. Partial / delisted-merged（7）— ledger=`partial`

| case_id | company_code | company_name | status | sources | disposition |
|---------|--------------|--------------|--------|---------|-------------|
| CE1E002 | 600001 | 邯郸钢铁 | partial | 4/10 | accept_with_caveat |
| CE1E003 | 600005 | 武钢股份 | partial | 4/10 | accept_with_caveat |
| CE1E034 | 600068 | 葛洲坝 | partial | 4/10 | accept_with_caveat |
| CE1E061 | 000003 | PT金田A | partial | 4/10 | accept_with_caveat |
| CE1E067 | 000015 | PT中浩A | partial | 4/10 | accept_with_caveat |
| CE1E070 | 000022 | 深赤湾A | partial | 4/10 | accept_with_caveat |
| CE1E071 | 000024 | 招商地产 | partial | 4/10 | accept_with_caveat |

### B. Empty-but-valid dividend（3）— ledger=`complete` · audit=`needs_review`

| case_id | company_code | company_name | ledger | audit | disposition |
|---------|--------------|--------------|--------|-------|-------------|
| CE1E176 | 688031 | 星环科技 | complete | needs_review | accept_with_caveat |
| CE1E188 | 688062 | 迈威生物 | complete | needs_review | accept_with_caveat |
| CE1E193 | 688071 | 华依科技 | complete | needs_review | accept_with_caveat |

**All caveat Case IDs:** CE1E002, CE1E003, CE1E034, CE1E061, CE1E067, CE1E070, CE1E071, CE1E176, CE1E188, CE1E193

Interpretation:
- Group A：退市/合并/PT；raw 多为 `http_error`/500；**不建议 re-live**。
- Group B：raw dividend=`valid_empty` · normalized `dividend_history.jsonl` 为 0 字节；ledger 保持 complete（与 runner 一致）；质量层 accept_with_caveat。

---

## Artifacts

| 文件 | 说明 |
|------|------|
| `outputs/harvest/cninfo_c_class/fuller_market_slice1_200/quality/company_harvest_status.csv` | **rebuilt 200 rows** |
| `company_harvest_status.csv.bak_pre_offline_rebuild_20260713T100619Z` | pre-rebuild backup（slice1 quality only） |
| [qa_closure_summary](cninfo_c_class_erad_fuller_market_slice1_qa_closure_summary.md) | 本文件 |
| [caveat_ledger](cninfo_c_class_erad_fuller_market_slice1_qa_closure_caveat_ledger.csv) | 10 caveat 明细 |
| [metrics](cninfo_c_class_erad_fuller_market_slice1_qa_closure_metrics.csv) | 闭合指标 |
| [reconcile](cninfo_c_class_erad_fuller_market_slice1_status_ledger_reconcile.csv) | old→new 行级对账 |
| [qa_closure_audit](cninfo_c_class_erad_fuller_market_slice1_qa_closure_audit/) | offline resume-audit 输出 |

---

## Protected Roots（untouched）

| 根 | 状态 |
|----|------|
| `outputs/harvest/cninfo_c_class/quality/`（863 primary） | **未修改** |
| `phase3_batch_500_001/` | **未修改** |
| `phase35_batch_500_001_resume/` | **未修改** |
| `outputs/snapshot/` | **未创建/未修改** |
| A/B/D tracks | **未触碰** |

仅修改 slice1 隔离根内 `quality/company_harvest_status.csv`（+ backup）与 `outputs/validation/cninfo_c_class_erad_fuller_market_slice1_*` QA 包。

---

## Gates

```
c_class_erad_fuller_market_slice1_qa_closure_gate = PASS_WITH_CAVEAT
c_class_erad_fuller_market_slice1_status_ledger_rebuild_gate = PASS_WITH_CAVEAT
approved_for_snapshot_rebuild = false
```

**NOT verified** · **NOT production_ready** · **NOT PASS**（bare） · snapshot **blocked**

Caveat 原因：7 partial（delisted/merged/PT）+ 3 empty-but-valid dividend needs_review；ledger 已与磁盘+universe 对齐，但 harvest success ≠ snapshot/production readiness。

---

## Remaining Issues

1. Snapshot 仍 **blocked**（`approved_for_snapshot_rebuild=false`）— 本任务不扩展 snapshot planning。
2. Runner Session 覆盖写入 status CSV 的行为仍是系统性 caveat（历史问题；本次已用离线重建修复 slice1 症状）。
3. 3 家 STAR empty dividend 质量 caveat 已文档化；不升级为 live retry。
4. PROJECT_CONTROL 由 Controller 在 Evidence Auditor 后更新（Executor 不改）。

---

## Next Recommended C-class Action

**Evidence Auditor** 核验本 QA 包与 protected-root 未触碰声明；随后 Controller 更新 PROJECT_CONTROL。  
可选后续（需另批）：slice2 planning — **非** snapshot rebuild。
