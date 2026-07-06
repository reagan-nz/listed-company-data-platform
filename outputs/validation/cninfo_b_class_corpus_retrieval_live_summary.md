# CNINFO B 类 Corpus Retrieval Live Metadata Validation Summary

_生成时间：2026-07-05（live metadata v1；仅公告 metadata；不下载 PDF）_

## 1. 目的

本次只做 **live metadata validation**：对 ready known-document case 调用
`hisAnnouncement/query` 检索公告标题、日期、pdf_url 可用性与路由分类。
**不下载 PDF，不解析 PDF，不入库。**

## 2. 输入

| 来源 | 路径 |
|------|------|
| Ready known-document cases | `fixtures/b_class/retrieval_validation/known_document_retrieval_cases.yaml` |
| B 类 registry | `config/cninfo_b_class_source_registry_draft.yaml` |
| Category routing | `config/cninfo_announcement_categories.yaml` |
| 脚本 | `lab/validate_cninfo_b_class_corpus_retrieval.py` |
| mode | **--live-metadata** |

Ready case IDs: `inquiry_known_003`, `regulatory_known_002`, `meeting_known_001`, `board_resolution_known_001`, `periodic_guard_002`

## 3. 总体结果

| 指标 | 数值 |
|------|------|
| total_cases | **5** |
| ready_cases | **5** |
| query_executed | **5** |
| pass | **5** |
| fail | **0** |
| ambiguous | **0** |
| not_found | **0** |
| request_error | **0** |
| result | **LIVE_PASS** |

## 4. 分 case 结果

| case_id | expected title pattern | matched title | matched date | pdf_url | route | case_result |
|---------|------------------------|---------------|--------------|---------|-------|-------------|
| `inquiry_known_003` | 关于深圳证券交易所年报问询函回复的公告 | 关于深圳证券交易所年报问询函回复的公告 | 2024-05-27 | true | cninfo_inquiry_reply_pdf / classified_correctly | **pass** |
| `regulatory_known_002` | 关于收到深圳证券交易所关注函的公告 | 关于收到深圳证券交易所关注函的公告 | 2023-01-31 | true | cninfo_inquiry_reply_pdf / classified_correctly | **pass** |
| `meeting_known_001` | 关于举办2024年度业绩说明会的公告 | 关于举办2024年度业绩说明会的公告 | 2025-05-08 | true | cninfo_meeting_notice_pdf / classified_correctly | **pass** |
| `board_resolution_known_001` | 董事会决议公告 | 董事会决议公告 | 2025-04-17 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `periodic_guard_002` | 年度报告摘要 | 2024年年度报告摘要 | 2025-04-01 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |

## 5. 质量边界

- 本次 **只验证 metadata retrieval**（标题 / 日期 / pdf_url 字段存在性）。
- **PDF 未下载**；**PDF 未解析**；未生成 chunk / embedding。
- **不代表** corpus parsing 成功；**不代表** RAG 可用。
- **不写 verified**；**不升级** source status。
- placeholder / non-guard category-sample case **未请求** CNINFO。
- guard case（`periodic_guard_*`）仅做 route/type false-positive 审计。

## 6. 下一步

1. 若 3/3 pass，可补 `board_resolution_known_001` / `periodic_guard_002` 等 ready case。
2. 若 fail，先分析 query params / title matching / date window。
3. 后续再考虑 category-sample live validation。
4. **暂不下载 PDF**；parse pipeline 仍保持 dry-run。

## 附录

详见 [cninfo_b_class_corpus_retrieval_live_report.csv](cninfo_b_class_corpus_retrieval_live_report.csv)。
