# CNINFO 数据源价值盘点：从年报 PDF 到公司动态属性

_最后更新：2026-07-01_

> 本文件是 **CNINFO 候选数据源价值盘点与验证计划**，属于数据源研究，不代表这些 CNINFO 子栏目已经全部完成采集，也不代表相关页面长期稳定可用。除年报 PDF 外，所有新栏目都必须先经过小样本验证，才能写成已验证数据源。

---

## 1. 为什么要单独研究 CNINFO

- 当前项目已经使用 CNINFO 年报 PDF 建立了 2024 年报结构化数据底座（`full_market_2024`）。
- 但 CNINFO 不只是年报 PDF 下载源。
- 它还可能包含：最新公告、信息披露 / 公告搜索、个股 F10、公司资料 / 公司要览、预约披露、股本结构、股东信息、公司治理、风险公告、监管问询 / 处罚 / 诉讼、融资融券、大宗交易、限售解禁、公开信息 / 异常交易、互动易、网络投票、IPO / 招股书、债券、基金等信息。
- 相比普通新闻网站、公司官网、互动问答，CNINFO 的优势是：**来源更正式、披露时间更清楚、URL / PDF 可追溯、公告类型相对标准化**。
- 所以 CNINFO 应作为动态平台的**第一优先级扩展数据源**，而不是和普通网页数据源放在同一优先级。

> 强调：本文件是候选数据源价值盘点和验证计划，不代表这些 CNINFO 子栏目已经全部完成采集。

---

## 2. CNINFO 在本项目中的定位

| 定位 | 说明 |
|---|---|
| 法定披露入口 | 年报、季报、半年报、临时公告等正式文件来源 |
| 公司属性补充源 | 个股 F10、公司资料、公司要览可补充 `company` / profile 属性 |
| 动态事件来源 | 最新公告、风险提示、分红、回购、重组、管理层变动等可生成 `event` |
| 证据追溯来源 | PDF、URL、公告时间、公告标题、正文证据句可构成证据链 |
| 数据源验证优先对象 | 比官网、新闻、互动问答更适合第一阶段验证 |

---

## 3. CNINFO 栏目盘点

> **Sub Issue 1.1：梳理 CNINFO 栏目与入口清单。** 本节系统性列出巨潮资讯网可能提供的栏目 / 入口，并初步判断数据类型、可提取信息、平台价值、优先级与当前状态。本节只做数据源研究，不涉及爬虫实现或数据库 schema。

### 3.1 栏目分组概览

| 分组 | 包含栏目 | 主要价值 |
|---|---|---|
| 公告与披露 | 最新公告、信息披露 / 公告搜索、年报 / 半年报 / 季报 | 文档流、正式事件、证据链 |
| 公司资料 | 个股 F10、公司资料 / 公司要览 | 公司静态属性、资料属性 |
| 治理与股东 | 公司治理、股本结构、股东信息、预约披露、网络投票 | 治理属性、股东快照、披露日历 |
| 风险与监管 | 风险公告 / 风险提示、监管问询 / 处罚 / 诉讼 | 风险事件、合规事件 |
| 资本运作 | 分红融资 | 分红、回购、定增、重组等高价值事件 |
| 市场行为 | 融资融券、大宗交易、限售解禁、公开信息 / 异常交易 | 市场行为属性（范围需克制） |
| 投资者互动 | 互动易 | 投资者问答候选 |
| 扩展披露 | IPO / 招股书、债券、基金 | 范围外扩展，当前暂缓 |

### 3.2 优先级与状态说明

**优先级定义：**

| 优先级 | 含义 |
|---|---|
| P0 | 第一阶段最值得验证，能直接补公司属性、公告流或基础时间线 |
| P1 | 价值高，但需要更细规则或字段结构更复杂 |
| P2 | 有价值，但暂时不是核心，可能会扩大项目范围 |
| 暂缓 | 当前阶段不做 |

**当前状态规则：**

- 已在 `full_market_2024` 中使用的**年报 PDF / 年报字段抽取**，可标为「已使用」。
- 其他栏目统一标为「候选 / 待验证」。
- 不写「稳定可用」「已完成采集」或「长期稳定可用」。

### 3.3 栏目 / 入口清单

| 栏目 / 入口 | 数据类型 | 可提取信息 | 对平台的价值 | 初步优先级 | 当前状态 |
|---|---|---|---|---|---|
| 最新公告 | 公告列表（HTML / API） | 公告标题、公告类型、发布时间、公告 URL、关联公司 | 补齐**文档流**；触发 `document_published` / `announcement_published` 等基础事件；支撑公司时间线 | P0 | 候选 / 待验证 |
| 信息披露 / 公告搜索 | 公告检索（HTML / API） | 按公司 / 类型 / 期间检索历史公告；公告元数据 | 补齐**历史文档流**；支持按类型回溯风险、分红、重组等公告 | P0 | 候选 / 待验证 |
| 年报 | 定期报告 PDF | 全文 PDF、`source_url`、`content_hash`、报告期；可抽取主营业务、研发、收入结构、风险因素等字段 | **已有基础**：支撑公司画像、字段查询、证据追溯；可扩展至多年份 | P0 | **已使用**（2024 年报 PDF + 字段抽取）；多年份扩展为候选 / 待验证 |
| 半年报 | 定期报告 PDF | 全文 PDF、报告期、中期财务与经营披露 | 补半年度文档流与字段；支持中期变化追踪 | P1 | 候选 / 待验证 |
| 季报 | 定期报告 PDF | 全文 PDF、报告期、季度财务与经营披露 | 补季度文档流；支持更高频字段变化 | P1 | 候选 / 待验证 |
| 个股 F10 | 结构化资料页（HTML） | 股票简称、交易所、板块、行业、公司简介、基础指标、部分治理与股东摘要 | 直接补 **company 基础属性**；降低对公司官网依赖 | P0 | 候选 / 待验证 |
| 公司资料 / 公司要览 | 结构化资料页（HTML） | 注册地址、办公地址、主营业务摘要、官网、联系方式、董秘等 | 补 **公司资料属性**；与 F10 交叉验证 | P0 | 候选 / 待验证 |
| 预约披露 | 计划时间表（HTML / 结构化） | 定期报告预约披露日期、报告类型 | 支撑 **披露日历**；可生成 `scheduled_disclosure` 类事件 | P1 | 候选 / 待验证 |
| 股本结构 | 结构化数据（HTML / 表格） | 总股本、流通股本、限售股、变动原因 | 补 **股本属性快照**；可与年报字段交叉验证 | P1 | 候选 / 待验证 |
| 股东信息 | 结构化数据（HTML / 表格） | 前十大股东、控股股东、实际控制人、股东户数 | 补 **股东属性快照**；支撑股权结构变化事件 | P1 | 候选 / 待验证 |
| 分红融资 | 公告 + 结构化摘要 | 分红预案 / 实施、回购、定增、重组、融资方案 | 高价值 **动态事件**（分红、回购、定增、重组） | P1 | 候选 / 待验证 |
| 公司治理 | 资料页 + 公告 | 董监高名单、董事会 / 监事会 / 股东大会信息、治理制度 | 补 **治理属性**；管理层变动可生成 `management_change` 事件 | P1 | 候选 / 待验证 |
| 风险公告 / 风险提示 | 临时公告 / 专项公告 | ST / *ST、退市风险、重大风险提示、异常波动公告 | 高价值 **风险事件**；用户关注度高 | P1 | 候选 / 待验证 |
| 监管问询 / 处罚 / 诉讼 | 临时公告 / 函件披露 | 问询函、关注函、处罚决定、诉讼、担保、违规 | **合规风险事件**；需规则分类与证据留存 | P1 | 候选 / 待验证 |
| 融资融券 | 市场数据（HTML / 表格） | 融资余额、融券余额、变动趋势 | **市场行为属性**；易扩大为行情平台，非第一阶段核心 | P2 | 候选 / 待验证 |
| 大宗交易 | 市场数据（HTML / 表格） | 成交日期、价格、成交量、买卖营业部 | **市场行为属性**；结构相对稳定但价值偏交易侧 | P2 | 候选 / 待验证 |
| 限售解禁 | 结构化数据（HTML / 表格） | 解禁日期、解禁数量、限售股东 | **市场行为事件**（`share_unlock`）；与股本结构关联 | P1 | 候选 / 待验证 |
| 公开信息 / 异常交易 | 市场数据（HTML / 表格） | 龙虎榜、异常波动、公开信息披露 | **市场行为属性**；解释空间较大，需克制接入 | P2 | 候选 / 待验证 |
| 互动易 | 投资者问答（HTML / 需交互） | 提问、回复、时间、涉及业务 / 风险表述 | **投资者互动候选**；解释空间大，先作候选事件来源 | P1 | 候选 / 待验证 |
| 网络投票 | 治理参与（HTML） | 股东大会议案、投票结果、参与情况 | **治理参与属性**；与股东大会事件关联 | P2 | 候选 / 待验证 |
| IPO / 招股书 | 文档（PDF / HTML） | 招股说明书、发行方案、历史上市信息 | 历史文档扩展；与当前 A 股存量公司动态平台主线关联较弱 | 暂缓 | 候选 / 待验证 |
| 债券 | 文档 + 结构化披露 | 债券发行、兑付、评级相关披露 | 超出当前上市公司主线范围 | 暂缓 | 候选 / 待验证 |
| 基金 | 文档 + 结构化披露 | 基金公告、净值、持仓相关披露 | 超出当前上市公司主线范围 | 暂缓 | 候选 / 待验证 |

### 3.4 P0 栏目小结（第一阶段优先验证）

| P0 栏目 | 为什么优先 |
|---|---|
| 最新公告 | 最接近现有 CNINFO 流程，能最快建立公告流与基础时间线 |
| 信息披露 / 公告搜索 | 与最新公告互补，支持历史公告回溯与类型筛选 |
| 年报 | 已有 2024 抽取基础；多年份 / 多报告类型扩展仍待验证 |
| 个股 F10 | 能直接补 company 基础属性，验证成本低 |
| 公司资料 / 公司要览 | 与 F10 互补，补注册信息、联系方式等公司资料属性 |

> 除上述「已使用」的年报 PDF / 年报字段外，P0 栏目的扩展接入仍须走小样本验证，不得视为已全部采集完成。

---

## 4. CNINFO 数据类型分类：属性、文档、事件、证据与候选数据

> **Sub Issue 1.2：将 CNINFO 数据分类为属性、文档、事件、证据和候选数据。** 在栏目盘点（第 3 节）基础上，本节按**平台用途**分类 CNINFO 可能提供的数据，判断其进入正式层、证据层还是候选层。本节只做分类研究，不涉及爬虫实现或数据库 schema 接入。

| 数据类型 | 示例字段 | 来源栏目 | 平台用途 | 建议层级 | 优先级 | 当前状态 |
|---|---|---|---|---|---|---|
| 公司基础属性 | `company_code`、`stock_short_name`、`company_name`、`exchange`、`board`、`industry`、`listing_status`、`is_st` | 个股 F10 / 公司资料 / 公司要览 | 识别公司、筛选公司、建立 `company` 主索引 | PostgreSQL `company` | P0 | 候选 / 待验证 |
| 公司资料属性 | `company_profile`、`main_business_summary`、`registered_address`、`office_address`、`website`、`contact_phone`、`contact_email`、`board_secretary` | 个股 F10 / 公司资料 | 补充公司画像和未来用户端公司资料页 | PostgreSQL `company_profile`；原始页面可进 MinIO / MongoDB | P0/P1 | 候选 / 待验证 |
| 文档属性 | `announcement_title`、`announcement_type`、`publish_time`、`report_period`、`source_url`、`pdf_url`、`content_hash` | 最新公告 / 信息披露 / 公告搜索 / 年报 / 半年报 / 季报 | 管理公告、定期报告和来源文档 | PostgreSQL `document` + `raw_file`；PDF 原件进 MinIO | P0 | 年报已使用；其他公告 / 报告待验证 |
| 财报字段属性 | `main_business`、`rnd_investment`、`revenue_by_region`、`revenue_by_segment`、`risk_factors`、`major_subsidiaries` | 年报 PDF / 后续半年报 / 季报 | 支持结构化查询、公司画像、证据引用 | PostgreSQL `field_value` + `quality_audit` | 年报已使用；半年报 / 季报扩展为 P1 | 2024 年报字段已使用；多年份 / 多报告类型待验证 |
| 动态事件属性 | `event_type`、`event_time`、`title`、`summary`、`importance_level`、`review_status`、`dedupe_key` | 最新公告 / 风险公告 / 分红融资 / 公司治理 / 监管问询 | 形成公司时间线，未来支持推送 | PostgreSQL `event`；低置信候选先入 MongoDB `raw_event_candidate` | P1 | 候选 / 待验证 |
| 风险异常属性 | `is_st`、`delisting_risk`、`regulatory_inquiry`、`penalty`、`litigation`、`guarantee_risk`、`abnormal_operation` | 风险公告 / 监管问询 / 处罚 / 诉讼 / 临时公告 | 风险识别、风险事件推送、公司风险画像 | PostgreSQL `event` + 未来候选 `risk_profile`；不确定内容先入 MongoDB candidate | P1 | 候选 / 待验证 |
| 股本股东属性 | `total_share_capital`、`float_share_capital`、`restricted_shares`、`top_shareholders`、`controlling_shareholder`、`actual_controller`、`shareholder_count` | 股本结构 / 股东信息 / 年报 / 季报 / F10 | 股权结构分析、公司控制权画像 | 验证后可映射到 PostgreSQL 未来候选 `share_structure` / `shareholder_snapshot` | P1 | 候选 / 待验证 |
| 公司治理属性 | `chairman`、`general_manager`、`executives`、`board_members`、`board_secretary`、`shareholder_meeting`、`management_change` | 公司治理 / F10 / 股东大会公告 / 临时公告 | 治理结构画像和治理事件时间线 | 验证后可映射到 PostgreSQL 未来候选 `management_profile` + `event` | P1 | 候选 / 待验证 |
| 资本运作事件 | `dividend_plan`、`share_repurchase`、`private_placement`、`equity_incentive`、`major_asset_restructuring` | 分红融资 / 公告 PDF / 信息披露 | 资本运作事件识别和推送 | PostgreSQL `event`；公告 PDF 进 MinIO | P1 | 候选 / 待验证 |
| 市场行为属性 | `margin_balance`、`margin_financing_change`、`block_trade_price`、`block_trade_volume`、`share_unlock_date`、`share_unlock_amount`、`abnormal_trading_reason` | 融资融券 / 大宗交易 / 限售解禁 / 公开信息 | 市场行为观察和辅助风险 / 交易事件 | 验证后可映射到 PostgreSQL 未来候选 `market_event` 或 `market_indicator_snapshot`；复杂数据先入 MongoDB | P2 | 候选 / 待验证 / 后续研究 |
| 投资者互动属性 | `question`、`answer`、`question_time`、`reply_time`、`topic`、`interaction_summary` | 互动易 | 投资者关注点分析，可能生成候选业务 / 风险事件 | MongoDB `raw_crawl_result` / `raw_event_candidate`；审核后才可晋升 PostgreSQL `event` | P2 | 候选 / 待验证 |
| 治理参与属性 | `voting_item`、`meeting_time`、`proposal_title`、`vote_result` | 网络投票 / 股东大会公告 | 治理参与记录和股东大会事件 | 验证后可映射到 PostgreSQL 未来候选 `governance_event` 或 `event`；原始页面进 MinIO / MongoDB | P2 | 候选 / 待验证 |
| 原始证据 | `pdf_file`、`html_snapshot`、`source_url`、`content_hash`、`source_page`、`evidence_text`、`crawl_time`、`parse_status` | 所有 CNINFO 文档和页面 | 保证字段、事件和回答可以追溯来源 | MinIO + PostgreSQL `raw_file` / `document` / `field_value` | P0 | 年报证据已使用；其他来源待验证 |
| 候选数据 | `raw_json`、`extracted_text`、`candidate_type`、`confidence_score`、`normalize_status`、`failure_reason` | 结构不稳定页面、互动易、复杂栏目、低置信事件 | 先保留原始信息，避免未审核内容直接进入正式库 | MongoDB `raw_crawl_result` / `raw_event_candidate` | P1/P2 | 候选 / 待验证 |

### 4.1 分类小结

1. **CNINFO 数据不能直接全部进入正式 PostgreSQL。** 只有经过验证、结构明确、来源清晰的数据才适合沉淀为正式属性、文档、字段或事件。
2. **稳定、结构明确、可验证的数据**（如已验证的公告元数据、F10 基础字段、来源明确的正式事件）才进入 PostgreSQL 正式层。
3. **PDF / HTML / 附件等原件**进入 MinIO，数据库只保留元数据与证据引用。
4. **结构不稳定、低置信、待审核的数据**（如互动易问答、复杂栏目原始 JSON、低置信事件候选）先进入 MongoDB，审核通过后再晋升。
5. 本分类结果将作为后续数据库接入的依据，但**当前阶段仍然不做数据库接入**，只做数据源价值研究与小样本验证规划。

> 说明：原「可补充的公司属性池」已并入上表；按数据类型而非栏目罗列，便于判断每层存储职责。第 5–7 节的事件类型、证据类型、三层映射与本节分类一致，互为补充。

---

## 5. 可生成的事件类型池

| 事件类型 | 来源栏目 | 示例触发条件 | 是否进入正式 `event` | 备注 |
|---|---|---|---|---|
| `document_published` | 最新公告 / 信息披露 | 有新文档发布 | 是 | 来源明确 |
| `periodic_report_published` | 年报 / 季报 / 半年报 | 定期报告披露 | 是 | 标准化程度高 |
| `announcement_published` | 最新公告 | 临时公告发布 | 是 | 来源明确 |
| `risk_update` | 风险公告 / 风险提示 | 新增重大风险表述 | 是 | 用户价值高 |
| `special_treatment_or_delisting` | 风险公告 / 监管披露 | ST / *ST / 退市风险 | 是 | 需规则确认 |
| `regulatory_inquiry` | 监管问询 | 问询函 / 关注函 | 是 | 来源明确 |
| `penalty_or_litigation` | 监管 / 临时公告 | 处罚 / 诉讼 / 担保 | 是 | 需规则分类 |
| `management_change` | 公司治理 / 公告 | 董监高变动 | 是 | 标准化程度较高 |
| `shareholder_meeting` | 公司治理 / 网络投票 | 股东大会召开 / 议案 | 是 | 来源明确 |
| `equity_change` | 股本 / 股东信息 | 股本或大股东变化 | 是，但需规则判断 | 按快照比对 |
| `dividend_plan` | 分红融资 | 分红预案 / 实施 | 是 | 来源明确 |
| `share_repurchase` | 分红融资 / 公告 | 回购预案 / 进展 | 是 | 来源明确 |
| `private_placement` | 分红融资 / 公告 | 定增方案 | 是 | 来源明确 |
| `major_asset_restructuring` | 公告 / 重组披露 | 重大资产重组 | 是 | 需规则分类 |
| `share_unlock` | 限售解禁 | 解禁时间到达 | 是 | 结构化触发 |
| `block_trade` | 大宗交易 | 大宗交易发生 | 审核后进入 | 结构不稳定先候选 |
| `margin_financing_change` | 融资融券 | 融资融券余额显著变化 | 审核后进入 | 阈值规则待定 |
| `scheduled_disclosure` | 预约披露 | 预约披露日期临近 | 是 | 披露日历 |
| `investor_interaction_candidate` | 互动易 | 投资者问答涉及业务/风险 | 否，先进入 MongoDB `raw_event_candidate` | 解释空间大 |

规则：

1. 正式公告、定期报告、风险提示等来源明确的，可以进入 PostgreSQL `event`。
2. 互动易、新闻类、解释空间较大的内容，先进入 MongoDB `raw_event_candidate`。
3. 抓取失败不是公司事件，不能进入 `event`，只能进入 `crawl_result` 或日志层。
4. 重复公告或重复候选事件要通过 `dedupe_key` 合并。
5. 未经验证的数据源不能直接生成正式 `event`。

---

## 6. 可保留的证据类型

| 证据类型 | 示例 | 存储层 | 用途 |
|---|---|---|---|
| 公告 PDF 原件 | 临时公告 PDF | MinIO `listed-company-raw` | 证据原件 |
| 年报 / 季报 / 半年报 PDF 原件 | 2024 年报 PDF | MinIO `listed-company-raw` | 证据原件 |
| 公告 URL | CNINFO 公告链接 | PostgreSQL `document` / `raw_file` | 溯源 |
| 公告标题和发布时间 | 标题 + `publish_time` | PostgreSQL `document` | 溯源与排序 |
| F10 页面快照 | F10 页面 HTML | MinIO `listed-company-snapshots` | 证据原件 |
| HTML 快照 | 栏目页面快照 | MinIO `listed-company-snapshots` | 证据原件 |
| 附件 | 公告附件 | MinIO `listed-company-attachments` | 证据原件 |
| PDF 页码 | `source_page` | PostgreSQL `field_value` | 定位证据 |
| 证据句 | `evidence_text` | PostgreSQL `field_value` | 字段依据 |
| `content_hash` | `sha256` | PostgreSQL `raw_file` | 去重与校验 |
| `source_url` | 原始链接 | PostgreSQL `raw_file` / `document` | 溯源 |
| `crawl_time` | 抓取时间 | MongoDB `raw_crawl_result` | 采集记录 |
| `parse_status` | 解析状态 | PostgreSQL / MongoDB | 流程状态 |
| `source_section` | 来源栏目标识 | MongoDB / PostgreSQL | 区分 CNINFO 栏目 |

> 证据链的目标是让字段、事件和用户答案都能回到原始来源，而不是只保存 LLM 总结。

---

## 7. 三层存储映射

- MinIO：原始 PDF / HTML / 附件 / 快照。
- MongoDB：原始抓取、解析中间结果、未标准化候选。
- PostgreSQL：正式公司属性、文档元数据、字段值、事件、证据引用。

| CNINFO 数据 | MinIO | MongoDB | PostgreSQL |
|---|---|---|---|
| 年报 PDF | 存原件 | 可选原始抓取记录 | `document` + `raw_file` + `field_value`（已有基础） |
| 季报 / 半年报 PDF | 存原件 | 可选原始抓取记录 | 验证后晋升 `document` + `field_value` |
| 最新公告列表 | 快照可选 | 先存原始列表 | 验证后晋升 `document` |
| 公告 PDF | 存原件 | 可选原始抓取记录 | `document` + `raw_file` |
| 个股 F10 | 页面快照 | 先存原始解析 | 验证后晋升 `company` / profile |
| 公司资料 / 公司要览 | 页面快照 | 先存原始解析 | 验证后晋升 `company` / profile |
| 预约披露 | 快照可选 | 先存候选 | 验证后晋升 `event`（`scheduled_disclosure`） |
| 股本结构 | 快照可选 | 先存原始解析 | 验证后晋升 `share_structure` |
| 股东信息 | 快照可选 | 先存原始解析 | 验证后晋升 `shareholder_snapshot` |
| 分红 / 回购 / 定增公告 | 存原件 | 先存候选 | 审核后晋升 `event` |
| 风险公告 | 存原件 | 先存候选 | 审核后晋升 `event`（`risk_update`） |
| 融资融券 | — | 先存原始（结构不稳定） | 暂缓，验证后再定 |
| 大宗交易 | — | 先存原始（结构不稳定） | 暂缓，验证后再定 |
| 限售解禁 | 快照可选 | 先存原始解析 | 验证后晋升 `event`（`share_unlock`） |
| 公开信息 | — | 先存原始（结构不稳定） | 暂缓 |
| 互动易问答 | 快照可选 | 先存 `raw_crawl_result` / `raw_event_candidate` | 审核后可晋升 `event` |
| 网络投票 | 快照可选 | 先存候选 | 暂缓，验证后再定 |

说明：只存原件的走 MinIO；结构不稳定或未标准化的先进 MongoDB 候选；来源明确且验证通过的才晋升 PostgreSQL 正式表；范围外或结构复杂的暂缓。

---

## 8. 数据源验证计划

> 未验证前只写「候选数据源」或「待验证栏目」，不要写「长期稳定可用」。

| 验证对象 | 样本量 | 访问方式 | 需要验证的字段 | 成功标准 | 失败记录 |
|---|---|---|---|---|---|
| 最新公告列表 | 50–100 家 | HTTP 优先 | 标题、类型、时间、URL | 列表可稳定获取、字段完整 | 改版、限流、字段缺失 |
| 公告 PDF 下载 | 50–100 份 | HTTP | PDF 本体、hash、URL | 可下载、hash 一致、可解析 | 404、扫描件无文本层 |
| 个股 F10 基础资料 | 30–50 家 | HTTP / Playwright | 简介、行业、板块、指标 | 关键字段可提取 | 动态渲染、结构不一 |
| 公司要览 | 30–50 家 | HTTP / Playwright | 注册信息、主营摘要 | 关键字段可提取 | 页面结构差异 |
| 预约披露 | 30–50 家 | HTTP | 预约披露日期 | 日期可提取且可比对 | 日期缺失、格式不一 |
| 风险公告 | 30–50 家 | HTTP | 风险类型、时间、正文 | 能识别风险类型 | 分类困难、口径不清 |
| 股本结构 | 30–50 家 | HTTP / Playwright | 总股本、流通股、限售股 | 数值可提取且自洽 | 单位/口径差异 |
| 股东信息 | 30–50 家 | HTTP / Playwright | 前十大股东、户数 | 名单可提取 | 表格结构不稳定 |
| 限售解禁 | 30–50 家 | HTTP | 解禁时间、数量 | 时间/数量可提取 | 缺失、口径差异 |
| 公开信息 | 20–30 家 | HTTP / Playwright | 龙虎榜 / 异常交易 | 记录可提取 | 结构复杂、频繁改版 |
| 互动易 | 20–30 家 | Playwright / BrowserUser | 问答对、时间 | 问答对可提取 | 反爬、分页复杂 |

每个验证对象都需记录：样本量、访问方式（HTTP / Playwright / BrowserUser / 人工）、成功标准、失败原因，并遵守法律授权与平台规则，不假设绕过登录、付费、验证码、权限或反爬。

---

## 9. 第一阶段优先级建议

### P0 第一阶段

- 最新公告列表；
- 公告 PDF 元数据；
- 个股 F10 基础资料；
- 公司要览；
- 公告类型分类；
- `document_published` / `announcement_published` 事件。

原因：这些最接近现有 CNINFO 年报流程，能最快补齐公司属性、文档流和基础时间线。

### P1 第二批

- 风险提示 / ST / 退市；
- 分红 / 回购 / 定增 / 重组；
- 股东大会 / 管理层变动；
- 预约披露；
- 股东 / 股本信息；
- 限售解禁。

原因：事件价值高，但需要更细的规则分类和去重。

### P2 后续

- 融资融券；
- 大宗交易；
- 公开信息；
- 互动易；
- 网络投票；
- IPO / 债券 / 基金。

原因：有价值但结构更复杂，且容易把项目范围扩大到市场交易数据平台，暂不作为第一阶段核心。

---

## 10. 暂缓范围

当前阶段暂缓：

- 全量实时行情；
- 高频交易数据；
- 新闻媒体大规模抓取；
- 对复杂页面大规模 BrowserUser 抓取；
- 未验证页面的长期稳定性承诺；
- 完整 RAG / Wiki / 推送产品；
- 把所有 CNINFO 栏目一次性接入。

---

## 11. 如何回填到主项目文档

| 应回填位置 | 回填内容 |
|---|---|
| `docs/data_sources.md` | 更新 CNINFO 数据源条目：已使用部分 + 待验证扩展 + 优先级 + 验证记录格式 |
| `plans/storage_schema_design_plan.md` | 只保留轻量引用，不展开全部 CNINFO 栏目 |
| `plans/dynamic_data_platform_plan.md` | 后续可在数据源验证部分引用 CNINFO 优先级 |
| `ROADMAP.md` | 如需要，可在后续阶段补「CNINFO 数据源扩展试点」 |

> CNINFO 的完整盘点放在本文件和 `docs/data_sources.md`，不要塞进 `plans/storage_schema_design_plan.md`。

CNINFO 第一阶段的价值不是只下载年报，而是作为动态平台的核心官方数据源，先补齐公司基础属性、最新公告流、正式文档证据链和基础事件时间线，再扩展到更复杂的市场行为和互动信息。
