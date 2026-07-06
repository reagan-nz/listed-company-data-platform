# CNINFO C 类 Basic Profile Schema Validation Summary

_生成时间：2026-07-06_

## 1. 目的

校验 mapper 生成的 `c_company_basic_profile` fixture JSONL。
**无网络**；**不写 verified**。

## 2. 输入

| 来源 | 路径 |
|------|------|
| Fixtures | `fixtures/c_class/basic_profile/basic_profile_fixtures.jsonl` |
| Schema | `schemas/c_class/c_company_basic_profile.schema.json` |
| 脚本 | `lab/validate_cninfo_c_class_basic_profile_schema.py` |

## 3. 总体结果

| 指标 | 数值 |
|------|------|
| total_fixtures | **2** |
| pass | **2** |
| fail | **0** |
| result | **PASS** |

## 4. 错误案例

_无 fail。_

## 5. 质量边界

- 2-company embedded sample only (300001, 688001).
- `source_status=testing`；**no verified**.
- No database ingestion.

## 6. 下一步

1. security_profile mapper draft.
2. Optional: expand fixtures after controlled live sample capture.
3. P2 source DevTools probe.

## 附录

详见 [cninfo_c_class_basic_profile_schema_validation_report.csv](cninfo_c_class_basic_profile_schema_validation_report.csv)。
