# CNINFO C-Class establishment_date Offline Re-map Summary

_生成时间：2026-07-08_

> 离线 re-map：仅读 `raw/basic_profile` · 仅写 `normalized/company_basic_profile`。**无 CNINFO** · **无 live** · **raw 未修改**

## Counts

| metric | value |
|--------|-------|
| input raw basic files | **863** |
| output normalized basic files | **863** |
| establishment_date present (parsed) | **863** |
| establishment_date null | **0** |
| establishment_date invalid / nonstandard | **0** |
| establishment_date not present | **0** |
| changed files count | **863** |
| CNINFO requests | **0** |

## parse_status breakdown

- `parsed`: **863**

## invalid / nonstandard sample（前 20）

| company_code | establishment_date |
|--------------|-------------------|

## 红线确认

- 未请求 CNINFO
- 未重跑 harvest live
- raw 数据未修改
- 未写 verified / 未入库 / MinIO / RAG

详见 [cninfo_c_class_establishment_date_remap_report.csv](cninfo_c_class_establishment_date_remap_report.csv)。
