# CNINFO B 类 Phase 3 EP002 Reachability Precheck Runner 实现摘要

_生成时间：2026-07-10_

> **性质：** offline runner prep · dry-run only · **无 CNINFO live** · **不是 verified**

---

## Runner

| 项 | 值 |
|----|-----|
| path | `lab/run_cninfo_b_class_phase3_100_ep002_reachability_precheck.py` |
| tests | `lab/test_cninfo_b_class_phase3_100_ep002_reachability_precheck_runner.py`（**26/26 PASS**） |
| output root | `outputs/validation/cninfo_b_class_phase3_100_ep002_reachability_precheck/` |

---

## CLI Flags

| Flag | 用途 |
|------|------|
| `--dry-run` | 默认模式；CNINFO **0** |
| `--live` | live precheck（须批准 flag） |
| `--candidates-csv` | precheck 候选 CSV（**必需**） |
| `--output-root` | 隔离输出根 |
| `--request-cap` | live CNINFO 硬上限（最大 **16**） |
| `--approve-b-class-phase3-100-ep002-reachability-precheck` | live 显式批准 |

---

## Approval Guard

- `--live` 无批准 flag → **`approve_b_class_phase3_100_ep002_reachability_precheck_required`**
- 错误批准 flag（Phase 3 expansion / failed retry / Phase 2.5 等）→ **`approve_b_class_phase3_100_ep002_reachability_precheck_wrong_flag`**
- 拒绝发生在 CNINFO 调用之前

---

## Candidate Validation

| 规则 | 状态 |
|------|------|
| candidate count = **8** | enforced |
| precheck_ids B3EP001–B3EP008 only | enforced |
| case_ids B3E001/B3E018/B3E035/B3E051/B3E074/B3E091/B3E096/B3E100 only | enforced |
| B3E087 excluded | **yes** |
| 8 recovered cases excluded | **yes** |
| prior B1E/B2E/B25E excluded | **yes** |
| `planned_check_type = ep002_orgid_reachability` | enforced |

---

## Request Cap

| 项 | 值 |
|----|-----|
| planned_request_count_total | **8** |
| cap | **≤ 16** |
| CNINFO calls（dry-run） | **0** |

---

## Dry-run Result

| 项 | 值 |
|----|-----|
| planned_ok | **8/8** |
| dry-run report | [b_class_phase3_100_ep002_reachability_precheck_dryrun_report.csv](cninfo_b_class_phase3_100_ep002_reachability_precheck/reports/b_class_phase3_100_ep002_reachability_precheck_dryrun_report.csv) |
| dry-run summary | [b_class_phase3_100_ep002_reachability_precheck_dryrun_summary.md](cninfo_b_class_phase3_100_ep002_reachability_precheck/reports/b_class_phase3_100_ep002_reachability_precheck_dryrun_summary.md) |

---

## Safety Confirmations

| 项 | 状态 |
|----|------|
| CNINFO calls | **0** |
| live precheck executed | **no** |
| retry_v2 universe created | **no** |
| EP001/EP004/EP005 validation | **blocked** |
| PDF/OCR/extraction | **blocked** |
| DB/MinIO/RAG | **blocked** |
| verified / production_ready | **blocked** |
| Phase 3 expansion reports mutated | **no** |
| Phase 3 failed-retry reports mutated | **no** |
| Phase 2.5 reports mutated | **no** |
| candidates CSV mutated | **no** |

---

## Future Live Command（NOT APPROVED · Do not execute）

```bash
cd listed_company_data_collector

python lab/run_cninfo_b_class_phase3_100_ep002_reachability_precheck.py \
  --live \
  --candidates-csv outputs/validation/cninfo_b_class_phase3_100_ep002_reachability_precheck_candidates.csv \
  --output-root outputs/validation/cninfo_b_class_phase3_100_ep002_reachability_precheck/ \
  --approve-b-class-phase3-100-ep002-reachability-precheck
```

---

## Gate

```text
b_class_phase3_100_ep002_reachability_precheck_runner_gate = READY_FOR_APPROVAL
```

**不是 PASS** · **不是 live_ready** · **不是 verified** · **不是 production_ready**
