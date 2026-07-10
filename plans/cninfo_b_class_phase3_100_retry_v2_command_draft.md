# CNINFO B 类 Phase 3 Retry v2 — Command Draft

_生成时间：2026-07-10_

> **性质：** 未来 live retry_v2 命令草案。**live 未批准** · **NOT APPROVED**

**EP002 precheck gate：** `b_class_phase3_100_ep002_reachability_precheck_execution_gate = PASS_WITH_CAVEAT`

**runner status：** `run_cninfo_b_class_phase25_expansion_validation.py` **已实现** `--phase3-100-retry-v2` · dry-run **91/91 planned_ok** · runner tests **26/26 PASS** · **live path implemented offline** · live-path tests **24/24 PASS**

---

## 1. 范围约束

| 项 | 值 |
|----|-----|
| retry_v2 universe | [cninfo_b_class_phase3_100_retry_v2_universe.csv](../outputs/validation/cninfo_b_class_phase3_100_retry_v2_universe.csv)（**91** 例） |
| source subset | persistent **91** only |
| excluded hold | B3E087 |
| excluded recovered | B3E003–B3E011（8 例） |
| CNINFO calls（dry-run 回合） | **0** |

### 禁止

- 全量 100-case rerun
- B3E087 rerun
- 8 recovered rerun
- prior B-class Phase 1/2/2.5 rerun
- replacement cases
- PDF / OCR / extraction / DB / MinIO / RAG
- verified / production_ready
- 写入 Phase 3 / failed-retry / EP002 precheck / Phase 2.5 基线

---

## 2. 输出隔离

**专用 retry_v2 输出根：**

```text
outputs/validation/cninfo_b_class_phase3_100_retry_v2/
```

---

## 3. Dry-Run Command（已完成 · offline only）

```bash
cd listed_company_data_collector

python lab/run_cninfo_b_class_phase25_expansion_validation.py \
  --phase3-100-retry-v2 \
  --dry-run \
  --universe-csv outputs/validation/cninfo_b_class_phase3_100_retry_v2_universe.csv \
  --output-root outputs/validation/cninfo_b_class_phase3_100_retry_v2/
```

**结果：** 91/91 planned_ok · planned_requests=182 · CNINFO **0**

---

## 4. Live Retry v2 Command Draft（NOT APPROVED · Do not execute）

```bash
# NOT APPROVED — 须用户显式批准 + live 路径实现后方可执行

cd listed_company_data_collector

python lab/run_cninfo_b_class_phase25_expansion_validation.py \
  --phase3-100-retry-v2 \
  --live \
  --universe-csv outputs/validation/cninfo_b_class_phase3_100_retry_v2_universe.csv \
  --output-root outputs/validation/cninfo_b_class_phase3_100_retry_v2/ \
  --approve-b-class-phase3-100-retry-v2
```

> **Do not execute.** approval_status = **NOT_APPROVED** · approved_for_live = **false** · live path **implemented offline only**

---

## 5. Execution Gate（future live）

| 条件 | Gate |
|------|------|
| acceptable ≥ **82/91** 且无 red-line | `b_class_phase3_100_retry_v2_execution_gate = PASS_WITH_CAVEAT` |
| acceptable < **82/91** | `b_class_phase3_100_retry_v2_execution_gate = FAIL_REVIEW_REQUIRED` |

**Never：** `PASS` · `verified` · `production_ready`

---

## 6. Approval Gate

```text
b_class_phase3_100_retry_v2_planning_gate = READY_FOR_APPROVAL
b_class_phase3_100_retry_v2_runner_extension_gate = READY_FOR_APPROVAL
b_class_phase3_100_retry_v2_live_path_gate = READY_FOR_APPROVAL
```

**NOT APPROVED** · **Do not execute live**
