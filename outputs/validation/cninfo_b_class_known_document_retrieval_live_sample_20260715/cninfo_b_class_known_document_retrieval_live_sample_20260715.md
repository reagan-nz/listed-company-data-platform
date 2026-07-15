# CNINFO B 类 Known-Document Retrieval Live Sample — B-R16-02

_生成时间：2026-07-15（live metadata；不下载 PDF）_

| 字段 | 值 |
|------|-----|
| task_id | B-R16-02 |
| track | B |
| executor | b-class-executor |
| controller_execution_allowed | false（本任务 objective 明确要求 small live sample） |
| predecessor | B-R16-01 @ 81c9ffa |
| mode | `lab/validate_cninfo_b_class_corpus_retrieval.py` `--live-metadata`（scoped known YAML） |
| CNINFO total | **8**（cap ≤20；cap_ok=true） |
| topSearch | 4 |
| hisAnnouncement/query | 4 |
| wall_time_s | **34.216** |
| result | **LIVE_PASS** |
| pass/fail/ambiguous | **4/0/0** |
| FP lineage invented | **无** |
| commit / push | **无** |
| capability_gain | `confirmed_live_metadata_retrieval_for_4_B-R16-01_promoted_ready_cases` |
| ready_for_commit | **true**（证据包；未改 fixture/代码） |

## 1. Allow-list

仅请求以下 4 条 B-R16-01 晋升 ready cases（排除其他 ready / guard）：

1. `inquiry_known_002`
2. `meeting_known_002`
3. `ir_activity_known_001`
4. `shareholder_meeting_known_001`

详见 [allow_list.md](allow_list.md)。

## 2. Per-case outcomes

| case_id | company | matched_title | matched_date | classification | case_result |
|---------|---------|---------------|--------------|----------------|-------------|
| `inquiry_known_002` | 601901 方正证券 | 关于2024年年度报告的信息披露监管问询函的回复公告 | 2025-06-13 | classified_correctly | **pass** |
| `meeting_known_002` | 688041 海光信息 | 海光信息技术股份有限公司关于召开重大资产重组事项投资者说明会的公告 | 2025-06-10 | classified_correctly | **pass** |
| `ir_activity_known_001` | 000559 万向钱潮 | 万向钱潮投资者关系活动记录表（2025年6月24日） | 2025-06-25 | classified_correctly | **pass** |
| `shareholder_meeting_known_001` | 300446 航天智造 | 关于召开2025年度第二次临时股东大会通知的公告 | 2025-06-24 | classified_correctly | **pass** |

## 3. 质量边界

- 仅 live metadata（标题 / 日期 / pdf_url 可用性 / 路由分类）。
- **未**下载 PDF；**未**解析；**未**写 verified；**未**升级 source status。
- **未**新造 offline §7 FP lineage。
- **未**触碰 A/C/D 文件。
- **未** commit / push。

## 4. 产物

| 文件 | 用途 |
|------|------|
| [allow_list.md](allow_list.md) | live allow-list |
| [known_document_retrieval_cases_live_sample_allowlist.yaml](known_document_retrieval_cases_live_sample_allowlist.yaml) | scoped known input |
| [category_sample_cases_live_sample_empty.yaml](category_sample_cases_live_sample_empty.yaml) | 空 category（排除 guard） |
| [cninfo_b_class_known_document_retrieval_live_sample_20260715_report.csv](cninfo_b_class_known_document_retrieval_live_sample_20260715_report.csv) | per-case CSV |
| [cninfo_b_class_known_document_retrieval_live_sample_20260715_summary.md](cninfo_b_class_known_document_retrieval_live_sample_20260715_summary.md) | live summary |
| [cninfo_b_class_known_document_retrieval_live_sample_20260715_metrics.md](cninfo_b_class_known_document_retrieval_live_sample_20260715_metrics.md) | CNINFO/wall metrics |

## 5. 下一步

1. Controller 可审阅本 live sample 证据包。
2. 若需全 ready 集 live（含既有 4 + guard），另开任务并单独 cap。
3. commit 边界由 controller 决定；本任务证据已齐，`ready_for_commit=true`。
