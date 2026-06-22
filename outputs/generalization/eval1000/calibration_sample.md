# Manual Calibration Worksheet - eval200 'plausible' proxy

_Sample: 60 cells (36 proxy-plausible, 24 not). Fixed seed -> reproducible._

## How to grade

For each row, open `source_url`, go to `page`, and compare against `evidence_sentence` / `value_preview`. Put one grade in `manual_grade` (in the CSV):

- **CORRECT** - right field content located.
- **PARTIAL** - right region but messy/incomplete/mislocated table.
- **WRONG** - extracted content points to the wrong place / not this field.
- **MISSED** - extractor returned not_found/nothing usable, but the field DOES exist in the report (recall false-negative).
- **ABSENT-OK** - `not_found` is the correct answer (field genuinely N/A; no data invented).

Then run `python lab/calibration_sample.py --score <filled.csv>` for the summary.

| id | code | field | proxy_status | plausible | page | evidence (preview) |
|---|---|---|---|---|---|---|
| 1 | 300537 | risk_factors | partial | N | 257 | 面临的风险，设定适当的风险可接受水平并设计相应 |
| 2 | 830964 | rnd_investment | not_found | N | 25 | 研发投入总额占营业收入的比重较上年发生显著变化的原因 |
| 3 | 832149 | rnd_investment | not_found | N | 31 | 研发投入总额占营业收入的比重较上年发生显著变化的原因 |
| 4 | 002573 | revenue_by_segment | found | Y | 22 | 分行业 生态环保业 8,716,335,330.31 7,249,101,839.23 16.83% 1.18% 2.34% -0.94% 分产品 大气业务 1 |
| 5 | 603697 | major_subsidiaries | found | Y | 24 | 主要控股参股公司分析 |
| 6 | 873152 | top_customers | partial | N | 19 | 主要客户情况 |
| 7 | 300507 | mda | found | Y | 12 | 管理层讨论与分析 一、报告期内公司所处行业情况 公司需遵守《深圳证券交易所上市公司自律监管指引第3 号——行业信息披露》中的“汽车制造相关业务”的披露要求 公司 |
| 8 | 688338 | revenue_by_segment | found | Y | 36 | 主营业务分行业情况 |
| 9 | 688348 | rnd_investment | found | Y | 27 | 研发投入合计 |
| 10 | 301419 | risk_factors | partial | N | 188 | 面临的风险，这些风险管理政 |
| 11 | 300057 | major_products | found | Y | 13 | 主要产品 产品用途 铝加工业务 铝箔、铝板带、涂碳箔 主要应用于电池、电容器、印制电路板等电子元器件领域；食 |
| 12 | 301526 | risk_factors | found | Y | 35 | 可能面对的风险及应对措施 |
| 13 | 837344 | top_suppliers | partial | N | 34 | 主要供应商、客户等。 |
| 14 | 601939 | top_suppliers | not_found | N | None |  |
| 15 | 835438 | revenue_by_region | found | Y | 20 | 分地区 营业收入 营业成本 毛利率% 营业收入 比上年同 期 增减% 营业成本 比上年同 期 增减% 毛利率比上 年同期增减 国内 559,615,483.46 |
| 16 | 832145 | top_customers | found | Y | 27 | 主要客户情况 |
| 17 | 301123 | industry_discussion | found | Y | 35 | 行业发展乐观 |
| 18 | 688772 | industry_discussion | found | Y | 16 | 所处行业情况 1、 行业的发展阶段、基本特点、主要技术门槛 （1）行业的发展及特点 根据应用领域的不同，锂离子电池可以分为消费类电池、动力及储能类电池。公司产品 |
| 19 | 920305 | top_suppliers | found | Y | 19 | 主要供应商情况 |
| 20 | 688543 | rnd_investment | not_found | N | 31 | 研发投入，进一步加大在导弹（火箭）固 |
| 21 | 601988 | top_suppliers | not_found | N | None |  |
| 22 | 688508 | risk_factors | found | Y | 24 | 风险因素 (一) 尚未盈利的风险 □适用 √不适用 (二) 业绩大幅下滑或亏损的风险 □适用 √不适用 (三) 核心竞争力风险 √适用 □不适用 （1）技术升级 |
| 23 | 920367 | top_customers | partial | N | 30 | 主要客户合同相关条款，评价新赣江药业公司的收入确认政策是否符合企业会计准则的 |
| 24 | 300424 | main_business_segments | found | Y | 14 | 报告期内公司从事的主要业务 （一）公司主营业务 航新科技自成立以来一直秉承“担当有为，精细致胜”的精神和“以科技护航，为梦想创新”的核心价值观，以“航 空报国” |
| 25 | 832491 | top_suppliers | partial | N | 31 | 主要供应商； |
| 26 | 300451 | major_products | found | Y | 14 | 主要产品及服务 自2021 年以来，随着云计算、大数据、物联网、人工智能等最新IT 技术在医疗行业场景中全面深入应用，公司通 过“慧康云”的发展战略，以数据驱动 |
| 27 | 300294 | rnd_investment | found | Y | 23 | 研发投入金额（元） |
| 28 | 002718 | major_products | found | Y | 11 | 报告期内公司从事的主要业务 （一）公司基本情况 公司2004 年发明集成吊顶，是集成吊顶行业的开创者。公司以“设计更好的顶与墙，为每个人提供更自由的场景生 活方 |
| 29 | 300496 | risk_factors | partial | N | 116 | 面临的风险水平。 |
| 30 | 688325 | revenue_by_region | found | Y | 31 | 主营业务分地区情况 |
| 31 | 300314 | top_customers | found | Y | 27 | 前五名客户合计销售金额（元） |
| 32 | 001326 | rnd_investment | not_found | N | 25 | 研发投入总额占营业收入的比重较上年发生显著变化的原因 |
| 33 | 001380 | rnd_investment | found | Y | 26 | 研发投入资本化的金额（元） |
| 34 | 301308 | top_customers | found | Y | 31 | 前五名客户合计销售金额（元） |
| 35 | 920060 | rnd_investment | not_found | N | 22 | 研发投入总额占营业收入的比重较上年发生显著变化的原因 |
| 36 | 300010 | revenue_by_region | found | Y | 18 | 分地区 北京 742,977,143.34 98.17% 974,643,806.52 98.17% -23.77% 华东 13,851,050.31 1.83 |
| 37 | 831906 | rnd_investment | not_found | N | 31 | 研发投入总额占营业收入的比重较上年发生显著变化的原因 |
| 38 | 600958 | top_suppliers | partial | N | 60 | 主要供应商。 |
| 39 | 002003 | risk_factors | found | Y | 31 | 可能面对的风险 面对当前的国内外宏观环境及经济形势，公司预计未来将可能面临以下风险： 1、宏观经济与景气度下行的风险。服饰辅料作为传统日用消费品，其发展受经济景 |
| 40 | 002197 | industry_discussion | found | Y | 11 | 公司所处行业情况 |
| 41 | 688702 | revenue_by_segment | found | Y | 30 | 主营业务分行业、分产品、分地区、分销售模式情况的说明 |
| 42 | 000166 | rnd_investment | partial | N | 134 | 研发费用以及IT人员投入等。 |
| 43 | 601880 | risk_factors | partial | N | 34 | 可能面对的风险 √适用 □不适用 2025 年，世界经济发展不确定因素增多，贸易保护主义和地缘政治风险可能加剧，影响全球供应链稳定和国际贸易发展；环渤海大型港口 |
| 44 | 600186 | top_suppliers | found | Y | 17 | 前五名供应商采购额139,586.51万元，占年度采购总额75.20%； |
| 45 | 600927 | industry_discussion | found | Y | 23 | 公司所处行业情况 |
| 46 | 601089 | mda | found | Y | 10 | 管理层讨论与分析 一、经营情况讨论与分析 2024 年，医药行业受人口老龄化加剧、政策监管趋严、技术驱动产业升级以及用药习惯提升 等影响，为医药企业的经营活动带 |
| 47 | 301002 | main_business_segments | found | Y | 19 | 报告期内公司从事的主要业务 公司需遵守《深圳证券交易所上市公司自律监管指引第4 号——创业板行业信息披露》中的“LED 产业链相关业务”的 披露要求 1、LED |
| 48 | 600063 | mda | found | Y | 11 | 管理层讨论与分析 一、经营情况讨论与分析 2024 年，面对全球经济增速放缓、国内房地产行业深度调整等内外部风险与挑战，公司管理 层和全体干部职工在董事会的正确 |
| 49 | 688320 | main_business_segments | found | Y | 38 | 公司主要从事工业自动化产品的研发、生产、销售及应用集成。 |
| 50 | 002302 | rnd_investment | not_found | N | 23 | 研发投入总额占营业收入的比重较上年发生显著变化的原因 |
| 51 | 603876 | major_products | found | Y | 16 | 主要产品 单位 生产量 销售量 库存量 生产量比 上年增减 （%） 销售量比 上年增减 （%） 库存量比 上年增减 （%） 铝箔产品 吨 834,274.46  |
| 52 | 300314 | main_business_segments | partial | N | 49 | 主营业务分析—研发投入”中列示的相关信息。 |
| 53 | 002086 | risk_factors | partial | N | 37 | 风险因素及对策 |
| 54 | 300292 | main_business_segments | found | Y | 12 | 报告期内公司从事的主要业务 （一）公司的主要产品及服务 1、移动信息服务 1.1 从事的主要业务、主要产品及其用途 公司旗下全资子公司国都互联主要从事企业移动信 |
| 55 | 002556 | major_subsidiaries | found | Y | 55 | 主要控股参股公司情况说明 |
| 56 | 002970 | risk_factors | partial | N | 2 | 风险提示： |
| 57 | 300726 | major_subsidiaries | found | Y | 27 | 主要控股参股公司情况说明 |
| 58 | 833030 | rnd_investment | not_found | N | 27 | 研发投入总额占营业收入的比重较上年发生显著变化的原因 |
| 59 | 601328 | revenue_by_region | partial | N | 45 | 按地区划分的贷款及不良贷款分布情况 |
| 60 | 603169 | top_suppliers | found | Y | 25 | 前五名供应商采购额88,106.67 万元，占年度采购总额20.96%； |
