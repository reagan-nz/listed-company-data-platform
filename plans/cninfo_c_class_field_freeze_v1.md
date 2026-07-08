# CNINFO C-Class Field Freeze v1

_生成时间：2026-07-08_

> **Field Freeze Review** — 基于 863 harvest、QA、promotion、raw_only policy、quality rules 的字段状态冻结说明。
> **不写 verified** · **不升级 testing_stable_sample** · **field inventory 未修改**。

**C-class 状态：** `HARVEST_COMPLETED_QA_ONGOING`

---

## Frozen Fields

当前已经可以作为标准字段（**64** 项）：

**normalized_core** — 已进入 normalized harvest 产物，可作为公司档案标准展示字段。

- `company_code` (cninfo_company_basic_profile)
- `company_name` (cninfo_company_basic_profile)
- `legal_name` (cninfo_company_basic_profile)
- `english_name` (cninfo_company_basic_profile)
- `legal_representative` (cninfo_company_basic_profile)
- `registered_address` (cninfo_company_basic_profile)
- `office_address` (cninfo_company_basic_profile)
- `listing_date` (cninfo_company_basic_profile)
- `registered_capital` (cninfo_company_basic_profile)
- `company_website` (cninfo_company_basic_profile)
- `business_scope` (cninfo_company_basic_profile)
- `industry` (cninfo_company_basic_profile)
- `listed_board` (cninfo_company_basic_profile)
- `exchange` (cninfo_company_basic_profile)
- `registered_address` (cninfo_company_contact_profile)
- `office_address` (cninfo_company_contact_profile)
- `postal_code` (cninfo_company_contact_profile)
- `company_website` (cninfo_company_contact_profile)
- `contact_email` (cninfo_company_contact_profile)
- `contact_phone` (cninfo_company_contact_profile)
- `contact_fax` (cninfo_company_contact_profile)
- `board_secretary_candidate` (cninfo_company_contact_profile)
- `main_business_summary` (cninfo_company_business_scope)
- `business_scope` (cninfo_company_business_scope)
- `company_profile_text` (cninfo_company_business_scope)
- `industry` (cninfo_company_industry_profile)
- `listed_board` (cninfo_company_industry_profile)
- `person_name` (cninfo_executive_profile)
- `position` (cninfo_executive_profile)
- `gender_candidate` (cninfo_executive_profile)
- `birth_year_candidate` (cninfo_executive_profile)
- `report_date` (cninfo_share_capital_profile)
- `total_share_capital` (cninfo_share_capital_profile)
- `float_share_capital` (cninfo_share_capital_profile)
- `restricted_share_capital` (cninfo_share_capital_profile)
- `report_period` (cninfo_top_shareholders_profile)
- `shareholder_name` (cninfo_top_shareholders_profile)
- `holding_shares` (cninfo_top_shareholders_profile)
- `holding_ratio` (cninfo_top_shareholders_profile)
- `rank` (cninfo_top_shareholders_profile)
- ... 共 64 项

---

## Candidate Fields

未来可能进入 normalized（**10** 项 approved · **19** 项 review queue）：

### approved_as_candidate

已通过 promotion candidate approval（含 establishment_date after patch），待 inventory 升格：

- `establishment_date` (cninfo_company_basic_profile)
- `education_candidate` (cninfo_executive_profile)
- `shareholder_type_candidate` (cninfo_top_shareholders_profile)
- `shareholder_type_candidate` (cninfo_top_float_shareholders_profile)
- `source_status` (cninfo_company_basic_profile)
- `source_status` (cninfo_executive_profile)
- `source_status` (cninfo_share_capital_profile)
- `source_status` (cninfo_top_shareholders_profile)
- `source_status` (cninfo_top_float_shareholders_profile)
- `source_status` (cninfo_dividend_financing_profile)

---

## Review Queue

等待进一步判断（**19** 项）：

**review_later** — mapper 未覆盖、语义待定义、或与 derived 源重复待产品决策。

- `main_business_summary` (cninfo_company_basic_profile)
- `company_profile_text` (cninfo_company_basic_profile)
- `index_or_plate_labels` (cninfo_company_basic_profile)
- `index_or_plate_labels` (cninfo_company_industry_profile)
- `shareholding_quantity_candidate` (cninfo_executive_profile)
- `compensation_candidate` (cninfo_executive_profile)
- `term_start_candidate` (cninfo_executive_profile)
- `term_end_candidate` (cninfo_executive_profile)
- `change_reason_or_source` (cninfo_share_capital_profile)
- `change_amount_candidate` (cninfo_share_capital_profile)
- `share_unit` (cninfo_share_capital_profile)
- `field_confidence` (cninfo_company_basic_profile)
- `field_confidence` (cninfo_executive_profile)
- `field_confidence` (cninfo_share_capital_profile)
- `field_confidence` (cninfo_top_shareholders_profile)
- `field_confidence` (cninfo_top_float_shareholders_profile)
- `field_confidence` (cninfo_dividend_financing_profile)
- `source_status` (cninfo_company_security_profile)
- `field_confidence` (cninfo_company_security_profile)

---

## Raw Evidence Only

保留原始证据（**13** 项）：

**raw_only** — 不进主 snapshot；由 `raw_record_json` 或专用 raw 文件追溯。

- `postal_code` (cninfo_company_basic_profile)
- `contact_email` (cninfo_company_basic_profile)
- `contact_phone` (cninfo_company_basic_profile)
- `contact_fax` (cninfo_company_basic_profile)
- `board_secretary_candidate` (cninfo_company_basic_profile)
- `listing_sponsor` (cninfo_company_basic_profile)
- `listing_sec_code` (cninfo_company_basic_profile)
- `person_id_candidate` (cninfo_executive_profile)
- `row_sequence_id` (cninfo_executive_profile)
- `unrestricted_share_candidate` (cninfo_share_capital_profile)
- `total_capital_candidate` (cninfo_share_capital_profile)
- `change_status_or_change_amount_candidate` (cninfo_top_shareholders_profile)
- `change_status_or_change_amount_candidate` (cninfo_top_float_shareholders_profile)

---

## Observe Only

仅观察（**14** 项 · security 源）：

**observe_only** — `cninfo_company_security_profile` 侧轨数据，不绑定主 harvest gate。

- `security_code` (cninfo_company_security_profile)
- `stock_short_name` (cninfo_company_security_profile)
- `security_type_code` (cninfo_company_security_profile)
- `trading_status_code` (cninfo_company_security_profile)
- `listing_age_years_candidate` (cninfo_company_security_profile)
- `is_finance_related_candidate` (cninfo_company_security_profile)
- `is_delisted` (cninfo_company_security_profile)
- `shanghai_hong_kong_connect_candidate` (cninfo_company_security_profile)
- `shenzhen_hong_kong_connect_candidate` (cninfo_company_security_profile)
- `exchange` (cninfo_company_security_profile)
- `listed_board` (cninfo_company_security_profile)
- `listing_date` (cninfo_company_security_profile)
- `listing_status` (cninfo_company_security_profile)
- `is_st_candidate` (cninfo_company_security_profile)

---

## 冻结边界

| 项 | 状态 |
|----|------|
| field_inventory.csv | **未修改**（本冻结为评审产物） |
| inventory 升格 | **未执行** |
| company_snapshot | **未实现** |
| harvest rerun | **不需要** |

## 推荐下一步

1. **field inventory 升格执行**（10 approved candidates）
2. **company_snapshot planning**
3. **security observe 决策** + BSE/abnormal 侧轨文档化

