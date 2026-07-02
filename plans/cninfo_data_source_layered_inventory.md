# CNINFO 数据源分层表与统一验证口径（Era C 权威文档）

_最后更新：2026-07-02_

> **本文件是 Era C 后续数据源分类与验证口径的权威文档。** 基于 CNINFO 官网人工观察、既有小样本验证结果与 [cninfo_announcement_acquisition_mechanism_summary.md](../outputs/validation/cninfo_announcement_acquisition_mechanism_summary.md) 的机制判断整理。
>
> **与旧文档的关系：**
> - 栏目细节、P0 验证模板、事件类型池 → 见 [cninfo_data_source_value_inventory.md](cninfo_data_source_value_inventory.md)（保留，不重复维护）。
> - **分类与验证口径以本文件 A–F 分层为准**；旧文档中的 P0/P1/P2 优先级与「单一 success rate」口径**不再作为 Era C 主判断标准**。
>
> **边界：** 本文档只做分类与验证口径设计；不写代码、不跑脚本、不联网、不接数据库/MinIO；`recommended_status` **不写 `verified`**。

---

## 1. 分层目的

不再把所有 CNINFO 数据混在同一个「P1 success rate / 随机公司覆盖率」里判断稳定性，而是：

1. 先区分哪些数据**像年报一样**可稳定获取（定期披露 + 标题稳定 + PDF）；
2. 再区分哪些数据**能找到**，但不是固定周期、固定 PDF 或固定字段；
3. **稳定数据先打通渠道**；非稳定数据后续单独研究获取方式。

---

## 2. 总体分层（A–F）

| 层级 | 数据源类型 | 典型例子 | 官网形态 | 是否像年报一样稳定 | 推荐验证优先级 |
|---|---|---|---|---|---|
| **A** | 类年报 PDF 文档流 | 年报、半年报、一季报、三季报、IPO 招股书 | 公告 PDF / 报告 PDF | **高**（最接近年报 pipeline） | **第一优先** |
| **B** | 公告 PDF 事件流 | 董事会、分红、增发、风险提示、退市等 | 公告 PDF | **中**（有 PDF，非每家公司固定发生） | 第二优先 |
| **C** | F10 / 公司资料表格 | 公司资料、概况、股本股东、治理、财务摘要 | 前端表格 / JS 页面 | **中**（依赖 stockCode + orgId） | 第二优先 |
| **D** | 固定表格资讯 / 市场行为 | 预约披露、融资融券、大宗交易、限售解禁、公开信息 | 表格 / 日期型页面 | **较高**（字段固定，可能比事件公告更稳） | **第一优先**（非 PDF 前沿） |
| **E** | 数据服务平台 / API / 商业服务 | webapi、数据 API、数据商城、智能公告 | JS 应用 / 数据服务 | **不确定**（可能权限/商业化） | 暂缓（仅可达性） |
| **F** | 问答 / 服务类入口 | 互动易、网络投票、调研、投资者问答 | 问答流 / 服务页面 | **低**（文本线索，非固定字段） | 第三优先（暂缓） |

---

## 3. 统一验证记录字段（所有层级共用）

每个数据源验证完成后，summary 顶部必须写明：

| 字段 | 说明 |
|---|---|
| `layer` | A / B / C / D / E / F |
| `source_name` | 数据源名称（如「年报」「融资融券」） |
| `denominator_definition` | 分母如何定义 |
| `numerator_definition` | 分子如何定义 |
| `success_metric` | 成功指标名称与公式 |
| `success_value` | 本次验证数值 |
| `recommended_status` | `candidate` / `testing` / `partial` / `postponed` / `rejected`（**不写 `verified`**） |
| `failure_reasons` | 失败原因分类 |
| `evidence_available` | 是否可保留 source_url / PDF / 快照 |
| `next_action` | 下一步 |

---

## 4. A 类：类年报 PDF 文档流

### 4.1 类级验证口径（强制）

| 项 | 定义 |
|---|---|
| **数据形态** | 公告 PDF / 定期报告 PDF；经 `hisAnnouncement/query` 或等价公告检索接口 |
| **典型字段** | `announcement_title`、`publish_time`、`pdf_url`、`report_period`、`content_hash`（可选） |
| **是否像年报一样稳定** | **是**——定期披露、标题模式相对稳定、每家公司应按报告期存在 |
| **推荐验证方式** | **per-company coverage**：`company × report_period`；多 strategy 仅作内部回退，**一份期望报告只计一行** |
| **分母** | mapped 样本公司 × 期望报告期集合（如近 2 个会计年度的年报、半年报、Q1、Q3 各 1 份） |
| **分子** | 命中目标报告且 `pdf_url` 非空、标题匹配报告类型、`report_period` 解析与期望一致（非 `unknown`） |
| **成功指标** | **coverage%** = 分子 / 分母 × 100%；并按 `report_type`、板块拆分 |
| **recommended_status 可用值** | `candidate`（未跑 coverage）/ `testing`（已跑小样本）/ `partial`（部分报告类型或板块缺口） |

> **重要：旧口径作废说明**  
> [cninfo_report_announcement_validation_summary.md](../outputs/validation/cninfo_report_announcement_validation_summary.md) 的 `success 368/780` 按 **(公司 × report_type × query_strategy)** 计行，同一公司同一份报告可能 1 success + 3 failed，**不能作为 A 类最终 coverage 结论**。该文件保留为**阶段快照**；Phase 1 将用 `validate_cninfo_report_coverage.py` 重算 per-company coverage。

### 4.2 数据源清单

| 数据源 | 数据形态 | 典型字段 | 是否像年报一样稳定 | 推荐验证方式 | 分母 | 分子 | 成功指标 | 当前状态 |
|---|---|---|---|---|---|---|---|---|
| 年报 | 公告 PDF | 标题、发布时间、PDF URL、报告期 | 高 | per-company coverage | 公司 × 期望年报期 | 命中且 PDF+报告期正确 | coverage% | `testing`（旧快照有信号，待 coverage 重算） |
| 半年报 | 公告 PDF | 同上 | 高 | 同上 | 公司 × 期望半年报期 | 同上 | coverage% | `testing`（待 coverage 重算） |
| 一季报 | 公告 PDF | 同上 | 高 | 同上 | 公司 × 期望 Q1 期 | 同上 | coverage% | `testing`（待 coverage 重算） |
| 三季报 | 公告 PDF | 同上 | 高 | 同上 | 公司 × 期望 Q3 期 | 同上 | coverage% | `testing`（待 coverage 重算） |
| IPO 招股书 | PDF 文档 | 标题、公司、披露时间、PDF URL | 中高（标题稳定、有 PDF，但非周期性） | **known-event benchmark**（已知 IPO 公司子集） | 已知有招股书的公司数 | 检索到匹配 PDF | 命中率% | `candidate` |
| 业绩快报 | 公告 PDF | 标题、发布时间、PDF URL | 中（有报告属性，非所有公司都有） | 待裁定：若偏事件则归 B | — | — | — | `candidate`（**暂列候选，需判断是否归入 B 类事件流**） |
| 业绩预告 | 公告 PDF | 标题、发布时间、PDF URL | 中（标题较稳，非固定披露） | 待裁定：更偏 B 类事件 | — | — | — | `candidate`（**暂列候选，需判断是否归入 B 类事件流**） |

### 4.3 A 类验证标准（对齐年报 pipeline）

- 是否找到目标 PDF；
- `pdf_url` 是否可用（HTTP 可达，本阶段可不下载正文）；
- 标题是否匹配报告期 / 报告类型；
- 是否可解析 `report_period`；
- 是否可进入未来 `raw_file` / `document` 候选层（仅作设计依据，当前不入库）。

---

## 5. B 类：公告 PDF 事件流

### 5.1 类级验证口径（强制）

| 项 | 定义 |
|---|---|
| **数据形态** | 临时公告 / 事件公告 PDF；多经 `hisAnnouncement/query`，宜配合 CNINFO 官方 **`category` 分类码** |
| **典型字段** | `announcement_title`、`publish_time`、`pdf_url`、`announcement_type`、规则分类置信度 |
| **是否像年报一样稳定** | **否**——大多有 PDF，但**不是每家公司每年都有**；随机公司覆盖率**无意义** |
| **推荐验证方式** | ① **corpus 可得性**：在时间窗内按 `category` 拉公告语料，看是否非空、关键字段是否可得、规则分类置信度；② **known-event benchmark**：对低频事件（增发、配股、股权激励、退市等）只选**已知发生过该事件**的公司 |
| **分母（corpus）** | 选定时间窗内、该 `category` 下期望能拉到的公告条数下限（或样本公司 corpus 是否非空） |
| **分子（corpus）** | 实际返回且含标题+时间+PDF 的条数；附 high/medium/low 规则置信度分布 |
| **分母（known-event）** | 人工/外部确认的「该公司确有该事件」公司数 |
| **分子（known-event）** | 检索并规则匹配到对应公告的公司数 |
| **成功指标** | corpus：**语料非空率**、**字段可得性%**、**规则 high+medium 占比**；known-event：**命中率%** |
| **recommended_status 可用值** | `candidate` / `testing` / `partial` |

> **禁止口径：** 不得用「30 家公司 × 14 类公告的 success rate」判断 B 类稳定性（见 [cninfo_announcement_acquisition_mechanism_summary.md](../outputs/validation/cninfo_announcement_acquisition_mechanism_summary.md)：瓶颈在查询覆盖，非仅关键词）。

### 5.2 数据源清单

| 数据源 | 官网入口 | 数据形态 | 是否固定发生 | 推荐处理方式 | 当前状态 |
|---|---|---|---|---|---|
| 董事会 | 董事会 | 公告 PDF | 较常见，非固定周期 | corpus + 规则分类 | `partial` |
| 监事会 | 监事会 | 公告 PDF | 较常见，当前命中低 | 调整查询 / 长窗口 | `candidate` |
| 股东会 / 股东大会 | 股东会 | 公告 PDF | 较常见 | corpus + 规则分类 | `testing` |
| 权益分派 / 分红 | 权益分派 | 公告 PDF | 较常见，非每家都有 | corpus + 时间窗口 | `testing` |
| 日常经营 | 日常经营 | 公告 PDF | 事件型 | 事件线索 | `candidate` |
| 公司治理 | 公司治理 | 公告 PDF | 事件/治理型 | 事件候选 | `candidate` |
| 中介报告 | 中介报告 | PDF | 辅助证据 | 证据层候选 | `candidate` |
| 首发 | 首发 | PDF | 发行事件 | 与 IPO 联动 | `candidate` |
| 增发 | 增发 | PDF | 低频 | known-event benchmark | `candidate` |
| 股权激励 | 股权激励 | 公告 PDF | 中低频 | known-event + 规则 | `partial` |
| 配股 | 配股 | PDF | 低频 | known-event benchmark | `candidate` |
| 解禁 | 解禁 | 公告 PDF | 事件型 | 更建议结合 D 类表格入口 | `candidate` |
| 公司债 | 公司债 | 公告 PDF | 融资事件 | 后续单独验证 | `candidate` |
| 可转债 | 可转债 | 公告 PDF | 融资事件 | 后续单独验证 | `candidate` |
| 其他融资 | 其他融资 | 公告 PDF | 低频 | known-event benchmark | `candidate` |
| 股权变动 | 股权变动 | 公告 PDF | 事件型 | 事件线索 | `candidate` |
| 补充更正 | 补充更正 | 公告 PDF | 辅助公告 | 文档修订线索 | `candidate` |
| 澄清致歉 | 澄清致歉 | 公告 PDF | 低频/风险 | 风险线索 | `candidate` |
| 风险提示 | 风险提示 | 公告 PDF | 风险事件 | 事件线索 | `candidate` |
| 特别处理和退市 | 特别处理和退市 | 公告 PDF | 低频但重要 | known-event / 风险事件 | `candidate` |
| 退市整理期 | 退市整理期 | 公告 PDF | 低频但重要 | known-event / 风险事件 | `candidate` |

---

## 6. C 类：F10 / 公司资料表格

### 6.1 类级验证口径（强制）

| 项 | 定义 |
|---|---|
| **数据形态** | 个股 F10 / 公司要览；前端 HTML 表格，常需 JS 渲染 |
| **典型字段** | `stock_short_name`、`exchange`、`board`、`industry`、`company_profile`、`registered_address`、`website`、`board_secretary` 等 |
| **是否像年报一样稳定** | **部分**——字段相对稳定，但**关键在 orgId mapping 与页面可达性**，非关键词检索 |
| **推荐验证方式** | stockCode + orgId 映射 → 页面可达性 → 静态 HTML / Playwright 字段提取；**字段可得性%** |
| **分母** | mapped 样本公司数 × 期望字段集合（按标签页分组） |
| **分子** | 成功提取且非空、语义可解释的字段数 |
| **成功指标** | **字段可得性%** = 分子 / 分母；另记 **reachability%**（页面是否打开） |
| **recommended_status 可用值** | `candidate` / `testing` / `partial` |

### 6.2 数据源清单（F10 标签页）

| 数据源 | 数据形态 | 主要内容 | 当前难点 | 当前状态 |
|---|---|---|---|---|
| 公司基本资料 | F10 表格 | 简称、行业、注册地址、电话、邮箱、董秘 | JS 渲染 / orgId | `partial`（Playwright 22/30） |
| 公司概况 | F10 表格 | 主营业务、公司简介 | JS 渲染 | `testing` |
| 股本股东 | F10 标签页 | 股本、股东、持股 | 入口与字段待确认 | `candidate`（needs_entry_discovery） |
| 治理结构 | F10 标签页 | 董事、高管、治理信息 | 入口与字段待确认 | `candidate`（needs_entry_discovery） |
| 财务摘要 | F10 标签页 | 财务指标摘要 | 入口与字段待确认 | `candidate`（needs_entry_discovery） |

---

## 7. D 类：固定表格资讯 / 市场行为数据

### 7.1 类级验证口径（强制）

| 项 | 定义 |
|---|---|
| **数据形态** | 独立表格页 / 日期维度列表；**非** `hisAnnouncement/query` 公告流 |
| **典型字段** | 因源而异（见下表）；共同点是**列名相对固定** |
| **是否像年报一样稳定** | **较高**——按交易日或披露计划更新，字段结构比随机事件公告更稳 |
| **推荐验证方式** | 浏览器 DevTools 抓取 XHR → 写入 `config/cninfo_table_sources.yaml` → config 驱动验证脚本；**字段可得性%** + **入口稳定性** |
| **分母** | 该数据源定义的期望字段集合（或期望返回行数 > 0） |
| **分子** | HTTP 成功且返回结构化行中，非空且可解析的字段数 |
| **成功指标** | **字段可得性%**；可选 **row_count > 0 比例** |
| **recommended_status 可用值** | `candidate` / `testing` / `partial` |

### 7.2 数据源清单

| 数据源 | 数据形态 | 可能字段 | 推荐优先级 | 当前状态 |
|---|---|---|---|---|
| 预约披露 | 表格 / 日期型 | 公司、报告类型、预约披露日期 | 第一优先 | `candidate` |
| 公开信息 / 异常交易 | 表格 | 代码、简称、公开原因、日期 | 第一优先 | `candidate` |
| 融资融券 | 表格 | 融资余额、买入额、融券余量、余额等 | 第一优先 | `candidate` |
| 大宗交易 | 表格 | 成交价、成交量、买卖营业部 | 第一优先 | `candidate` |
| 限售解禁 | 表格 | 公告日期、解禁数量、比例、可流通量 | 第一优先 | `candidate` |
| 深市日历 | 日历型 | 股东会、分红登记日、除权除息日等 | 第一/二优先 | `candidate` |
| 终止 / 退市 | 表格 / 事件页 | 终止上市、退市状态、日期 | 第二优先 | `candidate` |
| 股权质押 | 表格 / 查询 | 质押股数、比例、质押方、日期 | 第二优先 | `candidate` |
| 股东数据 | 表格 / 查询 | 股东名称、持股数量、比例、报告期 | 第二优先 | `candidate` |
| 股东增减持 | 表格 / 查询 | 增减持主体、数量、比例、日期 | 第二优先 | `candidate` |
| 高管持股 | 表格 / 查询 | 高管名称、持股数量、变动日期 | 第二优先 | `candidate` |
| 基金持股 | 表格 / 查询 | 基金名称、持股公司、持股比例 | 第二优先 | `candidate` |
| IPO 查询 | 表格 / 查询 | IPO 公司、阶段、发行信息 | 第二优先 | `candidate` |

---

## 8. E 类：数据服务平台 / API / 商业服务

### 8.1 类级验证口径（强制）

| 项 | 定义 |
|---|---|
| **数据形态** | webapi.cninfo.com.cn、数据 API、数据商城、智能公告、数据平台等 |
| **典型字段** | 不适用（本层不采业务数据） |
| **是否像年报一样稳定** | **不确定**——可能涉及登录、权限、商业化 |
| **推荐验证方式** | **仅可达性 / 权限三态判断**：`public_access` / `login_required` / `permission_or_commercial` |
| **分母** | 待测入口数 |
| **分子** | 明确判定为三态之一的入口数 |
| **成功指标** | 可达性分类完成率（非覆盖率） |
| **recommended_status 可用值** | `candidate` / `postponed` / `rejected`（若明确商业化且不可用） |

### 8.2 数据源清单

| 数据源 | 数据形态 | 风险 | 推荐处理 | 当前状态 |
|---|---|---|---|---|
| webapi.cninfo.com.cn | JS / SPA | 权限 / 商业服务 | 仅可达性与权限判断 | `postponed` |
| 数据 API | 数据服务入口 | 可能商业化 | 暂缓 | `postponed` |
| 数据商城 | 数据服务入口 | 可能商业化 | 暂缓 | `postponed` |
| 智能公告 | 数据服务入口 | 可能商业化 | 暂缓 | `postponed` |
| 数据平台 | 数据服务入口 | 权限不明 | 暂缓 | `postponed` |

**红线：** 不绕过权限；不作为当前稳定采集主线。

---

## 9. F 类：问答 / 服务类入口

### 9.1 类级验证口径（强制）

| 项 | 定义 |
|---|---|
| **数据形态** | 互动易、网络投票、调研、投资者问答等问答流 / 服务页 |
| **典型字段** | 问题、回复、时间（若可结构化） |
| **是否像年报一样稳定** | **否**——更像文本线索，非固定字段数据源 |
| **推荐验证方式** | **暂缓**；仅记录可达性与「是否结构化文本」 |
| **分母** | — |
| **分子** | — |
| **成功指标** | 暂不设覆盖率；仅 `reachable: yes/no` |
| **recommended_status 可用值** | `postponed` / `candidate` |

### 9.2 数据源清单

| 数据源 | 数据形态 | 推荐处理 | 当前状态 |
|---|---|---|---|
| 互动易 | 问答流 | 未来语料 / RAG 线索 | `postponed` |
| 网络投票 | 服务页面 | 治理辅助，暂缓 | `postponed` |
| 调研 | 公告 / 问答 / 文本 | 文本线索 | `postponed` |
| 投资者问答 | 问答流 | 未来语义检索 | `postponed` |

---

## 10. Phase 推进顺序（不要同时展开）

| Phase | 内容 | 状态 |
|---|---|---|
| **Phase 0** | 固化本 A–F 分层表与统一验证口径 | **已完成**（本文档） |
| **Phase 1** | 新建 `validate_cninfo_report_coverage.py`，重算 A 类 per-company coverage | **下一步** |
| **Phase 2** | D 类：手动抓 endpoint → `cninfo_table_sources.yaml` → 表格验证脚本 | 待 Phase 1 后 |
| **Phase 3** | B 类：官方 `category` 码 + corpus / known-event 口径改造 | 待 Phase 2 后 |
| **Phase 4** | C 类 F10 标签页；E 类可达性三态；F 类暂缓记录 | 待 Phase 3 后 |

---

## 11. 相关文档与产物

| 文档 / 产物 | 角色 |
|---|---|
| 本文档 | **分类 + 验证口径权威** |
| [cninfo_data_source_value_inventory.md](cninfo_data_source_value_inventory.md) | 栏目细节、P0 模板、事件/证据类型（交叉引用） |
| [eraC_execution_plan.md](eraC_execution_plan.md) | Composer / 便宜模型执行清单 |
| [cninfo_report_announcement_validation_summary.md](../outputs/validation/cninfo_report_announcement_validation_summary.md) | **阶段快照**（非最终 A 类 coverage 结论） |
| [cninfo_announcement_acquisition_mechanism_summary.md](../outputs/validation/cninfo_announcement_acquisition_mechanism_summary.md) | B 类机制：identity → retrieval → rule → semantic |
| [cninfo_capability_final_summary.md](../outputs/validation/cninfo_capability_final_summary.md) | Era C 阶段性总览（待各 Phase 完成后更新） |
