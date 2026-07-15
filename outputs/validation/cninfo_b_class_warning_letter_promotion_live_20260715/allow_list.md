# CNINFO B 类 Warning-Letter Promotion Live Allow-list — B-FM-09

_生成时间：2026-07-15_

## 范围

仅请求以下 **2** 条 B-FM-08 新晋 ready cases（排除既有 ready / placeholder / guard）：

1. `regulatory_known_001` — 壹网壹创 300792 · 「关于收到浙江证监局警示函的公告」 · 2025-06-22 ~ 2025-06-25
2. `inquiry_sample_001` — 警示函 · 2025-06-21 ~ 2025-06-25（全市场类别抽样）

## 输入文件

- known: `known_document_retrieval_cases_live_allowlist.yaml`
- category: `category_sample_cases_live_allowlist.yaml`

## 边界

- known：topSearch + hisAnnouncement/query metadata
- category：hisAnnouncement/query metadata（sse + szse）
- **不**下载 PDF；**不**解析；**不**写 verified；**不**升级 source status
- **不**触碰 A/C/D；**不** commit / push
- 不造 §7 FP lineage
