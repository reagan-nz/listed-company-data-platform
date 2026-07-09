# CNINFO A 类 Tiny Live Metadata Validation 执行摘要

_生成时间：2026-07-09 06:49:45 UTC_

> **性质：** A-class tiny live metadata validation · **无 PDF 下载/解析** · **不是 verified**

## Counts

| 指标 | 值 |
|------|-----|
| mode | live |
| universe size | 5 |
| companies executed | 5 |
| metadata found | 5 |
| success (found) | 5 |
| failure | 0 |
| CNINFO requests | 10 |
| PDF downloaded | **0** |
| PDF parsed | **0** |

## Endpoint usage

- topSearch/query: 5
- hisAnnouncement/query: 5

## QA

- only 5 companies: **yes**
- metadata only: **yes**
- no PDF download: **yes**
- no PDF parsing: **yes**
- output isolation: `/Users/zhao/Desktop/97/实操/数据收集测试/listed_company_data_collector/outputs/validation/cninfo_a_class_tiny_live_metadata`
- C-class untouched: **yes**
- B-class untouched: **yes**
- D-class untouched: **yes**

## Gate

```text
a_class_tiny_live_metadata_execution_gate = PASS_WITH_CAVEAT
```

**不是 PASS** · **不是 production_ready** · **不是 verified** · tiny sample only

## Caveats（须人工 review）

- ALM001 / ALM005：检索到 **半年报** 而非年报（`expected_period=2024-12-31`）；`quality_status=pass` 仅表示 metadata 字段齐全，**非** report_type 完全对齐
- ALM003：`688001` 对应 **华兴源创**（universe 公司名标注为华熙生物，代码/名称不一致）
- ALM004：命中 **英文版** 三季报（title exclusion 未覆盖 `（英文）` 变体）
- 全部 case：`pdf_downloaded=no` · `pdf_parsed=no` · `storage_status=not_attempted`

## Next recommended task

1. 修正 universe 公司名（ALM003）与 title exclusion（英文变体）
2. 加强 report_type / expected_period 标题匹配后 **重跑 tiny live** 或扩大样本
3. 人工 review live report → 决定是否扩展 registry `live_validation_status`
