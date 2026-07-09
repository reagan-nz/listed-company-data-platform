# CNINFO B 类 Phase 2.5 Expansion — Command Draft

_生成时间：2026-07-09_

> **性质：** 未来 Phase 2.5 live metadata expansion 命令草案。**不执行** · **NOT APPROVED**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**Phase 2 closure gate：** `b_class_phase2_expansion_closure_gate = PASS_WITH_CAVEAT`

**runner_extension_required：** **true**（需扩展 Phase 2 runner 或新建 Phase 2.5 runner）

---

## 1. 范围约束

| 项 | 值 |
|----|-----|
| universe | [cninfo_b_class_phase25_expansion_universe_draft.csv](../outputs/validation/cninfo_b_class_phase25_expansion_universe_draft.csv)（**50** 家） |
| schema | phase1_freeze_v1 · **15** required fields（**不变**） |
| endpoints | EP001 · EP002 · EP004 · EP005 only |
| max cases | **50** |
| CNINFO calls（本回合） | **0** |

### 禁止

- PDF download / parse / OCR / section extraction
- harvest 写入 `outputs/harvest/`
- DB / MinIO / RAG
- verified / testing_stable_sample
- 触碰 Phase 1 / Phase 2 / TLC002 输出根

---

## 2. 输出隔离

**专用输出根（强制）：**

```text
outputs/validation/cninfo_b_class_phase25_expansion/
```

---

## 3. Live Command Draft（NOT APPROVED）

```bash
# NOT APPROVED — 须 runner 扩展 + 用户显式批准后方可执行

cd listed_company_data_collector

python lab/run_cninfo_b_class_phase25_expansion_validation.py \
  --live \
  --universe-csv outputs/validation/cninfo_b_class_phase25_expansion_universe_draft.csv \
  --output-root outputs/validation/cninfo_b_class_phase25_expansion/ \
  --approve-b-class-phase25-expansion \
  --sleep-seconds 0.6 \
  --limit 50 \
  --resume
```

> **注：** `run_cninfo_b_class_phase25_expansion_validation.py` 为规划脚本名；可在未来回合由 Phase 2 runner 参数化。**本回合不创建该脚本。**

---

## 4. Metadata Only

- **metadata retrieval** only
- **pdf URL lineage** only（`adjunct_url` / `pdf_url` 登记）
- **no PDF download**
- **no PDF parse**

---

## 5. Rate Limit

| 项 | 值 |
|----|-----|
| `--sleep-seconds` | **0.6** |
| 并发 | **1** |
| HTTP 429 | 全局停止 |

---

## 6. Approval Gate

```text
b_class_phase25_expansion_planning_gate = READY_FOR_APPROVAL
```

**NOT APPROVED**

---

## 7. Red Lines

- No CNINFO in this planning round
- No live execution
- No PDF · No DB · No MinIO · No RAG
- No verified · No production_ready
