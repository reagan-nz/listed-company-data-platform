# CNINFO 公告类栏目验证配置摘要（Sub Issue 2）

## 1. 配置目标
- 为公告/文档类高价值栏目建立统一验证配置，便于后续小样本验证（Sub Issue 3）。
- 不联网、不访问 CNINFO、不跑验证脚本；仅基于 P0 现有成果梳理类别与字段。
- 统一字段结构：`category_key`, `category_name_cn`, `priority`, `data_type`, `keywords`, `expected_fields`, `suggested_storage_layer`, `validation_goal`, `notes`。

## 2. 覆盖范围
- 公告类别数量：14（半年报、季报、业绩预告、分红、股东大会、董事会、监事会、监管问询、处罚/诉讼、回购、定增、重组、股权激励、限售解禁）。
- 配置文件：`config/cninfo_announcement_categories.yaml`
- 参考输入：P0 公告验证结果（#82）、company identity mapping（Sub Issue 1）。

## 3. 按 data_type 分类
- document：2 类（半年报、季报）
- event_candidate：2 类（业绩预告、分红）
- governance_event_candidate：4 类（股东大会、董事会、监事会、股权激励）
- risk_event_candidate：2 类（监管问询、处罚/诉讼）
- capital_event_candidate：3 类（回购、定增、重组）
- market_event_candidate：1 类（限售解禁）

## 4. 按 priority 分类
- P1：13 类（除限售解禁外全部）
- P1/P2：1 类（限售解禁）

## 5. 核心字段要求（验证时应输出）
- 通用字段：`announcement_title`, `publish_time`, `source_url`, `pdf_url`
- 报告类额外字段：`report_period`（半年报、季报）
- 后续事件解析：根据 data_type 再细分（资本运作、风险、治理、市场事件）

## 6. 与 P0 最新公告列表的关系
- P0 已验证公告列表可用（34/40 公司成功，102/108 记录）；本配置在其基础上进一步细分公告类型，面向 P1 高价值栏目。
- 需要与 company identity mapping 一起使用，以确保公告查询使用正确的 `cninfo_stock_code` / `cninfo_announcement_query_code`。

## 7. 与 company identity mapping 的关系
- 公告查询依赖正确的代码映射（特别是 BSE 430→920、STAR/688 人工 orgId、600/300 经验规则、000 系列待补 orgId）。
- 未映射的样本（needs_orgid_mapping）应暂时跳过类型验证，避免伪造 orgId。

## 8. 后续 Sub Issue 3 使用方式
- 以 `config/cninfo_announcement_categories.yaml` 为驱动，选择小样本公司（优先 mapped）执行公告类型识别与字段验证。
- 验证输出按 category_key 统计 success/partial/failed 及字段可得性，记录 failure_reason 与 evidence URL。
- 首轮优先验证：document（半年报/季报）、风险（监管问询）、资本运作（回购/定增/重组）、治理（股东大会/董事会/监事会）、事件候选（业绩预告、分红），并关注 BSE/STAR 映射样本表现。

## 9. 边界说明
- 本次只写配置与摘要：**未联网、未访问 CNINFO、未跑验证、未生成真实结果**。
- 未修改现有验证 CSV、未改代码、未做数据库接入。
- 不写 verified；所有类别默认进入 `testing/partial` 验证阶段，需后续小样本验证结果支撑。
