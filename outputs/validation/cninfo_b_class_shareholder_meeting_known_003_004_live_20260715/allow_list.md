# CNINFO B 类 Shareholder Meeting Known-003/004 Live Allow-list — B-FM-19

_生成时间：2026-07-15_

## 范围

仅请求以下 **2** 条 B-FM-19 新晋 ready known-document（空 category YAML；排除既有 ready / placeholder / guard / 已 LIVE_PASS）：

1. `shareholder_meeting_known_003` — 迈克生物 300463 · `股东大会决议` · 2025-06-26 ~ 2025-06-29
2. `shareholder_meeting_known_004` — 中信特钢 000708 · `股东大会的公告` · 2025-06-25 ~ 2025-06-28

排除：`shareholder_meeting_known_001`（已 B-R16 LIVE_PASS）、`shareholder_meeting_known_002`（已 B-FM-17 LIVE_PASS）、`meeting_sample_002`（已 B-FM-15 LIVE_PASS）、全部 placeholder / guard。

## 输入文件

- known: `known_document_retrieval_cases_live_allowlist.yaml`
- category: `category_sample_cases_live_empty.yaml`（cases=[]）

## 边界

- known：topSearch + hisAnnouncement/query metadata
- **不**下载 PDF；**不**解析；**不**写 verified；**不**升级 source status
- **不**触碰 A/C/D；**不** commit / push
- 不造 §7 FP lineage
