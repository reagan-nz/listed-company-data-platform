# CNINFO C 类 Profile Schema Validation Summary

_生成时间：2026-07-05（offline known-company fixture schema validation）_

## 1. 目的

对 C 类 company profile logical record 做 **离线 JSON Schema 校验**。
**不请求 CNINFO、不 probe endpoint、不入库、不写 verified。**

## 2. 输入

| 来源 | 路径 |
|------|------|
| Fixture JSONL | `fixtures/c_class/known_company_profile_fixtures.jsonl` |
| Schemas | `schemas/c_class/` |
| 脚本 | `lab/validate_cninfo_c_class_profile_schema.py` |

## 3. 总体结果

| 指标 | 数值 |
|------|------|
| total_fixtures | **12** |
| pass | **12** |
| fail | **0** |
| result | **PASS** |

### by schema_name (pass)

- `c_company_basic_profile.schema.json`: **3**
- `c_company_profile_snapshot.schema.json`: **3**
- `c_executive_profile.schema.json`: **1**
- `c_profile_raw_snapshot.schema.json`: **3**
- `c_share_capital_profile.schema.json`: **1**
- `c_shareholder_profile.schema.json`: **1**

## 4. 错误案例

_无 fail。_

## 5. 质量边界

- fixture 仅为 **offline shape test**；不代表 CNINFO 实际返回。
- **endpoint 未 probe**；`fetch_status=not_started` 合法。
- **不写 verified**；不代表 source 可用。

## 6. 下一步

1. per-source DevTools probe。
2. 回填 endpoint / records_path。
3. 建立 C 类 known-company profile validation 脚本（小样本 live）。

## 附录

详见 [cninfo_c_class_profile_schema_validation_report.csv](cninfo_c_class_profile_schema_validation_report.csv)。
