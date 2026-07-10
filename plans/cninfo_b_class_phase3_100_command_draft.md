# CNINFO B 类 Phase 3 100-Company Expansion — Command Draft

_生成时间：2026-07-09_

> **性质：** 未来 Phase 3 100-company live metadata expansion 命令草案。**不执行** · **NOT APPROVED**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**Phase 2.5 failed retry closure gate：** `b_class_phase25_failed_retry_closure_gate = PASS_WITH_CAVEAT`

**runner_extension_required：** **false**（`--phase3-100` 与 `--approve-b-class-phase3-100-expansion` 已实现 · dry-run **100/100** · test **20/20 PASS**）

---

## 1. 范围约束

| 项 | 值 |
|----|-----|
| universe | [cninfo_b_class_phase3_100_universe_draft.csv](../outputs/validation/cninfo_b_class_phase3_100_universe_draft.csv)（**100** 家） |
| schema | phase1_freeze_v1 · **15** required fields（**不变**） |
| endpoints | EP001 · EP002 · EP004 · EP005 only |
| max cases | **100** |
| CNINFO calls（本回合） | **0** |

### 禁止

- PDF download / parse / OCR / section extraction
- harvest 写入 `outputs/harvest/`
- DB / MinIO / RAG
- verified / testing_stable_sample
- 触碰 Phase 1 / Phase 2 / Phase 2.5 / TLC002 输出根

---

## 2. 输出隔离

**专用输出根（强制）：**

```text
outputs/validation/cninfo_b_class_phase3_100_expansion/
```

---

## 3. Runner Extension（已完成 · 本回合未 live）

`lab/run_cninfo_b_class_phase25_expansion_validation.py` 已扩展：

| 扩展项 | 状态 |
|--------|------|
| `--phase3-100` | **implemented** |
| `--approve-b-class-phase3-100-expansion` | **implemented** |
| default universe | `cninfo_b_class_phase3_100_universe_draft.csv` |
| default output root | `cninfo_b_class_phase3_100_expansion/` |
| dry-run | **100/100 planned_ok** · CNINFO **0** |
| tests | **20/20 PASS** |

详见 [cninfo_b_class_phase3_100_runner_extension_summary.md](../outputs/validation/cninfo_b_class_phase3_100_runner_extension_summary.md)

---

## 4. Dry-Run Command（已执行 · 本回合）

```bash
cd listed_company_data_collector

python lab/run_cninfo_b_class_phase25_expansion_validation.py \
  --phase3-100 \
  --dry-run \
  --universe-csv outputs/validation/cninfo_b_class_phase3_100_universe_draft.csv \
  --output-root outputs/validation/cninfo_b_class_phase3_100_expansion/
```

---

## 5. Live Command Draft（NOT APPROVED · Do not execute）

```bash
# NOT APPROVED — 须 runner 扩展 + 用户显式批准后方可执行

cd listed_company_data_collector

python lab/run_cninfo_b_class_phase25_expansion_validation.py \
  --phase3-100 \
  --live \
  --universe-csv outputs/validation/cninfo_b_class_phase3_100_universe_draft.csv \
  --output-root outputs/validation/cninfo_b_class_phase3_100_expansion/ \
  --approve-b-class-phase3-100-expansion \
  --sleep-seconds 0.6 \
  --limit 100 \
  --resume
```

> **注：** `--phase3-100` 与 approval guard **已实现**；上述 live 命令 **NOT APPROVED** · **不得执行**，须用户显式批准。

---

## 6. Metadata Only

- **metadata retrieval** only
- **pdf URL lineage** only（`adjunct_url` / `pdf_url` 登记）
- **no PDF download**
- **no PDF parse**

---

## 7. Rate Limit

| 项 | 值 |
|----|-----|
| `--sleep-seconds` | **0.6** |
| 并发 | **1** |
| HTTP 429 | 全局停止 |

---

## 8. Approval Gate

```text
b_class_phase3_100_planning_gate = READY_FOR_APPROVAL
b_class_phase3_100_runner_extension_gate = READY_FOR_APPROVAL
```

**NOT APPROVED**

---

## 9. Red Lines

- No CNINFO in this planning round
- No live execution
- No PDF · No DB · No MinIO · No RAG
- No verified · No production_ready
