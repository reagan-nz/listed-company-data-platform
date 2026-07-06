# CNINFO C 类 Security Profile Mapper Summary

_生成时间：2026-07-06_

## 1. 目的

将 `marketOverview` 根对象映射为 `c_company_security_profile` fixture。**无网络请求**；**不写 verified**。

## 2. 输入

- 脚本：`lab/seed_cninfo_c_class_security_profile_fixtures.py`
- Mapper：`lab/cninfo_c_class_mappers.py` → `map_company_security_profile()`
- 样本：内置 **600000**、**300001**、**688001** marketOverview raw（3 条）

## 3. 结果

| 指标 | 数值 |
|------|------|
| samples | **3** |
| mapped | **3** |
| fixtures written | **3** |

## 4. 字段映射

| raw (marketOverview) | schema 字段 |
|----------------------|-------------|
| secCode | company_code, security_code |
| secName | company_name, stock_short_name |
| secType | security_type_code |
| tradingStatus | trading_status_code |
| age | listing_age_years_candidate |
| finance | is_finance_related_candidate |
| delisted | is_delisted |
| sshk | shanghai_hong_kong_connect_candidate |
| szhk | shenzhen_hong_kong_connect_candidate |

未映射 YAML expected_fields（listed_board、listing_date 等）保留在 raw_record_json。

## 5. 逐条映射

- `600000` 浦发银行: **mapped** (raw_fields=9, mapped=10)
- `300001` 特锐德: **mapped** (raw_fields=9, mapped=10)
- `688001` 华兴源创: **mapped** (raw_fields=9, mapped=10)

## 6. 质量边界

- Mapper draft；secType / tradingStatus / sshk / szhk 语义 candidate-level。
- `source_status=testing`；**无 verified**。
- 不入库；不保存完整 live response body。
- `exchange` 由 company_code 前缀推断（candidate）。

## 附录

详见 [cninfo_c_class_security_profile_mapper_report.csv](cninfo_c_class_security_profile_mapper_report.csv)。
