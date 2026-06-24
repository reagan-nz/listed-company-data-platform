# full_market_2024 Strict Audit Summary

_Generated: 2026-06-24 05:51 UTC_

## 1. Sample design

- **Method**: Hybrid — automated adversarial recheck over all non-financial ok companies, plus PDF-backed deep verification on a stratified manual subset.
- **Population**: 5621 non-financial companies with status=ok, all 11 industrial fields (61831 field-cells).
- **Targeted sample CSV**: 55 companies × 7 fields = 469 rows.
- **Manual PDF subset**: 15 companies × 7 targeted fields = 105 manual-verified cells.
- **Stratification**: board (bse/star/szse_main/chinext/sse_main) × proxy tier (high≥11, mid 9–10, low<9) × risky-field state (rnd/revenue plausible vs missing). Industry field unavailable (empty in YAML).
- **Targeted fields**: mda, main_business_segments, revenue_by_segment, revenue_by_region, rnd_investment, top_customers, top_suppliers.

## 2. Companies and fields audited

| scope | companies | field-cells |
|---|---:|---:|
| population (automated) | 5621 | 61831 |
| sample CSV (7 fields) | 55 | 469 |
| manual PDF (7 fields) | 15 | 105 |

## 3. Label counts (population, all 11 fields)

| label | count | pct |
|---|---:|---:|
| usable | 52699 | 85.2% |
| partial | 7636 | 12.3% |
| wrong | 876 | 1.4% |
| not_found_unverified | 620 | 1.0% |

## 4. Proxy vs strict comparison

| metric | mean / 11 |
|---|---:|
| proxy plausible (eval) | **10.61** |
| strict usable (automated, usable only) | **9.38** |
| strict lenient (usable + partial) | **10.73** |
| gap proxy − strict usable | **1.23** |

> Old baseline strict-usable **10.16/11** was on eval1000 with looser proxy (10.5/11). Current proxy already uses tightened rnd/table rules (10.35/11). **Do not claim strict improved** without like-for-like comparison.

## 5. Strict-usable estimate

- **Population automated strict-usable: 9.38 / 11** (85.2%) over 5621 non-financial companies.
- **Lenient band (usable+partial): 10.73 / 11** (97.6%).
- Manual PDF subset: 2 `not_found_missed` of 14 not_found-class cells in targeted fields (105 cells).
- Automated vs manual label agreement on manual subset: **48/105 (46%)** (same strict_label).

## 6. Major error patterns

**False positives (proxy=true, strict=wrong)** — top fields:
- `risk_factors`: 221
- `main_business_segments`: 85
- `industry_discussion`: 75
- `major_subsidiaries`: 55
- `mda`: 42
- `major_products`: 29

- proxy=true but strict=partial: **6431** cells (overstated as fully correct by proxy).
- Common rnd pattern: per-product R&D rows without clear total label ≥10万元.
- Common section pattern: short snippets or out-of-region extractions marked plausible.

## 7. Field-level observations (population)

| field | usable | partial | wrong | not_found_unverified |
|---|---:|---:|---:|---:|
| main_business_segments | 5459 | 75 | 85 | 2 |
| major_products | 5532 | 41 | 29 | 19 |
| revenue_by_segment | 5225 | 271 | 109 | 16 |
| revenue_by_region | 4861 | 469 | 258 | 33 |
| top_customers | 5309 | 276 | 0 | 36 |
| top_suppliers | 5375 | 215 | 0 | 31 |
| rnd_investment | 5078 | 212 | 0 | 331 |
| major_subsidiaries | 0 | 5549 | 55 | 17 |
| risk_factors | 4859 | 441 | 221 | 100 |
| industry_discussion | 5446 | 84 | 75 | 16 |
| mda | 5555 | 3 | 44 | 19 |

## 8. Board-level observations

| board | n | strict usable mean /11 |
|---|---:|---:|
| bse | 513 | 8.71 |
| star | 584 | 9.56 |
| szse_main | 1487 | 9.41 |
| chinext | 1385 | 9.65 |
| sse_main | 1652 | 9.25 |

## 9. Financial companies (qualitative, separate from headline)

- **平安银行 (000001)**, subtype `bank`: found=10/13, proxy_plausible=10/13, schema=bank. Numeric fields may contain table noise; not strict-audited for headline.
  - `mda`: status=found, evidence="管理层讨论与分析 36 平安银行股份有限公司 2024 年年度报告 贴现 185,729 5.5% - 214,799 6.3% - - 个人贷款（注） 1,7..."
  - `industry_discussion`: status=found, evidence="宏观经济预计仍将持续保持稳健增长，经济回升向好态势将进一步巩固和增强。..."
  - `risk_factors`: status=found, evidence="风险管理部等专业部门负责全行信用风险管理工作。..."
- **金融街 (000402)**, subtype `broker`: found=5/12, proxy_plausible=5/12, schema=broker. Numeric fields may contain table noise; not strict-audited for headline.
  - `industry_discussion`: status=found, evidence="经营环境及影响..."
  - `risk_factors`: status=found, evidence="风险管理委员会召开2 次会议、提名委员会召开3 次会议、薪酬与考核委员会召开1 次会议。..."
- **新华保险 (601336)**, subtype `insurer`: found=11/12, proxy_plausible=11/12, schema=insurer. Numeric fields may contain table noise; not strict-audited for headline.
  - `mda`: status=found, evidence="管理层讨论与分析 第四节 一、 财务情况 （一） 主要会计数据和财务指标 单位：百万元 主要会计数据 2024年 2023年 增减变动 2022年(1) 营业收..."
  - `industry_discussion`: status=found, evidence="所处行业情况 2024年，我国经济运行稳中有进，新质生产力稳步发展，改革开放持续深化，高质量发展扎实推进，市场 需求逐步恢复，利好保险业务发展；同时，外部环境复..."
  - `risk_factors`: status=found, evidence="可能面对的风险 2025年，当前社会经济发展回升向好态势持续巩固，但国际环境依然复杂严峻，内外部环境的复杂 性仍一定程度存在。近年社会经济环境、人口结构和客户需..."

## 10. Caveats

- This is an **automated adversarial recheck** over stored values, **not** manual validation of all 62,890 SQLite rows.
- `not_found_missed` is estimated only from **15-company PDF deep-read**, not the full population.
- `not_found_unverified` cells are conservatively excluded from strict-usable credit.
- Do not claim the entire full_market_2024 corpus is manually verified.
- Do not claim strict-usable improved vs historical 10.16/11 without noting proxy baseline shift.
