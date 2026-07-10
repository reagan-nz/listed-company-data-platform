# CNINFO B 类 Phase 3 EP002/orgId Reachability Precheck — Command Draft

_生成时间：2026-07-10_

> **性质：** precheck 命令草案。**live 未批准** · **NOT APPROVED**

**Closure gate：** `b_class_phase3_100_failed_retry_closure_gate = PASS_WITH_CAVEAT_NETWORK_UNRESOLVED`

**runner status：** `lab/run_cninfo_b_class_phase3_100_ep002_reachability_precheck.py` **已实现** · dry-run **8/8 planned_ok** · tests **26/26 PASS**

---

## 1. 范围约束

| 项 | 值 |
|----|-----|
| precheck candidates | [cninfo_b_class_phase3_100_ep002_reachability_precheck_candidates.csv](../outputs/validation/cninfo_b_class_phase3_100_ep002_reachability_precheck_candidates.csv)（**8** 例） |
| source universe | persistent **91** only |
| excluded hold | B3E087 |
| excluded recovered | B3E003–B3E011（8 例） |
| check type | `ep002_orgid_reachability` only |
| CNINFO calls（dry-run 回合） | **0** |

### 禁止

- metadata retry
- full 91-case retry
- EP001 / EP004 / EP005 validation
- PDF download / parse / OCR / extraction
- DB / MinIO / RAG
- verified / production_ready
- 写入 Phase 3 / failed-retry / Phase 2.5 基线

---

## 2. 输出隔离

**专用 precheck 输出根：**

```text
outputs/validation/cninfo_b_class_phase3_100_ep002_reachability_precheck/
```

---

## 3. Request Cap

| 项 | 值 |
|----|-----|
| candidates | **8** |
| max CNINFO requests | **≤ 16** |
| planned per candidate | **1** orgId probe |
| dry-run planned_request_count_total | **8** |

---

## 4. Dry-Run Command（已完成 · offline only）

```bash
cd listed_company_data_collector

python lab/run_cninfo_b_class_phase3_100_ep002_reachability_precheck.py \
  --dry-run \
  --candidates-csv outputs/validation/cninfo_b_class_phase3_100_ep002_reachability_precheck_candidates.csv \
  --output-root outputs/validation/cninfo_b_class_phase3_100_ep002_reachability_precheck/
```

**结果：** 8/8 planned_ok · planned_requests=8 · CNINFO **0**

---

## 5. Live Precheck Command Draft（NOT APPROVED · Do not execute）

```bash
# NOT APPROVED — 须用户显式批准后方可执行

cd listed_company_data_collector

python lab/run_cninfo_b_class_phase3_100_ep002_reachability_precheck.py \
  --live \
  --candidates-csv outputs/validation/cninfo_b_class_phase3_100_ep002_reachability_precheck_candidates.csv \
  --output-root outputs/validation/cninfo_b_class_phase3_100_ep002_reachability_precheck/ \
  --approve-b-class-phase3-100-ep002-reachability-precheck
```

> **Do not execute.** approval_status = **NOT_APPROVED**

---

## 6. Execution Gate（future live）

| 条件 | Gate |
|------|------|
| ≥ 60% candidates resolve orgId | `b_class_phase3_100_ep002_reachability_precheck_execution_gate = PASS_WITH_CAVEAT` |
| < 60% resolve orgId | `b_class_phase3_100_ep002_reachability_precheck_execution_gate = FAIL_REVIEW_REQUIRED` |

**Never：** `PASS` · `verified` · `production_ready`

---

## 7. Approval Gate

```text
b_class_phase3_100_ep002_reachability_precheck_planning_gate = READY_FOR_APPROVAL
b_class_phase3_100_ep002_reachability_precheck_runner_gate = READY_FOR_APPROVAL
```

**NOT APPROVED**
