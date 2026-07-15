# CNINFO B 类 Regulatory Work Letter Promotion Live Allow-list — B-FM-13

_生成时间：2026-07-15_

## 范围

仅请求以下 **2** 条 B-FM-12 新晋 ready cases（排除既有 ready / placeholder / guard / 其他 live）：

1. `inquiry_known_004` — 文投控股 600715 · CPA「…监管工作函的专项说明」全文 · 2025-04-27 ~ 2025-04-30
2. `inquiry_sample_003` — `监管工作函` · 2025-04-26 ~ 2025-04-30（全市场类别抽样）

## 输入文件

- known: `known_document_retrieval_cases_live_allowlist.yaml`
- category: `category_sample_cases_live_allowlist.yaml`

## 边界

- known：topSearch + hisAnnouncement/query metadata
- category：hisAnnouncement/query metadata（sse + szse）
- **不**下载 PDF；**不**解析；**不**写 verified；**不**升级 source status
- **不**触碰 A/C/D；**不** commit / push
- 不造 §7 FP lineage
