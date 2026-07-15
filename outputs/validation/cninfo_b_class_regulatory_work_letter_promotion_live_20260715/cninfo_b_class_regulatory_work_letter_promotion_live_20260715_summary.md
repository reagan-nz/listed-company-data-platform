# CNINFO B 类 Corpus Retrieval Live Metadata Validation Summary

_生成时间：2026-07-15（live metadata v1；仅公告 metadata；不下载 PDF）_

## 1. 目的

本次只做 **live metadata validation**：对 ready known-document case 调用
`hisAnnouncement/query` 检索公告标题、日期、pdf_url 可用性与路由分类。
**不下载 PDF，不解析 PDF，不入库。**

## 2. 输入

| 来源 | 路径 |
|------|------|
| Ready known-document cases | `outputs/validation/cninfo_b_class_regulatory_work_letter_promotion_live_20260715/known_document_retrieval_cases_live_allowlist.yaml` |
| B 类 registry | `config/cninfo_b_class_source_registry_draft.yaml` |
| Category routing | `config/cninfo_announcement_categories.yaml` |
| 脚本 | `lab/validate_cninfo_b_class_corpus_retrieval.py` |
| mode | **--live-metadata** |

Ready case IDs: `inquiry_known_004`, `inquiry_sample_003`

## 3. 总体结果

| 指标 | 数值 |
|------|------|
| total_cases | **2** |
| ready_cases | **2** |
| query_executed | **3** |
| pass | **2** |
| fail | **0** |
| ambiguous | **0** |
| not_found | **0** |
| request_error | **0** |
| result | **LIVE_PASS** |

## 4. 分 case 结果

| case_id | expected title pattern | matched title | matched date | pdf_url | route | case_result |
|---------|------------------------|---------------|--------------|---------|-------|-------------|
| `inquiry_known_004` | 中兴财光华会计师事务所（特殊普通合伙）关于对文投控股股份有限 | 中兴财光华会计师事务所（特殊普通合伙）关于对文投控股股份有限公司2024年年度报… | 2025-04-28 | true | cninfo_inquiry_reply_pdf / classified_correctly | **pass** |
| `inquiry_sample_003` | 监管工作函 | 鹏博士关于收到上海证券交易所《关于鹏博士电信传媒集团股份有限公司终止上市相关事项… | 2025-04-29 | true | cninfo_inquiry_reply_pdf / classified_correctly | **pass** |

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
