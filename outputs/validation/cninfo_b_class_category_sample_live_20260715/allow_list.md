# CNINFO B 类 Category-Sample Live Allow-list — B-FM-01

_生成时间：2026-07-15_

## 范围

仅请求以下 **4** 条正向 category-sample ready cases（空 known YAML；排除 placeholder / guard / 既有 known-document）：

1. `general_sample_001` — 董事会决议公告 · 2025-06-26 ~ 2025-06-29
2. `general_sample_002` — 权益分派 · 2025-06-17 ~ 2025-06-20
3. `general_sample_003` — 回购 · 2025-06-26 ~ 2025-06-29
4. `meeting_sample_001` — 说明会 · 2025-06-09 ~ 2025-06-12

## 输入文件

- known: `known_document_retrieval_cases_live_empty.yaml`（cases=[]）
- category: `category_sample_cases_live_allowlist.yaml`

## 边界

- 仅 `hisAnnouncement/query` metadata（sse + szse 各 1 次 / case）
- **不**下载 PDF；**不**解析；**不**写 verified；**不**升级 source status
- **不**触碰 A/C/D；**不** commit / push
