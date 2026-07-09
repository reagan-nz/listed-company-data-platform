# CNINFO A 类 Initial Planning Summary

_生成时间：2026-07-09_

> **性质：** 规划快照；不调用 CNINFO；不 live；不 harvest；不触碰 C-class Phase 3 live 输出根；不修改 B-class / C-class 输出。

---

## Architecture Decision

A-class 应以 **定期报告 document evidence 层**作为主线，对象模型收敛为三件：

1. **`report_document`** — 单份定期报告的主 metadata 记录
2. **`report_period_snapshot`** — 公司 × 报告期覆盖视图
3. **`document_lineage`** — PDF URL 与谱系登记（Phase 0 不下载）

设计决策：

- A-class 回答 **"What official documents explain this company?"**，覆盖年报 / 半年报 / 季报
- 继承 A-class Phase 1 `hisAnnouncement/query` retrieval 证据（94.10% effective coverage），但**从 coverage 验证升级为 metadata 对象层**
- PDF 正文下载、解析、RAG **全部 deferred**；`storage_status` 初值固定 `not_attempted`
- 与 B-class 分离：B-class 管非定期公告事件流；A-class 管周期性披露报告
- 与 C-class 通过 `company_code` 关联，**不 merge identity**

---

## Object Relationship

```text
C-class company (company_code, org_id, company_name)
        |
        v
A-class report_document (document_id, report_type, report_period, pdf_url, ...)
        |
        +---> report_period_snapshot (year, quarter, document_id, available_sections)
        |
        +---> document_lineage (source_url, raw_hash, storage_status, version)
        |
        v
future extraction (parse / chunk / embed) — deferred
```

---

## Source Discovery Status

| 候选源 | Endpoint | Confidence | 本轮状态 |
|--------|----------|------------|----------|
| Periodic report PDF | `hisAnnouncement/query` | high | 离线设计完成；继承 Phase 1 |
| Annual report metadata | `hisAnnouncement/query` + category | high | 离线设计完成 |
| Semi-annual report metadata | `hisAnnouncement/query` + category | high | 离线设计完成 |
| Quarterly report metadata | `hisAnnouncement/query` + category fallback | medium | 离线设计完成；SZSE 缺口已记录 |
| Report announcement lineage | 响应处理层 | medium | 对象已定义；未 live 验证 |

```text
a_class_source_discovery_gate = OFFLINE_DESIGN_COMPLETE
```

本轮 **无 CNINFO 调用** · **无 live** · **无 PDF 下载**。

---

## Blockers

| 阻塞项 | 说明 | 解除路径 |
|--------|------|----------|
| A-class JSON Schema 未 freeze | `report_document` 等三对象仅有架构描述 | 下一轮 offline schema freeze review |
| Quarterly SZSE 缺口 | P1 Q1 86.67% / Q3 90.00% | 离线规则 freeze + tiny live 定向复测（需批准） |
| dedup policy 未实现 | `document_id` vs `announcement_id` 未最终裁定 | offline decision matrix |
| `available_sections` 依赖 parser | 解析层 deferred | 不在 Phase 0/1 解除 |
| C-class Phase 3 live 并行 | 可能占带宽 | A-class live 需等 C-class harvest 完成或显式并行批准 |

---

## Future Validation Path

| 阶段 | 内容 | Gate |
|------|------|------|
| **Phase 0（本轮）** | 架构 + source discovery + readiness + field catalog | `DESIGN_STARTED` |
| **Phase 1** | schema freeze + offline fixture 骨架 + registry 草案 | `READY_FOR_SCHEMA_REVIEW` |
| **Phase 2** | tiny live metadata（3–5 家 known-company，仍不下载 PDF） | `READY_FOR_APPROVAL` |
| **Later** | PDF download / parse / RAG | deferred · 独立批准 |

Phase 2 tiny live 建议样本：600000 / 300001 / 688001（与 C-class known-company 矩阵对齐），每公司 4 report_type × 1 expected_period。

---

## Do Not Start Yet

- **no CNINFO**
- **no live**
- **no PDF download**
- **no PDF parsing**
- **no RAG / vector index**
- **no DB**
- **no MinIO**
- **no verified**
- **no testing_stable_sample upgrade**
- **no identity merge**
- **no C-class / B-class output modification**

---

## Parallel Execution Note

While C-class Phase 3 live harvest may be running in another terminal:

- A-class planning has started in this round only.
- No A-class live execution was performed.
- C-class status remains: **`SNAPSHOT_GENERATED_QA_REVIEW`**
- B-class outputs were **not modified**.
- C-class Phase 3 live output root was **not read or written** during this planning round.

---

## Deliverables（本轮）

| 产物 | 路径 |
|------|------|
| 架构计划 | [cninfo_a_class_report_metadata_architecture_plan.md](../../plans/cninfo_a_class_report_metadata_architecture_plan.md) |
| Source discovery 计划 | [cninfo_a_class_source_discovery_plan.md](../../plans/cninfo_a_class_source_discovery_plan.md) |
| Phase 1 minimum fields | [cninfo_a_class_phase1_minimum_fields.csv](cninfo_a_class_phase1_minimum_fields.csv)（**40** 字段） |
| Readiness matrix | [cninfo_a_class_readiness_matrix.csv](cninfo_a_class_readiness_matrix.csv)（**6** 组件） |
| Planning summary | 本文件 |

---

## Recommended Next A-class Task

**Offline：A-class Phase 1 schema freeze review + 从 P1 coverage CSV 派生 offline `report_document` fixture 骨架。**

仍不 live、不 harvest、不下载 PDF。

---

## Gate

```text
a_class_initial_planning_gate = DESIGN_STARTED
```
