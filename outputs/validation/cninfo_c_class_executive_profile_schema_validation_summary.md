# CNINFO C 类 Executive Profile Schema Validation Summary

_生成时间：2026-07-06_

## 1. 目的

校验 mapper 生成的 `c_executive_profile` fixture JSONL。
**无网络**；**不写 verified**。

## 2. 输入

| 来源 | 路径 |
|------|------|
| Fixtures | `fixtures/c_class/executive_profile/executive_profile_fixtures.jsonl` |
| Schema | `schemas/c_class/c_executive_profile.schema.json` |
| 脚本 | `lab/validate_cninfo_c_class_executive_profile_schema.py` |

## 3. 总体结果

| 指标 | 数值 |
|------|------|
| total_fixtures | **6** |
| pass_count | **6** |
| fail_count | **0** |
| result | **PASS** |

## 4. 错误案例

_无 fail。_

## 5. Schema 说明

- 使用既有 `c_executive_profile.schema.json`（未修改）。
- F005N/F012N/SEQID/F001V 保留在 `raw_record_json`；schema 无对应槽位。

## 6. 质量边界

- 6 embedded executive rows (2 per known company).
- `source_status=testing`；**no verified**.
- No database ingestion.

## 7. 下一步

1. share_capital_profile mapper draft.
2. top_shareholders / top_float_shareholders mapper draft.

## 附录

详见 [cninfo_c_class_executive_profile_schema_validation_report.csv](cninfo_c_class_executive_profile_schema_validation_report.csv)。
