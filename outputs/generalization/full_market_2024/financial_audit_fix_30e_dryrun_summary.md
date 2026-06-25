# Financial audit fix #30e dry-run — financial table plausibility

_Generated: 2026-06-25 | targeted extraction + audit dry-run on cached PDFs only_

## Verdict: **PASS**

| Gate | Result |
|---|---|
| All known manual WRONG table targets are strict wrong | **PASS** |
| 0 known manual WRONG table targets become usable | **PASS** |
| Manual CORRECT/PARTIAL table controls do not get mass downgraded | **PASS** |
| No profile/eval/population/sample CSV writes | **PASS** |

## Files changed

- `lab/strict_audit_financial_full_market.py`
- `lab/financial_audit_fix_30e_dryrun.py`
- `outputs/generalization/full_market_2024/financial_audit_fix_30e_dryrun_summary.md`

## Code changes

1. Tightened financial-only table reject vocabulary for `loan_structure`, `deposit_structure`, `regional_distribution` / `revenue_by_region`, and `revenue_by_segment`.
2. Added explicit total-only / no-breakdown guards for loan/deposit structure.
3. Added branch-roster reject for region tables and cost-only reject for segment tables without revenue rows.
4. Kept all changes inside `lab/strict_audit_financial_full_market.py`; no extraction writes, no non-fin audit changes.
5. Fixed the dry-run harness to resolve field specs by each company’s real `schema_profile`, which removes the earlier `601059 revenue_by_segment` artifact from cross-profile spec reuse.

## Table target list

| Code | Field | Scope |
|---|---|---|
| 601963 | `loan_structure` | manual WRONG target |
| 601963 | `deposit_structure` | manual WRONG target |
| 002966 | `loan_structure` | manual WRONG target |
| 600015 | `loan_structure` | manual WRONG target |
| 600000 | `loan_structure` | manual WRONG target |
| 600000 | `deposit_structure` | manual WRONG target |
| 002142 | `loan_structure` | manual WRONG target |
| 002142 | `deposit_structure` | manual WRONG target |
| 600000 | `regional_distribution` | manual WRONG target |
| 001236 | `revenue_by_region` | manual WRONG target |
| 002961 | `revenue_by_region` | manual WRONG target |
| 601878 | `revenue_by_segment` | manual WRONG target |
| 600369 | `revenue_by_segment` | manual WRONG target |
| 601696 | `revenue_by_segment` | manual WRONG target |
| 601136 | `revenue_by_segment` | manual WRONG target |
| 601336 | `revenue_by_segment` | manual WRONG target |
| 600927 | `revenue_by_segment` | manual WRONG target |
| 603093 | `revenue_by_segment` | manual WRONG target |

## Before / after strict table

| Code | Field | Before strict | After strict | Before status | After status |
|---|---|---|---|---|---|
| 601963 | `loan_structure` | wrong | **wrong** | partial | partial |
| 601963 | `deposit_structure` | wrong | **wrong** | partial | partial |
| 002966 | `loan_structure` | wrong | **wrong** | found | found |
| 600015 | `loan_structure` | wrong | **wrong** | found | found |
| 600000 | `loan_structure` | wrong | **wrong** | found | found |
| 600000 | `deposit_structure` | wrong | **wrong** | found | found |
| 002142 | `loan_structure` | wrong | **wrong** | partial | partial |
| 002142 | `deposit_structure` | wrong | **wrong** | partial | partial |
| 600000 | `regional_distribution` | wrong | **wrong** | partial | partial |
| 001236 | `revenue_by_region` | wrong | **wrong** | partial | partial |
| 002961 | `revenue_by_region` | wrong | **wrong** | partial | partial |
| 601878 | `revenue_by_segment` | wrong | **wrong** | partial | partial |
| 600369 | `revenue_by_segment` | wrong | **wrong** | found | found |
| 601696 | `revenue_by_segment` | wrong | **wrong** | partial | partial |
| 601136 | `revenue_by_segment` | wrong | **wrong** | partial | partial |
| 601336 | `revenue_by_segment` | wrong | **wrong** | partial | partial |
| 600927 | `revenue_by_segment` | wrong | **wrong** | partial | partial |
| 603093 | `revenue_by_segment` | wrong | **wrong** | partial | partial |

## Manual WRONG target results

| Code | Field | After strict | After reason | Preview |
|---|---|---|---|---|
| 601963 | `loan_structure` | wrong | empty rows | 发放贷款和垫款 – 11,382,623 25,084,138 98,329,196 211,362,100 76,627,959 – 4,477,829 427,263,845 金融投资－交易性金融资产 – 37,168,170 6,498,954 7,262,504 9,106,108 2,296,430 2,227,831 120,696 64,680 |
| 601963 | `deposit_structure` | wrong | empty rows | 吸收存款 (87,284,683) (21,033,344) (38,432,831) (83,015,223) (200,767,857) (39,453) – – (430,573,391) 应付债券 – (8,130,000) (25,899,898) (97,233,750) (19,376,363) (5,932,500) – – (156,572 |
| 002966 | `loan_structure` | wrong | loan table looks like interest income or asset composition | 发放贷款和垫款 |  | 12,574,619 |  |  | 11,917,139 / 存放中央银行款项 |  | 338,418 |  |  | 297,850 |
| 600015 | `loan_structure` | wrong | loan table looks like interest income or asset composition | 发放贷款和垫款 | 2,313,356 | 52.86 | 2,256,596 | 53.04 / 金融投资 | 1,651,055 | 37.73 | 1,605,288 | 37.73 |
| 600000 | `loan_structure` | wrong | loan table looks like interest income or asset composition | 报告期内，集团实现利息收入2,881.25亿元，同比减少94.73亿元，下降3… / 益率分别为3.61%、4.76%，较去年同期分别同比下降0.24和0.54个百… |
| 600000 | `deposit_structure` | wrong | deposit table looks like liability/cash-flow summary | 报告期末，本集团长期股权投资余额18.07亿元，较上年末下降36.04%。其中… / 比上年末下降40.44%。报告期末，本集团长期股权投资减值准备余额为零。 |
| 002142 | `loan_structure` | wrong | empty rows | 发放贷款及垫款 68,425 59,795 8,630 14.43% 存放同业 420 312 108 34.62% 存放中央银行 1,861 1,749 112 6.40% 拆出资金 1,276 1,257 19 1.51% 买入返售金融资产 679 687 (8) (1.16%) 债券投资 25,256 21,130 4,126 19.53% 信托及资管 |
| 002142 | `deposit_structure` | wrong | empty rows | 吸收存款 34,642 30,547 4,095 13.41% 卖出回购金融资产款 1,268 2,015 (747) (37.07%) 发行债券 9,316 9,474 (158) (1.67%) 租赁负债 92 106 (14) (13.21%) 利息净收入 47,993 40,907 7,086 17.32% 下表列示了生息资产和付息负债的平均余额、利 |
| 600000 | `regional_distribution` | wrong | empty rows | 长三 角地 区 宁波分行 宁波市江厦街21 号 1,206 41 155,652 南京分行 南京市玄武区中山东路303 号 2,904 110 360,719 苏州分行 苏州市工业园区钟园路718 号 968 31 117,416 合肥分行 合肥市滨湖区杭州路2608 号 1,239 46 124,823 上海自贸试 验区分行 上海市浦东新区浦东南路588  |
| 001236 | `revenue_by_region` | wrong | empty rows | 境内综合期货及期权经纪业务佣金率为万分之0.24，2023 年同期为万分之0.38。 (2) 资产管理业务 截至2024 年12 月31 日，公司资产管理规模人民币161.12 亿元，较2023 年末的资产管理规模人民币184.22 亿元， 同比减少12.54%；资产管理业务实现收入（不包括纳入合并范围的结构化主体产生的手续费收入）人民币600.19 万元， |
| 002961 | `revenue_by_region` | wrong | empty rows | 境内 外股 票 601318 中国 平安 9,888 ,847. 58 公允 价值 计量 7,254 ,000. 00 3,347 ,206. 68 8,236 ,889. 44 8,234 ,319. 82 2,657 ,830. 38 9,477 ,000. 00 交易 性金 融资 产 自有 资金 期末持有的其他证券投 资 135,6 05,48 7.4 |
| 601878 | `revenue_by_segment` | wrong | empty rows | 手续费及佣金的净额78.51 亿元，代理买卖证券收到的现金净增加额96.52 亿元，为交易目 的而持有的金融资产净减少额62.69 亿元，返售业务资金净减少额22.49 亿元，收到其他与经营 活动有关的现金165.71 亿元；现金流出363.03 亿元，主要包括融出资金净增加额43.51 亿元， 回购业务资金净减少额14.36 亿元，支付给职工以及为职工支付 |
| 600369 | `revenue_by_segment` | wrong | segment table looks like cash-flow/cost/income-statement page | 证券经纪业务 | 业务及管理费、税金及附加、 减值损失、其他业务成本 | 764,048,953.88 | 44.48 | 696,955,263.97 | 39.00 / 证券自营业务 | 业务及管理费、税金及附加、 减值损失 | 103,049,481.81 | 6.00 | 47,923,244.70 | 2.68 |
| 601696 | `revenue_by_segment` | wrong | empty rows | 手续费及佣金的现金38.87 亿元， 占经营活动现金流入的比例为20.37%；为交易目的而持有的金融资产净减少额32.84 亿元，占比 17.21%；拆入资金净增加额26.50 亿元，占比13.89%；为交易目的而持有的金融负债净增加额7.33 亿元，占比3.84%；收到其他与经营活动有关的现金1.29 亿元，占经营活动现金流入的比例为0.68%。 现金流出 |
| 601136 | `revenue_by_segment` | wrong | empty rows | 手续费及佣金净收入 1,358,776,141.59 877,492,121.83 54.85% 投资收益 1,122,970,579.05 997,257,888.49 12.61% 其他收益 10,632,618.95 7,136,931.41 48.98% 公允价值变动收益 19,126,283.23 195,705,648.00 -90.23% 汇兑 |
| 601336 | `revenue_by_segment` | wrong | empty rows | 寿险业务以外的其他股东价值变化。 六、 敏感性测试 敏感性测试是在一系列不同的假设基础上完成的。在每一项敏感性测试中，只有相关的假设会发生变化，其他假 设保持不变。本公司的敏感性测试结果汇总如下： 单位：百万元 2024年12月31日有效业务价值和 一年新业务价值敏感性测试结果 扣除要求资本成本后的 有效业务价值 扣除要求资本成本后的 一年新业务价值 情景  |
| 600927 | `revenue_by_segment` | wrong | segment table looks like cash-flow/cost/income-statement page | 手续费及佣金净收入 | 二十一4 | 443,608,320.10 | 532,618,126.19 / 利息净收入 | 二十一3 | 299,681,326.65 | 531,385,227.46 |
| 603093 | `revenue_by_segment` | wrong | segment table looks like cash-flow/cost/income-statement page | 手续费及佣金净收入 | 二十二4 | 313,977,499.99 | 423,427,111.05 / 利息净收入 | 二十二3 | 183,365,108.78 | 151,059,695.58 |

## Manual CORRECT/PARTIAL control results

Controls evaluated: **26**

| Code | Field | Manual | Before strict | After strict | After reason |
|---|---|---|---|---|---|
| 000001 | `deposit_structure` | PARTIAL | usable | usable | 6 data rows |
| 000001 | `loan_structure` | PARTIAL | usable | usable | 6 data rows |
| 000001 | `regional_distribution` | CORRECT | wrong | wrong | empty rows |
| 001236 | `revenue_by_segment` | CORRECT | wrong | wrong | empty rows |
| 002142 | `regional_distribution` | CORRECT | wrong | wrong | empty rows |
| 002961 | `revenue_by_segment` | CORRECT | partial | partial | status=partial |
| 002966 | `deposit_structure` | CORRECT | usable | usable | 7 data rows |
| 002966 | `regional_distribution` | CORRECT | wrong | wrong | empty rows |
| 600015 | `deposit_structure` | CORRECT | wrong | wrong | deposit table looks like liability/cash-flow summary |
| 600015 | `regional_distribution` | CORRECT | usable | usable | 7 data rows |
| 600016 | `loan_structure` | PARTIAL | wrong | wrong | empty rows |
| 600318 | `regional_distribution` | PARTIAL | wrong | wrong | empty rows |
| 600816 | `regional_distribution` | CORRECT | partial | partial | single data row (single data row) |
| 600908 | `deposit_structure` | CORRECT | wrong | wrong | deposit table looks like liability/cash-flow summary |
| 600908 | `loan_structure` | CORRECT | usable | usable | 4 data rows |
| 600908 | `regional_distribution` | CORRECT | usable | usable | 2 data rows |
| 600927 | `revenue_by_region` | CORRECT | usable | usable | revenue_table_plausible |
| 601059 | `revenue_by_segment` | CORRECT | usable | usable | revenue_table_plausible |
| 601328 | `deposit_structure` | CORRECT | wrong | wrong | empty rows |
| 601328 | `loan_structure` | CORRECT | wrong | wrong | empty rows |
| 601328 | `regional_distribution` | CORRECT | wrong | wrong | empty rows |
| 601377 | `revenue_by_segment` | PARTIAL | wrong | wrong | empty rows |
| 601628 | `revenue_by_segment` | CORRECT | wrong | wrong | empty rows |
| 601939 | `regional_distribution` | CORRECT | wrong | wrong | empty rows |
| 601963 | `regional_distribution` | CORRECT | wrong | wrong | empty rows |
| 603093 | `revenue_by_region` | CORRECT | usable | usable | revenue_table_plausible |

## Risk caveats

- Control rows newly downgraded to `wrong`: **0**.
- Earlier `601059 revenue_by_segment` downgrade was a harness/report artifact: the prior harness keyed specs only by field name and could evaluate a broker row with another financial subtype’s field spec.
- This dry-run re-extracts target rows from cached PDFs only; it does not rewrite profiles, population CSVs, or evaluation artifacts.
- Region-table semantics still intentionally allow some banking loan-by-region distribution tables when they contain real region + numeric distribution rows.

## Sample apply recommendation: **Deferred pending review**

Do not sample-apply this yet unless you explicitly accept any control downgrades and want the stricter table safety tradeoff.

## Safe-to-commit list

- `lab/strict_audit_financial_full_market.py`
- `lab/financial_audit_fix_30e_dryrun.py`
- `outputs/generalization/full_market_2024/financial_audit_fix_30e_dryrun_summary.md`

## Do-not-commit list

- any `company_profile.json`
- `financial_audit_population.csv`
- `financial_audit_summary.md`
- `financial_audit_sample.csv`
- any `eval_results.json`
