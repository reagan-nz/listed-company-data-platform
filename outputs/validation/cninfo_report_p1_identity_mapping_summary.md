# CNINFO A 类报告 P1 identity mapping 摘要

- 生成时间：2026-07-02T10:12:36.573746+00:00
- 脚本：`lab/build_cninfo_report_p1_identity_mapping.py`
- 计划文档：[cninfo_report_p1_expansion_plan.md](cninfo_report_p1_expansion_plan.md)

## 1. 输入文件

- P1 样本：`outputs/validation/cninfo_report_p1_sample_companies.csv`
- P0 mapping：`outputs/validation/cninfo_company_identity_mapping.csv`
- 全市场 YAML：`lab/eval_companies_full_market_2024.yaml`

## 2. 样本与 mapping 规模

- P1 样本总数：**200**
- **mapped**：**199**
- **needs_orgid_mapping**：**1**
- 若全部 mapped 运行 coverage，expected rows ≈ 796（mapped × 4 report_type）

## 3. 按 sample_layer（mapped / 层内总数）

| sample_layer | mapped | total |
|--------------|--------|-------|
| bse | 40 | 40 |
| chinext | 40 | 40 |
| sse_main | 40 | 40 |
| star | 40 | 40 |
| szse_main | 39 | 40 |

## 4. 按 exchange / board（mapped 家数）

### exchange

- BSE：40/40 mapped
- SSE：80/80 mapped
- SZSE：79/80 mapped

### board

- 主板：79/80 mapped
- 创业板：40/40 mapped
- 北交所：40/40 mapped
- 科创板：40/40 mapped

## 5. mapping_source 分布

- full_market_yaml：195
- p0_identity_mapping：5

## 6. 来源统计

- 来自 P0 identity mapping：**5**
- 来自 full_market_yaml：**195**
- inferred_code_only / unknown：**0**

## 7. 仍 needs_orgid_mapping 的公司

| company_code | company_name | sample_layer | mapping_source | notes |
|--------------|--------------|--------------|----------------|-------|
| 000001 | 平安银行 | szse_main | p0_identity_mapping | orgId missing; needs mapping; do not fabricate |

## 8. 是否足够运行 P1 coverage

- **可以部分运行 P1 coverage**：199/200 家 mapped，expected rows = **796**；skipped = 4 行。

## 9. 下一步运行命令

```bash
python lab/validate_cninfo_report_coverage.py \
  --input-mapping outputs/validation/cninfo_report_p1_identity_mapping.csv \
  --output-prefix outputs/validation/cninfo_report_p1_coverage \
  --sample-csv outputs/validation/cninfo_report_p1_sample_companies.csv
```

## 10. 边界

- 未联网；未访问 CNINFO；未伪造 orgId
- 未修改 P0 mapping / P1 sample CSV
- BSE 430→920 仅在 YAML 中 orgId 一致时自动提升 query code
- 创业板 numeric orgId 来自 YAML；P0 重叠公司仍保留 P0 mapping
- **不写 verified**
