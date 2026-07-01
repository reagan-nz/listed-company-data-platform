# 数据来源

## 当前已验证数据源

### 巨潮资讯网（CNINFO）

| 属性 | 说明 |
|---|---|
| **名称** | 巨潮资讯网（www.cninfo.com.cn） |
| **用途** | A 股上市公司年报 PDF 获取与基础字段抽取 |
| **当前状态** | **已验证可用**，1000 家评估中 946 家成功 |
| **获取方式** | HTTP API 查询公告列表 → 筛选全文年报 → 下载 static.cninfo.com.cn PDF |
| **实现** | [lab/probe_cninfo.py](../lab/probe_cninfo.py) |
| **可获得字段** | 11 项基础字段（见 [database_schema.md](database_schema.md)） |

**获取流程**：

1. 从 CNINFO 股票列表 API 获取 `orgId`（`lab/sample_universe.py`）
2. 按 stock_code + orgId 查询 2024–2025 年度公告
3. `pick_full_report()` 筛选全文年报（排除摘要/取消/更正/H 股优先选 A 股）
4. 下载 PDF 到 `outputs/generalization/<code>/<code>.pdf`
5. 解析并抽取字段

**优点**：

- 官方披露渠道，数据权威
- 覆盖全部 A 股（含主板/创业板/科创板/北交所）
- 年报结构相对标准化，锚点抽取可行
- 免费公开访问，无需登录

**限制**：

- 网络不稳定（VPN 断开导致 timeout；已实现断点续跑）
- 部分公司无 2024 年报（退市/ST，status=no_announcement）
- 扫描件 PDF 无文本层（status=no_text_layer，需 OCR）
- 摘要 vs 全文：probe 必须筛选全文（已实现 `pick_full_report`）
- A+H 双上市：H 股年报结构不同（已实现 A 股优先）
- 金融公司披露格式与工业 schema 不匹配

**合规注意事项**：

- 仅访问公开披露信息，符合信息披露法规
- 请求频率控制在 1 req/s（`--throttle 1.0`）
- 不绕过任何访问控制
- 存储 PDF 仅供内部分析，不对外再分发
- 遵守网站 robots.txt 与服务条款

**当前结论**：CNINFO 年报是当前最可靠、覆盖最广的数据源，作为第一阶段唯一数据源。后续可叠加其他源补充。

---

## CNINFO 巨潮资讯网（数据源价值挖掘）

> 本节是 CNINFO 数据源价值的摘要视图。完整盘点见 [plans/cninfo_data_source_value_inventory.md](../plans/cninfo_data_source_value_inventory.md)。除年报 PDF 外，所有扩展栏目都必须先经过小样本验证才能写成已验证数据源。

### 数据源定位

CNINFO 是当前项目**第一优先级的官方披露数据源**。当前已使用的是 2024 年报 PDF、`source_url`、PDF hash 和年报字段抽取；后续还应验证最新公告、个股 F10、公司要览、预约披露、股本股东、风险公告、分红回购定增、互动易等扩展价值。

### 已使用部分

| 数据类型 | 当前状态 | 说明 |
|---|---|---|
| 2024 年报 PDF | 已使用 | `full_market_2024` 全市场抽取来源 |
| PDF `source_url` | 已使用 | 每份年报保留官方链接 |
| PDF hash / `sha256` | 已使用 | 去重与一致性校验 |
| 年报结构化字段 | 已使用 | 11 项基础字段抽取 |
| 证据句 / 页码 | 已使用 | 字段级证据留存 |
| 质量审计标签 | 已使用 | `usable` / `partial` / `wrong` / `not_found_missed` |

### 待验证扩展部分

> 以下均为**候选 / 待验证栏目**，尚未采集完成，也不代表页面长期稳定可用。

| 数据类型 | 可补充属性 | 示例字段 | 可能用途 | 优先级 | 当前状态 |
|---|---|---|---|---|---|
| 最新公告 | 文档属性 | 标题、类型、时间、URL | 文档流与事件时间线 | P0 | **P0 小样本已完成**（34/40 公司；`testing / partial`） |
| 信息披露 / 公告搜索 | 文档属性 | 历史公告检索 | 补齐历史文档流 | P0 | 待验证 |
| 个股 F10 / 公司资料 | 公司静态属性 | 行业、板块、简介 | 公司画像 | P0 | **P0 小样本已完成**（Playwright 22/30；`partial / testing`） |
| 公司要览 | 公司资料属性 | 注册信息、主营摘要 | 公司画像 | P0 | 待验证（与 F10 部分重叠，未单独验证） |
| 预约披露 | 披露计划 | 预约披露日期 | 披露日历 | P1 | 待验证 |
| 股本结构 | 股本属性 | 总股本、流通股、限售股 | 股本快照 | P1 | 待验证 |
| 股东信息 | 股东属性 | 前十大股东、股东户数 | 股东快照 | P1 | 待验证 |
| 分红 / 回购 / 定增 | 动态事件 | 分红、回购、定增预案 | 高价值事件 | P1 | 待验证 |
| 风险公告 | 风险异常属性 | ST、退市、风险提示 | 风险事件 | P1 | 待验证 |
| 公司治理 | 治理属性 | 董监高、股东大会 | 治理属性与事件 | P1 | 待验证 |
| 融资融券 | 市场行为属性 | 融资融券余额 | 市场行为 | P2 | 候选 |
| 大宗交易 | 市场行为属性 | 大宗交易记录 | 市场行为 | P2 | 候选 |
| 限售解禁 | 市场行为属性 | 解禁时间、数量 | 市场行为事件 | P1 | 待验证 |
| 公开信息 | 市场行为属性 | 龙虎榜 / 异常交易 | 市场行为 | P2 | 候选 |
| 互动易 | 投资者互动属性 | 问答对 | 投资者互动候选 | P1 | 候选 |
| 网络投票 | 治理参与属性 | 议案与投票 | 治理参与 | P2 | 候选 |

### 第一阶段建议优先验证

| 优先级 | 内容 | 原因 |
|---|---|---|
| P0 | 最新公告列表 + 公告 PDF 元数据；个股 F10 / 公司资料基础字段；公司要览；公告类型分类 | 最接近现有年报流程，能最快补齐公司属性、文档流和基础时间线 |
| P1 | 风险提示 / ST / 退市；分红 / 回购 / 定增 / 重组；管理层变动 / 股东大会；预约披露；股东股本信息 | 事件价值高，但需要更细的规则分类和去重 |
| P2 | 融资融券、大宗交易、公开信息、互动易、网络投票、IPO、债券、基金 | 有价值但结构复杂，易扩大范围，暂不作为第一阶段核心 |

### 验证记录格式

每个 CNINFO 子栏目验证完成后，按统一模板记录结果（不做真实验证前，栏目保持「候选 / 待验证」）。`verified` 仅表示当前小样本通过，不代表长期稳定可用。

| 字段 | 说明 |
|---|---|
| `source_section` | CNINFO 栏目标识 |
| `test_date` | 验证日期 |
| `sample_size` | 样本量 |
| `access_method` | HTTP / Playwright / BrowserUser / 人工 |
| `target_fields` | 计划验证的字段 |
| `success_count` | 成功数 |
| `failure_count` | 失败数 |
| `success_rate` | 成功率 |
| `data_obtained` | 本次样本验证可获取的数据 |
| `data_missing` | 本次未获取到的数据 |
| `failure_reasons` | 失败原因 |
| `compliance_risk` | 合规风险（低 / 中 / 高） |
| `evidence_available` | 是否可保留 URL / PDF / 快照等证据 |
| `recommended_status` | 建议状态：`candidate` / `testing` / `verified` / `partial` / `postponed` / `rejected` |
| `next_action` | 下一步动作 |

完整验证模板、状态定义与 mock 示例见 [plans/cninfo_data_source_value_inventory.md](../plans/cninfo_data_source_value_inventory.md) 第 8 节。

### CNINFO P0 小样本验证结果（已完成）

> 完整总结见 [outputs/validation/cninfo_p0_validation_final_summary.md](../outputs/validation/cninfo_p0_validation_final_summary.md)（Issue #81–#84）。

| 项目 | 说明 |
|---|---|
| **验证阶段** | P0 小样本验证已完成（2026-07）；40 家样本，覆盖主板 / 创业板 / 科创板 / 北交所 |
| **当前阶段** | 部分可用，部分仍需 orgId 映射 / 字段稳定性处理；**未做数据库接入** |
| **样本清单** | #81：`cninfo_p0_sample_companies.csv`（40 家） |

**分项摘要：**

| P0 对象 | 小样本结果 | recommended_status |
|---|---|---|
| 最新公告列表 | 34/40 公司成功；102/108 公告记录；字段完整度 102/108 | `testing / partial` |
| 公告 PDF 元数据 | 100/100 下载与 hash 成功；sha256 基于 PDF 二进制 | `testing`（P0 中表现最好） |
| 个股 F10 / 公司资料 | 旧接口不可用；新入口 `#companyProfile`；Playwright 22/30 可提取核心字段 | `partial / testing` |

**要点：**

- **PDF 元数据**表现最好，可作为后续 `raw_file` / MinIO 接入候选依据（当前未接入）。
- **最新公告列表**整体可用，但 **6 家 BSE 430 old code** 仍失败，需映射回退。
- **F10 / 公司资料**有价值，但依赖 **stockCode + orgId 映射** 与 **Playwright**（静态 HTML 0/23）；10 家仍 `needs_orgid_mapping`。
- 所有状态为 **`testing / partial`**，**不写 `verified`**，不代表长期稳定可用。

**后续限制：** 暂不全量 Playwright；先补 orgId 映射与抽取规则稳定性，再考虑数据库接入。

### 当前结论

CNINFO 不应只被视为年报 PDF 下载源，而应作为动态平台第一优先级官方数据源。当前已经验证的是年报 PDF 抽取；**P0 小样本验证（最新公告、PDF 元数据、F10 公司资料）已完成**，结论为部分可用、部分待映射处理。下一步应补全 orgId 映射、BSE 公告代码回退、F10 抽取稳定性，再考虑 P1 栏目与数据库接入。

完整盘点见 [plans/cninfo_data_source_value_inventory.md](../plans/cninfo_data_source_value_inventory.md)。

---

## 预留数据源（待接入）

以下数据源已在 [config/sources.yaml](../config/sources.yaml) 中定义框架，或在路线图中规划，**尚未接入抽取 pipeline**。

| 数据源 | 类别 | 预期用途 | 状态 | 备注 |
|---|---|---|---|---|
| 上交所 / 深交所公告 | 交易所 | 临时公告、重大事项 | 待接入 | collectors/ 有框架 |
| 公司官网 IR 页面 | 官网 | 投资者关系、业务介绍 | 待接入 | 需 BrowserUser |
| 上证 e 互动 / 深交所互动易 | 互动 | 投资者问答 | 待接入 | 需 BrowserUser |
| 政府采购网 | 政采 | 中标信息、合同 | 待接入 | 公开但需搜索 |
| 国家知识产权局 | 专利 | 专利数量、技术方向 | 待接入 | 公开 API 有限 |
| 商标局 | 商标 | 商标注册信息 | 待接入 | |
| 新闻 / 舆情 | 媒体 | 事件信号（标题+链接） | 待接入 | 不存全文 |
| 企查查 / 天眼查 | 商业 | 工商信息、关联关系 | 待评估 | 付费/授权限制 |
| 雪球 / 股吧 / 微博 | 社交 | 舆情信号 | 待评估 | 仅 metadata |
| Tushare / AkShare | 金融 API | 行情、财务指标 | 待评估 | 授权/许可不确定 |
| BrowserUser 可访问网页 | 智能体 | 上述复杂/交互页面的补充 | 规划中 | 见 v0.5 plan |

**接入原则**：

- 先验证公开可获取性，再写 collector
- 每条记录保留 `source_url` + 获取时间
- 强反爬/付费/需登录源：记录为限制，不绕过
- BrowserUser 仅作补充，不替代 CNINFO 年报主链路
