# CNINFO D 类 Source Discovery 计划

_最后更新：2026-07-09_

> **性质：** 规划 only；本轮 **不调用 CNINFO**、不 live、不 harvest、不下载文件。  
> **前置：** [cninfo_d_class_market_data_architecture_plan.md](cninfo_d_class_market_data_architecture_plan.md) · [config/cninfo_table_sources.yaml](../config/cninfo_table_sources.yaml) · [config/cninfo_d_class_source_registry_draft.yaml](../config/cninfo_d_class_source_registry_draft.yaml)  
> **并行约束：** C-class `SNAPSHOT_GENERATED_QA_REVIEW` 不变；B-class tiny live 待批准；不读写在跑 harvest 输出根。

---

## Discovery Strategy

D-class Phase 0 source discovery **不复跑 live**，而是：

1. **复用 Phase 2 已验证 endpoint 证据**（`testing_stable_sample` × 10，其中 7 源为本轮市场行为主线）；
2. **对照既有 registry YAML + UI 字段语义文档**，整理 endpoint candidate 与字段缺口；
3. **定义下一验证步骤**（offline fixture / field freeze / tiny harvest approval），但 **本轮不执行**。

### Step 1. 复用 Phase 2 验证产物（已完成 · 离线阅读）

| 产物 | 路径 |
|------|------|
| Phase 2 总总结 | [cninfo_table_sources_phase2_current_final_summary.md](../outputs/validation/cninfo_table_sources_phase2_current_final_summary.md) |
| P1 分源 | [cninfo_table_sources_priority1_summary.md](../outputs/validation/cninfo_table_sources_priority1_summary.md) |
| P2 分源 | [cninfo_table_sources_priority2_current_summary.md](../outputs/validation/cninfo_table_sources_priority2_current_summary.md) |
| 配置 | [config/cninfo_table_sources.yaml](../config/cninfo_table_sources.yaml) |
| 稳定性 | [cninfo_table_sources_multidate_stability_summary.md](../outputs/validation/cninfo_table_sources_multidate_stability_summary.md) · [priority2_stability](../outputs/validation/cninfo_table_sources_priority2_stability_summary.md) |

### Step 2. 对照 registry / schema / fixture（已完成 · 离线阅读）

| 产物 | 路径 |
|------|------|
| Registry YAML | [config/cninfo_d_class_source_registry_draft.yaml](../config/cninfo_d_class_source_registry_draft.yaml) |
| Schema draft | [plans/cninfo_d_class_schema_draft.md](cninfo_d_class_schema_draft.md) |
| Mapping review | [plans/cninfo_d_class_source_to_schema_mapping_review.md](cninfo_d_class_source_to_schema_mapping_review.md) |
| Fixtures | [fixtures/d_class/](../fixtures/d_class/) · validation [summary](../outputs/validation/cninfo_d_class_schema_validation_summary.md) |

### Step 3. 逐源 discovery 表（本轮交付 · **无 live**）

见下文 §「逐源 Discovery 记录」。

### Step 4. Readiness matrix + planning summary（本轮交付）

见 `outputs/validation/cninfo_d_class_readiness_matrix.csv` · `cninfo_d_class_initial_planning_summary.md`。

### Step 5. 未来 live / harvest（**不做**）

须满足：readiness P0 项 `design_complete` · 用户显式批准 · 不与 C-class Phase 3 live 抢带宽。

---

## 逐源 Discovery 记录

> **confidence 口径：** `high` = Phase 2 sample_ok + UI 表头对照；`medium` = endpoint 可达但部分字段语义待确认；`low` = endpoint 未验证或仅 UI 线索。  
> **本轮全部为离线整理，confidence 来自历史 Phase 2 记录，非本轮 live 复测。**

---

### 1. 融资融券（margin_trading）

| 项 | 内容 |
|----|------|
| **Purpose** | 公司级融资融券日度行为与余额指标 |
| **Endpoint candidate** | `POST https://www.cninfo.com.cn/data20/marginTrading/detailList`（空 body，无 query） |
| **UI evidence** | 页面 `commonUrl?url=data/rzrq-zjlx`（资讯 → 数据 → 融资融券）；DevTools 观测 `detailList` 返回 `data.records` |
| **Related endpoint** | `data20/marginTrading/market?tdate=` 为市场汇总级，**非**公司级主线 |
| **Expected fields** | `TRADEDATE` · `SECCODE` · `SECNAME` · `F001N`–`F009N` · `F010V`–`F012V` · `MEMO` |
| **Product fields（意图）** | `company_code` · `company_name` · `trade_date` · `financing_balance` · `financing_buy_amount` · `margin_balance` · `margin_sell_amount` · `total_margin_balance` |
| **Confidence** | **high**（endpoint + 行结构稳定；F00xN 语义 medium） |
| **Risk** | 字段单位（元/万元）未 fully freeze；无日期参数时返回全量快照，harvest 须设计增量/分页策略 |
| **Next validation step** | 离线：field semantics freeze CSV 对照 UI 表头；未来 tiny harvest dry-run（按 `trade_date` 抽样） |

---

### 2. 大宗交易（block_trade）

| 项 | 内容 |
|----|------|
| **Purpose** | 大宗交易成交汇总 |
| **Endpoint candidate** | `POST https://www.cninfo.com.cn/data20/ints/statistics?tdate=YYYY-MM-DD` |
| **UI evidence** | 页面 `commonUrl?url=data/dzjy`；Referer 与 tab 标题「大宗交易」一致 |
| **Expected fields** | `SECCODE` · `SECNAME` · `TRADEDATE` · `F001N`（笔数）· `F002N`（成交量）· `F003N`（成交额）· `F004N`（均价） |
| **Product fields（意图）** | `company_code` · `company_name` · `trade_date` · `transaction_price` · `transaction_volume` · `transaction_amount` · `buyer` · `seller` |
| **Confidence** | **high**（endpoint + 汇总字段）；**buyer/seller = low**（当前 endpoint 无买卖双方明细） |
| **Risk** | 产品字段 `buyer`/`seller` 在 Phase 2 样本中**未观测**；须另寻 detail endpoint 或降级为汇总-only |
| **Next validation step** | 离线：将 buyer/seller 标为 `phase2_gap`；DevTools 探测是否存在 per-deal detail API（**未来回合，非本轮**） |

---

### 3. 限售解禁（restricted_shares_unlock）

| 项 | 内容 |
|----|------|
| **Purpose** | 限售股解禁日程与规模 |
| **Endpoint candidate** | `POST https://www.cninfo.com.cn/data20/liftBan/detail?tdate=YYYY-MM-DD` |
| **UI evidence** | 页面 `commonUrl?url=data/restricted-shares`；表头含解禁日期、解禁数量、解禁比例等 |
| **Expected fields** | `SECCODE` · `SECNAME` · `DECLAREDATE` · `F003D` · `F004N` · `F005N` · `F008N` |
| **Product fields（意图）** | `company_code` · `company_name` · `announcement_date` · `unlock_date` · `unlock_amount` · `unlock_ratio` · `tradable_amount` |
| **Confidence** | **high**（endpoint + 核心字段）；`F008N` tradable 语义 **medium** |
| **Risk** | 按 `tdate` 单日查询，全历史 harvest 须日期循环；低交易日可能返回空 list（合法空态） |
| **Next validation step** | 离线：mapping review 对齐 `d_company_event`；未来 multidate dry-run 设计（不执行） |

---

### 4. 股权质押（equity_pledge）

| 项 | 内容 |
|----|------|
| **Purpose** | 股权质押风险与质押状态 |
| **Endpoint candidate** | `POST https://www.cninfo.com.cn/data20/equityPledge/list?tdate=YYYY-MM-DD` |
| **UI evidence** | 页面 `commonUrl?url=data/person-stock-data-tables` tab「股权质押」 |
| **Expected fields** | `SECCODE` · `SECNAME` · `DECLAREDATE` · `F001V` · `F003V` · `F006N` · `F007N` · `F008V` · `F012N` · `F018N` |
| **Product fields（意图）** | `company_code` · `company_name` · `pledge_date` · `pledged_shares` · `pledge_ratio` · `pledgee` · `pledge_status` |
| **Confidence** | **medium**（endpoint high；F006N 单位可能为万股；质权人/状态字段映射 medium） |
| **Risk** | 单行可能含多笔质押语义；`pledge_status` 需从 `F008V`/`F018N` 规则化，易误判 |
| **Next validation step** | 离线：UI 表头 freeze + mapper 规则文档；fixture 扩样（**无 live**） |

---

### 5. 股东增减持（shareholder_change）

| 项 | 内容 |
|----|------|
| **Purpose** | 股东持股变动（增持/减持） |
| **Endpoint candidate** | `POST https://www.cninfo.com.cn/data20/shareholeder/detail?type=inc|desc&tdate=YYYY-MM-DD` |
| **UI evidence** | 页面 `commonUrl?url=data/person-stock-data-tables` tab「股东增减持」；路径拼写 `shareholeder`（CNINFO 原文） |
| **Expected fields** | `DECLAREDATE` · `SECCODE` · `SECNAME` · `VARYDATE` · `F002V` · `F004N` · `F005N` · `F007V` |
| **Product fields（意图）** | `company_code` · `company_name` · `shareholder_name` · `change_type` · `change_amount` · `change_ratio` · `change_date` |
| **Confidence** | **high**（inc/desc 双模式已验证；UI 语义已对照） |
| **Risk** | 须分别拉取 `type=inc` 与 `type=desc`；`desc` 模式 `tdate` 可为 null；endpoint 路径拼写非标准 |
| **Next validation step** | 离线：registry `supported_modes` 文档化；mapper 双模式 fixture 已有，可扩 QA 规则 |

---

### 6. 高管持股变化（executive_shareholding）

| 项 | 内容 |
|----|------|
| **Purpose** | 高管及相关人员持股变动 |
| **Endpoint candidate** | `POST https://www.cninfo.com.cn/data20/leader/detail?timeMark=oneMonth&varyType=b` |
| **UI evidence** | 页面 `commonUrl?url=data/person-stock-data-tables` tab「高管持股」 |
| **Expected fields** | `SECCODE` · `SECNAME` · `ENDDATE` · `DECLAREDATE` · `HUMANNAME` · `F001V`–`F011V` |
| **Product fields（意图）** | `executive_name` · `position` · `change_type` · `change_amount` · `change_date`（+ `company_code`） |
| **Confidence** | **medium**（endpoint high；`varyType` / F004N–F009N 语义 medium） |
| **Risk** | `timeMark` / `varyType` 参数组合影响结果集；职位字段可能分布在 F001V/F002V；与 C-class `executive_profile` 易混淆 |
| **Next validation step** | 离线：边界文档复核 [cninfo_c_vs_b_vs_d_boundary.md](cninfo_c_vs_b_vs_d_boundary.md)；`varyType` 枚举 freeze（无 live） |

---

### 7. 预约披露 / 信息披露日历（disclosure_schedule）

| 项 | 内容 |
|----|------|
| **Purpose** | 定期报告预约披露与变更日程 |
| **Endpoint candidate** | `POST https://www.cninfo.com.cn/new/information/getPrbookInfo`（form：`sectionTime` · `market` · `pagenum` · `pagesize`） |
| **UI evidence** | 页面 `disclosure/list/notice`；返回 `prbookinfos` 数组（非 `data.records`） |
| **Expected fields** | `seccode` · `secname` · `orgId` · `f001d_0102`–`f006d_0102` · `latest_time` |
| **Product fields（意图）** | `company_code` · `report_type` · `planned_date` · `actual_date` · `change_history` |
| **Confidence** | **high**（endpoint + 日程字段）；`latest_time` **low**（UI 不可见，常 null） |
| **Risk** | `records_path=prbookinfos` 与其他源不同；变更日期字段 f003–f005 语义需 freeze；与 A-class 报告期联动复杂 |
| **Next validation step** | 离线：`d_disclosure_schedule` schema 对齐；与 A-class `sectionTime` 参数矩阵文档化 |

---

## Reuse vs Gap

### 可直接复用（Phase 2 / Phase 3 既有）

- 7 个 endpoint 均已 Phase 2 `testing_stable_sample` 验证
- [cninfo_d_class_source_registry_draft.yaml](../config/cninfo_d_class_source_registry_draft.yaml) 十源 registry
- [lab/cninfo_d_class_mappers.py](../lab/cninfo_d_class_mappers.py) + 11 fixture schema validation PASS
- C-class `company_code` universe（863 snapshot / eval YAML）作未来 harvest 身份键

### 仍缺失（Phase 0 识别 · 不执行）

| 缺口 | 影响源 | 优先级 |
|------|--------|--------|
| 市场行为层统一 harvest 架构 | 全部 7 源 | P0 |
| 字段语义 freeze CSV（7 源产品字段） | 全部 | P0 |
| 大宗交易买卖双方明细 endpoint | `block_trade` | P1 |
| D-class harvest runner + output root 设计 | 全部 | P1 |
| 公司级 event timeline 读模型 | 聚合层 | P2 |
| B-class `event_document_link` 挂接规则 | 证据层 | P2 |

---

## Red Lines

- **No CNINFO** · **No live** · **No harvest** · **No PDF**
- **No DB** · **No MinIO** · **No RAG**
- **No verified** · **No testing_stable_sample upgrade**
- **No C-class / B-class output modification**
