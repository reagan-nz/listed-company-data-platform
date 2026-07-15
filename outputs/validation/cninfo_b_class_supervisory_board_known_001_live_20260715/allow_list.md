# CNINFO B 类 Supervisory Board Known-001 Live Allow-list — B-FM-23

_生成时间：2026-07-15_

## 范围

仅请求以下 **1** 条 B-FM-23 新晋 ready known-document（空 category YAML；排除既有 ready / placeholder / guard / 已 LIVE_PASS）：

1. `supervisory_board_known_001` — 网宿科技 300017 · `第二十四次会议决议公告` · 2025-06-26 ~ 2025-06-29

排除：`shareholder_meeting_known_001`–`007`（均已 LIVE_PASS）、`board_resolution_known_001`（本包不重开）、`meeting_sample_002`（已 LIVE_PASS）、全部 placeholder / guard。

## 输入文件

- known: `known_document_retrieval_cases_live_allowlist.yaml`
- category: `category_sample_cases_live_empty.yaml`（cases=[]）

## 边界

- known：topSearch + hisAnnouncement/query metadata
- **不**下载 PDF；**不**解析；**不**写 verified；**不**升级 source status
- **不**触碰 A/C/D；**不** commit / push
- 不造 §7 FP lineage
