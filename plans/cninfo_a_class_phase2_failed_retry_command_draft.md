# CNINFO A 类 Phase 2 Failed Cases Isolated Retry — Command Draft

_生成时间：2026-07-09_

> **性质：** 未来 isolated retry 命令草案。**不执行** · **NOT APPROVED**

**Phase 2 execution gate：** `a_class_phase2_metadata_execution_gate = FAIL_REVIEW_REQUIRED`

---

## 1. 范围约束

| 项 | 值 |
|----|-----|
| retry universe | [cninfo_a_class_phase2_failed_retry_universe.csv](../outputs/validation/cninfo_a_class_phase2_failed_retry_universe.csv)（**8** 家） |
| successful cases excluded | A2M001–A2M004, A2M006–A2M009, A2M014–A2M017（**12** 家） |
| schema | a_class_phase1_freeze_v1（**不变**） |
| matching | v2 · `MATCHING_LOGIC_VERSION = "v2"`（**不变**） |
| max retry cases | **8** |
| CNINFO calls（本回合） | **0** |

### 明确包含

- **metadata only**
- isolated retry for failed cases only
- v2 title/period matching（不变）

### 明确禁止

- **no PDF download**
- **no PDF parse**
- **no OCR**
- **no extraction**
- **no DB**
- **no MinIO**
- **no RAG**
- rerun successful 12 cases
- universe replacement
- schema / matching logic change

---

## 2. 输出隔离

**专用 retry 输出根（强制）：**

```text
outputs/validation/cninfo_a_class_phase2_metadata_retry/
```

**Universe path：**

```text
outputs/validation/cninfo_a_class_phase2_failed_retry_universe.csv
```

**禁止写入：**

- `outputs/validation/cninfo_a_class_phase2_metadata_expansion/`（Phase 2 live baseline）
- `outputs/validation/cninfo_a_class_tiny_live_metadata/`（Phase 1）

---

## 3. 规划命令（未来回合 · NOT APPROVED）

```bash
cd listed_company_data_collector

python lab/run_cninfo_a_class_phase2_metadata_expansion.py \
  --retry-failed-only \
  --live \
  --universe-csv outputs/validation/cninfo_a_class_phase2_failed_retry_universe.csv \
  --output-root outputs/validation/cninfo_a_class_phase2_metadata_retry/ \
  --approve-a-class-phase2-failed-retry
```

### Dry-run（规划）

```bash
python lab/run_cninfo_a_class_phase2_metadata_expansion.py \
  --retry-failed-only \
  --dry-run \
  --universe-csv outputs/validation/cninfo_a_class_phase2_failed_retry_universe.csv \
  --output-root outputs/validation/cninfo_a_class_phase2_metadata_retry/
```

### 批准 flag 占位

```text
--approve-a-class-phase2-failed-retry
```

**状态：NOT APPROVED**

---

## 4. Gate（本回合）

```text
a_class_phase2_failed_retry_planning_gate = READY_FOR_APPROVAL
```

**不是 PASS** · **不是 live_ready** · **不是 verified** · **不是 production_ready**
