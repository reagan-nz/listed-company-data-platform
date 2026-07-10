# CNINFO A 类 Phase 3 50-Company Expansion — Command Draft

_生成时间：2026-07-10_

> **性质：** 未来 Phase 3 50-company live metadata expansion 命令草案。**不执行** · **NOT APPROVED**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`（不变）

**Phase 2 final closure gate：** `a_class_phase2_metadata_final_closure_gate = PASS_WITH_CAVEAT`

**Phase 2 commit：** `cad5ed1`

**runner_extension_required：** **false**（`--phase3-50` dry-run **50/50** · test **26/26 PASS**）

**live_path_required：** **false**（`process_phase3_50_live` **已实现** · live-path test **28/28 PASS** · **NOT APPROVED live**）

---

## 1. 范围约束

| 项 | 值 |
|----|-----|
| universe | [cninfo_a_class_phase3_50_company_universe_draft.csv](../outputs/validation/cninfo_a_class_phase3_50_company_universe_draft.csv)（**50** 家 · A3M001–A3M050） |
| schema | a_class_phase1_freeze_v1 · **22** required fields（**不变**） |
| matching | v2 · `MATCHING_LOGIC_VERSION = "v2"` |
| max cases | **50** |
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
- 触碰 Phase 1 / Phase 2 / retry / precheck 既有输出根
- 重跑 Phase 2 effective accepted 20

---

## 2. 输出隔离

**专用输出根（强制）：**

```text
outputs/validation/cninfo_a_class_phase3_50_company_expansion/
```

**Universe path：**

```text
outputs/validation/cninfo_a_class_phase3_50_company_universe_draft.csv
```

---

## 3. 硬编码常量（未来 runner 须遵守）

```python
# 规划常量 — 未来回合实现；Phase 3 全程禁止

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
STORAGE_STATUS_PHASE3 = "not_attempted"
```

---

## 4. 规划命令（未来回合 · NOT APPROVED）

```bash
cd listed_company_data_collector

python lab/run_cninfo_a_class_phase2_metadata_expansion.py \
  --phase3-50 \
  --live \
  --universe-csv outputs/validation/cninfo_a_class_phase3_50_company_universe_draft.csv \
  --output-root outputs/validation/cninfo_a_class_phase3_50_company_expansion/ \
  --approve-a-class-phase3-50-company-expansion
```

**Acceptance threshold（规划 · 本回合未 live 评估）：**

```text
≥40/50 acceptable → a_class_phase3_50_company_execution_gate = PASS_WITH_CAVEAT
<40/50 acceptable → a_class_phase3_50_company_execution_gate = FAIL_REVIEW_REQUIRED
```

### 批准 flag 占位

```text
--approve-a-class-phase3-50-company-expansion
```

**状态：NOT APPROVED**

须用户显式批准后方可执行 live metadata validation。

---

## 5. Dry-run 命令（已实现 · 本回合已执行）

```bash
python lab/run_cninfo_a_class_phase2_metadata_expansion.py \
  --phase3-50 \
  --dry-run \
  --universe-csv outputs/validation/cninfo_a_class_phase3_50_company_universe_draft.csv \
  --output-root outputs/validation/cninfo_a_class_phase3_50_company_expansion/
```

Dry-run **不调用 CNINFO**；**50/50 planned_ok** · CNINFO **0**。

---

## 6. 执行前检查清单

- [ ] Phase 2 closure reviewed（effective **20/20** · commit **`cad5ed1`**）
- [ ] v2 matching policy reviewed
- [ ] 50-company universe CSV 人工审阅
- [ ] report-type mix 20/10/10/10 确认
- [ ] Phase 1/Phase 2 overlap **0** 确认
- [ ] output root 隔离确认
- [ ] `--approve-a-class-phase3-50-company-expansion` 显式批准
- [x] runner extension 实现并通过测试（**26/26 PASS**）
- [x] dry-run **50/50 planned_ok**

---

## 7. 预期产物

| 产物 | 路径 |
|------|------|
| expansion report | `reports/a_class_phase3_50_company_expansion_report.csv` |
| expansion summary | `reports/a_class_phase3_50_company_expansion_summary.md` |
| quality report | `reports/a_class_phase3_50_company_expansion_quality_report.csv` |
| raw metadata | `raw_metadata/A3M*.json` |

**不含：** PDF 文件 · parsed text · DB dump · MinIO object · embedding · RAG index

---

## 8. Gate（本回合）

```text
a_class_phase3_50_company_planning_gate = READY_FOR_APPROVAL
a_class_phase3_50_company_runner_extension_gate = READY_FOR_APPROVAL
a_class_phase3_50_company_live_path_gate = READY_FOR_APPROVAL
```

**不是 PASS。** **不是 live_ready。** **不是 verified。** **不是 production_ready。**
