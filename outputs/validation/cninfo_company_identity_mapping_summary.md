# CNINFO company identity mapping 初版（Sub Issue 1）

## 输入
- `outputs/validation/cninfo_p0_sample_companies.csv`
- `outputs/validation/cninfo_f10_entry_mapping.csv`
- `outputs/validation/cninfo_f10_orgid_mapping_analysis.md`
- `outputs/validation/cninfo_p0_validation_final_summary.md`

## 总览
- 样本总数：40（与 P0 样本一致）
- 映射状态：mapped 30 / needs_orgid_mapping 10 / partial 0 / failed 0
- 数据未联网、未访问 CNINFO、未跑新验证；仅基于现有 P0 结果生成映射表。

## 按 exchange / board
- SSE 主板：10 mapped（600 系列，经验规则）
- SZSE 主板：10 needs_orgid_mapping（000 系列）
- SZSE 创业板：7 mapped（300 系列，经验规则）
- SSE 科创板：7 mapped（STAR 人工 orgId）
- BSE 北交所：6 mapped（430→920 + 人工 orgId）

## 映射规则与置信度
- 600 / 300：`mapping_source=manual_rule`，`mapping_confidence=medium`（P0 经验规则）；需要后续更大样本验证。
- STAR / 688：`mapping_source=manual_search`，`mapping_confidence=high`（人工 orgId，当前样本）；原 `gshk0000+后三位` 规则已废弃。
- BSE / 430→920：`mapping_source=manual_search`，`mapping_confidence=high`（人工 orgId，当前样本）；仅适用于当前 6 家样本。
- needs_orgid_mapping（000 系列 10 家）：`mapping_source=unknown`，`mapping_confidence=low`，`needs_manual_review=yes`；不伪造 orgId。

## 关键清单
- needs_orgid_mapping（10）：000001, 000002, 000004, 000006, 000007, 000008, 000009, 000010, 000011, 000012
- BSE 手工映射（6）：430017, 430047, 430090, 430139, 430198, 430300（stockCode 920xxx + 人工 orgId）
- STAR 手工映射（7）：688001–688007（stockCode 原值 + 人工 orgId，含 99000... 与 gfbj... 形态）

## 对后续验证的影响
- 公告列表：BSE 需 430→920 / orgId 回退；SZSE 000 系列需补 orgId 后再提取。
- F10 / 公司资料：依赖 stockCode + orgId；已映射样本可继续 Playwright 抽取；未映射样本暂不进入字段验证。
- P1 / P2 栏目：在进入新栏目前，优先补齐 orgId 映射和公告查询 code 映射。

## 边界说明
- 未联网、未访问 CNINFO、未跑新验证。
- 未修改任何已有验证 CSV；未改代码；未做数据库接入。
- 映射结论仅代表当前 P0 小样本；`mapping_status` 和置信度需在后续样本中持续校正；不写 verified。
