# CNINFO 公告类栏目失败原因分析（Sub Issue 4）

## 1. 分析目标
- 基于 Sub Issue 3 的公告类别小样本验证结果进行复盘与改进思路。
- 不联网、不重新抓取、不改配置，**仅分析现有 success / failed 分布**。

## 2. 总体结果
- 样本公司：40；mapped：30；needs_orgid_mapping：10（未参与本轮验证）。
- 公告类别：14；公司×类别组合：470。
- 结果分布：success 106 / partial 0 / failed 364。
- 当前高失败率**不等于数据源不可用**，更多是关键词匹配、时间范围、事件低频或映射缺口导致。

## 3. 按公告类别成功率分层

| category_key | 中文名 | success | failed | success_rate | 可用性判断 | next_action |
|---|---|---:|---:|---:|---|---|
| shareholder_meeting | 股东大会 | 51 | 13 | 0.80 | 高可用 | 继续验证，保持现有关键词 |
| dividend_distribution | 权益分派/分红 | 20 | 17 | 0.54 | 高可用（需补充变体） | 扩充关键词后复跑 |
| quarterly_report | 季报 | 12 | 18 | 0.40 | 中等可用 | 扩充季度/年份写法；必要时加报告期参数 |
| share_repurchase | 回购 | 6 | 27 | 0.18 | 中等可用 | 增加“进展/完成/计划”类关键词 |
| equity_incentive | 股权激励 | 5 | 27 | 0.16 | 中等可用 | 增加授予/解除限售等变体 |
| regulatory_inquiry | 监管问询/监管函 | 4 | 28 | 0.12 | 中等可用 | 增加“回复公告/关注函回复”等变体 |
| board_meeting | 董事会 | 4 | 28 | 0.12 | 中等可用 | 增加届次/第X次会议写法 |
| performance_forecast | 业绩预告 | 1 | 29 | 0.03 | 低可用/需排查 | 保留候选，扩关键词后再试 |
| dividend_distribution | （见上） | — | — | — | — | — |
| share_repurchase | （见上） | — | — | — | — | — |
| major_asset_restructuring | 重大资产重组 | 1 | 29 | 0.03 | 低可用/需排查 | 低频，保持候选 |
| penalty_litigation | 处罚/诉讼 | 1 | 29 | 0.03 | 低可用/需排查 | 语义区分处罚/诉讼，后续语义分类 |
| private_placement | 定增 | 1 | 29 | 0.03 | 低可用/需排查 | 低频，保持候选 |
| semi_annual_report | 半年报 | 0 | 30 | 0.00 | 低可用/需排查 | 可能需报告期参数 + 关键词扩充 |
| supervisory_board | 监事会 | 0 | 30 | 0.00 | 低可用/需排查 | 增加届次/会议次序关键词 |
| share_unlock | 限售解禁 | 0 | 30 | 0.00 | 低可用/需排查 | 增加“上市流通提示”类关键词 |

（注：表内出现的重复行用“见上”说明，真实数据如上统计）

## 4. 失败原因类型归纳
- **keyword_mismatch**：标题变体未覆盖（如“第X次会议”“提示性公告”“回复公告”）。
- **low_frequency_event**：重组、定增、处罚、诉讼、业绩预告等事件低频，40 家小样本命中概率低。
- **time_window_issue**：公告窗口可能未涵盖报告期（半年报、部分季报）。
- **report_category_parameter_needed**：半年报/季报可能需报告类别或报告期参数，而非仅标题关键词。
- **mapping_gap**：10 家 `needs_orgid_mapping` 未参与；映射缺口限制了覆盖度。
- **title_semantics_unclear**：处罚/诉讼、问询/回复、回购进展等需语义判断，简单关键词不足。
- **source_not_suitable_for_category**：少数类别可能需要更长时间跨度或不同入口才能命中（例如重组预案历史公告）。

## 5. 关键词改进建议（方向示例）
- **semi_annual_report**：增加“半年度报告摘要”“2025年半年度报告”“2024年半年度报告”。
- **quarterly_report**：增加“一季度报告”“三季度报告”“2025年第一季度报告”等年份+季度组合。
- **supervisory_board**：增加“第X届监事会”“监事会第X次会议”“监事会决议公告”。
- **share_unlock**：增加“上市流通提示性公告”“限售股解禁”“首次公开发行部分限售股上市流通”。
- **regulatory_inquiry**：增加“回复公告”“关于对问询函的回复”“关注函回复”“监管工作函”。
- **penalty_litigation**：区分“重大诉讼”“累计诉讼”“行政监管措施”“行政处罚决定书”等。
- **share_repurchase**：增加“回购进展公告”“回购完成”“回购实施进展”。
- **equity_incentive**：增加“限制性股票激励计划”“股票期权激励计划”“授予公告”“解除限售”。
- **private_placement / major_asset_restructuring**：增加“配套募集资金”“发行股份购买资产”“重组草案/预案”。
- **performance_forecast**：增加“业绩快报”“经营预告”。

## 6. 对后续验证策略的影响
- 公告标题关键词匹配 **不是严格分类 API**，更合理流程：先拉取公告 corpus → 关键词/规则初筛 → NLP/LLM/人工规则做语义分类。
- 低频事件不能以单次小样本直接判定不可用，应结合更长时间窗口与更大样本。
- 报告类（半年报/季报）可能需要设置报告期/类别参数，而非纯标题匹配。

## 7. 推荐下一步
- **可继续验证**：shareholder_meeting，dividend_distribution，quarterly_report，share_repurchase，equity_incentive。
- **优化关键词后重跑**：semi_annual_report，supervisory_board，share_unlock，regulatory_inquiry，penalty_litigation。
- **低频保留候选**：major_asset_restructuring，private_placement，performance_forecast。
- **暂不进入数据库接入**：所有类别仍处于 `testing / partial`，不写 `verified`。

## 8. 边界说明
- 未联网、未访问 CNINFO、未重新跑验证。
- 未修改原始验证 CSV、未改配置、未改代码。
- 未做数据库 / MinIO 接入；未下载或解析 PDF；未做 OCR。
- 分析结论仅基于当前 P1 小样本结果。
