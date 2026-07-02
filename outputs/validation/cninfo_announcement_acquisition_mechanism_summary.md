# CNINFO 公告类数据获取机制总结（Sub Issue 5）

## 1. 背景
- CNINFO P0/P1 公告类验证已完成小样本验证。公告系统可用，但更像“公告搜索系统”，不是严格结构化 event API。
- 当前链路：身份映射 → 公告检索 → 规则分类 → 可选语义复核。

## 2. 当前验证结果概览
- company identity mapping：40 样本，mapped 30 / needs_orgid_mapping 10。
- P1 公告类验证（14 类，470 组合）：success 106 / failed 364。
- 接入 retrieval strategy 后：success 106 / failed 364（较旧关键词未提升）。
- 规则回放（106 条已有公告标题）：均可匹配；high 23 / medium 83。
- 结论：规则层能分类已有公告，但无法解决“公告没被查询出来”的问题。

## 3. 核心判断
- CNINFO 公告数据源有价值，公告列表 / PDF URL / 发布时间等基础字段可用。
- 公告类别不是现成结构化分类；当前分类本质是“检索 + 规则分类”。
- 单纯增加关键词难以明显提升覆盖率，瓶颈在查询策略（时间窗口、报告类别参数、低频事件、映射覆盖）。
- 下一步重点应优化“查询与覆盖”，而非继续堆关键词。

## 4. 公告获取机制分层
1) **identity mapping 层**：`company_code`/`cninfo_stock_code`/`cninfo_org_id`/`announcement_query_code`；未映射样本先跳过深度验证。  
2) **announcement retrieval 层**：拉取公告标题、发布时间、pdf_url、公告类型（HTTP 公告查询）。  
3) **rule classification 层**：用 must/optional/exclude 做类别与置信度标注；适合高/中可用类别。  
4) **semantic review 层**：暂不强制 LLM；低置信、多标签、semantic_later 时预留 DeepSeek/Agnes，当前仅输出 `llm_review_needed`。

## 5. 按类别的推荐获取策略

| category_key | 中文名 | 当前结果 | recommended_access_method | recommended_status | next_action |
|---|---|---|---|---|---|
| shareholder_meeting | 股东大会 | success 51 | http_announcement_search + rule_classification | testing | 继续规则验证 |
| dividend_distribution | 权益分派/分红 | success 20 | http_announcement_search + rule_classification | testing | 继续规则验证 |
| quarterly_report | 季报 | success 12 | http_announcement_search + rule_classification | testing | 继续规则验证；必要时加报告期 |
| share_repurchase | 回购 | success 6 | http_announcement_search_with_longer_window + rule_classification | partial | 扩关键词+延时间窗 |
| equity_incentive | 股权激励 | success 5 | http_announcement_search_with_longer_window + rule_classification | partial | 扩关键词+延时间窗 |
| regulatory_inquiry | 监管问询 | success 4 | http_announcement_search + rule_classification | partial | 覆盖“回复”类标题 |
| board_meeting | 董事会 | success 4 | http_announcement_search + rule_classification | partial | 补届次/次数关键词 |
| major_asset_restructuring | 重大资产重组 | success 1 | http_announcement_search_with_longer_window + rule_classification | candidate | 低频，拉长时间窗 |
| private_placement | 定增 | success 1 | http_announcement_search_with_longer_window + rule_classification | candidate | 低频，拉长时间窗 |
| performance_forecast | 业绩预告 | success 1 | http_announcement_search_with_longer_window + rule_classification | candidate | 低频，拉长时间窗 |
| penalty_litigation | 处罚/诉讼 | success 1 | http_announcement_search_with_longer_window + rule_classification | candidate | 低频，需语义区分 |
| semi_annual_report | 半年报 | success 0 | report_category_or_period_query + http_announcement_search | candidate | 需报告期/类别参数 |
| share_unlock | 限售解禁 | success 0 | http_announcement_search_with_longer_window + rule_classification | candidate | 低频，提示性公告写法 |
| supervisory_board | 监事会 | success 0 | http_announcement_search_with_longer_window + rule_classification | candidate | 补届次/次数关键词 |

（recommended_status 不写 verified）

## 6. LLM 在当前机制中的位置
- 不需要对每条公告接入 LLM；LLM 不负责抓取网页。
- LLM 仅用于低置信、多标签、semantic_later 的小规模复核；无 API / 未显式开启时应跳过。
- 先让规则层输出 `llm_review_needed`，后续按需调用 DeepSeek / Agnes。

## 7. 为什么 retrieval strategy 没提升 success
- retrieval strategy 改进的是“标题分类规则”；失败多数是 **查询阶段未命中公告**：时间窗口、报告类别/期参数、事件低频、映射覆盖、接口返回范围等。
- 因此 success 未提升并不代表规则无效，而是瓶颈在“能否把公告查出来”。

## 8. 下一步建议
1. 报告类（半年报/季报）增加报告期/类别查询机制。  
2. 低频事件使用更长时间窗口。  
3. 补齐 10 家 `needs_orgid_mapping`，提升可检索样本覆盖。  
4. 对 high/medium 置信类别继续规则验证；对 low/multi/semantic_later 小规模接 LLM 复核。  
5. 暂不做全量公告抓取；暂不做数据库接入。  

## 9. 边界说明
- 本文档仅为机制总结；未联网、未重新跑验证、未修改 CSV、未接 LLM、未做数据库/MinIO 接入。
- 不代表长期稳定可用；不写 verified。
