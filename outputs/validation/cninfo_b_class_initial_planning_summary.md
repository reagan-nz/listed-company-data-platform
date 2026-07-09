# CNINFO B 类 Initial Planning Summary

_生成时间：2026-07-09_

> **性质：** 规划快照；不调用 CNINFO；不 live；不 harvest；不触碰 C-class Phase 3 live 输出根。

---

## Current Conclusion

B-class 应以 **metadata discovery + PDF URL lineage + quality review** 作为第一阶段主线，而不是直接进入 PDF 下载、解析或 RAG。

理由：

1. 仓库已有较完整的 B-class corpus / schema / routing / registry 草案，以及 5-case live metadata v1 证据，但**缺少面向“公告元数据层”的统一 Phase 0 收敛**。
2. A-class Phase 1 已证明 `hisAnnouncement/query` 对定期报告检索可用（94.10% effective coverage），可作为 B-class `periodic_report_pdf` 的继承基线。
3. C-class 当前处于 `SNAPSHOT_GENERATED_QA_REVIEW`，且 Phase 3 batch 500 live harvest 可能正在另一终端运行；B-class 应并行做**纯离线规划**，避免干扰 C-class 输出与带宽。

B-class **不是** C-class F10 profile 数据的替代品；二者通过 `company_code` / `org_id` 关联，职责分离。

---

## Recommended First Phase

### B-class Phase 0: source discovery and schema design

| 步骤 | 内容 | 本轮状态 |
|------|------|----------|
| 1 | 发布架构计划 | 完成 |
| 2 | 发布 source discovery 计划 | 完成 |
| 3 | 发布 readiness matrix | 完成 |
| 4 | 离线盘点既有 A/B artifacts | 完成 |
| 5 | 冻结 Phase 1 minimum fields CSV | 待做 |
| 6 | 生成 endpoint candidate 表 | 待做 |
| 7 | tiny offline sample review | 待做 |
| 8 | 请求 live approval | **不做** |

Phase 0 交付物：

- [cninfo_b_class_announcement_metadata_architecture_plan.md](../../plans/cninfo_b_class_announcement_metadata_architecture_plan.md)
- [cninfo_b_class_source_discovery_plan.md](../../plans/cninfo_b_class_source_discovery_plan.md)
- [cninfo_b_class_readiness_matrix.csv](cninfo_b_class_readiness_matrix.csv)
- [cninfo_b_class_existing_artifact_inventory.csv](cninfo_b_class_existing_artifact_inventory.csv)
- [cninfo_b_class_existing_artifact_inventory_summary.md](cninfo_b_class_existing_artifact_inventory_summary.md)

---

## Do Not Start Yet

- **no live CNINFO**
- **no PDF download**
- **no PDF parsing**
- **no RAG / vector index**
- **no DB**
- **no MinIO**
- **no verified**
- **no testing_stable_sample upgrade**
- **no C-class Phase 3 output modification**（尤其 `outputs/harvest/cninfo_c_class/phase3_batch_500_001/`）

---

## Parallel Execution Note

While C-class Phase 3 live harvest may be running in another terminal:

- B-class planning has started in this round only.
- No B-class live execution was performed.
- C-class status remains: **`SNAPSHOT_GENERATED_QA_REVIEW`**
- C-class Phase 3 live output root was **not read or written** during this planning round.

---

## Recommended Next B-class Task

**Offline：生成 `cninfo_b_class_endpoint_candidate_table.csv` + `cninfo_b_class_phase1_minimum_fields.csv`，并对照既有 registry YAML 做 schema freeze v1 review。**

仍不 live、不 harvest、不下载 PDF。

---

## Gate

```text
b_class_initial_planning_gate = DESIGN_STARTED
b_class_existing_artifact_inventory_gate = PASS
```
