# CNINFO A 类报告 P1 扩展样本摘要

- 生成时间：2026-07-02T10:06:40.377560+00:00
- 脚本：`lab/build_cninfo_report_p1_sample_companies.py`
- 计划文档：[cninfo_report_p1_expansion_plan.md](cninfo_report_p1_expansion_plan.md)

## 1. 输入来源

- 主列表：`lab/eval_companies_full_market_2024.yaml`
- P0 对照：`outputs/validation/cninfo_p0_sample_companies.csv`（40 家）

## 2. 抽样规则

- 按 `board` 字段分 5 层，每层目标 40 家，层内按 `stock_code` 排序后等距抽取
- 排除简称含 ST / *ST / 退 的公司
- 代码段推断与 YAML `board` 不一致的条目跳过
- **不联网；不写入 orgId**

## 3. 样本规模

- **总样本数：200**（目标 200 = 5 × 40）
- 与 P0 重叠：**5** 家（`is_p0_overlap=yes`）

## 4. 各层样本数

| sample_layer | exchange | board | 目标 | 已抽 | 池内可用 | 是否足额 |
|--------------|----------|-------|------|------|----------|----------|
| sse_main | SSE | 主板 | 40 | 40 | 1662 | 是 |
| szse_main | SZSE | 主板 | 40 | 40 | 1437 | 是 |
| chinext | SZSE | 创业板 | 40 | 40 | 1359 | 是 |
| star | SSE | 科创板 | 40 | 40 | 598 | 是 |
| bse | BSE | 北交所 | 40 | 40 | 570 | 是 |

## 5. 按 exchange / board

### exchange

- BSE：40
- SSE：80
- SZSE：80

### board

- 主板：80
- 创业板：40
- 北交所：40
- 科创板：40

## 6. 不足层说明

- 五层均达到目标 40 家。

## 7. 后续步骤

1. **扩展 identity mapping**：为 P1 200 家生成 `cninfo_report_p1_identity_mapping.csv`
   - 可参考 YAML 中已有 `orgid`（不伪造；无 orgId 标 `needs_orgid_mapping`）
   - 创业板注意：F10 `gssh*` 对公告查询可能无效，需 numeric orgId（见 P0 诊断）
2. **运行 P1 coverage**（本地、合规网络）：
   ```bash
   python lab/validate_cninfo_report_coverage.py \
     --input-mapping outputs/validation/cninfo_report_p1_identity_mapping.csv \
     --output-prefix outputs/validation/cninfo_report_p1_coverage \
     --sample-csv outputs/validation/cninfo_report_p1_sample_companies.csv
   ```
3. 对比 P0 baseline（113/120 = 94.17%），评估跨板块稳定性

## 8. 边界

- 未下载/解析 PDF；未接数据库；未写 verified
- 本 CSV **不是** coverage 分母文件；coverage 以 mapping CSV 中 `mapped` 公司为准
