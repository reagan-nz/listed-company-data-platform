# CNINFO C-Class 889 Non-BSE 1000-like Live — Failure Diagnosis

_生成时间：2026-07-07_

## 1. 执行摘要

基于 [cninfo_c_class_smoke_1000_non_bse_live_report.csv](cninfo_c_class_smoke_1000_non_bse_live_report.csv)（**889** 家 · **6223** live cases · **未新增 CNINFO 请求**）。

| 指标 | 值 |
|------|-----|
| 主判定 pass | **5064** |
| 主判定 fail | **270** |
| security observe_pass | **889** |
| blocked | **14** |
| 429 | **0** |
| http_error cases | **142** |
| Overall | **LIVE_PARTIAL** |

**核心结论：** 失败**非全市场系统性不稳定**，主要由 **26 家主判定 6/6 全失败**（多为 *ST / 退市残留 / 旧代码异常，HTTP 500）与 **runner 将 `empty_but_valid_response` 计为 fail**（89 条，含 star basic 11 家）叠加。剔除全失败异常公司后，basic reachability 由 94.5% 升至约 **97.3%**。**chinext 最稳**；**sse_main** 受异常公司拖累最明显；**dividend 维持 GO（决策）**；**top_float 建议 source_partial**；**security 继续 observe-only**。

## 2. Failure cases 明细

共 **270** 条 `case_result=fail`，已导出 [cninfo_c_class_smoke_1000_non_bse_failure_cases.csv](cninfo_c_class_smoke_1000_non_bse_failure_cases.csv)。

| retrieval_status | count |
|------------------|-------|
| `http_error` | 142 |
| `empty_but_valid_response` | 89 |
| `schema_unexpected` | 25 |
| `blocked` | 14 |

| source_id | fail_count |
|-----------|------------|
| `cninfo_top_float_shareholders_profile` | 58 |
| `cninfo_company_basic_profile` | 49 |
| `cninfo_executive_profile` | 48 |
| `cninfo_share_capital_profile` | 44 |
| `cninfo_top_shareholders_profile` | 42 |
| `cninfo_dividend_financing_profile` | 29 |

## 3. Company-level failure clustering

- **至少 1 个主源 fail 的公司：** **88** 家
- **主判定 6/6 全失败：** **26** 家
- **仅股东源 empty_but_valid：** **4** 家
- **单源失败：** **23** 家
- **多源部分失败：** **35** 家

### 3.1 主判定 6/6 全失败（26 家）

| code | name | board | 典型 status |
|------|------|-------|-------------|
| `000043` | 中航善达 | `szse_main` | `http_error` |
| `000416` | *ST民控 | `szse_main` | `http_error` |
| `000562` | 宏源证券 | `szse_main` | `http_error` |
| `000569` | 长城股份 | `szse_main` | `http_error` |
| `000638` | *ST万方 | `szse_main` | `http_error` |
| `000765` | *ST华信 | `szse_main` | `http_error` |
| `000787` | *ST创智 | `szse_main` | `http_error` |
| `000827` | *ST长兴 | `szse_main` | `http_error` |
| `000982` | 中银绒业 | `szse_main` | `http_error` |
| `002113` | *ST天润 | `szse_main` | `http_error` |
| `002325` | *ST洪涛 | `szse_main` | `http_error` |
| `002503` | *ST搜特 | `szse_main` | `http_error` |
| `002776` | *ST柏龙 | `szse_main` | `http_error` |
| `300116` | *ST保力 | `chinext` | `http_error` |
| `300262` | *ST巴安 | `chinext` | `http_error` |
| `600112` | *ST天成 | `sse_main` | `http_error` |
| `600247` | *ST成城 | `sse_main` | `http_error` |
| `600253` | 天方药业 | `sse_main` | `http_error` |
| `600260` | *ST凯乐 | `sse_main` | `http_error` |
| `600286` | S*ST国瓷 | `sse_main` | `http_error` |
| `600357` | 承德钒钛 | `sse_main` | `http_error` |
| `600393` | ST粤泰 | `sse_main` | `http_error` |
| `600700` | *ST数码 | `sse_main` | `http_error` |
| `600842` | 中西药业 | `sse_main` | `http_error` |
| `601258` | *ST庞大 | `sse_main` | `http_error` |
| `603056` | 德邦股份 | `sse_main` | `http_error` |

分布：szse_main **13** · sse_main **11** · chinext **2**。多为名称含 *ST / 历史退市残留，应在样本清洗层进一步剔除或标记 `abnormal_review`，而非 endpoint 系统性故障。

### 3.2 仅股东源 empty_but_valid（4 家）

| code | name | board | failed sources |
|------|------|-------|----------------|
| `301123` | 奕东电子 | `chinext` | cninfo_top_shareholders_profile |
| `301669` | 高特电子 | `chinext` | cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `688048` | 长光华芯 | `star` | cninfo_top_float_shareholders_profile |
| `688797` | 臻宝科技 | `star` | cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |

### 3.3 单源失败 Top pattern

| source_id | companies |
|-----------|-----------|
| `cninfo_company_basic_profile` | 8 |
| `cninfo_top_float_shareholders_profile` | 5 |
| `cninfo_executive_profile` | 4 |
| `cninfo_share_capital_profile` | 3 |
| `cninfo_dividend_financing_profile` | 2 |
| `cninfo_top_shareholders_profile` | 1 |

### 3.4 全量公司聚类表（88 家）

| code | name | board | failed_source_count | pattern | failed_source_ids |
|------|------|-------|---------------------|---------|-------------------|
| `000043` | 中航善达 | `szse_main` | 6 | `all6_main_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `000416` | *ST民控 | `szse_main` | 6 | `all6_main_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `000562` | 宏源证券 | `szse_main` | 6 | `all6_main_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `000569` | 长城股份 | `szse_main` | 6 | `all6_main_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `000638` | *ST万方 | `szse_main` | 6 | `all6_main_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `000765` | *ST华信 | `szse_main` | 6 | `all6_main_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `000787` | *ST创智 | `szse_main` | 6 | `all6_main_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `000827` | *ST长兴 | `szse_main` | 6 | `all6_main_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `000895` | 双汇发展 | `szse_main` | 1 | `single_source_fail` | cninfo_executive_profile |
| `000982` | 中银绒业 | `szse_main` | 6 | `all6_main_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `002113` | *ST天润 | `szse_main` | 6 | `all6_main_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `002325` | *ST洪涛 | `szse_main` | 6 | `all6_main_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `002503` | *ST搜特 | `szse_main` | 6 | `all6_main_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `002710` | 慈铭体检 | `szse_main` | 3 | `multi_partial_fail` | cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `002776` | *ST柏龙 | `szse_main` | 6 | `all6_main_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `300116` | *ST保力 | `chinext` | 6 | `all6_main_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `300262` | *ST巴安 | `chinext` | 6 | `all6_main_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `300472` | *ST新元 | `chinext` | 2 | `multi_partial_fail` | cninfo_company_basic_profile;cninfo_top_float_shareholders_profile |
| `301123` | 奕东电子 | `chinext` | 1 | `only_shareholder_empty_but_valid` | cninfo_top_shareholders_profile |
| `301295` | 美硕科技 | `chinext` | 1 | `single_source_fail` | cninfo_company_basic_profile |
| `301507` | 民生健康 | `chinext` | 1 | `single_source_fail` | cninfo_company_basic_profile |
| `301578` | 辰奕智能 | `chinext` | 2 | `multi_partial_fail` | cninfo_company_basic_profile;cninfo_top_float_shareholders_profile |
| `301583` | 托伦斯 | `chinext` | 3 | `multi_partial_fail` | cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `301669` | 高特电子 | `chinext` | 2 | `only_shareholder_empty_but_valid` | cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `600007` | 中国国贸 | `sse_main` | 2 | `multi_partial_fail` | cninfo_company_basic_profile;cninfo_executive_profile |
| `600112` | *ST天成 | `sse_main` | 6 | `all6_main_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `600117` | 西宁特钢 | `sse_main` | 1 | `single_source_fail` | cninfo_top_float_shareholders_profile |
| `600186` | 莲花控股 | `sse_main` | 1 | `single_source_fail` | cninfo_company_basic_profile |
| `600187` | *ST国中 | `sse_main` | 1 | `single_source_fail` | cninfo_top_float_shareholders_profile |
| `600202` | 哈空调 | `sse_main` | 1 | `single_source_fail` | cninfo_company_basic_profile |
| `600247` | *ST成城 | `sse_main` | 6 | `all6_main_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `600253` | 天方药业 | `sse_main` | 6 | `all6_main_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `600260` | *ST凯乐 | `sse_main` | 6 | `all6_main_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `600286` | S*ST国瓷 | `sse_main` | 6 | `all6_main_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `600302` | ST标准 | `sse_main` | 1 | `single_source_fail` | cninfo_executive_profile |
| `600328` | 中盐化工 | `sse_main` | 2 | `multi_partial_fail` | cninfo_dividend_financing_profile;cninfo_share_capital_profile |
| `600357` | 承德钒钛 | `sse_main` | 6 | `all6_main_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `600375` | 汉马科技 | `sse_main` | 2 | `multi_partial_fail` | cninfo_share_capital_profile;cninfo_top_shareholders_profile |
| `600393` | ST粤泰 | `sse_main` | 6 | `all6_main_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `600398` | 海澜之家 | `sse_main` | 1 | `single_source_fail` | cninfo_share_capital_profile |
| `600483` | 福能股份 | `sse_main` | 1 | `single_source_fail` | cninfo_top_shareholders_profile |
| `600662` | 外服控股 | `sse_main` | 2 | `multi_partial_fail` | cninfo_executive_profile;cninfo_top_float_shareholders_profile |
| `600700` | *ST数码 | `sse_main` | 6 | `all6_main_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `600716` | 凤凰股份 | `sse_main` | 2 | `multi_partial_fail` | cninfo_executive_profile;cninfo_share_capital_profile |
| `600794` | 保税科技 | `sse_main` | 2 | `multi_partial_fail` | cninfo_executive_profile;cninfo_top_float_shareholders_profile |
| `600842` | 中西药业 | `sse_main` | 6 | `all6_main_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `600881` | 亚泰集团 | `sse_main` | 2 | `multi_partial_fail` | cninfo_executive_profile;cninfo_share_capital_profile |
| `600882` | 妙可蓝多 | `sse_main` | 2 | `multi_partial_fail` | cninfo_executive_profile;cninfo_top_float_shareholders_profile |
| `600958` | 东方证券 | `sse_main` | 1 | `single_source_fail` | cninfo_company_basic_profile |
| `601113` | 华鼎股份 | `sse_main` | 3 | `multi_partial_fail` | cninfo_company_basic_profile;cninfo_executive_profile;cninfo_top_float_shareholders_profile |
| `601206` | 海尔施 | `sse_main` | 3 | `multi_partial_fail` | cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `601258` | *ST庞大 | `sse_main` | 6 | `all6_main_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `601328` | 交通银行 | `sse_main` | 1 | `single_source_fail` | cninfo_top_float_shareholders_profile |
| `601368` | 绿城水务 | `sse_main` | 2 | `multi_partial_fail` | cninfo_company_basic_profile;cninfo_executive_profile |
| `601566` | 九牧王 | `sse_main` | 1 | `single_source_fail` | cninfo_executive_profile |
| `601668` | 中国建筑 | `sse_main` | 2 | `multi_partial_fail` | cninfo_executive_profile;cninfo_top_shareholders_profile |
| `601939` | 建设银行 | `sse_main` | 2 | `multi_partial_fail` | cninfo_company_basic_profile;cninfo_top_float_shareholders_profile |
| `603056` | 德邦股份 | `sse_main` | 6 | `all6_main_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `603107` | 上海汽配 | `sse_main` | 2 | `multi_partial_fail` | cninfo_company_basic_profile;cninfo_top_shareholders_profile |
| `603408` | 建霖家居 | `sse_main` | 1 | `single_source_fail` | cninfo_dividend_financing_profile |
| `603698` | 航天工程 | `sse_main` | 3 | `multi_partial_fail` | cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile |
| `603839` | 安正时尚 | `sse_main` | 1 | `single_source_fail` | cninfo_share_capital_profile |
| `603889` | 新澳股份 | `sse_main` | 2 | `multi_partial_fail` | cninfo_executive_profile;cninfo_top_shareholders_profile |
| `603897` | 长城科技 | `sse_main` | 2 | `multi_partial_fail` | cninfo_share_capital_profile;cninfo_top_float_shareholders_profile |
| `603898` | 好莱客 | `sse_main` | 1 | `single_source_fail` | cninfo_top_float_shareholders_profile |
| `603926` | 铁流股份 | `sse_main` | 1 | `single_source_fail` | cninfo_executive_profile |
| `605028` | 世茂能源 | `sse_main` | 3 | `multi_partial_fail` | cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile |
| `605050` | 福然德 | `sse_main` | 1 | `single_source_fail` | cninfo_top_float_shareholders_profile |
| `688035` | 德邦科技 | `star` | 2 | `multi_partial_fail` | cninfo_share_capital_profile;cninfo_top_float_shareholders_profile |
| `688048` | 长光华芯 | `star` | 1 | `only_shareholder_empty_but_valid` | cninfo_top_float_shareholders_profile |
| `688081` | 兴图新科 | `star` | 3 | `multi_partial_fail` | cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `688082` | 盛美上海 | `star` | 2 | `multi_partial_fail` | cninfo_company_basic_profile;cninfo_top_float_shareholders_profile |
| `688087` | 英科再生 | `star` | 2 | `multi_partial_fail` | cninfo_executive_profile;cninfo_top_float_shareholders_profile |
| `688096` | 京源环保 | `star` | 4 | `multi_partial_fail` | cninfo_company_basic_profile;cninfo_executive_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `688107` | 安路科技 | `star` | 1 | `single_source_fail` | cninfo_share_capital_profile |
| `688168` | 安博通 | `star` | 2 | `multi_partial_fail` | cninfo_company_basic_profile;cninfo_top_shareholders_profile |
| `688187` | 时代电气 | `star` | 3 | `multi_partial_fail` | cninfo_company_basic_profile;cninfo_executive_profile;cninfo_top_float_shareholders_profile |
| `688235` | 百济神州 | `star` | 4 | `multi_partial_fail` | cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `688244` | 永信至诚 | `star` | 3 | `multi_partial_fail` | cninfo_company_basic_profile;cninfo_executive_profile;cninfo_top_float_shareholders_profile |
| `688273` | 麦澜德 | `star` | 1 | `single_source_fail` | cninfo_company_basic_profile |
| `688286` | 敏芯股份 | `star` | 3 | `multi_partial_fail` | cninfo_company_basic_profile;cninfo_executive_profile;cninfo_share_capital_profile |
| `688291` | 金橙子 | `star` | 2 | `multi_partial_fail` | cninfo_company_basic_profile;cninfo_top_float_shareholders_profile |
| `688363` | 华熙生物 | `star` | 2 | `multi_partial_fail` | cninfo_company_basic_profile;cninfo_top_float_shareholders_profile |
| `688468` | 科美诊断 | `star` | 1 | `single_source_fail` | cninfo_company_basic_profile |
| `688539` | 高华科技 | `star` | 1 | `single_source_fail` | cninfo_dividend_financing_profile |
| `688688` | 蚂蚁集团 | `star` | 3 | `multi_partial_fail` | cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `688718` | 唯赛勃 | `star` | 1 | `single_source_fail` | cninfo_company_basic_profile |
| `688797` | 臻宝科技 | `star` | 2 | `only_shareholder_empty_but_valid` | cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |

## 4. Board-level diagnosis

| board | companies | main_cases | pass | fail | blocked | http_error | reachability% | 主要失败 source |
|-------|-----------|------------|------|------|---------|------------|---------------|-----------------|
| `chinext` | 233 | 1398 | 1374 | 24 | 3 | 9 | 98.3% | `cninfo_company_basic_profile`(6), `cninfo_top_float_shareholders_profile`(6), `cninfo_top_shareholders_profile`(5) |
| `sse_main` | 292 | 1752 | 1631 | 121 | 3 | 63 | 93.1% | `cninfo_executive_profile`(26), `cninfo_top_float_shareholders_profile`(25), `cninfo_share_capital_profile`(21) |
| `star` | 125 | 750 | 707 | 43 | 0 | 0 | 94.3% | `cninfo_top_float_shareholders_profile`(13), `cninfo_company_basic_profile`(11), `cninfo_executive_profile`(6) |
| `szse_main` | 239 | 1434 | 1352 | 82 | 8 | 70 | 94.3% | `cninfo_executive_profile`(14), `cninfo_share_capital_profile`(14), `cninfo_top_shareholders_profile`(14) |

### 4.1 板块解读

- **chinext（最稳）：** main reachability **~98.3%**；fail 仅 24/1398；2 家 6/6 全失败（*ST保力、*ST巴安）。
- **sse_main（偏低）：** basic **93.5%**、executive **91.1%**、top_float **91.4%**；**11 家 6/6 全失败**占 fail 大头；剔除后 basic 明显提升。
- **star：** basic pass **91.2%** 但 reachability **100%**（HTTP 200）；11 家 basic fail 均为 **`empty_but_valid_response`**，属 runner 口径而非 HTTP 故障；top_float **89.6%** pass，13 fail 中多数为 empty_but_valid / schema。
- **szse_main：** 各主源 pass **~94%**，接近门槛；**13 家 6/6 全失败**（旧深主板异常代码）是主要拖累。

## 5. Source-level diagnosis

| source_id | pass | fail | reachable | reach% | blocked | http_error | schema_unexpected | valid_empty | empty_but_valid |
|-----------|------|------|-----------|--------|---------|------------|-------------------|-------------|-----------------|
| `cninfo_company_basic_profile` | 840 | 49 | 840 | 94.5% | 3 | 23 | 0 | 0 | 23 |
| `cninfo_dividend_financing_profile` | 860 | 29 | 860 | 96.7% | 2 | 24 | 3 | 34 | 0 |
| `cninfo_executive_profile` | 841 | 48 | 841 | 94.6% | 3 | 23 | 8 | 0 | 14 |
| `cninfo_share_capital_profile` | 845 | 44 | 845 | 95.1% | 1 | 25 | 4 | 0 | 14 |
| `cninfo_top_shareholders_profile` | 847 | 42 | 847 | 95.3% | 2 | 24 | 2 | 0 | 14 |
| `cninfo_top_float_shareholders_profile` | 831 | 58 | 831 | 93.5% | 3 | 23 | 8 | 0 | 24 |
| `cninfo_company_security_profile` | 0 | 0 | 889 | 100.0% | 0 | 0 | 0 | 0 | 0 |

### 5.1 关键判断

- **basic_profile 94.5%：** 主要由 **26 家全源失败** + **23 条 empty_but_valid** 拖累；剔除全失败公司后 pass **~97.3%**。
- **dividend 96.7%：** error_rate 2.9%，**维持 GO（决策）**；不执行 YAML。
- **top_float 93.5%：** 58 fail 中 **24** 为 empty_but_valid；建议标记 **source_partial**（reachable 与 non_empty 分离统计）。
- **security observe-only：** **889/889 observe_pass**，blocked/http_error=0；**继续保持 observe-only**，不绑定主 gate。
- **schema_unexpected 25 条：** 分散于 executive/share_cap/top_float/dividend；多为 `data.records missing`，需个案而非改 endpoint。

## 6. 与 195 non-BSE 对比

| 维度 | 195 non-BSE (172) | 889 non-BSE |
|------|-------------------|-------------|
| 规模 | 172 | 889 |
| 主判定 pass% | ~97%+ | 5064/5334=**95.0%** |
| 失败形态 | 少数 *ST + 股东 empty | 26 家全失败 + 政策性 empty_but_valid |
| 结论 | 稳定 | 放大后暴露**样本清洗缺口**，非 endpoint 全面退化 |

## 7. Gate 与下一步建议

| 问题 | 建议 |
|------|------|
| non-BSE C-class 是否继续推进？ | **YES（CONDITIONAL）** — 主源整体可用，fail 可解释 |
| 是否重跑 889 全量？ | **NO** — 成本高；优先清洗样本 + 针对性重试 |
| 是否只重试 failed companies？ | **YES** — 建议对 **88 家** fail 公司做 targeted retry（或剔除 26 家 abnormal 后重跑余下） |
| dividend_history YAML backfill | **GO（决策 only）** — 96.7% reach；**不执行 YAML** |
| 哪些 source 应 partial？ | **top_float**（及股东源 empty_but_valid 口径）、 scattered **schema_unexpected** |
| full-market non-BSE planning | **可进入规划** — 前提：扩充 abnormal_review 清洗规则；runner 修正 empty_but_valid 计 fail |
| targeted retry 优先级 | ① 26 家 6/6 → 样本剔除/标记 ② 12 家 blocked ③ 单源 fail 23 家 |

## 8. 红线确认

- 本轮 **无 live** · **无 CNINFO** · **无 YAML backfill** · **无 DB** · **无 verified**

## 9. 参考

- [live report](cninfo_c_class_smoke_1000_non_bse_live_report.csv)
- [live summary](cninfo_c_class_smoke_1000_non_bse_live_summary.md)
- [failure cases](cninfo_c_class_smoke_1000_non_bse_failure_cases.csv)
- [universe split plan](../plans/cninfo_c_class_universe_split_and_sample_cleaning_plan.md)
- [200 BSE diagnosis](cninfo_c_class_scale_smoke_200_bse_diagnosis.md)
