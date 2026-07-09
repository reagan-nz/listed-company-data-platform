# CNINFO A 类 Phase 1 Schema Freeze Review Summary

_生成时间：2026-07-09_

> **性质：** 离线评审快照；不调用 CNINFO；不 live；不下载 PDF；不写 verified。  
> **评审文档：** [cninfo_a_class_phase1_schema_freeze_review.md](../../plans/cninfo_a_class_phase1_schema_freeze_review.md)  
> **决策矩阵：** [cninfo_a_class_phase1_field_decision_matrix.csv](cninfo_a_class_phase1_field_decision_matrix.csv)  
> **原始 catalog 未修改：** [cninfo_a_class_phase1_minimum_fields.csv](cninfo_a_class_phase1_minimum_fields.csv)

---

## Review Conclusion

A-class Phase 1 freeze v1 提议覆盖三对象：

- `report_document` — 定期报告主 metadata
- `report_period_snapshot` — company × report_type × expected_period 覆盖视图
- `document_lineage` — PDF URL 谱系（`storage_status=not_attempted`）

相较 minimum fields catalog（40 字段），freeze v1 提议：

| 级别 | 数量 | 说明 |
|------|------|------|
| **required** | **22** | +1：`raw_hash` 从 recommended 升级为 required |
| **recommended** | **13** | 含展示、审计、lineage 副本字段 |
| **future** | **4** | `available_sections` · `download_time` · `file_hash` · `file_size` |
| **removed** | **2** | `notes` · `mime_type` — 排除出 Phase1 归一化契约 |

### 按对象拆分

| 对象 | required | recommended | future | removed |
|------|----------|-------------|--------|---------|
| report_document | 13 | 5 | 0 | 1 |
| report_period_snapshot | 4 | 3 | 1 | 0 |
| document_lineage | 5 | 5 | 3 | 1 |

---

## Key Decisions

1. **`raw_hash` upgrade**：`report_document.raw_hash` 从 recommended 升为 required，作为无 PDF 下载条件下的 lineage 变更检测门禁。
2. **`notes` removed**：自由文本不进 Phase1 harvest 产出契约。
3. **`mime_type` removed**：未下载 PDF 无法验证 MIME；从 `document_lineage` 契约中移除。
4. **`available_sections` deferred**：明确依赖 future parser，Phase1 不填。
5. **`pdf_url` required 但可 null**：not_found 行仍须携带字段，值为 null。

---

## Fixture Skeleton

| 文件 | 路径 |
|------|------|
| report_document | [fixtures/a_class/phase1/report_document_fixture.json](../../fixtures/a_class/phase1/report_document_fixture.json) |
| report_period_snapshot | [fixtures/a_class/phase1/report_period_snapshot_fixture.json](../../fixtures/a_class/phase1/report_period_snapshot_fixture.json) |
| document_lineage | [fixtures/a_class/phase1/document_lineage_fixture.json](../../fixtures/a_class/phase1/document_lineage_fixture.json) |

全部为合成占位符；`_fixture_meta.cninfo_called = false`。

---

## Offline Lint

| 项 | 内容 |
|----|------|
| 脚本 | [lab/lint_cninfo_a_class_phase1_freeze_v1.py](../../lab/lint_cninfo_a_class_phase1_freeze_v1.py) |
| 摘要 | [cninfo_a_class_phase1_freeze_v1_lint_summary.md](cninfo_a_class_phase1_freeze_v1_lint_summary.md) |
| 规则数 | **10**（R-A1-001 – R-A1-010） |

---

## Parallel Execution Note

- C-class status remains: **`SNAPSHOT_GENERATED_QA_REVIEW`**
- B-class outputs: **unchanged**
- CNINFO calls this round: **0**
- No C-class / B-class output modification

---

## Gate

```text
a_class_phase1_schema_freeze_review_gate = READY_FOR_APPROVAL
```

**不是 PASS。** 需人工批准后进入下一 offline 任务（P1 coverage CSV → fixture 扩展或 tiny live 规划）。

---

## Recommended Next Task

人工 review / approve schema freeze v1 → 从 `cninfo_report_p1_coverage_validation.csv` 派生更多 offline `report_document` fixture（仍无 live、无 PDF）。
