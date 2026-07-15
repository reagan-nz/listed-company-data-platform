# CNINFO B 类 Legal Opinion Known-001/002 Live Allow-list — B-FM-25

_生成时间：2026-07-15_

## 范围

仅请求以下 **2** 条 B-FM-25 新晋 ready known-document（空 category YAML；排除既有 ready / placeholder / guard / 已 LIVE_PASS）：

1. `legal_opinion_known_001` — 永兴材料 002756 · `第一次临时股东大会的法律意见书` · 2025-06-01 ~ 2025-06-04
2. `legal_opinion_known_002` — 金自天正 600560 · `年度股东会的法律意见书` · 2025-06-25 ~ 2025-06-28

排除：`supervisory_board_known_001`–`002`（已 LIVE_PASS）、`shareholder_meeting_known_001`–`007`（均已 LIVE_PASS）、`board_resolution_known_001`（本包不重开）、`meeting_sample_002`（已 LIVE_PASS）、全部 placeholder / guard。

## 输入文件

- known: `known_document_retrieval_cases_live_allowlist.yaml`
- category: `category_sample_cases_live_empty.yaml`（cases=[]）

## 边界

- known：topSearch + hisAnnouncement/query metadata
- **不**下载 PDF；**不**解析；**不**写 verified；**不**升级 source status
- **不**触碰 A/C/D；**不** commit / push
- 不造 §7 FP lineage
