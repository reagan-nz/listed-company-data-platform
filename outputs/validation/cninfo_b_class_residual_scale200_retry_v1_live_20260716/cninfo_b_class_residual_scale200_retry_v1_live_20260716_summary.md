# CNINFO B 类 Corpus Retrieval Live Metadata Validation Summary

_生成时间：2026-07-16（live metadata v1；仅公告 metadata；不下载 PDF）_

## 1. 目的

本次只做 **live metadata validation**：对 ready known-document case 调用
`hisAnnouncement/query` 检索公告标题、日期、pdf_url 可用性与路由分类。
**不下载 PDF，不解析 PDF，不入库。**

## 2. 输入

| 来源 | 路径 |
|------|------|
| Ready known-document cases | `outputs/validation/cninfo_b_class_residual_scale200_retry_v1_live_20260716/known_document_retrieval_cases_live_allowlist.yaml` |
| B 类 registry | `config/cninfo_b_class_source_registry_draft.yaml` |
| Category routing | `config/cninfo_announcement_categories.yaml` |
| 脚本 | `lab/validate_cninfo_b_class_corpus_retrieval.py` |
| mode | **--live-metadata** |

Ready case IDs: `legal_opinion_known_033`, `bond_trustee_report_known_023`, `tracking_rating_report_known_015`, `tracking_rating_report_known_023`, `continuous_supervision_annual_known_012`, `legal_opinion_known_065`, `company_articles_known_010`

## 3. 总体结果

| 指标 | 数值 |
|------|------|
| total_cases | **7** |
| ready_cases | **7** |
| query_executed | **7** |
| pass | **6** |
| fail | **0** |
| ambiguous | **1** |
| not_found | **0** |
| request_error | **0** |
| result | **PARTIAL** |

## 4. 分 case 结果

| case_id | expected title pattern | matched title | matched date | pdf_url | route | case_result |
|---------|------------------------|---------------|--------------|---------|-------|-------------|
| `legal_opinion_known_033` | 法律意见书 | 汉嘉设计2024年年度股东大会法律意见书 | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `bond_trustee_report_known_023` | 平安证券股份有限公司关于广发证券股份有限公司完成注册资本工商 | 平安证券股份有限公司关于广发证券股份有限公司完成注册资本工商变更登记并修订公司章… | 2025-05-12 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `tracking_rating_report_known_015` | 跟踪评级结果的公告 | 富春染织关于“富春转债”2024年跟踪评级结果的公告 | 2025-04-30 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `tracking_rating_report_known_023` | 荣晟环保 | 浙江荣晟环保纸业股份有限公司关于“荣23转债”2025年跟踪评级结果的公告 | 2025-04-18 | true | cninfo_general_announcement_pdf / ambiguous | **ambiguous** |
| `continuous_supervision_annual_known_012` | 华兴证券有限公司关于江苏三房巷聚材股份有限公司2024年持续 | 华兴证券有限公司关于江苏三房巷聚材股份有限公司2024年持续督导年度报告书 | 2025-05-08 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `legal_opinion_known_065` | 债券持有人会议的法律意见书 | 北京市中伦律师事务所关于乐普医疗“乐普转2”2025年第一次债券持有人会议的法律… | 2025-05-15 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `company_articles_known_010` | 关于取消监事会并修订《公司章程》公告 | 关于取消监事会并修订《公司章程》公告 | 2025-06-29 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |

## 5. 质量边界

- 本次 **只验证 metadata retrieval**（标题 / 日期 / pdf_url 字段存在性）。
- **PDF 未下载**；**PDF 未解析**；未生成 chunk / embedding。
- **不代表** corpus parsing 成功；**不代表** RAG 可用。
- **不写 verified**；**不升级** source status。
- placeholder category-sample case **未请求** CNINFO。
- guard case（`periodic_guard_*`）仅做 route/type false-positive 审计。
- 正向 category-sample（`*_sample_*` ready）做全市场 metadata 抽样 + 类型审计。

## 6. 下一步

1. 若 category-sample live pass，可继续补 inquiry/meeting 类 placeholder。
2. 若 fail，先分析 query params / title matching / date window。
3. **暂不下载 PDF**；parse pipeline 仍保持 dry-run。

## 附录

详见 [cninfo_b_class_corpus_retrieval_live_report.csv](cninfo_b_class_corpus_retrieval_live_report.csv)。
