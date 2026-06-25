# R&D residual fix #32c-R0 dry-run summary

_Generated: 2026-06-25 | experimental candidate selector over cached PDFs; no profile writes_

## Verdict interpretation

- **P0 mandatory targets:** 7/8 improved under experimental selector.
- **Controls:** 1/5 regressed — need production fallback / tighter guards before port.
- Overall verdict **FAIL** — P0 signal strong; refine before production merge.

## Verdict: **FAIL**
| Gate | Result |
|---|---|
| Rows evaluated (targets + controls) | **207** |
| Target rows improved (experimental vs stored strict) | **117** |
| Target rows regressed | **0** |
| Mandatory examples improved | **7/8** |
| P0 rows improved | **32** |
| Control rows regressed | **1** |
| Some P0 rows show improved selection | **PASS** |
| No obvious control downgrade | **FAIL** |
| No profile/eval/audit writes | **PASS** |

## Files changed

- `lab/rnd_residual_fix_32c_dryrun.py` (new)
- `outputs/generalization/full_market_2024/rnd_residual_fix_32c_dryrun_summary.md` (new)

## Scope

- R&D P0/P1 residual candidates from `revenue_rnd_residual_candidates_32.csv`
- Mandatory examples: 600011, 600020, 301221, 000333, 688081, 600029, 600115, 600844
- Plus representative P0 codes from CSV
- Clean strict-usable controls: 000063, 002415, 300750, 600519, 601012, 688111
- Compares **stored** vs **fresh extract_field()** vs **experimental selector** (dry-run only)

## Target examples (mandatory)

| Code | Name | Stored | Fresh | Experimental | Exp reason |
|---|---|---|---|---|---|
| 600011 | 华能国际 | partial | partial | **usable** | total R&D label '研发投入合计' amount>=100000 |
| 600020 | 中原高速 | partial | partial | **usable** | total R&D label '研发投入合计' amount>=100000 |
| 301221 | 光庭信息 | partial | partial | **usable** | total R&D label '研发投入合计' amount>=100000 |
| 000333 | 美的集团 | partial | partial | **partial** | status=partial |
| 688081 | 兴图新科 | not_found_unverified | not_found_unverified | **usable** | total R&D label '研发投入合计' amount>=100000 |
| 600029 | 南方航空 | not_found_unverified | not_found_unverified | **usable** | total R&D label '研发投入合计' amount>=100000 |
| 600115 | 中国东航 | not_found_unverified | not_found_unverified | **usable** | total R&D label '研发投入合计' amount>=100000 |
| 600844 | 金煤科技 | not_found_unverified | not_found_unverified | **usable** | total R&D label '研发投入合计' amount>=100000 |

## Improved targets

| Code | Name | P | Stored → Exp | Stored preview → Exp preview |
|---|---|---|---|---|
| 301221 | 光庭信息 | P2 | partial → **usable** | 研发投入合计=7,021.75 万元 → 研发投入合计=70,217,500 |
| 600011 | 华能国际 | P0 | partial → **usable** | 研发费用=1,658,380,654 → 研发投入合计=1,696,000,000 |
| 600019 | 宝钢股份 | P1 | partial → **usable** | 研发投入合计=25,044; 费用化研发投入=3,779 → 研发投入合计=25,044,000,000 |
| 600020 | 中原高速 | P0 | partial → **usable** | 研发费用=500,000.00 → 研发投入合计=6,407,300 |
| 600026 | 中远海能 | P1 | partial → **usable** | 研发投入合计=5,405.70; 费用化研发投入=5,200.59 → 研发投入合计=54,057,000 |
| 600029 | 南方航空 | P0 | not_found_unverified → **usable** | 研发投入合计 545 研发投入总额占营业收入比例（%） 0.31 研发投入资本化的比重（%） 0.18 → 研发投入合计=545,000,000 |
| 600057 | 厦门象屿 | P0 | partial → **usable** | 费用化研发投入=9,622.42 → 研发投入合计=116,710,200 |
| 600058 | 五矿发展 | P1 | partial → **usable** | 研发投入合计=4,800.92; 费用化研发投入=1,372.21 → 研发投入合计=48,009,200 |
| 600064 | 南京高科 | P1 | partial → **usable** | 研发投入合计=4,121.08 → 研发投入合计=41,210,800 |
| 600097 | 开创国际 | P0 | not_found_unverified → **usable** | 研发投入总额占营业收入比例（%） 0.05 研发投入资本化的比重（%） (2).研发人员情况表 □适用 √不适用 (3) → 研发投入合计=1,228,000 |
| 600113 | 浙江东日 | P0 | not_found_unverified → **usable** | 研发投入， 加快培育和发展科技创新能力，切实推进公司业务向产业链上下游延伸，较好地完成了年度的各 项工作任务。 （一）夯 → 研发投入合计=9,036,200 |
| 600115 | 中国东航 | P0 | not_found_unverified → **usable** | 研发投入合计 350 研发投入总额占营业收入比例（%） 0.26 研发投入资本化的比重（%） 2.00 → 研发投入合计=350,000,000 |
| 600125 | 铁龙物流 | P0 | not_found_unverified → **usable** | 研发投入合计 28.25 研发投入总额占营业收入比例（%） 0.002 研发投入资本化的比重（%） (2).研发人员情况 → 研发投入合计=282,500 |
| 600135 | 乐凯胶片 | P1 | partial → **usable** | 研发投入合计=10,159.19 → 研发投入合计=101,591,900 |
| 600221 | 海航控股 | P1 | partial → **usable** | 研发投入合计=36,483 → 研发投入合计=36,483,000 |
| 600236 | 桂冠电力 | P1 | partial → **usable** | 研发投入合计=25,095.67 → 研发投入合计=250,956,700 |
| 600293 | 三峡新材 | P1 | partial → **usable** | 研发投入合计=7,111.90 → 研发投入合计=71,119,000 |
| 600323 | 瀚蓝环境 | P1 | partial → **usable** | 研发投入合计=14,204.34; 费用化研发投入=7,366.91 → 研发投入合计=142,043,400 |
| 600343 | 航天动力 | P1 | partial → **usable** | 研发投入合计=5,541.76; 费用化研发投入=4,933.12 → 研发投入合计=55,417,600 |
| 600346 | 恒力石化 | P0 | partial → **usable** | 研发费用=170,288.42 → 研发投入合计=1,703,000,000 |
| 600354 | 敦煌种业 | P0 | partial → **usable** | 费用化研发投入=20,312,119.73 → 研发投入合计=26,459,835 |
| 600362 | 江西铜业 | P0 | not_found_unverified → **usable** | 研发投入合计 60.12 研发投入总额占营业收入比例（%） 1.15 研发投入资本化的比重（%） 8.17 (2).研发 → 研发投入合计=6,012,000,000 |
| 600415 | 小商品城 | P1 | partial → **usable** | 研发投入合计=5,218.95; 费用化研发投入=2,322.14 → 研发投入合计=52,189,500 |
| 600425 | 青松建化 | P1 | partial → **usable** | 研发投入合计=10,382.19 → 研发投入合计=103,821,900 |
| 600487 | 亨通光电 | P0 | partial → **usable** | 费用化研发投入=1,741,785,134.75 → 研发投入合计=1,894,602,593 |
| 600488 | 津药药业 | P1 | partial → **usable** | 研发投入合计=24,763.65; 费用化研发投入=20,449.20 → 研发投入合计=247,636,500 |
| 600525 | ST长园 | P1 | partial → **usable** | 研发投入合计=87,271.59; 费用化研发投入=86,991.96 → 研发投入合计=872,715,900 |
| 600548 | 深高速 | P1 | partial → **usable** | 研发投入合计=32,931 → 研发投入合计=32,931,000 |
| 600565 | ST迪马 | P0 | partial → **usable** | 费用化研发投入=46,326,410.65 → 研发投入合计=51,565,213 |
| 600613 | 神奇制药 | P1 | partial → **usable** | 研发投入合计=3,288.51 → 研发投入合计=32,885,100 |
| 600668 | 尖峰集团 | P1 | partial → **usable** | 研发投入合计=12,633.60; 费用化研发投入=10,589.79 → 研发投入合计=126,336,000 |
| 600710 | 苏美达 | P1 | partial → **usable** | 研发投入合计=47,630.93; 费用化研发投入=38,287.13 → 研发投入合计=476,309,300 |
| 600733 | 北汽蓝谷 | P0 | partial → **usable** | 费用化研发投入=94,380,985.37 → 研发投入合计=3,191,257,789 |
| 600737 | 中粮糖业 | P1 | partial → **usable** | 研发投入合计=5,654.04 → 研发投入合计=56,540,400 |
| 600750 | 华润江中 | P1 | partial → **usable** | 研发投入合计=21,357.87; 费用化研发投入=10,774.09 → 研发投入合计=213,578,700 |
| 600798 | 宁波海运 | P0 | not_found_unverified → **usable** | 研发投入合计 18.82 研发投入总额占营业收入比例（%） 0.01% 研发投入资本化的比重（%） (2).研发人员情况 → 研发投入合计=188,200 |
| 600808 | 马钢股份 | P0 | partial → **usable** | 研发费用=1,103,101,885 → 研发投入合计=3,646,000,000 |
| 600826 | 兰生股份 | P0 | not_found_unverified → **usable** | 研发投入总额占营业收入比例（%） 0.11 研发投入资本化的比重（%） - (2).研发人员情况表 √适用□不适用 公司 → 研发投入合计=1,848,800 |
| 600844 | 金煤科技 | P0 | not_found_unverified → **usable** | 研发费用减少，主要原因系报告期对纳入口径进行合规性调减所致。 经营活动产生的现金流量净额变动原因说明：经营活动产生的现金 → 研发投入合计=2,161,600 |
| 600855 | 航天长峰 | P1 | partial → **usable** | 研发投入合计=9,204.70; 费用化研发投入=8,845.67 → 研发投入合计=92,047,000 |
| 600900 | 长江电力 | P0 | partial → **usable** | 研发费用=890,719,278.34 → 研发投入合计=2,311,277,700 |
| 600905 | 三峡能源 | P1 | partial → **usable** | 研发投入合计=76,333.35; 研发投入=7.63 亿元 → 研发投入合计=763,333,500 |
| 600938 | 中国海油 | P1 | partial → **usable** | 研发投入合计=45.06亿元; 费用化研发投入=34.36亿元 → 研发投入合计=4,506,000,000 |
| 600960 | 渤海汽车 | P1 | partial → **usable** | 研发投入合计=9,134.26 → 研发投入合计=91,342,600 |
| 600971 | 恒源煤电 | P1 | partial → **usable** | 研发投入合计=37,951.22 → 研发投入合计=379,512,200 |
| 600988 | 赤峰黄金 | P1 | partial → **usable** | 研发投入合计=6,361.59 → 研发投入合计=63,615,900 |
| 601088 | 中国神华 | P1 | partial → **usable** | 研发投入合计=4,148; 费用化研发投入=2,727 → 研发投入合计=4,148,000,000 |
| 601158 | 重庆水务 | P1 | partial → **usable** | 研发投入合计=1,928.17; 费用化研发投入=1,897.06 → 研发投入合计=19,281,700 |
| 601186 | 中国铁建 | P0 | partial → **usable** | 费用化研发投入=25,713,270 → 研发投入合计=25,733,643,000 |
| 601238 | 广汽集团 | P0 | partial → **usable** | 研发费用=0.78 亿元 → 研发投入合计=7,508,000,000 |
| 601566 | 九牧王 | P1 | partial → **usable** | 研发投入合计=4,108.73 → 研发投入合计=41,087,300 |
| 601727 | 上海电气 | P0 | not_found_unverified → **usable** | 研发投入总额占营业收入比例（%） 4.9 研发投入资本化的比重（%） 0.5 (2).研发人员情况表 √适用 □不适用  → 研发投入合计=5,694,000,000 |
| 601799 | 星宇股份 | P1 | partial → **usable** | 研发投入合计=65,549.27 → 研发投入合计=655,492,700 |
| 601808 | 中海油服 | P1 | partial → **usable** | 研发投入合计=1,782.2; 费用化研发投入=1,384.9 → 研发投入合计=1,782,200,000 |
| 601865 | 福莱特 | P0 | not_found_unverified → **usable** | 研发投入总额占营业收入比例（%） 3.24 研发投入资本化的比重（%） - (2).研发人员情况表 √适用 □不适用 公 → 研发投入合计=604,790,000 |
| 601898 | 中煤能源 | P0 | not_found_unverified → **usable** | 研发投入总额占营业收入比例（%） 2.24 研发投入资本化的比重（%） 26.43 注：相关统计口径参照国家统计局《关于 → 研发投入合计=4,237,000,000 |
| 601969 | 海南矿业 | P1 | partial → **usable** | 研发投入合计=50,527.37 → 研发投入合计=50,527,370 |
| 603000 | 人民网 | P0 | partial → **usable** | 费用化研发投入=11,522.28 万元 → 研发投入合计=125,766,096 |
| 603031 | 安孚科技 | P0 | partial → **usable** | 费用化研发投入=135,854,472.84 → 研发投入合计=135,854,474 |
| 603065 | 宿迁联盛 | P1 | partial → **usable** | 研发投入合计=3,463.62 → 研发投入合计=34,636,200 |
| 603068 | 博通集成 | P1 | partial → **usable** | 研发投入合计=27,309.62 → 研发投入合计=273,096,200 |
| 603100 | 川仪股份 | P1 | partial → **usable** | 研发投入合计=53,522.82 → 研发投入合计=535,228,200 |
| 603107 | 上海汽配 | P1 | partial → **usable** | 研发投入合计=6,588.37 → 研发投入合计=65,883,700 |
| 603191 | 望变电气 | P1 | partial → **usable** | 研发投入合计=14,747.59 → 研发投入合计=147,475,900 |
| 603299 | 苏盐井神 | P1 | partial → **usable** | 研发投入合计=23,903.45 → 研发投入合计=239,034,500 |
| 603698 | 航天工程 | P0 | partial → **usable** | 费用化研发投入=246,676,800.81 → 研发投入合计=246,711,585 |
| 603737 | 三棵树 | P1 | partial → **usable** | 研发投入合计=28,934.58 → 研发投入合计=289,345,800 |
| 603776 | 永安行 | P0 | partial → **usable** | 研发费用=35,306,135.73 → 研发投入合计=35,306,136 |
| 603855 | 华荣股份 | P1 | partial → **usable** | 研发投入合计=21,550.73 → 研发投入合计=215,507,300 |
| 603880 | 南卫股份 | P1 | partial → **usable** | 研发投入合计=2,872.19 → 研发投入合计=28,721,900 |
| 605199 | ST葫芦娃 | P0 | partial → **usable** | 费用化研发投入=202,080,443.80 → 研发投入合计=249,539,785 |
| 605358 | 立昂微 | P1 | partial → **usable** | 研发投入合计=29,038.32 → 研发投入合计=290,383,200 |
| 605598 | 上海港湾 | P1 | partial → **usable** | 研发投入合计=4,058.39 → 研发投入合计=40,583,900 |
| 688047 | 龙芯中科 | P1 | partial → **usable** | 研发投入合计=53,120.25 → 研发投入合计=531,202,500 |
| 688049 | 炬芯科技 | P1 | partial → **usable** | 研发投入合计=21,512.39; 研发费用=21,512.39 万元 → 研发投入合计=215,123,900 |
| 688056 | 莱伯泰科 | P1 | partial → **usable** | 研发投入合计=5,126.93 → 研发投入合计=51,269,300 |
| 688081 | 兴图新科 | P0 | not_found_unverified → **usable** | 研发投入 35,638,014.38 32,066,192.73 11.14 资本化研发投入 5,113,367.43  → 研发投入合计=40,751,382 |
| 688085 | 三友医疗 | P1 | partial → **usable** | 研发投入合计=8,428.84; 研发费用=8,428.84 万元 → 研发投入合计=84,288,400 |
| 688097 | 博众精工 | P1 | partial → **usable** | 研发投入合计=51,404.42 → 研发投入合计=514,044,200 |
| 688115 | 思林杰 | P1 | partial → **usable** | 研发投入合计=4,923.94 → 研发投入合计=49,239,400 |
| 688116 | 天奈科技 | P1 | partial → **usable** | 研发投入合计=10,932.69; 研发费用=1,448.64 万元 → 研发投入合计=109,326,900 |
| 688126 | 沪硅产业 | P1 | partial → **usable** | 研发投入合计=26,681.71 → 研发投入合计=266,817,100 |
| 688165 | 埃夫特 | P1 | partial → **usable** | 研发投入合计=13,341.22; 研发投入总额=13,341.22 万元 → 研发投入合计=133,412,200 |
| 688181 | 八亿时空 | P1 | partial → **usable** | 研发投入合计=8,802.95 → 研发投入合计=88,029,500 |
| 688217 | 睿昂基因 | P1 | partial → **usable** | 研发投入合计=6,247.07 → 研发投入合计=62,470,700 |
| 688244 | 永信至诚 | P1 | partial → **usable** | 研发投入合计=9,266.42 → 研发投入合计=92,664,200 |
| 688295 | 中复神鹰 | P1 | partial → **usable** | 研发投入合计=19,022.63 → 研发投入合计=190,226,300 |
| 688303 | 大全能源 | P1 | partial → **usable** | 研发投入合计=38,705.87 → 研发投入合计=387,058,700 |
| 688320 | 禾川科技 | P1 | partial → **usable** | 研发投入合计=16,093.03 → 研发投入合计=160,930,300 |
| 688336 | 三生国健 | P1 | partial → **usable** | 研发投入合计=54,059.70 → 研发投入合计=540,597,000 |
| 688345 | 博力威 | P1 | partial → **usable** | 研发投入合计=13,391.45 → 研发投入合计=133,914,500 |
| 688363 | 华熙生物 | P1 | partial → **usable** | 研发投入合计=46,624.98 → 研发投入合计=466,249,800 |
| 688376 | 美埃科技 | P1 | partial → **usable** | 研发投入合计=7,785.56 → 研发投入合计=77,855,600 |
| 688382 | 益方生物 | P1 | partial → **usable** | 研发投入合计=38,434.70 → 研发投入合计=384,347,000 |
| 688409 | 富创精密 | P1 | partial → **usable** | 研发投入合计=22,139.81 → 研发投入合计=221,398,100 |
| 688425 | 铁建重工 | P1 | partial → **usable** | 研发投入合计=91,595.10 → 研发投入合计=915,951,000 |
| 688429 | 时创能源 | P0 | not_found_unverified → **usable** | 研发费用和营业成本中确认了相应的股份支付金额。 4、现金流 √适用□不适用 单位：元币种：人民币 项目 本期数 上年同期 → 研发投入合计=231,489,952 |
| 688432 | 有研硅 | P1 | partial → **usable** | 研发投入合计=7,828.07 → 研发投入合计=78,280,700 |
| 688466 | 金科环境 | P1 | partial → **usable** | 研发投入合计=2,948.60 → 研发投入合计=29,486,000 |
| 688509 | 正元地信 | P1 | partial → **usable** | 研发投入合计=5,799.13 → 研发投入合计=57,991,300 |
| 688525 | 佰维存储 | P1 | partial → **usable** | 研发投入合计=44,743.21 → 研发投入合计=447,432,100 |
| 688538 | 和辉光电 | P1 | partial → **usable** | 研发投入合计=49,526.92 → 研发投入合计=495,269,200 |
| 688545 | 兴福电子 | P1 | partial → **usable** | 研发投入合计=7,692.30 → 研发投入合计=76,923,000 |
| 688571 | 杭华股份 | P0 | partial → **usable** | 研发费用=55,043,208.13 → 研发投入合计=55,043,208 |
| 688584 | 上海合晶 | P1 | partial → **usable** | 研发投入合计=9,992.77 → 研发投入合计=99,927,700 |
| 688606 | 奥泰生物 | P1 | partial → **usable** | 研发投入合计=9,582.49 → 研发投入合计=95,824,900 |
| 688612 | 威迈斯 | P1 | partial → **usable** | 研发投入合计=38,528.94 → 研发投入合计=385,289,400 |
| 688653 | 康希通信 | P1 | partial → **usable** | 研发投入合计=10,765.20 → 研发投入合计=107,652,000 |
| 688656 | 浩欧博 | P1 | partial → **usable** | 研发投入合计=4,626.90 → 研发投入合计=46,269,000 |
| 688657 | 浩辰软件 | P1 | partial → **usable** | 研发投入合计=8,419.28 → 研发投入合计=84,192,800 |
| 688661 | 和林微纳 | P1 | partial → **usable** | 研发投入合计=5,694.27 → 研发投入合计=56,942,700 |
| 688667 | 菱电电控 | P1 | partial → **usable** | 研发投入合计=15,737.07 → 研发投入合计=157,370,700 |
| 688679 | 通源环境 | P1 | partial → **usable** | 研发投入合计=4,840.39 → 研发投入合计=48,403,900 |
| 688690 | 纳微科技 | P1 | partial → **usable** | 研发投入合计=17,716.56 → 研发投入合计=177,165,600 |
| 688702 | 盛科通信 | P1 | partial → **usable** | 研发投入合计=42,846.10 → 研发投入合计=428,461,000 |
| 688709 | 成都华微 | P1 | partial → **usable** | 研发投入合计=15,374.30 → 研发投入合计=153,743,000 |
| 688733 | 壹石通 | P1 | partial → **usable** | 研发投入合计=4,828.31 → 研发投入合计=48,283,100 |

## Regressed targets

_None_

## Controls

| Code | Stored | Fresh | Experimental | Regressed? |
|---|---|---|---|---|
| 002415 | usable | usable | partial | yes |
| 300750 | usable | usable | usable | no |
| 600519 | usable | usable | usable | no |
| 601012 | usable | usable | usable | no |
| 688111 | usable | usable | usable | no |

## Failure / not-solved cases

- **000333** 美的集团: stored=partial, exp=partial — narrative_or_mixed_unit_partial

## Recommended next step

1. **Refine experiment** — add control-safe fallback (keep production extract when situation-table miss).
2. **Then implement production helper** for situation-table-first path only.
3. Re-run dry-run until controls pass; defer refresh/apply until PASS.

## Safe to commit

- `lab/rnd_residual_fix_32c_dryrun.py`
- `outputs/generalization/full_market_2024/rnd_residual_fix_32c_dryrun_summary.md`

## Do not commit

- Profiles, eval_results, audit summaries, refresh CSVs, SQLite, YAML

