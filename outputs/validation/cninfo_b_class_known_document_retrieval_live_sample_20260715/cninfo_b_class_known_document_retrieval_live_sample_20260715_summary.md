# CNINFO B 类 Corpus Retrieval Live Metadata Validation Summary

_生成时间：2026-07-15（live metadata v1；仅公告 metadata；不下载 PDF）_

## 1. 目的

本次只做 **live metadata validation**：对 ready known-document case 调用
`hisAnnouncement/query` 检索公告标题、日期、pdf_url 可用性与路由分类。
**不下载 PDF，不解析 PDF，不入库。**

## 2. 输入

| 来源 | 路径 |
|------|------|
| Ready known-document cases | `outputs/validation/cninfo_b_class_known_document_retrieval_live_sample_20260715/known_document_retrieval_cases_live_sample_allowlist.yaml` |
| B 类 registry | `config/cninfo_b_class_source_registry_draft.yaml` |
| Category routing | `config/cninfo_announcement_categories.yaml` |
| 脚本 | `lab/validate_cninfo_b_class_corpus_retrieval.py` |
| mode | **--live-metadata** |

Ready case IDs: `inquiry_known_002`, `meeting_known_002`, `ir_activity_known_001`, `shareholder_meeting_known_001`

## 3. 总体结果

| 指标 | 数值 |
|------|------|
| total_cases | **4** |
| ready_cases | **4** |
| query_executed | **4** |
| pass | **4** |
| fail | **0** |
| ambiguous | **0** |
| not_found | **0** |
| request_error | **0** |
| result | **LIVE_PASS** |

## 4. 分 case 结果

| case_id | expected title pattern | matched title | matched date | pdf_url | route | case_result |
|---------|------------------------|---------------|--------------|---------|-------|-------------|
| `inquiry_known_002` | 信息披露监管问询函的回复公告 | 关于2024年年度报告的信息披露监管问询函的回复公告 | 2025-06-13 | true | cninfo_inquiry_reply_pdf / classified_correctly | **pass** |
| `meeting_known_002` | 关于召开重大资产重组事项投资者说明会的公告 | 海光信息技术股份有限公司关于召开重大资产重组事项投资者说明会的公告 | 2025-06-10 | true | cninfo_meeting_notice_pdf / classified_correctly | **pass** |
| `ir_activity_known_001` | 投资者关系活动记录表 | 万向钱潮投资者关系活动记录表（2025年6月24日） | 2025-06-25 | true | cninfo_meeting_notice_pdf / classified_correctly | **pass** |
| `shareholder_meeting_known_001` | 股东大会通知 | 关于召开2025年度第二次临时股东大会通知的公告 | 2025-06-24 | true | cninfo_general_announcement_pdf / classified_correctly | **pass** |

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
