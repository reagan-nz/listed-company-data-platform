# CNINFO C-Class Field Inventory（Era C Phase 4）

_生成时间：2026-07-07_

> **目的：** 基于现有 schema、mapper、fixture、live summary 与 source status decision，整理 C-class **当前可覆盖字段清单**，为后续 **raw + normalized harvest** 做准备。
>
> **不是**新 endpoint discovery · **不是** harvest 执行 · **不写 verified** · **不升级 testing_stable_sample**。

**机器可读清单：** [cninfo_c_class_field_inventory.csv](../outputs/validation/cninfo_c_class_field_inventory.csv)（**120** 行）

**证据链：**

- Schema：`schemas/c_class/`
- Mapper：`lab/cninfo_c_class_mappers.py`
- Registry 草案：`config/cninfo_c_class_source_candidates.yaml`
- Source status：[cninfo_c_class_source_status_decision.md](cninfo_c_class_source_status_decision.md)
- Post-retry：[cninfo_c_class_889_post_retry_decision.md](cninfo_c_class_889_post_retry_decision.md)
- Live summary：stable 200 · 889 rerun · partial-fail retry

---

## 一、Field Inventory 的目的

| 项 | 说明 |
|----|------|
| **是什么** | 已验证 source 上 **raw → normalized** 字段映射清单 + fill 证据 + caveat |
| **不是什么** | 新 discovery、live 重跑、YAML backfill 执行、DB 入库 |
| **服务于** | harvest planning 前的 **字段范围冻结**；raw snapshot 与 normalized snapshot 切分 |
| **红线** | no verified · no testing_stable_sample · 不请求 CNINFO |

### 字段三分法（`include_in_normalized_snapshot`）

| 分类 | CSV 值 | 含义 | 数量 |
|------|--------|------|------|
| **normalized_core** | `yes` | 确定进入 normalized company snapshot（含 lineage 必需字段） | **64** |
| **review_later** | `review` | 语义不稳、mapper 未覆盖或 schema 槽位待确认 | **31** |
| **raw_only** | `no` | 仅保留 raw_record_json；或 observe-only 不进主 snapshot | **25** |

---

## 二、按 Source 分节

### 2.1 `cninfo_company_basic_profile`（direct）

| 项 | 值 |
|----|-----|
| endpoint | `getCompanyIntroduction` |
| schema | `c_company_basic_profile` |
| mapper | `map_company_basic_profile` |
| source_status | **proceed_testing_with_caveat** |
| 字段数 | **29**（25 业务 + 4 lineage） |
| fill 证据 | stable200 key fill **100%**；889 reach **97.0%** |

**normalized_core（mapper 已映射）：** `legal_name` · `english_name` · `legal_representative` · `registered_address` · `office_address` · `listing_date` · `registered_capital` · `company_website` · `business_scope` · `industry` · `listed_board` · `exchange`

**review_later：** `main_business_summary`(F015V) · `company_profile_text`(F017V) · `establishment_date`(F010D) · `index_or_plate_labels`(F044V)

**raw_only：** 联系字段 F012V–F014V · F006V · F018V · listing F047V 等（由 derived contact 或 raw 保留）

---

### 2.2 `cninfo_company_contact_profile`（derived）

| 项 | 值 |
|----|-----|
| derived_from | `cninfo_company_basic_profile` · `basicInformation[0]` |
| source_status | **derived_no_separate_fetch** |
| 字段数 | **8** |
| fill 证据 | 889 derived **≥98.9%** |

**normalized_core：** `registered_address` · `office_address` · `postal_code` · `company_website` · `contact_email` · `contact_phone` · `contact_fax` · `board_secretary_candidate`

**caveat：** 无独立 HTTP；完全依赖 basic 可达性。

---

### 2.3 `cninfo_company_business_scope`（derived）

| 项 | 值 |
|----|-----|
| derived_from | basic `F015V` / `F016V` / `F017V` |
| source_status | **derived_no_separate_fetch** |
| 字段数 | **3** |
| fill 证据 | 889 **≥99.7%** |

**normalized_core：** `main_business_summary` · `business_scope` · `company_profile_text`

---

### 2.4 `cninfo_company_industry_profile`（derived）

| 项 | 值 |
|----|-----|
| derived_from | basic `F032V` / `F044V` / `MARKET` |
| source_status | **derived_no_separate_fetch** |
| 字段数 | **3** |
| fill 证据 | F032V **99.7%** · F044V **95.5%** |

**normalized_core：** `industry` · `listed_board`

**review_later：** `index_or_plate_labels`（F044V 语义弱于 F032V）

**caveat：** 非完整行业分类体系；observed-only 语义。

---

### 2.5 `cninfo_executive_profile`（direct）

| 项 | 值 |
|----|-----|
| endpoint | `getCompanyExecutives` |
| schema | `c_executive_profile` |
| mapper | `map_company_executive_profile` |
| source_status | **proceed_testing_with_caveat** |
| record_level | **executive**（一人一行） |
| 字段数 | **15**（11 业务 + 4 lineage） |
| fill 证据 | 889 reach **93.8%**；partial retry **97.6%**；post-retry **1** empty_but_valid residual |

**normalized_core：** `person_name` · `position` · `gender_candidate` · `birth_year_candidate`

**review_later：** `education_candidate` · `shareholding_quantity_candidate` · `compensation_candidate` · `term_start_candidate` · `term_end_candidate`（schema 有槽位，mapper 未映射）

**raw_only：** `person_id_candidate` · `row_sequence_id`

**caveat：** **executive caveat** — 困难样本敏感；empty_but_valid 仍可能判 fail。

---

### 2.6 `cninfo_share_capital_profile`（direct）

| 项 | 值 |
|----|-----|
| endpoint | `getStockStructure` |
| schema | `c_share_capital_profile` |
| mapper | `map_company_share_capital_profile` |
| source_status | **source_partial** |
| record_level | **share_capital**（一期一行） |
| 字段数 | **13**（9 业务 + 4 lineage） |
| fill 证据 | 889 reach **94.2%**；partial retry **80.5%**；**8** empty_but_valid residual |

**normalized_core：** `report_date` · `total_share_capital` · `float_share_capital` · `restricted_share_capital`

**review_later：** `change_reason_or_source` · `unrestricted_share_candidate` · `change_amount_candidate` · `total_capital_candidate` · `share_unit`

**caveat：** **share_capital source_partial** — 不可假设全市场非空；单位语义 candidate-level。

---

### 2.7 `cninfo_top_shareholders_profile`（direct）

| 项 | 值 |
|----|-----|
| endpoint | `getTopTenStockholders` |
| schema | `c_shareholder_profile` · scope=`top_shareholder` |
| mapper | `map_company_shareholder_profile` |
| source_status | **proceed_testing_with_caveat** |
| record_level | **shareholder** |
| 字段数 | **11**（7 业务 + 4 lineage） |
| fill 证据 | 889 reach **97.0%**；empty_but_valid 单独统计 |

**normalized_core：** `report_period` · `shareholder_name` · `holding_shares` · `holding_ratio` · `rank`

**review_later：** `shareholder_type_candidate`

**raw_only：** `change_status_or_change_amount_candidate`（F007V）

**caveat：** reachable **≠** non_empty；empty_but_valid **case_result=pass**。

---

### 2.8 `cninfo_top_float_shareholders_profile`（direct）

| 项 | 值 |
|----|-----|
| endpoint | `getTopTenCirculatingStockholders` |
| schema | `c_shareholder_profile` · scope=`top_float_shareholder` |
| source_status | **source_partial** |
| record_level | **shareholder** |
| 字段数 | **11**（同 top_sh 字段形状） |
| fill 证据 | 889 reach **97.0%**；non_empty 低于 reach |

**caveat：** **top_float source_partial** — 主 gate 区分 reach vs non_empty；不要求全公司非空。

---

### 2.9 `cninfo_dividend_financing_profile` / **dividend_history**（direct）

| 项 | 值 |
|----|-----|
| endpoint | `getCompanyHisDividend` |
| logical_name | **dividend_history**（窄化命名，≠ financing） |
| source_status | **proceed_testing** |
| record_level | **dividend**（一条分红记录一行） |
| 字段数 | **9**（5 业务 + 4 lineage） |
| mapper | **尚无独立 mapper**；live 以 raw records + field fill 统计 |
| fill 证据 | 889 reach **97.0%**；stable200 **100%**；partial retry **100%** |

**normalized_core（规划）：** `report_period` · `dividend_plan_text` · `announcement_date_candidate` · `ex_right_dividend_date_candidate` · `dividend_payment_date_candidate`

**caveat：** **dividend_history ≠ financing** — 仅历史分红；不覆盖配股/增发；YAML **GO（决策 only）** · **不执行** backfill。

---

### 2.10 `cninfo_company_security_profile`（observe_only）

| 项 | 值 |
|----|-----|
| endpoint | `marketOverview` |
| schema | `c_company_security_profile` |
| mapper | `map_company_security_profile` |
| source_status | **observe_only** |
| record_level | **security** |
| 字段数 | **18**（14 业务 + 4 lineage） |
| fill 证据 | 889 observe **100%** |

**mapper 已映射（observe 侧）：** `stock_short_name` · `security_code` · `security_type_code` · `trading_status_code` · `listing_age_years_candidate` · `is_finance_related_candidate` · `is_delisted` · 沪港通/深港通 candidate · `exchange`

**review_later / raw_only：** `listed_board` · `listing_date` · `listing_status` · `is_st_candidate`（schema 有槽位，mapper v1 未填）

**caveat：** **security observe-only** — 不绑定主 gate；`secType=szshe` 硬编码；**不进主 normalized snapshot**（`include=no`）。

---

## 三、Harvest 相关 Caveat 汇总

| caveat | 影响 |
|--------|------|
| **26 家 all6 hold** | harvest universe 排除；`eval_companies_c_class_889_rerun_all6_hold.yaml` |
| **share_capital source_partial** | normalized 可收 reachable 空 records；不可作全市场 non_empty gate |
| **executive caveat** | 纳入 snapshot 但标注 source_status / field_confidence |
| **top_float source_partial** | 区分 reach vs non_empty |
| **security observe-only** | 单独 observe 表/分区，不混入主 profile snapshot |
| **dividend_history ≠ financing** | 命名窄化；不承诺融资事件 |
| **no verified** | 全字段 `source_status=testing` 级别 |
| **no testing_stable_sample** | 不升级样本 tier |

---

## 四、不要做的事（本轮）

- 不请求 CNINFO
- 不跑 live
- 不实际 harvest
- 不写 YAML backfill
- 不入库
- 不写 verified
- 不升级 testing_stable_sample
- 不新增 endpoint discovery

---

## 五、Harvest Planning 门槛判断

| 问题 | 判断 |
|------|------|
| field inventory 是否完成？ | **是**（本文档 + CSV） |
| 是否可进入 harvest planning？ | **是** — 字段清单已足够起草 raw/normalized harvest 设计 |
| 是否可立即执行 harvest live？ | **否** — 需先 harvest planning 文档（universe − 26 hold；caveat 模板） |
| dividend mapper 缺口？ | `dividend_history` 需补 mapper draft（可放在 planning 阶段，非本轮） |

**建议下一步：** 起草 `cninfo_c_class_harvest_plan.md`（universe、raw/normalized 分层、26 hold 排除、source_partial 标注模板）。

---

## 六、字段统计摘要

| source_id | 字段数 | source_type | source_status |
|-----------|--------|-------------|---------------|
| `cninfo_company_basic_profile` | 29 | direct | proceed_testing_with_caveat |
| `cninfo_company_contact_profile` | 8 | derived | derived_no_separate_fetch |
| `cninfo_company_business_scope` | 3 | derived | derived_no_separate_fetch |
| `cninfo_company_industry_profile` | 3 | derived | derived_no_separate_fetch |
| `cninfo_executive_profile` | 15 | direct | proceed_testing_with_caveat |
| `cninfo_share_capital_profile` | 13 | direct | source_partial |
| `cninfo_top_shareholders_profile` | 11 | direct | proceed_testing_with_caveat |
| `cninfo_top_float_shareholders_profile` | 11 | direct | source_partial |
| `cninfo_dividend_financing_profile` | 9 | direct | proceed_testing |
| `cninfo_company_security_profile` | 18 | observe_only | observe_only |
| **合计** | **120** | | |

| include_in_normalized_snapshot | 数量 | 对应分类 |
|--------------------------------|------|----------|
| `yes` | **64** | normalized_core |
| `review` | **31** | review_later |
| `no` | **25** | raw_only / observe 排除 |
