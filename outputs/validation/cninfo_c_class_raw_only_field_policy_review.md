# CNINFO C-Class raw_only 25 字段最终政策复判

_生成时间：2026-07-08_

> 离线政策复判。**无 CNINFO** · **无 harvest 重跑** · **未改 field inventory** · **无 verified**

---

## 1. Overall Result

**raw_only total = 25**（`include_in_normalized_snapshot=no`）

| 项 | 值 |
|----|-----|
| 输入 | [cninfo_c_class_field_inventory.csv](cninfo_c_class_field_inventory.csv) |
| 产物 | [cninfo_c_class_raw_only_field_policy_review.csv](cninfo_c_class_raw_only_field_policy_review.csv) |
| 本轮性质 | **仅 policy review**；不改 inventory · 不改 normalized |

**C-class 状态：** `HARVEST_COMPLETED_QA_ONGOING`

---

## 2. Policy Distribution

| recommended_policy | count |
|--------------------|-------|
| observe_only_excluded | **14** |
| keep_raw_only_permanently | **7** |
| keep_raw_only_for_now | **2** |
| convert_to_review_later_candidate | **1** |
| lineage_only | **1** |
| **合计** | **25** |

---

## 3. Keep Raw Only Permanently（7）

| source | field | normalized_field | 原因 |
|--------|-------|------------------|------|
| basic | F006V | postal_code | contact derived 已覆盖 |
| basic | F012V | contact_email | contact derived 已覆盖 |
| basic | F013V | contact_phone | contact derived 已覆盖 |
| basic | F014V | contact_fax | contact derived 已覆盖 |
| basic | F018V | board_secretary_candidate | contact derived 已覆盖 |
| basic | SECCODE | listing_sec_code | 与 company_code 冗余 |
| executive | F001V | person_id_candidate | 内部人员 ID，非产品字段 |

---

## 4. Keep Raw Only For Now（2）

| source | field | normalized_field | 未来复判条件 |
|--------|-------|------------------|--------------|
| top_shareholders | F007V | change_status_or_change_amount_candidate | 变动文本 parser 规则稳定后 |
| top_float | F007V | change_status_or_change_amount_candidate | top_float source_partial 政策收口后 |

---

## 5. Convert To Review Later Candidate（1）

| source | field | normalized_field | 原因 |
|--------|-------|------------------|------|
| basic | F047V | listing_sponsor | 保荐机构有展示价值；未进 snapshot schema；宜转 review_later 复判 |

---

## 6. Observe Only Excluded（14）

**source：** `cninfo_company_security_profile`（全部 14 个 `include=no` 业务字段）

| 字段示例 | 原因 |
|----------|------|
| secCode · secName · secType · tradingStatus | security **observe_only** |
| age · finance · delisted · sshk · szhk | 不进主 company snapshot |
| exchange · listed_board · listing_date · listing_status · is_st_candidate | 待 security observe 决策 |

---

## 7. Lineage Only（1）

| source | field | normalized_field | 原因 |
|--------|-------|------------------|------|
| executive | SEQID | row_sequence_id | 行级去重/追溯；不进用户 snapshot |

---

## 8. Source Summary

| source_id | raw_only_count | keep_permanent | keep_for_now | review_later_candidate | observe_only_excluded | lineage_only |
|-----------|----------------|----------------|--------------|--------------------------|----------------------|--------------|
| cninfo_company_basic_profile | 7 | 6 | 0 | 1 | 0 | 0 |
| cninfo_executive_profile | 2 | 1 | 0 | 0 | 0 | 1 |
| cninfo_top_shareholders_profile | 1 | 0 | 1 | 0 | 0 | 0 |
| cninfo_top_float_shareholders_profile | 1 | 0 | 1 | 0 | 0 | 0 |
| cninfo_company_security_profile | 14 | 0 | 0 | 0 | 14 | 0 |

---

## 推荐下一步

- **establishment_date mapper patch implementation**（独立轮次）
- **F047V listing_sponsor** 可在下一轮 review_later 复判中并入（optional）
- **security observe 决策** 后再评估 14 字段是否侧轨展示

---

## 红线确认

- 未请求 CNINFO · 未改 field inventory · raw/normalized 未改
