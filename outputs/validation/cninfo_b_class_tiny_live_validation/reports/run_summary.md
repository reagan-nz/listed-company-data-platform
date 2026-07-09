# CNINFO B 类 Tiny Live Metadata Validation 执行摘要

_生成时间：2026-07-09 05:57:26 UTC_

> **性质：** 首次 B-class CNINFO metadata live validation · **无 PDF 下载/解析**

## Counts

| 指标 | 值 |
|------|-----|
| mode | live |
| companies executed | 5 |
| CNINFO requests | 8 |
| success (found) | 4 |
| failure | 1 |
| PDF download | **disabled** |
| PDF parse | **disabled** |

## Endpoint usage

- EP001: 4
- EP002: 4
- EP004: 2
- EP005: 3

## QA

- only 5 companies: **yes**
- allowed endpoints only: **yes**
- no PDF download: **yes**
- no PDF parsing: **yes**
- output isolation: `/Users/zhao/Desktop/97/实操/数据收集测试/listed_company_data_collector/outputs/validation/cninfo_b_class_tiny_live_validation`
- C-class Phase3 untouched: **yes**

## Gate

```text
b_class_tiny_live_validation_execution_gate = PASS_WITH_CAVEAT
```

**不是 PASS** · **不是 verified** · tiny sample only

