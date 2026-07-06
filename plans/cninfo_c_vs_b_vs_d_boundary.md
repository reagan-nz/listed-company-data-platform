# CNINFO C 类与 B / D 类边界

_最后更新：2026-07-05_

> **上级：** [cninfo_data_source_layered_inventory.md](cninfo_data_source_layered_inventory.md)  
> **C 类设计：** [cninfo_c_class_f10_source_discovery_design.md](cninfo_c_class_f10_source_discovery_design.md)  
> **B/D 边界（既有）：** [cninfo_b_vs_d_class_boundary.md](cninfo_b_vs_d_class_boundary.md)

---

## 1. 核心区别

| 维度 | **B 类** | **C 类** | **D 类** |
|------|----------|----------|----------|
| **数据形态** | 文档 — PDF / 公告全文 | Profile snapshot — F10 / 公司资料 | 固定表格 JSON rows |
| **核心对象** | `document` → `chunk` → `citation` | `company_profile_snapshot` | `d_company_event` / `d_company_metric_*` |
| **典型入口** | `hisAnnouncement/query` | F10 标签页 / profile API | `data20/*` 等 |
| **时间语义** | 披露日 + 文档版本 | 画像快照时点 | 事件日 / 交易日 / 报告期 |
| **下游用途** | RAG、citation、证据引用 | company Wiki、company card | timeline、alerts、screening |
| **验证口径** | corpus retrieval、known-document | field presence%、known-company | field availability%、endpoint 稳定 |
| **Registry layer** | `document_corpus` | `company_profile` | `company_event` / `company_metric_*` |

**一句话：** B 类 **读文档**；C 类 **读画像**；D 类 **读表格行**。

---

## 2. 举例

### B 类（document corpus）

| 示例 | document_type |
|------|---------------|
| 平安银行 2024 年年度报告 PDF | `annual_report` |
| 交易所问询函回复公告 | `inquiry_reply` |
| 业绩说明会公告 | `meeting_notice` |
| 投资者关系活动记录表 | `investor_relations_activity` |

### C 类（company profile snapshot）

| 示例 | source_category |
|------|-----------------|
| 公司简介、主营业务段落（F10 表格字段） | `business_scope` / `basic_profile` |
| 高管列表（姓名、职务、任期） | `executive_profile` |
| 注册资本、上市日期 | `basic_profile` |
| 十大股东 / 十大流通股东 snapshot | `shareholder_profile` |
| 总股本 / 流通股本结构表 | `share_capital_profile` |
| 电话、邮箱、注册地址 | `contact_profile` |

### D 类（fixed-table event / metric）

| 示例 | source_id（示意） |
|------|-------------------|
| 大宗交易 row | `block_trade` |
| 股权质押 row | `equity_pledge` |
| 融资融券日度 row | `margin_trading` |
| 股东人数变化 row | `shareholder_data` |
| 高管持股变动 row | `management_share_change`（若注册） |
| 限售解禁 row | `restricted_shares_unlock` |

---

## 3. 不要混淆

| 反模式 | 正确归类 |
|--------|----------|
| 高管 **持股变动** 公告 / 表格行 | **D 类 event**（动态变动），不是 C 类 `executive_profile` 静态名单 |
| 投资者关系活动 **记录表** PDF | **B 类 document**（`investor_relations_activity`），不是 C 类 contact profile |
| **股东人数变化** 按报告期 metric | **D 类** `shareholder_data`，不是 C 类 top shareholder snapshot |
| **十大股东** F10 表格 snapshot | **C 类** `shareholder_profile` |
| 年报 PDF 中的「公司简介」章节 | **B 类** 文本证据；可 **补充** C 类，但不替代 F10 snapshot source |
| 业绩预告 **公告** | B 类 `announcement`；不是 D 类 metric（除非另有固定表 API） |
| F10 **财务摘要** 指标表 | C 类 profile 候选；不是 A 类 report PDF retrieval |
| 把 C 类 `raw_record_json` 直接 chunk 进 RAG | 应走 B 类 parse pipeline；C 类字段用于 Wiki card |

---

## 4. 产品用途

| 层 | 产品用途 | 典型 UI |
|----|----------|---------|
| **B** | citation / RAG / evidence | 公告原文、引用片段、问答证据 |
| **C** | company wiki profile / company card / static facts | 公司主页侧栏、基础资料卡 |
| **D** | timeline / alerts / screening | 事件流、预警、量化筛选 |

---

## 5. 连接方式（设计层）

跨层关联建议键：

| 关联键 | B | C | D |
|--------|---|---|---|
| `company_code` | ✓ | ✓ | ✓ |
| `org_id` | ✓ | ✓ | 部分源 |
| 披露 / 报告日 | `announcement_date` | `snapshot_date` | `event_date` / `trade_date` |
| 人员名 | 公告正文 | `executive_profile.person_name` | event 主体 |
| 股东名 | 公告正文 | `shareholder_profile` | `shareholder_change` |

**原则：** 允许 **link** 与 **交叉验证**；禁止 **合并 registry** 或 **共用 schema 文件**。

---

## 6. Era C Phase 状态（2026-07-05）

| 层 | Phase 状态 |
|----|------------|
| A | Phase 1 收口，`testing_stable_sample` 口径 |
| B | corpus 设计 + live metadata v1（5 ready case） |
| C | **本批启动设计草案**；endpoint 未 probe |
| D | Phase 2 十源 `testing_stable_sample` + Phase 3 schema |

---

## 参考

| 文档 | 路径 |
|------|------|
| C 类发现设计 | [cninfo_c_class_f10_source_discovery_design.md](cninfo_c_class_f10_source_discovery_design.md) |
| C 类数据模型 | [cninfo_c_class_profile_data_model_draft.md](cninfo_c_class_profile_data_model_draft.md) |
| B vs D（既有） | [cninfo_b_vs_d_class_boundary.md](cninfo_b_vs_d_class_boundary.md) |
| 候选 YAML | [cninfo_c_class_source_candidates.yaml](../config/cninfo_c_class_source_candidates.yaml) |
