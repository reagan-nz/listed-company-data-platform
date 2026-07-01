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
| 最新公告 | 公告列表（HTML / API） | 公告标题、公告类型、发布时间、公告 URL、关联公司 | 补齐**文档流**；触发 `document_published` / `announcement_published` 等基础事件；支撑公司时间线 | P0 | **P0 小样本已完成**（34/40 公司；`testing / partial`） |
| 信息披露 / 公告搜索 | 公告检索（HTML / API） | 按公司 / 类型 / 期间检索历史公告；公告元数据 | 补齐**历史文档流**；支持按类型回溯风险、分红、重组等公告 | P0 | 候选 / 待验证 |
| 年报 | 定期报告 PDF | 全文 PDF、`source_url`、`content_hash`、报告期；可抽取主营业务、研发、收入结构、风险因素等字段 | **已有基础**：支撑公司画像、字段查询、证据追溯；可扩展至多年份 | P0 | **已使用**（2024 年报 PDF + 字段抽取）；多年份扩展为候选 / 待验证 |
| 半年报 | 定期报告 PDF | 全文 PDF、报告期、中期财务与经营披露 | 补半年度文档流与字段；支持中期变化追踪 | P1 | 候选 / 待验证 |
| 季报 | 定期报告 PDF | 全文 PDF、报告期、季度财务与经营披露 | 补季度文档流；支持更高频字段变化 | P1 | 候选 / 待验证 |
| 个股 F10 | 结构化资料页（HTML） | 股票简称、交易所、板块、行业、公司简介、基础指标、部分治理与股东摘要 | 直接补 **company 基础属性**；降低对公司官网依赖 | P0 | **P0 小样本已完成**（Playwright 22/30；`partial / testing`） |
| 公司资料 / 公司要览 | 结构化资料页（HTML） | 注册地址、办公地址、主营业务摘要、官网、联系方式、董秘等 | 补 **公司资料属性**；与 F10 交叉验证 | P0 | 候选 / 待验证（F10 已覆盖部分字段，未单独验证） |
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

> 除上述「已使用」的年报 PDF / 年报字段外，P0 栏目的扩展接入仍须走小样本验证，不得视为已全部采集完成。其中**最新公告列表、公告 PDF 元数据、个股 F10 / 公司资料**的 P0 小样本验证已于 Issue #81–#84 完成（详见 [outputs/validation/cninfo_p0_validation_final_summary.md](../outputs/validation/cninfo_p0_validation_final_summary.md)），结论为部分可用（`testing / partial`），不等于全量采集完成。

---

## 4. CNINFO 数据类型分类：属性、文档、事件、证据与候选数据

> **Sub Issue 1.2：将 CNINFO 数据分类为属性、文档、事件、证据和候选数据。** 在栏目盘点（第 3 节）基础上，本节按**平台用途**分类 CNINFO 可能提供的数据，判断其进入正式层、证据层还是候选层。本节只做分类研究，不涉及爬虫实现或数据库 schema 接入。

| 数据类型 | 示例字段 | 来源栏目 | 平台用途 | 建议层级 | 优先级 | 当前状态 |
|---|---|---|---|---|---|---|
| 公司基础属性 | `company_code`、`stock_short_name`、`company_name`、`exchange`、`board`、`industry`、`listing_status`、`is_st` | 个股 F10 / 公司资料 / 公司要览 | 识别公司、筛选公司、建立 `company` 主索引 | PostgreSQL `company` | P0 | F10 P0 小样本部分可用（`partial / testing`） |
| 公司资料属性 | `company_profile`、`main_business_summary`、`registered_address`、`office_address`、`website`、`contact_phone`、`contact_email`、`board_secretary` | 个股 F10 / 公司资料 | 补充公司画像和未来用户端公司资料页 | PostgreSQL `company_profile`；原始页面可进 MinIO / MongoDB | P0/P1 | F10 P0 小样本部分可用（Playwright 22/30；`partial / testing`） |
| 文档属性 | `announcement_title`、`announcement_type`、`publish_time`、`report_period`、`source_url`、`pdf_url`、`content_hash` | 最新公告 / 信息披露 / 公告搜索 / 年报 / 半年报 / 季报 | 管理公告、定期报告和来源文档 | PostgreSQL `document` + `raw_file`；PDF 原件进 MinIO | P0 | 年报已使用；最新公告 + PDF 元数据 P0 小样本已完成（`testing / partial`） |
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

> **Sub Issue 2.1：设计 CNINFO 数据源验证记录模板。** Parent Issue 1 已完成栏目盘点、数据类型分类与第一阶段优先级；Parent Issue 2 进入 CNINFO 验证框架。本节包含验证记录模板与状态定义，以及 **P0 小样本验证结果摘要**（Issue #81–#84）。

> 未验证前只写「候选数据源」或「待验证栏目」，不要写「长期稳定可用」。

### 8.0 P0 小样本验证结果（已完成，Issue #81–#84）

CNINFO P0 小样本验证**已完成**（2026-07）。完整总结见 [outputs/validation/cninfo_p0_validation_final_summary.md](../outputs/validation/cninfo_p0_validation_final_summary.md)。

| P0 对象 | Issue | 小样本结果 | recommended_status | 说明 |
|---|---|---|---|---|
| 样本公司清单 | #81 | 40 家，四板块 | — | 输入基础；部分辅助字段 unknown |
| 最新公告列表 | #82 | 34/40 公司；102/108 公告记录 | `testing / partial` | BSE 430 old code 6 家失败 |
| 公告 PDF 元数据 | #83 | 100/100 success | `testing` | P0 中表现最好；未接 MinIO |
| 个股 F10 / 公司资料 | #84 | reachability 23 success；Playwright 22/30 | `partial / testing` | 依赖 stockCode+orgId+Playwright |

**边界（必须保持）：**

- P0 验证完成 **≠** 全量采集完成；**≠** 长期稳定 `verified`。
- 仍维持「候选 / 待验证 / 不长期承诺」边界；`recommended_status` 为 `testing` 或 `partial / testing`，**不写 `verified`**。
- **当前不做数据库接入**；验证结果仅作为后续 PostgreSQL / MongoDB / MinIO 设计依据。
- 分项细节见 `outputs/validation/` 下各 CSV / summary，F10 详见 `cninfo_f10_validation_final_summary.md`。

### 候选验证对象清单（按优先级分批执行）

下表包含后续可能验证的 CNINFO 子栏目，并不代表第一阶段全部执行；第一阶段仍以第 9.2 节定义的 P0 为准。

| 验证对象 | 样本量 | 访问方式 | 需要验证的字段 | 成功标准 | 失败记录 |
|---|---|---|---|---|---|
| 最新公告列表 | 50–100 家 | HTTP 优先 | 标题、类型、时间、URL | 列表可获取、关键字段完整 | 改版、限流、字段缺失 |
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

每个验证对象都需按 **8.1 模板** 记录：样本量、访问方式、成功率、失败原因，并遵守法律授权与平台规则，不假设绕过登录、付费、验证码、权限或反爬。

### 8.1 验证记录模板

每个 CNINFO 子栏目在被标记为「已验证」之前，都必须先完成小样本验证，并按统一格式记录结果。验证记录**不是为了证明该栏目一定可用**，而是为了客观记录它在样本测试中的字段可得性、稳定性、失败原因和后续建议。

| 字段 | 说明 | 示例 |
|---|---|---|
| `source_section` | CNINFO 子栏目名称 | 最新公告 / 个股 F10 / 公告 PDF |
| `test_date` | 测试日期 | 2026-07-01 |
| `sample_size` | 样本数量 | 50 家公司 |
| `sample_companies` | 样本公司范围，需覆盖不同板块和行业 | 主板 / 创业板 / 科创板 / 北交所公司混合样本 |
| `access_method` | 访问方式 | HTTP / Playwright / BrowserUser / 人工 |
| `target_fields` | 计划验证的字段 | `announcement_title`, `publish_time`, `source_url`, `pdf_url` |
| `success_count` | 成功获取关键字段的样本数量 | 45 |
| `failure_count` | 失败样本数量 | 5 |
| `success_rate` | 成功率 | 90% |
| `data_obtained` | 实际成功获取到的字段 | 标题、发布时间、PDF URL |
| `data_missing` | 缺失字段 | 部分公司缺少公告类型 |
| `failure_reasons` | 失败原因 | 页面结构变化、字段缺失、PDF 404、动态渲染、分页异常 |
| `compliance_risk` | 是否存在登录、验证码、付费、权限、反爬等风险 | 低 / 中 / 高 |
| `evidence_available` | 是否能保留 `source_url`、PDF、HTML 快照、`content_hash` 等证据 | 是 / 部分 / 否 |
| `recommended_status` | 验证后建议状态 | `candidate` / `testing` / `verified` / `partial` / `postponed` / `rejected` |
| `recommendation` | 后续建议 | 进入 P0 小样本抓取 / 暂缓 / 需要 Playwright / 需要人工复核 |
| `next_action` | 下一步动作 | 扩大样本 / 写抓取脚本 / 更新 `docs/data_sources.md` / 保持候选 |

### 8.2 验证状态定义

| 状态 | 含义 | 使用条件 |
|---|---|---|
| `candidate` | 候选数据源 | 已发现价值，但尚未完成小样本验证 |
| `testing` | 正在验证 | 已选择样本并开始测试字段可得性 |
| `verified` | 已通过当前小样本验证 | 关键字段成功率达到设定标准，且证据可追溯 |
| `partial` | 部分可用 | 部分字段可稳定获取，但存在缺失字段或特定失败情况 |
| `postponed` | 暂缓 | 价值存在，但当前阶段优先级低、成本高或范围外 |
| `rejected` | 不建议继续 | 小样本验证失败率高、字段不可用、合规风险高或证据不可追溯 |

> `verified` 只代表**当前小样本验证通过**，不代表长期稳定可用；后续仍需持续监控。

### 8.3 验证通过标准

P0 栏目要从「候选」进入「已验证」，至少需要满足：

1. 样本量足够，例如 20–50 家公司（具体按栏目调整）；
2. 关键字段成功率达到预设标准（**具体阈值按栏目决定，但必须记录成功率和失败原因**；不要求 100% 成功）；
3. 每条数据可以保留 `source_url` 或原始文件证据；
4. 失败样本有明确 `failure_reason`；
5. 不存在明显登录、验证码、付费、权限或高反爬风险；
6. 字段结构足够稳定，可以支持后续小样本脚本化；
7. 结果已更新到 `docs/data_sources.md`。

### 8.4 验证记录示例

以下为「最新公告列表」的**记录格式 mock 示例**，不代表真实验证结果：

| 字段 | 示例值 |
|---|---|
| `source_section` | 最新公告 |
| `test_date` | 2026-07-01 |
| `sample_size` | 50 |
| `access_method` | HTTP 优先 |
| `target_fields` | `company_code`, `announcement_title`, `publish_time`, `source_url`, `pdf_url` |
| `success_count` | mock: 45 |
| `failure_count` | mock: 5 |
| `success_rate` | mock: 90% |
| `data_obtained` | mock: 标题、发布时间、PDF URL |
| `data_missing` | mock: 部分公告缺少类型 |
| `failure_reasons` | mock: 分页异常、PDF URL 缺失 |
| `compliance_risk` | mock: 低 |
| `evidence_available` | mock: 是 |
| `recommended_status` | mock: `testing` |
| `recommendation` | mock: 继续扩大样本 |
| `next_action` | mock: 准备最新公告 P0 小样本验证 |

> 这是记录格式示例，不代表真实验证结果。P0 四项（样本清单、最新公告、PDF 元数据、F10）的真实结果见 [outputs/validation/cninfo_p0_validation_final_summary.md](../outputs/validation/cninfo_p0_validation_final_summary.md) 第 8.0 节。

### 8.5 P0 验证计划：最新公告列表

> **Sub Issue 2.2：准备 CNINFO 最新公告列表的 P0 验证计划。** 本节在 8.1 验证记录模板基础上，为第一个 P0 栏目设计小样本验证方案；**只做验证计划，不做真实验证、不写爬虫、不做数据库接入。**

#### 8.5.1 验证目标

最新公告列表是 CNINFO 第一阶段最重要的 P0 栏目之一。验证它的目标**不是立即全量抓取**，而是判断它是否能稳定提供公告标题、发布时间、公告链接、PDF 链接、关联公司等基础字段，从而支持后续 document 元数据、公告流和基础时间线。

需要强调：

- 本节只是**验证计划**；
- **不代表**最新公告列表已经完成采集；
- **不代表**该栏目长期稳定可用；
- **不做**数据库接入；
- **不写**爬虫实现。

#### 8.5.2 样本设计

| 项 | 设计 |
|---|---|
| 样本量 | 20–50 家公司 |
| 样本覆盖 | 主板、创业板、科创板、北交所尽量都覆盖 |
| 行业覆盖 | 制造业、信息技术、医药、消费、金融或类金融、能源/材料等尽量混合 |
| 公司类型覆盖 | 正常上市公司、ST / 风险类公司、不同市值公司、公告频率较高和较低公司 |
| 时间范围 | 优先验证最近 3–6 个月公告；如接口支持，再测试历史公告回溯 |
| 样本公司记录 | 记录 `company_code`、`company_name`、`exchange`、`board`、`industry`、`sample_reason` |

#### 8.5.3 目标字段

| 字段 | 说明 | 是否关键字段 |
|---|---|---|
| `company_code` | 股票代码 | 是 |
| `company_name` | 公司名称或证券简称 | 是 |
| `announcement_title` | 公告标题 | 是 |
| `announcement_type` | 公告类型，如年报、临时公告、风险提示等；如果 CNINFO 不直接给出，可后续通过标题规则推断 | 部分关键 |
| `publish_time` | 公告发布时间 | 是 |
| `source_url` | 公告详情页或来源链接 | 是 |
| `pdf_url` | 公告 PDF 下载链接 | 是 |
| `file_type` | PDF / HTML / attachment 等 | 否 |
| `crawl_time` | 本次验证时间 | 是 |
| `failure_reason` | 失败原因 | 是，失败样本必须记录 |

#### 8.5.4 访问方式

访问方式优先级如下：

1. **HTTP / API 优先**  
   如果公告列表可以通过公开接口或静态请求获得，优先使用 HTTP，因为更稳定、成本低、便于记录。

2. **Playwright 作为备用**  
   如果页面依赖 JS 渲染或分页复杂，再使用 Playwright。

3. **BrowserUser 暂不作为第一选择**  
   只有在页面强交互、普通 HTTP / Playwright 不够时再考虑。

**不绕过**登录、验证码、付费、权限或强反爬。

#### 8.5.5 成功标准

| 维度 | 成功标准 |
|---|---|
| 字段完整性 | 关键字段 `company_code`、`announcement_title`、`publish_time`、`source_url` 或 `pdf_url` 能稳定获得 |
| 证据可追溯 | 每条公告至少有 `source_url` 或 `pdf_url` |
| 失败可解释 | 失败样本必须有 `failure_reason` |
| 样本覆盖 | 样本覆盖不同板块和行业 |
| 合规风险 | 不存在明显登录、验证码、付费、权限或高反爬问题 |
| 可脚本化 | 如果字段结构相对稳定，可以进入下一步小脚本验证 |
| docs 更新 | 验证完成后，需要更新 `docs/data_sources.md` 中 CNINFO 的对应状态 |

具体成功率阈值根据测试结果确定，但必须记录 `success_count`、`failure_count`、`success_rate`；不要求 100% 成功。

#### 8.5.6 失败原因分类

| `failure_reason` | 说明 |
|---|---|
| `page_structure_changed` | 页面结构变化 |
| `missing_company_mapping` | 公司代码 / orgId / 名称无法匹配 |
| `missing_announcement_title` | 公告标题缺失 |
| `missing_publish_time` | 发布时间缺失 |
| `missing_pdf_url` | PDF 链接缺失 |
| `pdf_404` | PDF 链接失效 |
| `pagination_error` | 分页异常 |
| `rate_limited` | 请求频率限制 |
| `js_render_required` | 需要 JS 渲染 |
| `captcha_or_login_required` | 出现验证码或登录要求 |
| `network_timeout` | 网络超时 |
| `unknown_error` | 未知错误，需要人工检查 |

#### 8.5.7 验证结果记录格式

最新公告列表验证完成后，需要按 **8.1 验证记录模板** 记录结果。

以下为 mock 示例，**不代表真实验证结果**：

| 字段 | 示例值 |
|---|---|
| `source_section` | 最新公告 |
| `test_date` | 2026-07-01 |
| `sample_size` | mock: 30 |
| `access_method` | mock: HTTP 优先 |
| `target_fields` | `company_code`, `announcement_title`, `publish_time`, `source_url`, `pdf_url` |
| `success_count` | mock: 27 |
| `failure_count` | mock: 3 |
| `success_rate` | mock: 90% |
| `data_obtained` | mock: 标题、发布时间、PDF URL |
| `data_missing` | mock: 部分公告缺少公告类型 |
| `failure_reasons` | mock: `missing_pdf_url`, `pagination_error` |
| `compliance_risk` | mock: 低 |
| `evidence_available` | mock: 是 |
| `recommended_status` | mock: `testing` |
| `recommendation` | mock: 扩大样本并准备小脚本验证 |
| `next_action` | mock: 进入公告 PDF 元数据验证计划 |

> 这是 mock 示例，不代表真实验证结果。

#### 8.5.8 与后续任务的关系

**如果最新公告列表验证通过**，后续可以进入：

- 公告 PDF 元数据验证；
- document 元数据字段设计；
- `document_published` / `announcement_published` 事件规则；
- `docs/data_sources.md` 状态更新；
- 后续 PostgreSQL / MinIO / MongoDB 接入建议。

**如果验证失败或部分可用**，则：

- 保持 `candidate` / `partial` 状态；
- 记录失败原因；
- 判断是否需要 Playwright；
- 暂不进入数据库接入。

### 8.6 P0 验证计划：公告 PDF 元数据

> **Sub Issue 2.3：准备 CNINFO 公告 PDF 元数据的 P0 验证计划。** 本节在 8.5 最新公告列表验证计划基础上，设计公告 PDF 元数据的小样本验证方案；**只做验证计划，不做真实验证、不写爬虫、不做数据库接入。**

#### 8.6.1 验证目标

公告 PDF 元数据验证的目标，是在最新公告列表能提供 `pdf_url` / `source_url` 的基础上，进一步判断公告 PDF 是否能够稳定下载、识别、去重和追溯。

它主要验证：

- PDF 是否能通过公开链接访问；
- PDF 是否能下载；
- 是否能计算 `content_hash` / `sha256`；
- 是否能记录 `file_size`、`mime_type`、`download_time`、`download_status`；
- 是否能保留 `source_url` 与 `pdf_url`；
- 是否能为后续 MinIO 原件层和 PostgreSQL `raw_file` / `document` 元数据提供依据。

需要强调：

- 本节只是**验证计划**；
- **不代表**公告 PDF 下载已经完成；
- **不代表** PDF 链接长期稳定可用；
- **不做**真实下载；
- **不写**爬虫；
- **不做** MinIO / PostgreSQL / MongoDB 接入。

#### 8.6.2 样本设计

| 项 | 设计 |
|---|---|
| 样本量 | 50–100 份公告 PDF |
| 样本来源 | 优先来自 8.5 最新公告列表验证中获得的 `pdf_url` / `source_url` |
| 公告类型覆盖 | 定期报告、临时公告、风险提示、分红回购、公司治理、监管问询等尽量混合 |
| 公司覆盖 | 尽量覆盖不同板块、行业和公告频率不同的公司 |
| 文件类型覆盖 | 普通文本 PDF、扫描 PDF、带附件公告、可能较大的 PDF |
| 时间范围 | 优先最近 3–6 个月公告；如可行，再抽取较早公告测试链接可用性 |
| 样本记录 | 记录 `company_code`、`company_name`、`announcement_title`、`announcement_type`、`publish_time`、`source_url`、`pdf_url`、`sample_reason` |

#### 8.6.3 目标字段

| 字段 | 说明 | 是否关键字段 |
|---|---|---|
| `company_code` | 股票代码 | 是 |
| `company_name` | 公司名称或证券简称 | 是 |
| `announcement_title` | 公告标题 | 是 |
| `announcement_type` | 公告类型 | 部分关键 |
| `publish_time` | 公告发布时间 | 是 |
| `source_url` | 公告来源链接或详情页链接 | 是 |
| `pdf_url` | PDF 下载链接 | 是 |
| `download_status` | 下载状态，例如 `success` / `failed` / `skipped` | 是 |
| `http_status_code` | HTTP 状态码，例如 200 / 403 / 404 / 500 | 是 |
| `content_hash` | PDF 文件 sha256，用于去重和一致性校验 | 是，下载成功时必须记录 |
| `file_size` | PDF 文件大小 | 是，下载成功时必须记录 |
| `mime_type` | 文件类型，例如 `application/pdf` | 是 |
| `download_time` | 下载时间 | 是 |
| `has_text_layer` | PDF 是否可能有文本层，后续解析时需要 | 否，本阶段可选 |
| `failure_reason` | 失败原因 | 是，失败样本必须记录 |

#### 8.6.4 访问方式

访问方式优先级如下：

1. **HTTP 直接下载优先**  
   如果 `pdf_url` 是公开静态链接，优先使用 HTTP 下载，记录 `http_status_code`、`file_size`、`mime_type`、`content_hash`。

2. **source_url 回退**  
   如果 `pdf_url` 缺失或失效，可以回到 `source_url` / 公告详情页查找 PDF 链接。

3. **Playwright 备用**  
   如果 PDF 链接由前端动态生成或页面依赖 JS 渲染，再考虑 Playwright。

4. **BrowserUser 暂不作为第一选择**  
   除非普通 HTTP / Playwright 无法获取，且确实属于高价值 P0 验证。

**不绕过**登录、验证码、付费、权限或强反爬。

#### 8.6.5 成功标准

| 维度 | 成功标准 |
|---|---|
| PDF 可访问 | 公开 `pdf_url` 能返回有效响应，例如 HTTP 200 |
| 文件可识别 | `mime_type` 或文件头能确认是 PDF |
| hash 可计算 | 下载成功的 PDF 能计算 sha256 / `content_hash` |
| 文件元数据完整 | `file_size`、`download_time`、`download_status` 能记录 |
| 证据可追溯 | 每份 PDF 都能关联 `source_url` / `pdf_url` / `announcement_title` / `publish_time` |
| 失败可解释 | 失败样本必须记录 `failure_reason` 和 `http_status_code` |
| 合规风险 | 不存在明显登录、验证码、付费、权限或高反爬问题 |
| 后续可接入 | 如果结果稳定，后续可为 MinIO `object_key`、`raw_file` 元数据、`document` 关联提供依据 |

具体阈值按栏目和样本决定，但必须记录 `success_count`、`failure_count`、`success_rate`；不要求 100% 成功。

#### 8.6.6 失败原因分类

| `failure_reason` | 说明 |
|---|---|
| `missing_pdf_url` | 缺少 PDF 链接 |
| `invalid_pdf_url` | PDF 链接格式无效 |
| `pdf_404` | PDF 不存在或链接失效 |
| `pdf_403` | 访问被拒绝 |
| `pdf_500` | 服务器错误 |
| `not_pdf_content` | 返回内容不是 PDF |
| `download_timeout` | 下载超时 |
| `file_too_large` | 文件过大，超过验证阶段限制 |
| `hash_failed` | hash 计算失败 |
| `mime_type_missing` | 无法判断文件类型 |
| `source_url_missing` | 缺少来源链接 |
| `source_pdf_mismatch` | `source_url` 与 `pdf_url` 无法对应 |
| `scan_pdf_no_text_layer` | 扫描件 PDF 无文本层，后续解析可能需要 OCR |
| `rate_limited` | 请求频率限制 |
| `captcha_or_login_required` | 出现验证码或登录要求 |
| `unknown_error` | 未知错误，需要人工检查 |

#### 8.6.7 content_hash / sha256 规则

`content_hash` 建议使用 **sha256**。

计算对象应为 **PDF 原始二进制内容**，而不是 URL、标题或解析文本。

用途包括：

- 文件去重；
- 校验重复下载是否一致；
- 作为 `raw_file` 记录的重要字段；
- 后续生成 MinIO `object_key` 时作为辅助依据。

> 本节只定义规则，**不实际计算 hash**。

#### 8.6.8 验证结果记录格式

公告 PDF 元数据验证完成后，需要按 **8.1 验证记录模板** 记录结果。

以下为 mock 示例，**不代表真实验证结果**：

| 字段 | 示例值 |
|---|---|
| `source_section` | 公告 PDF 元数据 |
| `test_date` | 2026-07-01 |
| `sample_size` | mock: 80 |
| `access_method` | mock: HTTP 直接下载 |
| `target_fields` | `company_code`, `announcement_title`, `pdf_url`, `http_status_code`, `content_hash`, `file_size`, `mime_type` |
| `success_count` | mock: 72 |
| `failure_count` | mock: 8 |
| `success_rate` | mock: 90% |
| `data_obtained` | mock: PDF URL、HTTP 状态码、文件大小、sha256 |
| `data_missing` | mock: 部分公告缺少 PDF URL |
| `failure_reasons` | mock: `pdf_404`, `download_timeout`, `not_pdf_content` |
| `compliance_risk` | mock: 低 |
| `evidence_available` | mock: 是 |
| `recommended_status` | mock: `testing` |
| `recommendation` | mock: 继续验证 object_key 规则和 raw_file 字段映射 |
| `next_action` | mock: 准备 F10 / 公司资料验证计划 |

> 这是 mock 示例，不代表真实验证结果。

#### 8.6.9 与后续任务的关系

**如果公告 PDF 元数据验证通过**，后续可以进入：

- MinIO `object_key` 规则设计；
- `raw_file` 元数据字段映射；
- `document` 与 `raw_file` 关联规则；
- 公告 PDF 正文解析验证；
- `field_value` / `event` 的证据追溯设计；
- `docs/data_sources.md` 状态更新。

**如果验证失败或部分可用**，则：

- 保持 `candidate` / `partial` 状态；
- 记录失败原因；
- 判断是否需要回到 `source_url` 查找 PDF；
- 判断是否需要 Playwright；
- 暂不进入 MinIO / PostgreSQL 接入。

### 8.7 P0 验证计划：个股 F10 / 公司资料

> **Sub Issue 2.4：准备 CNINFO 个股 F10 / 公司资料的 P0 验证计划。** 本节在 8.5、8.6 验证计划基础上，设计个股 F10 / 公司资料 / 公司要览的小样本验证方案；**只做验证计划，不做真实验证、不写爬虫、不做数据库接入。**

#### 8.7.1 验证目标

个股 F10 / 公司资料 / 公司要览验证的目标，是判断 CNINFO 是否能稳定提供公司基础属性和公司资料属性，例如股票简称、交易所、板块、行业、上市状态、公司简介、主营业务摘要、注册地址、办公地址、官网、联系方式、董秘等。

这些字段未来可能用于：

- 补充 PostgreSQL `company` 基础表；
- 形成未来候选 `company_profile`；
- 支持公司画像页；
- 支持用户按行业、板块、上市状态筛选公司；
- 与年报字段和公告数据交叉验证。

需要强调：

- 本节只是**验证计划**；
- **不代表** F10 / 公司资料已经完成采集；
- **不代表**页面长期稳定可用；
- **不做**真实抓取；
- **不写**爬虫；
- **不做** PostgreSQL / MongoDB / MinIO 接入。

#### 8.7.2 样本设计

| 项 | 设计 |
|---|---|
| 样本量 | 30–50 家公司 |
| 样本覆盖 | 主板、创业板、科创板、北交所尽量都覆盖 |
| 行业覆盖 | 制造业、信息技术、医药、消费、金融或类金融、能源/材料等尽量混合 |
| 公司类型覆盖 | 正常上市公司、ST / 风险类公司、不同市值公司、上市时间较长和较新的公司 |
| 字段覆盖 | 优先验证基础字段，再验证公司简介、联系方式、董秘等资料字段 |
| 样本公司记录 | 记录 `company_code`、`company_name`、`exchange`、`board`、`industry`、`listing_status`、`sample_reason` |

#### 8.7.3 目标字段

| 字段 | 说明 | 建议去向 | 是否关键字段 |
|---|---|---|---|
| `company_code` | 股票代码 | PostgreSQL `company` | 是 |
| `company_name` | 公司全称 | PostgreSQL `company` | 是 |
| `stock_short_name` | 股票简称 | PostgreSQL `company` | 是 |
| `exchange` | 交易所，例如 SSE / SZSE / BSE | PostgreSQL `company` | 是 |
| `board` | 板块，例如主板 / 创业板 / 科创板 / 北交所 | PostgreSQL `company` | 是 |
| `industry` | 行业分类 | PostgreSQL `company` 或未来候选 `company_profile` | 是 |
| `listing_status` | 上市状态 | PostgreSQL `company` | 是 |
| `is_st` | 是否 ST / *ST | PostgreSQL `company` 或风险事件辅助字段 | 部分关键 |
| `company_profile` | 公司简介 | 未来候选 `company_profile` | 部分关键 |
| `main_business_summary` | 主营业务摘要 | 未来候选 `company_profile`；可与年报字段交叉验证 | 部分关键 |
| `registered_address` | 注册地址 | 未来候选 `company_profile` | 否 |
| `office_address` | 办公地址 | 未来候选 `company_profile` | 否 |
| `website` | 公司官网 | 未来候选 `company_profile` | 否 |
| `contact_phone` | 联系电话 | 未来候选 `company_profile` | 否 |
| `contact_email` | 联系邮箱 | 未来候选 `company_profile` | 否 |
| `board_secretary` | 董秘 | 未来候选 `company_profile` / `management_profile` | 否 |
| `source_url` | F10 / 公司资料来源链接 | 证据引用 | 是 |
| `crawl_time` | 本次验证时间 | 验证记录 | 是 |
| `failure_reason` | 失败原因 | 验证记录 | 是，失败样本必须记录 |

#### 8.7.4 访问方式

访问方式优先级如下：

1. **HTTP / API 优先**  
   如果 F10 / 公司资料可通过公开接口或静态请求获得，优先使用 HTTP。

2. **Playwright 备用**  
   如果页面依赖 JS 渲染、字段由前端动态加载或分页/标签切换复杂，再使用 Playwright。

3. **BrowserUser 暂不作为第一选择**  
   只有在普通 HTTP / Playwright 无法处理，且该字段确实有高价值时再考虑。

4. **人工抽样对照**  
   对于字段含义容易混淆的内容，例如行业、板块、主营业务摘要，可以人工抽查少量样本，判断字段语义是否正确。

**不绕过**登录、验证码、付费、权限或强反爬。

#### 8.7.5 成功标准

| 维度 | 成功标准 |
|---|---|
| 公司识别 | `company_code`、`company_name`、`stock_short_name` 能匹配到同一家公司 |
| 基础字段完整性 | `exchange`、`board`、`industry`、`listing_status` 等基础字段能稳定获得 |
| 资料字段可用性 | `company_profile`、`main_business_summary`、`registered_address`、`office_address`、`website`、`contact_phone`、`contact_email`、`board_secretary` 等字段至少部分可获得，并记录缺失情况 |
| 证据可追溯 | 每条公司资料至少有 `source_url` 或页面快照来源 |
| 字段语义清楚 | 字段含义能被解释清楚，避免把指标、摘要、公告内容混成公司基础属性 |
| 失败可解释 | 失败样本必须有 `failure_reason` |
| 合规风险 | 不存在明显登录、验证码、付费、权限或高反爬问题 |
| 后续可接入 | 如果结果稳定，后续可为 `company` / `company_profile` 字段映射提供依据 |

具体阈值按字段类型决定，但必须记录 `success_count`、`failure_count`、`success_rate`；不要求 100% 成功。

#### 8.7.6 失败原因分类

| `failure_reason` | 说明 |
|---|---|
| `missing_company_code` | 股票代码缺失 |
| `missing_company_name` | 公司名称缺失 |
| `company_mapping_failed` | 公司代码、名称、orgId 无法对应 |
| `f10_page_not_found` | F10 页面不存在 |
| `company_profile_missing` | 公司简介缺失 |
| `industry_missing` | 行业字段缺失 |
| `board_missing` | 板块字段缺失 |
| `listing_status_missing` | 上市状态缺失 |
| `contact_info_missing` | 联系方式缺失 |
| `board_secretary_missing` | 董秘字段缺失 |
| `field_semantics_unclear` | 字段语义不清楚，无法判断是否可作为正式属性 |
| `page_structure_changed` | 页面结构变化 |
| `js_render_required` | 需要 JS 渲染 |
| `rate_limited` | 请求频率限制 |
| `captcha_or_login_required` | 出现验证码或登录要求 |
| `network_timeout` | 网络超时 |
| `unknown_error` | 未知错误，需要人工检查 |

#### 8.7.7 字段分层规则

F10 / 公司资料字段不能全部直接进入 `company` 表，应按字段稳定性和用途分层：

| 字段层级 | 示例字段 | 后续建议 |
|---|---|---|
| 公司主索引字段 | `company_code`、`company_name`、`stock_short_name`、`exchange`、`board`、`listing_status` | 验证通过后可映射到 PostgreSQL `company` |
| 公司画像字段 | `industry`、`company_profile`、`main_business_summary` | 验证后可进入 `company` 或未来候选 `company_profile`；需要和年报字段交叉验证 |
| 联系方式字段 | `registered_address`、`office_address`、`website`、`contact_phone`、`contact_email` | 更适合未来候选 `company_profile`，不急于进入第一阶段核心 `company` 表 |
| 治理辅助字段 | `board_secretary`、部分高管/董监高摘要 | 未来可进入 `company_profile` 或 `management_profile` 候选方向，不在当前阶段落地 |
| 证据字段 | `source_url`、`crawl_time`、页面快照 | `source_url` 进入证据引用；页面快照未来可进 MinIO；当前阶段只做验证计划 |

#### 8.7.8 验证结果记录格式

F10 / 公司资料验证完成后，需要按 **8.1 验证记录模板** 记录结果。

以下为 mock 示例，**不代表真实验证结果**：

| 字段 | 示例值 |
|---|---|
| `source_section` | 个股 F10 / 公司资料 |
| `test_date` | 2026-07-01 |
| `sample_size` | mock: 40 |
| `access_method` | mock: HTTP 优先，Playwright 备用 |
| `target_fields` | `company_code`, `stock_short_name`, `exchange`, `board`, `industry`, `company_profile`, `website` |
| `success_count` | mock: 34 |
| `failure_count` | mock: 6 |
| `success_rate` | mock: 85% |
| `data_obtained` | mock: 股票简称、交易所、板块、行业、公司简介 |
| `data_missing` | mock: 部分公司缺少联系方式或董秘字段 |
| `failure_reasons` | mock: `js_render_required`, `contact_info_missing`, `field_semantics_unclear` |
| `compliance_risk` | mock: 低 |
| `evidence_available` | mock: 部分 |
| `recommended_status` | mock: `testing` |
| `recommendation` | mock: 扩大样本并人工抽查字段语义 |
| `next_action` | mock: 准备公司资料字段映射建议 |

> 这是 mock 示例，不代表真实验证结果。

#### 8.7.9 与后续任务的关系

**如果 F10 / 公司资料验证通过**，后续可以进入：

- `company` 字段映射建议；
- 未来候选 `company_profile` 字段设计；
- 公司属性样例页；
- F10 与年报字段交叉验证；
- `docs/data_sources.md` 状态更新；
- 后续 PostgreSQL / MinIO / MongoDB 接入建议。

**如果验证失败或部分可用**，则：

- 保持 `candidate` / `partial` 状态；
- 记录失败原因；
- 判断是否需要 Playwright；
- 判断哪些字段只保留候选、不进入正式 `company`；
- 暂不进入数据库接入。

---

## 9. 第一阶段优先级建议

> **Sub Issue 1.3：定义 CNINFO 第一阶段验证优先级。** 在栏目盘点（第 3 节）与数据类型分类（第 4 节）基础上，本节收敛 P0 / P1 / P2 / 暂缓 的判断标准与第一阶段验证边界。本节只做优先级规划，不涉及爬虫实现或数据库 schema 接入。

### 9.1 优先级判断标准

优先级**不是**按「信息看起来多不多」来排，而是按以下维度判断：

| 判断维度 | 说明 |
|---|---|
| 来源权威性 | 是否来自 CNINFO 正式披露或官方资料页 |
| 结构稳定性 | 字段是否相对固定，是否适合小样本验证 |
| 证据可追溯性 | 是否有 PDF / URL / 页面快照 / 发布时间 |
| 公司属性价值 | 是否能直接补充 `company` / `company_profile` |
| 时间线价值 | 是否能生成 `document_published` / `announcement_published` / `risk_update` 等事件 |
| 接近现有流程程度 | 是否和现有年报 PDF 抽取流程接近 |
| 范围控制 | 是否会把项目扩大成行情平台、新闻平台或交易数据平台 |

**结论：** 第一阶段优先验证那些「权威、稳定、可追溯、能补公司属性或公告流、且接近现有 CNINFO 年报流程」的内容。

### 9.2 P0：第一阶段必须优先验证

| P0 内容 | 对应栏目 | 主要验证字段 | 为什么优先 | 后续可能进入 |
|---|---|---|---|---|
| 最新公告列表 | 最新公告 | `company_code`、`company_name`、`announcement_title`、`announcement_type`、`publish_time`、`source_url`、`pdf_url` | 最适合建立公告流和基础公司时间线 | PostgreSQL `document` / `event`；PDF 进入 MinIO |
| 信息披露 / 公告搜索 | 信息披露 / 公告搜索 | `company_code`、`announcement_title`、`announcement_type`、`publish_time`、`source_url`、`pdf_url`、`search_filter` | 支持历史公告回溯和按类型筛选，补充最新公告列表 | PostgreSQL `document`；候选事件进入 MongoDB / `event` |
| 年报多年份扩展 | 年报 | `report_year`、`document_type`、`source_url`、`pdf_url`、`content_hash`、`parse_status` | 2024 年报已有基础，多年份扩展最接近现有流程 | MinIO raw file；PostgreSQL `document` / `field_value` / `quality_audit` |
| 个股 F10 基础资料 | 个股 F10 | `company_code`、`stock_short_name`、`exchange`、`board`、`industry`、`listing_status`、`is_st` | 能直接补充 `company` 基础属性 | PostgreSQL `company` / 未来候选 `company_profile` |
| 公司资料 / 公司要览 | 公司资料 / 公司要览 | `company_profile`、`main_business_summary`、`registered_address`、`office_address`、`website`、`contact_phone`、`contact_email`、`board_secretary` | 能补充公司画像和未来用户端公司资料页 | 未来候选 PostgreSQL `company_profile`；原始页面进 MinIO / MongoDB |

> P0 不代表已完成采集，只是**优先验证对象**；每项仍需记录样本量、访问方式、成功率与失败原因。

### 9.3 P1：第二批验证

| P1 内容 | 对应栏目 | 主要价值 | 为什么不放 P0 |
|---|---|---|---|
| 半年报 / 季报 | 半年报 / 季报 | 补中期 / 季度文档流与字段 | 需扩展解析流程，不如年报成熟 |
| 预约披露 | 预约披露 | 披露日历、`scheduled_disclosure` 事件 | 需单独字段规则 |
| 风险公告 / 风险提示 | 风险公告 / 风险提示 | ST、退市、重大风险提示 | 需公告类型识别与规则分类 |
| 监管问询 / 处罚 / 诉讼 | 监管问询 / 处罚 / 诉讼 | 合规风险事件 | 类型多样，需细分类 |
| 分红 / 回购 / 定增 / 重组 | 分红融资 / 公告 PDF | 资本运作高价值事件 | 需事件类型与去重规则 |
| 股东大会 / 管理层变动 | 公司治理 / 临时公告 | 治理事件时间线 | 需与 F10 / 公告交叉验证 |
| 股本结构 | 股本结构 / F10 / 年报 | 股本属性快照 | 字段口径需比对 |
| 股东信息 | 股东信息 / 年报 / 季报 | 股东属性快照 | 表格结构可能不稳定 |
| 限售解禁 | 限售解禁 | 解禁事件 | 需与股本结构关联验证 |

这些内容价值高，但需要更细的公告类型识别、字段结构判断、规则分类或跨期比对，因此放在 P1。

### 9.4 P2：后续研究

| P2 内容 | 对应栏目 | 价值 | 为什么后置 |
|---|---|---|---|
| 融资融券 | 融资融券 | 市场行为观察 | 易扩大为行情 / 交易数据平台 |
| 大宗交易 | 大宗交易 | 交易侧辅助信息 | 价值偏交易侧，非公司属性主线 |
| 公开信息 / 异常交易 | 公开信息 / 异常交易 | 异常波动、龙虎榜 | 解释空间大、噪音较高 |
| 互动易 | 互动易 | 投资者关注点 | 需交互抓取，结构不稳定 |
| 网络投票 | 网络投票 | 治理参与记录 | 与股东大会事件关联，优先级低于 P1 |

这些内容有价值，但可能引入市场行为数据、交易解释、复杂交互页面或较高噪音，容易扩大项目范围，因此后置。

### 9.5 暂缓范围

| 暂缓内容 | 原因 |
|---|---|
| IPO / 招股书 | 与当前 A 股存量公司动态平台主线关联较弱 |
| 债券 | 超出当前上市公司主线范围 |
| 基金 | 超出当前上市公司主线范围 |
| 全量实时行情 | 非 CNINFO 第一阶段主线 |
| 高频交易数据 | 非 CNINFO 第一阶段主线 |
| 新闻媒体大规模抓取 | 非官方披露，合规与范围风险高 |
| 大规模 BrowserUser 抓取 | 成本高、稳定性差，当前不优先 |
| 完整 RAG / Wiki / 推送产品 | 应用层能力，当前阶段不做 |

这些不是当前 CNINFO 第一阶段主线，后续可作为扩展方向，但**当前不进入验证任务**。

### 9.6 第一阶段验证边界

第一阶段**只验证 P0**，不同时验证 P1 / P2。P0 小样本验证（最新公告、PDF 元数据、F10 公司资料）**已于 Issue #81–#84 完成**，结论为部分可用，详见第 8.0 节与 [cninfo_p0_validation_final_summary.md](../outputs/validation/cninfo_p0_validation_final_summary.md)。P1 栏目待 P0 映射与稳定性问题进一步收敛后再启动。

请明确：

- **P0 不代表已完成全量采集**；P0 只是优先验证对象。
- 所有 P0 内容仍需记录：样本量、访问方式、成功率、失败原因。
- **当前阶段仍然不做数据库接入**；验证结果以后才作为 PostgreSQL / MongoDB / MinIO 接入依据。

---

## 10. 总体暂缓范围

第 9.5 节列的是 CNINFO 第一阶段验证中的暂缓项；本节从整个项目范围角度汇总当前阶段不进入执行的内容。

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
