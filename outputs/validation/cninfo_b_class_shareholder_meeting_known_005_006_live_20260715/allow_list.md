# CNINFO B 类 Shareholder Meeting Known-005/006 Live Allow-list — B-FM-21

_生成时间：2026-07-15_

## 范围

仅请求以下 **2** 条 B-FM-21 新晋 ready known-document（空 category YAML；排除既有 ready / placeholder / guard / 已 LIVE_PASS）：

1. `shareholder_meeting_known_005` — 康平科技 300907 · `临时股东会决议` · 2025-06-29 ~ 2025-07-02
2. `shareholder_meeting_known_006` — 孚日股份 002083 · `股东会的通知` · 2025-06-25 ~ 2025-06-28

排除：`shareholder_meeting_known_001`（已 B-R16 LIVE_PASS）、`shareholder_meeting_known_002`（已 B-FM-17 LIVE_PASS）、`shareholder_meeting_known_003`/`004`（已 B-FM-19 LIVE_PASS）、`meeting_sample_002`（已 B-FM-15 LIVE_PASS）、全部 placeholder / guard。

BD2E258（年度股东会决议）本包不晋升：与 known_005 同属简称决议族，route 已由 B-FM-20 锁测覆盖；留作后续 known_007 候选。

## 输入文件

- known: `known_document_retrieval_cases_live_allowlist.yaml`
- category: `category_sample_cases_live_empty.yaml`（cases=[]）

## 边界

- known：topSearch + hisAnnouncement/query metadata
- **不**下载 PDF；**不**解析；**不**写 verified；**不**升级 source status
- **不**触碰 A/C/D；**不** commit / push
- 不造 §7 FP lineage
