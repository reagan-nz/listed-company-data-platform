# CNINFO B 类 Non-periodic Document Fixture Seed Summary

_生成时间：2026-07-15（offline known-document benchmark → non-periodic metadata）_

## 1. 目的

从 offline **known-document benchmark** 派生非定期公告 `b_document` metadata fixture。
**不代表真实 CNINFO retrieval coverage**；无 `pdf_url`；不请求 CNINFO。

## 2. 输入

| 来源 | 路径 |
|------|------|
| Known-document benchmark | `fixtures/b_class/known_documents/known_document_benchmark.yaml` |
| B 类 registry | `config/cninfo_b_class_source_registry_draft.yaml` |
| Category routing | `config/cninfo_announcement_categories.yaml` |
| Schema | `schemas/b_class/b_document.schema.json` |
| Seed 脚本 | `lab/seed_cninfo_b_class_non_periodic_document_fixtures.py` |
| Validation 脚本 | `lab/validate_cninfo_b_class_non_periodic_document_schema.py` |

## 3. 总体结果

| 指标 | 数值 |
|------|------|
| benchmark_total | **38** |
| seeded_non_periodic | **30** |
| skipped_periodic | **8** |
| schema_pass | **30** |
| schema_fail | **0** |
| raw_file_seeded | **0** |

## 4. 按 source_id 统计

- `cninfo_inquiry_reply_pdf`: **3**
- `cninfo_meeting_notice_pdf`: **3**
- `cninfo_general_announcement_pdf`: **24**

## 5. 按 document_type 统计

- `inquiry_reply`: **1**
- `regulatory_inquiry`: **2**
- `meeting_notice`: **2**
- `investor_relations_activity`: **1**
- `board_resolution`: **1**
- `shareholder_meeting_material`: **1**
- `announcement`: **21**
- `other`: **1**

## 6. false_positive_reason 同源覆盖（fixture metadata）

- `announcement_preview`: **4**
- `wrong_company`: **4**
- `unrelated_announcement`: **6**
- `(none)`: **16**

Document fixture：`fixtures/b_class/document/non_periodic_document_fixtures.jsonl`

## 7. 质量边界

- 这些是 **offline title fixtures**，不是 CNINFO corpus parsing 结果。
- **没有真实 CNINFO retrieval**；`retrieval_status=found` 仅表示 benchmark 路由命中，非 Phase 1 式 coverage。
- **没有 `pdf_url`**；不能代表 retrieval coverage%。
- `source_confidence=candidate`；**未升级**为 `testing_stable_sample`。
- **不写 verified**。
- `wrong_period` 行仍 route periodic，**不**进入本 non_periodic fixture（见 skipped_periodic）。

### raw_file

Non-periodic fixtures 为 **title-only metadata**，无 `pdf_url`，**不生成** `b_raw_file` fixture。
`non_periodic_raw_file_fixtures.jsonl` 为空文件；待后续小样本 CNINFO 请求补 URL 后再派生 raw_file。

## 8. 下一步

1. 可选：同步 parse_run dry-run（当前可能仍停在旧 non_periodic 行数）。
2. validation_design §7 标题路由 FP 类已齐；后续价值在 retrieval/live 验证，非再开离线 FP lineage。
3. 后续用真实 known-document benchmark 替换离线标题样例。
4. **暂不解析 PDF；不重开 BD2E624。**

## 附录

- [cninfo_b_class_non_periodic_document_seed_report.csv](cninfo_b_class_non_periodic_document_seed_report.csv)
- [cninfo_b_class_non_periodic_document_schema_validation_report.csv](cninfo_b_class_non_periodic_document_schema_validation_report.csv)
