# CNINFO B 类 Corpus Retrieval Live Metadata Validation Summary

_生成时间：2026-07-15（live metadata v1；仅公告 metadata；不下载 PDF）_

## 1. 目的

本次只做 **live metadata validation**：对 ready known-document case 调用
`hisAnnouncement/query` 检索公告标题、日期、pdf_url 可用性与路由分类。
**不下载 PDF，不解析 PDF，不入库。**

## 2. 输入

| 来源 | 路径 |
|------|------|
| Ready known-document cases | `outputs/validation/cninfo_b_class_verification_opinion_known_001_002_live_20260715/known_document_retrieval_cases_live_allowlist.yaml` |
| B 类 registry | `config/cninfo_b_class_source_registry_draft.yaml` |
| Category routing | `config/cninfo_announcement_categories.yaml` |
| 脚本 | `lab/validate_cninfo_b_class_corpus_retrieval.py` |
| mode | **--live-metadata** |

Ready case IDs: `verification_opinion_known_001`, `verification_opinion_known_002`

## 3. 总体结果

| 指标 | 数值 |
|------|------|
| total_cases | **2** |
| ready_cases | **2** |
| query_executed | **2** |
| pass | **2** |
| fail | **0** |
| ambiguous | **0** |
| not_found | **0** |
| request_error | **0** |
| result | **LIVE_PASS** |

## 4. 分 case 结果

| case_id | expected title pattern | matched title | matched date | pdf_url | route | case_result |
|---------|------------------------|---------------|--------------|---------|-------|-------------|
| `verification_opinion_known_001` | 募集资金等额置换的核查意见 | 华泰联合证券有限责任公司关于三六零安全科技股份有限公司使用自有资金支付募投项目部… | 2025-06-27 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |
| `verification_opinion_known_002` | 限售股上市流通的核查意见 | 中信建投证券股份有限公司关于北京福元医药股份有限公司首次公开发行限售股上市流通的… | 2025-06-24 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |

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
