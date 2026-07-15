# CNINFO B 类 CPA Inquiry-Reply Promotion Live Allow-list — B-FM-03

_生成时间：2026-07-15_

## 范围

仅请求以下 **2** 条 B-FM-03 新晋 ready cases（排除既有 ready / placeholder / guard）：

1. `inquiry_known_001` — 华钰矿业 601020 · CPA 全文「…信息披露监管问询函的回复」 · 2025-06-23 ~ 2025-06-26
2. `inquiry_sample_002` — 问询函的回复 · 2025-06-23 ~ 2025-06-28（全市场类别抽样）

## 输入文件

- known: `known_document_retrieval_cases_live_allowlist.yaml`
- category: `category_sample_cases_live_allowlist.yaml`

## 边界

- known：topSearch + hisAnnouncement/query metadata
- category：hisAnnouncement/query metadata（sse + szse）
- **不**下载 PDF；**不**解析；**不**写 verified；**不**升级 source status
- **不**触碰 A/C/D；**不** commit / push
- 不造 §7 FP lineage
