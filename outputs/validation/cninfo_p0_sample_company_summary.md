# CNINFO P0 样本公司清单（生成摘要）

本清单基于本地已有输出生成，供后续 #82 / #83 / #84 P0 验证使用。

## 数据来源
- outputs/generalization/full_market_2024/

## 样本概况
- 样本总数：40
- 覆盖板块：主板(20), 创业板(7), 科创板(7), 北交所(6)
- 已知行业覆盖：暂无（industry 多为 unknown）
- 仍为 unknown 的字段：announcement_frequency_group, industry, listing_status, market_cap_group
- 说明：上述 unknown 不影响第一轮验证，仍可用于页面可达性、字段可得性和失败原因记录；后续可补齐。

## 边界确认
- 未访问 CNINFO，未联网。
- 未下载 PDF，未计算 hash。
- 未做数据库接入。
- 仅读取本地已有抽取结果，未修改计划文档和存储设计文档。

## 过滤情况
- 跳过 company_name 为空或含 `_unknown_name` 的样本：6 条（不计入样本总数）
