# CNINFO C 类 Share Capital Profile Mapper Summary

_生成时间：2026-07-06_

## 1. 目的

将 `getStockStructure` 单行 `data.records[]` 映射为 `c_share_capital_profile` fixture。
**无网络请求**；**不写 verified**。

## 2. 字段映射

| raw | schema |
|-----|--------|
| VARYDATE | report_date |
| F021N | total_share_capital |
| F022N | float_share_capital |
| F023N | restricted_share_capital |
| F002V / F024N / F028N / F003N | raw_record_json only |

## 3. 结果

| 指标 | 数值 |
|------|------|
| samples | **6** |
| mapped | **6** |
| fixtures written | **6** |

## 4. 逐条映射

- `600000` 2025-12-31: **mapped** (mapped=3)
- `600000` 2025-10-27: **mapped** (mapped=3)
- `300001` 2026-06-03: **mapped** (mapped=3)
- `300001` 2025-12-31: **mapped** (mapped=3)
- `688001` 2026-05-18: **mapped** (mapped=3)
- `688001` 2025-12-31: **mapped** (mapped=3)

## 5. 质量边界

- FxxxN 单位 candidate-level；行可能为定期报告或股本变动事件。
- `source_status=testing`；**无 verified**。

## 附录

详见 [cninfo_c_class_share_capital_profile_mapper_report.csv](cninfo_c_class_share_capital_profile_mapper_report.csv)。
