# CNINFO C-Class Full Harvest QA Flag Triage

_生成时间：2026-07-08_

> 离线分层 review planning。**无 CNINFO** · **无 live** · **无 raw/normalized 修改** · **无 verified**

## Triage Conclusion

**PASS_WITH_CAVEAT_REVIEW_QUEUE_READY**

### 背景

- QA 结论：**PASS_WITH_CAVEAT**
- Full harvest gate：**PASS_WITH_RESUME**
- raw 6041/6041 · normalized 8630/8630 · companies 863/863 · blocked=0 · http_error=0 · hold_overlap=0
- QA flags 总计：**72**（dividend_parse=12 · source_caveat=54 · missing_normalized_core=6）

## 分层概览

| Tier | 范围 | 公司数 | 行数 |
|------|------|--------|------|
| **P0** | missing_normalized_core | 6 | 12 |
| **P1** | dividend_parse needs_review | 12 | 12 |
| **P2** | source_caveat / empty_but_valid | 28 | 54 |

## P0 · missing_normalized_core（优先人工检查）

_共 6 家公司 · 12 个字段缺口；均为 derived/industry nullable，**非 harvest 文件缺失**。_

| company_code | company_name | source | field | 原因 |
|--------------|--------------|--------|-------|------|
| 002710 | 慈铭体检 | industry | F032V | normalized_core 字段未填充 filled=0 |
| 002710 | 慈铭体检 | industry | F044V | normalized_core 字段未填充 filled=0 |
| 601206 | 海尔施 | industry | F032V | normalized_core 字段未填充 filled=0 |
| 601206 | 海尔施 | industry | F044V | normalized_core 字段未填充 filled=0 |
| 688235 | 百济神州 | contact | F018V | normalized_core 字段未填充 filled=0 |
| 688235 | 百济神州 | business_scope | F016V | normalized_core 字段未填充 filled=0 |
| 688688 | 蚂蚁集团 | industry | F032V | normalized_core 字段未填充 filled=0 |
| 688688 | 蚂蚁集团 | industry | F044V | normalized_core 字段未填充 filled=0 |
| 688795 | 摩尔线程 | contact | F014V | normalized_core 字段未填充 filled=0 |
| 688795 | 摩尔线程 | industry | F044V | normalized_core 字段未填充 filled=0 |
| 688809 | 强一股份 | contact | F014V | normalized_core 字段未填充 filled=0 |
| 688809 | 强一股份 | industry | F044V | normalized_core 字段未填充 filled=0 |

**P0 建议：** 人工核对 basic JSON 中对应 raw 字段是否源端为空；**不触发 harvest 重跑**。

## P1 · dividend_parse needs_review

_77 家公司 · **12** 条 needs_review 事件（自 normalized dividend_history）。_

### F007V pattern 分布（needs_review 事件级）

| pattern | 中文标签 | count | share |
|---------|----------|-------|-------|
| `other_unparseable` | 其他无法解析文本 | **5** | 41.7% |
| `cash_plus_stock_transfer_combo` | 送股/转增+派现组合 | **3** | 25.0% |
| `stock_or_transfer_combo` | 送股/转增组合 | **2** | 16.7% |
| `tax_inclusive_exclusive_complex` | 含税/不含税复杂表达 | **2** | 16.7% |

### Top F007V 文本（needs_review）

| count | F007V text | pattern |
|-------|------------|---------|
| 1 | 10送1派1.00元 | 送股/转增+派现组合 |
| 1 | 94和95未分配利润均结转至上市后分配 | 其他无法解析文本 |
| 1 | 10转增8 股 | 送股/转增组合 |
| 1 | 10派1.5 元（含税） | 含税/不含税复杂表达 |
| 1 | 10送14转増1股派3.5元(含税) | 送股/转增+派现组合 |
| 1 | 10派1.2 元（含税） | 含税/不含税复杂表达 |
| 1 | 95年度利润滚存至96年度一并分配 | 其他无法解析文本 |
| 1 | 95年7月至12月利润全部上交 | 其他无法解析文本 |
| 1 | 95年度利润只对老股东分配 | 其他无法解析文本 |
| 1 | 未分配利润滚存96年度合并派发 | 其他无法解析文本 |
| 1 | 10送3.5元 | 送股/转增组合 |
| 1 | 10送5转增15派1.5元(含税) | 送股/转增+派现组合 |

### Parser 判断

- needs_review 以零散文本为主，保留人工 review 队列。

### P1 公司列表（77）

`000011`, `000655`, `000905`, `002019`, `002041`, `002060`, `600702`, `600716`, `600728`, `600777`, `600877`, `603023`

## P2 · source_caveat / empty_but_valid

_54 条 flag · **28** 家公司；`source_partial` / `empty_but_valid` **不自动 FAIL**。_

### 按 source 汇总

| source | flag 条数 | 公司数 | source_status |
|--------|-----------|--------|---------------|
| executive | 9 | 9 | `proceed_testing_with_caveat` |
| share_capital | 10 | 10 | `source_partial` |
| top_float | 19 | 19 | `source_partial` |
| top_shareholders | 16 | 16 | `proceed_testing_with_caveat` |

### P2 公司列表

`000037`, `000055`, `002255`, `002258`, `002267`, `002290`, `002302`, `002322`, `002338`, `002355`, `002360`, `002361`, `002710`, `300510`, `300513`, `300793`, `301330`, `301332`, `301333`, `301382`, `301390`, `301391`, `301419`, `301583`, `301669`, `601206`, `688688`, `688797`

## 结论枚举说明

| 结论 | 含义 |
|------|------|
| `PASS_WITH_CAVEAT_REVIEW_QUEUE_READY` | review 队列可开工；无主导 parser/data 修复项 |
| `NEED_PARSER_PATCH` | needs_review 存在重复 F007V pattern，建议 patch dividend parser |
| `NEED_DATA_REPAIR` | P0 指向 harvest 数据损坏需重跑（本轮未触发） |

## 输入

- `outputs/validation/cninfo_c_class_full_harvest_qa_flags.csv`
- `outputs/validation/cninfo_c_class_full_harvest_qa_review.md`
- `outputs/validation/cninfo_c_class_harvest_full_summary.md`
- `outputs/harvest/cninfo_c_class/quality/field_fill_rate.csv`

## 输出

- `outputs/validation/cninfo_c_class_full_harvest_qa_flag_triage.csv`（78 rows）
- `outputs/validation/cninfo_c_class_full_harvest_qa_flag_triage.md`

## 红线确认

- 未请求 CNINFO · 未重跑 live · 未修改 raw/normalized
- 未写 verified · 未升级 testing_stable_sample
- 未入库 / MinIO / RAG / YAML backfill
