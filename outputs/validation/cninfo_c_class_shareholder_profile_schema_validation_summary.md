# CNINFO C 类 Shareholder Profile Schema Validation Summary

_生成时间：2026-07-06_

## 3. 总体结果

| 指标 | 数值 |
|------|------|
| total_fixtures | **12** |
| pass_count | **12** |
| fail_count | **0** |
| result | **PASS** |

## 4. 错误案例

_无 fail。_

## 5. Schema 说明

- 使用既有 `c_shareholder_profile.schema.json`（未修改）。
- `shareholder_scope`：`top_shareholder` | `top_float_shareholder`。
- F007V 保留在 `raw_record_json`。

## 6. 下一步

1. P2-A mapper summary / cross-mapper review.
2. P2-B probe（industry / business_scope / dividend / contact）.
