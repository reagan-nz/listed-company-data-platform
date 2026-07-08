# CNINFO C-Class dividend_history Offline Re-map Summary

_生成时间：2026-07-08_

> 离线 re-map：仅读 raw/dividend_history · 仅写 normalized/dividend_history。**无 CNINFO** · **无 live** · **raw 未修改**

## Counts

| metric | value |
|--------|-------|
| input raw dividend files | **863** |
| output normalized dividend files | **863** |
| before needs_review (events) | **80** |
| after needs_review (events) | **12** |
| parsed events before | **7053** |
| parsed events after | **7297** |
| partial events before | **1367** |
| partial events after | **1191** |
| empty_but_valid companies | **38** |
| changed files count | **197** |

## Company-level parse status

### before

- `empty_but_valid`: **38**
- `parsed`: **248**
- `partial`: **577**

### after

- `empty_but_valid`: **38**
- `parsed`: **293**
- `partial`: **532**

## Changed files sample（前 20）

| company_code | before_nr | after_nr | before_company | after_company |
|--------------|-----------|----------|----------------|---------------|
| 000021 | 1 | 0 | partial | partial |
| 000037 | 1 | 0 | partial | partial |
| 000055 | 1 | 0 | partial | partial |
| 000069 | 0 | 0 | partial | partial |
| 000155 | 1 | 0 | partial | parsed |
| 000419 | 0 | 0 | partial | partial |
| 000550 | 1 | 0 | partial | partial |
| 000559 | 1 | 0 | partial | partial |
| 000596 | 1 | 0 | partial | parsed |
| 000619 | 1 | 0 | partial | partial |
| 000630 | 1 | 0 | partial | partial |
| 000637 | 1 | 0 | partial | partial |
| 000723 | 0 | 0 | partial | partial |
| 000729 | 1 | 0 | partial | partial |
| 000777 | 1 | 0 | partial | partial |
| 000786 | 1 | 0 | partial | partial |
| 000789 | 1 | 0 | partial | partial |
| 000878 | 1 | 0 | partial | partial |
| 000890 | 1 | 0 | partial | partial |
| 000895 | 1 | 0 | partial | partial |

## 红线确认

- 未请求 CNINFO
- 未重跑 harvest live
- raw 数据未修改
- 未写 verified / 未入库 / MinIO / RAG

详见 [cninfo_c_class_dividend_history_remap_report.csv](cninfo_c_class_dividend_history_remap_report.csv)。
