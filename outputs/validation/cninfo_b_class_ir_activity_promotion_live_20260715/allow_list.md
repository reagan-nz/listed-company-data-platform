# CNINFO B 类 IR Activity Promotion Live Allow-list — B-FM-10

_生成时间：2026-07-15_

## 范围

仅请求以下 **4** 条 B-FM-05/06 新晋 ready cases（排除既有 ready / placeholder / guard / 警示函 live）：

1. `ir_activity_known_002` — 吉林化纤 000420 · 「投资者网上集体接待日」 · 2025-05-19 ~ 2025-05-22
2. `ir_activity_known_003` — 新乡化纤 000949 · 「投资者开放日」 · 2025-06-02 ~ 2025-06-05
3. `ir_activity_sample_001` — 投资者网上集体接待日 · 2025-05-08 ~ 2025-05-22（全市场类别抽样）
4. `ir_activity_sample_002` — 投资者开放日 · 2025-06-01 ~ 2025-06-05（全市场类别抽样）

## 输入文件

- known: `known_document_retrieval_cases_live_allowlist.yaml`
- category: `category_sample_cases_live_allowlist.yaml`

## 边界

- known：topSearch + hisAnnouncement/query metadata
- category：hisAnnouncement/query metadata（sse + szse）
- **不**下载 PDF；**不**解析；**不**写 verified；**不**升级 source status
- **不**触碰 A/C/D；**不** commit / push
- 不造 §7 FP lineage
