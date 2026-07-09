# CNINFO A 类 Phase 2 Metadata Expansion — Command Draft

_生成时间：2026-07-09_

> **性质：** 未来 Phase 2 metadata expansion 命令草案。**不执行** · **NOT APPROVED**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`（不变）

**Phase 1 boundary gate：** `a_class_phase1_boundary_gate = PASS_WITH_CAVEAT`

**runner_extension_required：** **true**（Phase 2 专用 runner 扩展 **未实现**；可基于 Phase 1 tiny live runner 派生）

---

## 1. 范围约束

| 项 | 值 |
|----|-----|
| universe | [cninfo_a_class_phase2_metadata_universe_draft.csv](../outputs/validation/cninfo_a_class_phase2_metadata_universe_draft.csv)（**20** 家 · A2M001–A2M020） |
| schema | a_class_phase1_freeze_v1 · **22** required fields（**不变**） |
| objects | `report_document` · `report_period_snapshot` · `document_lineage` |
| matching | v2 · `MATCHING_LOGIC_VERSION = "v2"` |
| max cases | **20** |
| CNINFO calls（本回合） | **0** |

### 明确包含

- **metadata only**
- report-type 专用标题匹配
- period 匹配
- pdf URL lineage 登记（**不下载**）

### 明确禁止

- **no PDF download**
- **no PDF parse**
- **no OCR**
- **no extraction**（section / table）
- **no DB**
- **no MinIO**
- **no RAG**
- verified / production_ready / testing_stable_sample 升级
- 触碰 Phase 1 输出根 `outputs/validation/cninfo_a_class_tiny_live_metadata/`
- 触碰 C-class / B-class / D-class 既有输出

---

## 2. 输出隔离

**专用输出根（强制）：**

```text
outputs/validation/cninfo_a_class_phase2_metadata_expansion/
```

**Universe path：**

```text
outputs/validation/cninfo_a_class_phase2_metadata_universe_draft.csv
```

建议子路径：

```text
outputs/validation/cninfo_a_class_phase2_metadata_expansion/
  reports/
    a_class_phase2_metadata_expansion_report.csv
    a_class_phase2_metadata_expansion_summary.md
    a_class_phase2_metadata_expansion_quality_report.csv
  raw_metadata/
    A2M001.json … A2M020.json
```

---

## 3. 硬编码常量（未来 runner 须遵守）

```python
# 规划常量 — 未来回合实现；Phase 2 全程禁止

DOWNLOAD_PDF = False
PARSE_PDF = False
ENABLE_OCR = False
ENABLE_SECTION_EXTRACTION = False
ENABLE_TABLE_EXTRACTION = False
WRITE_DB = False
WRITE_MINIO = False
ENABLE_RAG = False
WRITE_VERIFIED = False
UPGRADE_TESTING_STABLE_SAMPLE = False
MATCHING_LOGIC_VERSION = "v2"
STORAGE_STATUS_PHASE2 = "not_attempted"
```

---

## 4. 规划命令（未来回合 · NOT APPROVED）

```bash
cd listed_company_data_collector

python lab/run_cninfo_a_class_phase2_metadata_expansion.py \
  --universe-csv outputs/validation/cninfo_a_class_phase2_metadata_universe_draft.csv \
  --output-root outputs/validation/cninfo_a_class_phase2_metadata_expansion/ \
  --matching-logic-version v2 \
  --approve-a-class-phase2-metadata-expansion
```

### 批准 flag 占位

```text
--approve-a-class-phase2-metadata-expansion
```

**状态：NOT APPROVED**

须用户显式批准后方可执行 live metadata validation。

---

## 5. Dry-run 命令（未来 runner 实现后）

```bash
python lab/run_cninfo_a_class_phase2_metadata_expansion.py \
  --universe-csv outputs/validation/cninfo_a_class_phase2_metadata_universe_draft.csv \
  --output-root outputs/validation/cninfo_a_class_phase2_metadata_expansion/ \
  --dry-run
```

Dry-run **不调用 CNINFO**；仅校验 universe CSV 结构与 code/name 一致性。

---

## 6. 执行前检查清单

- [ ] Phase 1 boundary reviewed（`PASS_WITH_CAVEAT`）
- [ ] v2 matching policy reviewed
- [ ] 20-company universe CSV 人工审阅
- [ ] report-type mix ~8/4/4/4 确认
- [ ] output root 隔离确认
- [ ] `--approve-a-class-phase2-metadata-expansion` 显式批准
- [ ] runner extension 实现并通过测试

---

## 7. 预期产物

| 产物 | 路径 |
|------|------|
| expansion report | `reports/a_class_phase2_metadata_expansion_report.csv` |
| expansion summary | `reports/a_class_phase2_metadata_expansion_summary.md` |
| quality report | `reports/a_class_phase2_metadata_expansion_quality_report.csv` |
| raw metadata | `raw_metadata/A2M*.json` |

**不含：** PDF 文件 · parsed text · DB dump · MinIO object · embedding · RAG index

---

## 8. Gate（本回合）

```text
a_class_phase2_metadata_planning_gate = READY_FOR_APPROVAL
```

**不是 PASS。** **不是 live_ready。** **不是 verified。** **不是 production_ready。**
