# CNINFO C 类 Registry Lint Summary

## 1. 目的

本地 **candidate YAML / JSON Schema** 一致性检查。
**不请求 CNINFO**；不 probe endpoint；不写 verified。

## 2. 输入

| 来源 | 路径 |
|------|------|
| C 类 candidate registry | `config/cninfo_c_class_source_candidates.yaml` |
| Schemas | `schemas/c_class/` |
| 脚本 | `lab/lint_cninfo_c_class_registry.py` |

## 3. 总体结果

| 指标 | 数值 |
|------|------|
| total_rules | **14** |
| sources | **10** |
| fail | **0** |
| warn | **0** |
| info | **4** |
| result | **PASS** |

## 4. 重点检查

- **source_layer** = `company_profile`（R002）
- **verified** 全部为 false（R003）
- **recommended_status** 不超过 `testing`（R005；**6 testing / 4 candidate**）
- **endpoint** 已回填：**6/10** source 有 `endpoint.url`（R006）；4 仍 null（P3 candidate）
- **industry_profile** 无 endpoint 时应有 `derived_from_candidate`（R014）
- **无 B/D source_id 混入**（R012）

## 5. 问题清单

_无 FAIL / WARN。_

## 6. 质量边界

- Lint PASS **不代表** F10 endpoint 已确认。
- **不代表** 字段已在 UI/DevTools 验证。
- **不写 verified**。

## 7. 下一步

1. C 类 P2-A live validation（3 家 × 4 源，默认 dry-run）。
2. P2-A mapper draft（executive / share_capital / shareholders）。
3. P3 source DevTools probe（business_scope / contact / dividend_financing）。

## 附录

详见 [cninfo_c_class_registry_lint_report.csv](cninfo_c_class_registry_lint_report.csv)。
