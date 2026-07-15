# CNINFO B 类 Shareholder Meeting Sample Promotion Live Allow-list — B-FM-15

_生成时间：2026-07-15_

## 范围

仅请求以下 **1** 条 B-FM-14 新晋 ready category-sample（空 known YAML；排除既有 ready / placeholder / guard / known_001）：

1. `meeting_sample_002` — `股东大会通知` · 2025-06-22 ~ 2025-06-26（全市场类别抽样）

排除：`shareholder_meeting_known_001`（已 B-R16 LIVE_PASS，本包不重复消耗 CNINFO）、`meeting_sample_001`（说明会边角，已 LIVE_PASS）、全部 placeholder / guard。

## 输入文件

- known: `known_document_retrieval_cases_live_empty.yaml`（cases=[]）
- category: `category_sample_cases_live_allowlist.yaml`

## 边界

- category：hisAnnouncement/query metadata（sse + szse）
- **不**下载 PDF；**不**解析；**不**写 verified；**不**升级 source status
- **不**触碰 A/C/D；**不** commit / push
- 不造 §7 FP lineage
