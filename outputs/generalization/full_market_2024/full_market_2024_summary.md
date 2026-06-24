# full_market_2024 Summary

_Generated: 2026-06-24 | Milestone: extraction + merge + SQLite import + hybrid strict audit **complete**_

> **Caveat**：本 milestone 表示管道执行、数据库导入与混合 strict 审计均已完成。**不等于** 62,890 条 SQLite 记录已全量人工验证。strict **9.01/11** 为自动化 adversarial 全 population 估计，经 15 家公司 PDF deep-read 小样本校准。

---

## Final status counts

| status | count | pct | 说明 |
|---|---:|---:|---|
| **total** | **6124** | 100% | full_market_2024 universe 全部 A 股公司数 |
| **ok** | **5707** | 93.2% | 成功找到年报并完成抽取（≠ 每字段正确） |
| no_announcement | 417 | 6.8% | CNINFO 当前规则下未找到可用 2024 年报 |
| **error** | **0** | 0% | 技术失败（688267 中触媒经重试恢复） |

- non-financial ok: **5621**
- financial ok: **86**（使用金融子 schema，**不纳入**非金融 11 字段 headline）

## Board counts (universe YAML)

| board | 中文 | count |
|---|---|---:|
| bse | 北交所 | 577 |
| star | 科创板 | 613 |
| szse_main | 深市主板 | 1646 |
| chinext | 创业板 | 1442 |
| sse_main | 沪市主板 | 1846 |

## Non-financial proxy (headline)

| metric | value |
|---|---:|
| Mean proxy plausible | **10.35 / 11** (n=5621) |

### Comparison vs controlled eval runs

| run | universe | ok | no_ann | error | non-fin proxy |
|---|---:|---:|---:|---:|---:|
| eval1000_v2 | 1020 | 947 | 73 | 0 | **10.33/11** |
| independent eval1000 | 1000 | 918 | 82 | 0 | **10.30/11** |
| **full_market_2024** | **6124** | **5707** | **417** | **0** | **10.35/11** |

> 全市场规模 proxy 与 v2/independent 一致（Δ ≤ 0.05），说明管道规模泛化良好。

## Hybrid strict audit (non-financial headline)

| metric | value | 说明 |
|---|---:|---|
| Population recheck | 5621 × 11 = **61,831** cells | 自动化 adversarial |
| **strict usable** | **9.01 / 11** (81.9%) | usable only；比 proxy 更保守 |
| strict lenient | **10.47 / 11** (95.2%) | usable + partial 上界 |
| gap (proxy − strict usable) | **1.34** | |
| Sample CSV | 55 cos × 7 fields = 476 rows | 分层抽样 |
| Manual PDF deep-read | 15 cos × 7 fields = 105 rows | 小样本校准 |
| Manual vs automated agreement | 52/105 (50%) | 同 strict_label |

> **不得将 9.01/11 与旧 eval1000 strict 10.16/11 比较为「改善」或「下降」**：旧 baseline 基于 proxy 10.5/11（Issue #1/#2 前）；当前 proxy 已收紧至 10.35/11。

### Board-level strict usable (non-financial)

| board | 中文 | n (ok) | strict usable /11 |
|---|---|---:|---:|
| bse | 北交所 | 513 | **7.14** |
| sse_main | 沪市主板 | 1652 | 8.53 |
| szse_main | 深市主板 | 1487 | 9.42 |
| star | 科创板 | 584 | 9.47 |
| chinext | 创业板 | 1385 | **9.66** |

**主要风险**：BSE 模板适配不足；rnd_investment not_found_missed；revenue 表格 page-boundary / 切片问题；金融数值噪声（金融公司不在 headline 内）。

详见 [strict_audit_summary.md](strict_audit_summary.md)、[strict_audit_sample.csv](strict_audit_sample.csv)。

## Key field proxy rates (non-financial)

| field | plausible | rate |
|---|---:|---:|
| rnd_investment | 3817/5621 | 67.9% |
| revenue_by_region | 5093/5621 | 90.6% |
| revenue_by_segment | 5386/5621 | 95.8% |

## Financial subtypes (ok, n=86)

| subtype | count |
|---|---:|
| bank | 43 |
| broker | 37 |
| other_financial | 4 |
| insurer | 2 |

> 金融字段质量需单独 review；未纳入 strict headline。

## SQLite import (run_name=`full_market_2024`)

| table | rows | 说明 |
|---|---:|---|
| company_basic | 6124 | = 公司数 |
| report_source | 6124 | = 公司数 |
| extracted_field | **62,890** | **公司-字段记录**，非公司数 |
| evaluation_result | **62,890** | **公司-字段记录**，非公司数 |

---

## 指标解释 / Metric Definitions

| 术语 | English | 含义 |
|---|---|---|
| **total** | total | full_market_2024 universe 中的 A 股公司总数。 |
| **ok** | ok | 脚本成功找到 2024 年报公告/PDF、下载/解析并写出 `company_profile.json`。**不等于每个字段都完全正确。** |
| **no_announcement** | no_announcement | CNINFO 当前查询规则下未找到可用 2024 年报。不一定是代码 bug。 |
| **error** | error | 网络/下载/解析等技术失败。本 run 最终为 0。 |
| **proxy plausible** | proxy plausible | 自动 plausibility：字段结构看起来合理。**不等于人工确认正确。** |
| **strict usable** | strict usable | adversarial 审计标签（usable only）。**9.01/11** = 全 population 自动化 + 15 家 PDF 小样本校准。 |
| **strict lenient** | strict lenient | usable + partial 上界（10.47/11）：证据相关但可能不完整/有噪声。 |
| **manual PDF deep-read** | manual PDF deep-read | 读取 PDF 页文本验证 evidence；检查 not_found 是否应为 missed。非全量人工验证。 |
| **非金融 headline** | non-financial headline | 11 字段均值仅统计工业类公司；金融公司用独立子 schema。 |
| **SQLite 行数** | SQLite rows | extracted_field / evaluation_result 行数 = 公司×字段记录，不是公司数。 |

### 板块名称 / Board translations

| code | 中文 |
|---|---|
| bse | 北交所 |
| star | 科创板 |
| szse_main | 深市主板 |
| chinext | 创业板 |
| sse_main | 沪市主板 |

---

## Caveats

1. **非全量人工验证**：62,890 SQLite 行未经逐条人工核对。
2. **strict 9.01/11** 是自动化 adversarial 估计 + 15 家 PDF 校准，不是 population 级人工审计。
3. **不得声称 strict 优于/劣于旧 10.16/11**（不同 proxy baseline 与 universe）。
4. Root symlinks `{code}` → `{board}/{code}` 供 `db_import.py` 查找 profile。
5. 重跑 merge 后需重新生成本 summary 与 strict audit 报告。

## Related docs

- [strict_audit_summary.md](strict_audit_summary.md)
- [eval_summary.md](eval_summary.md)
- [CURRENT_STATUS.md](../../../CURRENT_STATUS.md)
- [docs/evaluation_method.md](../../../docs/evaluation_method.md)
