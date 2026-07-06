# CNINFO C 类 Security Profile Schema Validation Summary

_生成时间：2026-07-06_

## 1. 目的

校验 mapper 生成的 `c_company_security_profile` fixture JSONL。
**无网络**；**不写 verified**。

## 2. 输入

| 来源 | 路径 |
|------|------|
| Fixtures | `fixtures/c_class/security_profile/security_profile_fixtures.jsonl` |
| Schema | `schemas/c_class/c_company_security_profile.schema.json` |
| 脚本 | `lab/validate_cninfo_c_class_security_profile_schema.py` |

## 3. 总体结果

| 指标 | 数值 |
|------|------|
| total_fixtures | **3** |
| pass_count | **3** |
| fail_count | **0** |
| result | **PASS** |

## 4. 错误案例

_无 fail。_

## 5. Schema 说明

- 本轮新增 `c_company_security_profile.schema.json`（draft-07），对齐 marketOverview 字段与 lineage required 闭包。
- YAML `expected_fields` 中 listing_date / listed_board 等未在 mapper v1 填充，schema 中为可选 null。

## 6. 质量边界

- 3-company embedded marketOverview sample (600000, 300001, 688001).
- `source_status=testing`；**no verified**.
- No database ingestion.

## 7. 下一步

1. Optional: map getHeadStripData annex fields.
2. P2 DevTools probe for remaining candidate sources.
3. Expand secType validation across more board samples.

## 附录

详见 [cninfo_c_class_security_profile_schema_validation_report.csv](cninfo_c_class_security_profile_schema_validation_report.csv)。
