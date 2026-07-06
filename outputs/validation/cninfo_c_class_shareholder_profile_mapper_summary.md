# CNINFO C 类 Shareholder Profile Mapper Summary

_生成时间：2026-07-06_

## 1. 目的

将 `getTopTenStockholders` / `getTopTenCirculatingStockholders` 单行 `data.records[]`
映射为 `c_shareholder_profile` fixture。**无网络请求**；**不写 verified**。

## 2. 字段映射

| raw | schema |
|-----|--------|
| F001D | report_period |
| F002V | shareholder_name |
| F003N | holding_shares |
| F004N | holding_ratio |
| F005N | rank |
| F006V | shareholder_type_candidate |
| F007V | raw_record_json only |

**shareholder_scope：** `top_shareholder`（cninfo_top_shareholders_profile）·
`top_float_shareholder`（cninfo_top_float_shareholders_profile）

## 3. 结果

| 指标 | 数值 |
|------|------|
| samples | **12** |
| mapped | **12** |
| top_shareholder | **6** |
| top_float_shareholder | **6** |
| fixtures written | **12** |

## 4. 逐条映射

- `600000` top_shareholder rank=1 上海国际集团有限公司: **mapped** (mapped=6)
- `600000` top_shareholder rank=2 中国移动通信集团广东有限公司: **mapped** (mapped=6)
- `600000` top_float_shareholder rank=1 上海国际集团有限公司: **mapped** (mapped=6)
- `600000` top_float_shareholder rank=2 中国移动通信集团广东有限公司: **mapped** (mapped=6)
- `300001` top_shareholder rank=1 青岛德锐投资有限公司: **mapped** (mapped=6)
- `300001` top_shareholder rank=2 香港中央结算有限公司: **mapped** (mapped=6)
- `300001` top_float_shareholder rank=1 青岛德锐投资有限公司: **mapped** (mapped=6)
- `300001` top_float_shareholder rank=2 香港中央结算有限公司: **mapped** (mapped=6)
- `688001` top_shareholder rank=1 苏州源华创兴投资管理有限公司: **mapped** (mapped=6)
- `688001` top_shareholder rank=2 陈文源: **mapped** (mapped=6)
- `688001` top_float_shareholder rank=1 苏州源华创兴投资管理有限公司: **mapped** (mapped=6)
- `688001` top_float_shareholder rank=2 陈文源: **mapped** (mapped=6)

## 5. 质量边界

- F003N 单位 candidate-level；响应常含多期 × 10 股东。
- `source_status=testing`；**无 verified**。

## 附录

详见 [cninfo_c_class_shareholder_profile_mapper_report.csv](cninfo_c_class_shareholder_profile_mapper_report.csv)。
