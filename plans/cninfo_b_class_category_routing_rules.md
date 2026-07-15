# CNINFO B 类 Category Routing Rules

_最后更新：2026-07-05_

> **配置：** [config/cninfo_announcement_categories.yaml](../config/cninfo_announcement_categories.yaml)  
> **验证：** [cninfo_b_class_validation_design.md](cninfo_b_class_validation_design.md)  
> **Registry：** [config/cninfo_b_class_source_registry_draft.yaml](../config/cninfo_b_class_source_registry_draft.yaml)

---

## 1. 目的

在 B 类 document corpus 中，**title filter 不是简单删除**，而是将公告标题 **路由** 到正确的 `source_id` 与 `document_type`。

Phase 1 为 **定期报告 effective found** 定义的 exclusion 列表，在 B 类整体语料视角下应理解为：

- 对 `cninfo_periodic_report_pdf`：**排除**（不得计为年报/季报全文）；
- 对其他 B source：**可能为正向匹配**（问询函、说明会等）；
- 对 `cninfo_general_announcement_pdf`：**保留** 被 periodic 踢出的标题并 **重新分类**。

---

## 2. Periodic report routing

**目标 source：** `cninfo_periodic_report_pdf`  
**category：** `periodic_report`

### 2.1 准入条件（须同时满足）

1. 标题命中对应 `document_type` 的 `positive_patterns`；
2. `parsed_report_period == expected_period`（expected-period validation）；
3. **未**命中 `exclusion_patterns`；
4. `pdf_url` 可用。

### 2.2 必须拒绝为定期报告全文

以下不得作为 `annual_report` / `semi_annual_report` / `quarterly_report_*` 的 effective found：

- 摘要、解读  
- 问询函、回复公告、监管问询函、关注函  
- 说明会、业绩说明会、投资者说明会、交流会  
- 提示性公告、披露提示性公告、预告公告  
- 延期披露、关于延期披露  
- 关于披露（交叉披露其他公司报告）

---

## 3. Excluded from periodic, retained in corpus

| 被 periodic 排除的标题类型 | 建议路由 | document_type |
|---------------------------|----------|---------------|
| 问询函 / 回复公告 / 关注函 | `cninfo_inquiry_reply_pdf` | `inquiry_reply` / `regulatory_inquiry` |
| 说明会 / 业绩说明会 / 投资者说明会 / 投资者关系活动记录表 | `cninfo_meeting_notice_pdf` | `meeting_notice` / `investor_relations_activity` |
| 延期披露 / 关于延期披露 | `cninfo_general_announcement_pdf` | `announcement`（disclosure_related） |
| 摘要 / 解读 | `cninfo_general_announcement_pdf` | `announcement` / `other`（非 report 主 corpus） |
| 董事会决议 / 股东（大）会通知·决议·召开公告（非说明会；不含法律意见书/会议材料；「股东会」=「股东大会」同义） | `cninfo_general_announcement_pdf` | `board_resolution` / `shareholder_meeting_material` |
| 法律意见书 / 法律意见（会议与非会议：增持、差异化分红、可转债等；B-FM-26） | `cninfo_general_announcement_pdf` | `announcement`（勿落 `other`；勿抬成会议材料） |
| 核查意见（保荐机构募资置换/限售流通等；B-FM-27） | `cninfo_general_announcement_pdf` | `announcement`（勿落 `other`） |
| 保荐书 / 权益变动报告书（上市保荐书、简式权益变动等；B-FM-28） | `cninfo_general_announcement_pdf` | `announcement`（勿落 `other`） |
| 受托管理事务报告 / 跟踪评级报告（债券受托管理、主体/债项跟踪评级；B-FM-29） | `cninfo_general_announcement_pdf` | `announcement`（勿落 `other`） |
| 持续督导年度报告书 / 持续督导培训情况的报告（保荐机构督导材料；B-FM-30） | `cninfo_general_announcement_pdf` | `announcement`（勿进 `annual_report`；勿落 `other`） |
| 非标准审计意见消除专项说明 / 前次募集资金使用情况报告（B-FM-32；窄 pattern，不泛化「专项说明」） | `cninfo_general_announcement_pdf` | `announcement`（勿落 `other`） |
| 独立董事专门会议的审核意见 / 独立董事提名人声明与承诺（B-FM-33；窄 pattern，勿裸「审核意见」） | `cninfo_general_announcement_pdf` | `announcement`（勿落 `other`） |
| 资产评估说明 / 独立审计报告（B-FM-34；窄 pattern，勿裸「说明」；含「年度报告」/「年报」的审计报告仍 periodic） | `cninfo_general_announcement_pdf` | `announcement`（勿落 `other`） |
| 买卖公司股票的自查报告 / 员工持股计划（B-FM-35；窄 pattern，勿裸「自查报告」；不硬推章程/制度/薪酬） | `cninfo_general_announcement_pdf` | `announcement`（勿落 `other`） |
| 公司章程 / 募集资金管理制度（B-FM-36；窄 pattern，勿裸「章程」/「管理制度」；一般管理制度/薪酬/名单/简报/ESG 可仍 other） | `cninfo_general_announcement_pdf` | `announcement`（勿落 `other`） |
| 独立非执行董事工作制度 / 总经理工作细则（B-FM-37；窄 pattern，勿裸「工作制度」/「工作细则」；一般管理制度/薪酬/名单/简报/ESG 可仍 other） | `cninfo_general_announcement_pdf` | `announcement`（勿落 `other`） |
| 货币资金管理制度 / 对外担保管理制度（B-FM-38；窄 pattern，勿裸「管理制度」；分子公司/薪酬/名单/简报/ESG 可仍 other；≠对外担保情况简报） | `cninfo_general_announcement_pdf` | `announcement`（勿落 `other`） |
| 子公司管理制度 / 薪酬与考核方案（B-FM-39；窄 pattern，勿裸「管理制度」/「薪酬」；名单/简报/ESG/对外担保情况简报可仍 other） | `cninfo_general_announcement_pdf` | `announcement`（勿落 `other`） |

**原则：** `retrieval_status=title_excluded` 仅表示 **未进入 periodic_report**；应尝试次级路由，并设 `classification_status=title_excluded_from_periodic_but_routed` 或 `ambiguous`。

---

## 4. Priority order

标题分类 **按顺序** 匹配，先命中先路由（长短语优先）：

| 优先级 | 规则组 | route_to |
|--------|--------|----------|
| 1 | inquiry / reply patterns（问询函、回复公告、关注函、回复函） | `cninfo_inquiry_reply_pdf` |
| 2 | meeting / IR patterns（业绩说明会、投资者说明会、说明会、交流会、投资者关系活动记录表） | `cninfo_meeting_notice_pdf` |
| 3 | periodic report exact patterns（年度报告、半年度报告、第一/三季度报告全文等）+ period match + **无** exclusion | `cninfo_periodic_report_pdf` |
| 4 | summary / preview / delayed disclosure（摘要、预告、延期披露） | `cninfo_general_announcement_pdf`（子类型见 §3） |
| 5 | general announcement fallback（公告、决议、股东大会/股东会、董事会、监事会等） | `cninfo_general_announcement_pdf` |

**注意：** 优先级 1–2 必须在优先级 3 之前，避免「关于年报的问询函回复」被「报告」子串误路由到 periodic。

---

## 5. Ambiguous title handling

| 情况 | 处理 |
|------|------|
| 同时命中 periodic positive 与 exclusion | **exclusion 优先** → 不进入 periodic；尝试 1–2 或 4–5 |
| 同时命中 inquiry 与 meeting 关键词 | `classification_status=ambiguous`；保留 `raw title` |
| 标题含「报告」但为问询函回复 | 优先级 1 → `inquiry_reply`；`false_positive_reason=inquiry_reply_as_report` 若曾误进 periodic |
| 无规则命中 | `general_announcement` fallback + `document_type=other` + `rule_confidence=low` |
| 不确定 | **不强行归类**；`classification_status=ambiguous` |

---

## 6. Examples

| # | 示例标题（示意） | route_to | document_type | 备注 |
|---|-----------------|----------|---------------|------|
| 1 | 平安银行股份有限公司2024年年度报告 | `cninfo_periodic_report_pdf` | `annual_report` | period=2024 |
| 2 | 平安银行股份有限公司2024年半年度报告 | `cninfo_periodic_report_pdf` | `semi_annual_report` | |
| 3 | 某某公司2024年第一季度报告全文 | `cninfo_periodic_report_pdf` | `quarterly_report_q1` | |
| 4 | 某某公司2024年第三季度报告 | `cninfo_periodic_report_pdf` | `quarterly_report_q3` | |
| 5 | 关于2024年年度报告的补充公告 | `cninfo_general_announcement_pdf` | `announcement` | 非全文；含「报告」但非 periodic |
| 6 | 深圳证券交易所年报问询函 | `cninfo_inquiry_reply_pdf` | `regulatory_inquiry` | periodic exclusion |
| 7 | 关于深圳证券交易所问询函的回复公告 | `cninfo_inquiry_reply_pdf` | `inquiry_reply` | |
| 8 | 2024年度业绩说明会投资者关系活动记录表 | `cninfo_meeting_notice_pdf` | `investor_relations_activity` | periodic exclusion |
| 9 | 关于召开2024年年度股东大会的通知 | `cninfo_general_announcement_pdf` | `shareholder_meeting_material` | 非说明会 |
| 9b | 2025年第二次临时股东大会决议公告 | `cninfo_general_announcement_pdf` | `shareholder_meeting_material` | B-FM-18；非董事会决议 |
| 9c | 关于召开2025年第二次临时股东大会的公告 | `cninfo_general_announcement_pdf` | `shareholder_meeting_material` | B-FM-18；无「通知」字样 |
| 9d | 2025年第五次临时股东会决议公告 | `cninfo_general_announcement_pdf` | `shareholder_meeting_material` | B-FM-20；「股东会」同义 |
| 9e | 关于召开2025年第二次临时股东会的通知 | `cninfo_general_announcement_pdf` | `shareholder_meeting_material` | B-FM-20；简称通知 |
| 10 | 关于延期披露2024年年度报告的公告 | `cninfo_general_announcement_pdf` | `announcement` | `delayed_disclosure_notice` |

---

## 7. 与 D 类的边界（路由层）

| 标题/数据 | B 类路由 | 非 B 类 |
|-----------|----------|---------|
| 年报 PDF 标题 | `cninfo_periodic_report_pdf` | — |
| 限售解禁 **表格 JSON row** | — | D 类 `restricted_shares_unlock` |
| 预约披露 **schedule row** | — | D 类 `disclosure_schedule` |
| 异常交易 **marketList row** | — | D 类 `abnormal_trading` |

---

## 8. 配置同步

本规则与以下文件 **须保持一致**：

- `config/cninfo_announcement_categories.yaml` — `positive_patterns` / `exclusion_patterns` / `route_to`
- `config/cninfo_b_class_source_registry_draft.yaml` — 各 source 的 title patterns
- `lab/validate_cninfo_report_coverage.py` — Phase 1 `OFFICIAL_REPORT_TITLE_EXCLUSIONS`（**只读继承，本阶段不改脚本**）

---

## 9. 当前不做

- 不运行在线分类；不请求 CNINFO  
- 不下载 PDF  
- 不写 verified  
- 不修改 Phase 1 脚本  

---

## 10. 产物索引

| 文档 | 说明 |
|------|------|
| [cninfo_b_class_validation_design.md](cninfo_b_class_validation_design.md) | 三种 validation 口径 |
| [cninfo_b_class_source_registry_design.md](cninfo_b_class_source_registry_design.md) | B 类 registry |
