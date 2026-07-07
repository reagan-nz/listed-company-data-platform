# CNINFO C-Class Stable 200 Non-BSE Live — Diagnosis

_生成时间：2026-07-07_

## 1. 执行摘要

基于 [cninfo_c_class_stable_200_live_report.csv](cninfo_c_class_stable_200_live_report.csv)（**200** 家 · **1400** cases · **未新增 CNINFO**）。

| 指标 | 值 |
|------|-----|
| 主判定 pass | **1069** |
| 主判定 fail | **131** |
| security observe_pass | **200** |
| blocked / 429 / http_error | **0** / **0** / **0** |
| Overall | **LIVE_PARTIAL** |

**核心结论：** fail **不是网络问题**（http_error=0），而是 **114 条 `schema_unexpected`（`data.records missing`）** + **17 条 `empty_but_valid_response`**（含 basic 15）。**30 家公司**至少 1 主源 fail，其中 **12 家 6/6 全失败** — 说明 **six_fail_hold 清洗不足**，stable 200 仍混入异常公司。**sse_main/chinext 偏弱**（reach ~82–84%），**star/szse_main 稳定**（~97%）。**dividend 90%** 低于 889 的 96.7%，主因是与其它源共享的 `records missing` 簇，非分红 endpoint 单独退化。

## 2. Failure cases 明细

共 **131** 条 fail → [cninfo_c_class_stable_200_failure_cases.csv](cninfo_c_class_stable_200_failure_cases.csv)

### 2.1 retrieval_status 分布

| status | count |
|--------|-------|
| `schema_unexpected` | 114 |
| `empty_but_valid_response` | 17 |

### 2.2 为何 http_error=0 但 fail=131？

- 全部 fail 的 `retrieval_status` 仅为 **`schema_unexpected`（114）** 或 **`empty_but_valid_response`（17）**
- HTTP 多为 **200**；JSON 层成功，但 runner 期望的 `data.records` **路径缺失** → 计为 `schema_unexpected` + `case_result=fail`
- **不是** blocked / 429 / 连接错误

### 2.3 schema_unexpected 形态

| error_message | count |
|---------------|-------|
| `data.records missing` | **114** |

典型：executive / share_capital / dividend / 股东源 返回 200，但 payload 无 `data.records` list（或路径为空）。

### 2.4 per-source fail

| source_id | fail | 主要 fail 原因 |
|-----------|------|----------------|
| `cninfo_company_basic_profile` | 15 | {'empty_but_valid_response': 15} |
| `cninfo_dividend_financing_profile` | 20 | {'schema_unexpected': 20} |
| `cninfo_executive_profile` | 26 | {'schema_unexpected': 24, 'empty_but_valid_response': 2} |
| `cninfo_share_capital_profile` | 23 | {'schema_unexpected': 23} |
| `cninfo_top_shareholders_profile` | 24 | {'schema_unexpected': 24} |
| `cninfo_top_float_shareholders_profile` | 23 | {'schema_unexpected': 23} |

## 3. Company-level clustering

- 至少 1 主源 fail：**30** 家
- **6/6 全失败：** **12** 家
- **5+ 源失败：** **18** 家
- 多源部分失败：**13**
- 单源失败：**5**
- 仅股东 empty_but_valid：**0**

### 3.1 6/6 或 5/6 主源失败

| code | name | board | failed_sources |
|------|------|-------|----------------|
| `300261` | 雅本化学 | `chinext` | 6/6 · all6_main_fail |
| `300288` | 朗玛信息 | `chinext` | 6/6 · all6_main_fail |
| `300355` | 蒙草生态 | `chinext` | 6/6 · all6_main_fail |
| `300414` | 中光防雷 | `chinext` | 6/6 · all6_main_fail |
| `600061` | 国投资本 | `sse_main` | 6/6 · all6_main_fail |
| `600063` | 皖维高新 | `sse_main` | 6/6 · all6_main_fail |
| `600130` | 波导股份 | `sse_main` | 6/6 · all6_main_fail |
| `600203` | 福日电子 | `sse_main` | 6/6 · all6_main_fail |
| `600207` | 安彩高科 | `sse_main` | 6/6 · all6_main_fail |
| `600233` | 圆通速递 | `sse_main` | 6/6 · all6_main_fail |
| `600390` | 五矿资本 | `sse_main` | 6/6 · all6_main_fail |
| `600523` | 贵航股份 | `sse_main` | 6/6 · all6_main_fail |
| `300112` | 万讯自控 | `chinext` | 5/6 · multi_partial_fail |
| `300267` | 尔康制药 | `chinext` | 5/6 · multi_partial_fail |
| `300329` | 海伦钢琴 | `chinext` | 5/6 · multi_partial_fail |
| `600076` | 康欣新材 | `sse_main` | 5/6 · multi_partial_fail |
| `600153` | 建发股份 | `sse_main` | 5/6 · multi_partial_fail |
| `600398` | 海澜之家 | `sse_main` | 5/6 · multi_partial_fail |

### 3.2 dividend / basic fail 公司

- **dividend fail：** 20 家（均为 schema_unexpected · records missing）
- **basic fail：** 15 家（均为 empty_but_valid_response · HTTP 200）

### 3.3 全量聚类表（30 家）

| code | name | board | failed_source_count | pattern | failed_source_ids |
|------|------|-------|---------------------|---------|-------------------|
| `000723` | 美锦能源 | `szse_main` | 1 | `single_source_fail` | cninfo_executive_profile |
| `000729` | 燕京啤酒 | `szse_main` | 1 | `single_source_fail` | cninfo_company_basic_profile |
| `000735` | 罗牛山 | `szse_main` | 1 | `single_source_fail` | cninfo_executive_profile |
| `000919` | 金陵药业 | `szse_main` | 4 | `multi_partial_fail` | cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `300107` | 建新股份 | `chinext` | 4 | `multi_partial_fail` | cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `300112` | 万讯自控 | `chinext` | 5 | `multi_partial_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_shareholders_profile |
| `300239` | 东宝生物 | `chinext` | 4 | `multi_partial_fail` | cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `300261` | 雅本化学 | `chinext` | 6 | `all6_main_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `300267` | 尔康制药 | `chinext` | 5 | `multi_partial_fail` | cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `300288` | 朗玛信息 | `chinext` | 6 | `all6_main_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `300329` | 海伦钢琴 | `chinext` | 5 | `multi_partial_fail` | cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `300355` | 蒙草生态 | `chinext` | 6 | `all6_main_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `300412` | 迦南科技 | `chinext` | 1 | `single_source_fail` | cninfo_top_float_shareholders_profile |
| `300414` | 中光防雷 | `chinext` | 6 | `all6_main_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `300420` | 五洋自控 | `chinext` | 2 | `multi_partial_fail` | cninfo_dividend_financing_profile;cninfo_executive_profile |
| `600061` | 国投资本 | `sse_main` | 6 | `all6_main_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `600063` | 皖维高新 | `sse_main` | 6 | `all6_main_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `600076` | 康欣新材 | `sse_main` | 5 | `multi_partial_fail` | cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `600117` | 西宁特钢 | `sse_main` | 4 | `multi_partial_fail` | cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `600130` | 波导股份 | `sse_main` | 6 | `all6_main_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `600153` | 建发股份 | `sse_main` | 5 | `multi_partial_fail` | cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `600203` | 福日电子 | `sse_main` | 6 | `all6_main_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `600207` | 安彩高科 | `sse_main` | 6 | `all6_main_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `600233` | 圆通速递 | `sse_main` | 6 | `all6_main_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `600389` | 江山股份 | `sse_main` | 2 | `multi_partial_fail` | cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `600390` | 五矿资本 | `sse_main` | 6 | `all6_main_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `600398` | 海澜之家 | `sse_main` | 5 | `multi_partial_fail` | cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `600523` | 贵航股份 | `sse_main` | 6 | `all6_main_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile;cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `688105` | 诺唯赞 | `star` | 4 | `multi_partial_fail` | cninfo_company_basic_profile;cninfo_dividend_financing_profile;cninfo_executive_profile;cninfo_share_capital_profile |
| `688138` | 清溢光电 | `star` | 1 | `single_source_fail` | cninfo_top_shareholders_profile |

## 4. Board-level diagnosis

| board | companies | main_cases | pass | fail | reachability% | schema_unexpected | empty_but_valid | 主要弱 source |
|-------|-----------|------------|------|------|---------------|-------------------|-----------------|---------------|
| `star` | 28 | 168 | 163 | 5 | 97.0% | 4 | 1 | `cninfo_company_basic_profile`(1), `cninfo_dividend_financing_profile`(1), `cninfo_executive_profile`(1) |
| `szse_main` | 54 | 324 | 317 | 7 | 97.8% | 4 | 9 | `cninfo_executive_profile`(3), `cninfo_company_basic_profile`(1), `cninfo_share_capital_profile`(1) |
| `sse_main` | 66 | 396 | 327 | 69 | 82.6% | 61 | 8 | `cninfo_top_shareholders_profile`(13), `cninfo_top_float_shareholders_profile`(13), `cninfo_executive_profile`(12) |
| `chinext` | 52 | 312 | 262 | 50 | 84.0% | 45 | 6 | `cninfo_executive_profile`(10), `cninfo_share_capital_profile`(9), `cninfo_top_shareholders_profile`(9) |

### 4.1 解读

- **star / szse_main（稳定）：** reach **~97%**；fail 分散且少（5–7/板块主 cases）。
- **sse_main / chinext（偏弱）：** reach **~83%**；fail 占 stable 200 大头（69+50）；schema_unexpected 集中。
- **样本清洗不足：** 12 家 6/6 本不应出现在「清洗后 stable」集；多为 sse/chinext 按 code 排序前段公司，可能含 ST/异常上市状态/旧代码。
- **重复 orgid：** 001267 保留；未见新一轮 duplicate 簇。

## 5. Source-level diagnosis

| source | reach% | fail | status 建议 | 是否降级 |
|--------|--------|------|-------------|----------|
| `cninfo_company_basic_profile` | 92.5% | 15 | **proceed_testing_with_caveat** | 维持；补充 basic empty_but_valid 口径 |
| `cninfo_dividend_financing_profile` | 90.0% | 20 | **conditional GO → HOLD until cleaning** | 全局 GO 改为 **conditional** |
| `cninfo_executive_profile` | 87.0% | 26 | **proceed_testing_with_caveat** | 维持 caveat |
| `cninfo_share_capital_profile` | 88.5% | 23 | **source_partial** | 维持 partial |
| `cninfo_top_shareholders_profile` | 88.0% | 24 | **proceed_testing_with_caveat** | 维持；schema 簇需剔除 |
| `cninfo_top_float_shareholders_profile` | 88.5% | 23 | **source_partial** | 维持 partial |
| `cninfo_company_security_profile` | 100.0% | 0 | **observe_only** | 否 |

### 5.1 dividend 90% vs 889 96.7% 解释

| 维度 | 889 non-BSE | stable 200 |
|------|-------------|------------|
| dividend reach | **96.7%** | **90.0%** |
| 主要 fail 形态 | http_error（26 家 six_fail）+ 分散 schema | **集中 schema_unexpected**（20 家 · 与 12 家 6/6 重叠） |
| 解释 | 889 含已识别异常公司拉高 http_error | stable 剔除 six_fail 后暴露 **records missing 簇**；非 endpoint 全局退化 |

股东 empty_but_valid：policy 已对股东源计 pass+reachable；**basic 的 15 条 empty_but_valid 仍计 fail**（runner 口径差异）。

## 6. Gate 与下一步

| 问题 | 建议 |
|------|------|
| stable 200 是否达标？ | **NO（LIVE_PARTIAL）** — 未证明清洗后稳定；12 家 6/6 为红线 |
| 重跑 stable 200 全量？ | **NO** — 先扩充清洗规则 + 替换 12 家异常 |
| failed-company targeted retry？ | **YES（条件）** — 对 **30 家** fail 公司；优先 12 家 6/6 剔除后小集重试 |
| 清洗规则不够？ | **YES** — 需将 stable 200 中 6/6 模式纳入 abnormal / second-pass hold |
| 按 board 拆 gate？ | **YES** — star/szse **~97%** 可与 sse/chinext **~83%** 分轨评估 |
| dividend YAML backfill | **HOLD until cleaning**（由全局 GO 降为 conditional） |
| non-BSE C-class | **仍 CONDITIONAL YES** — 好板块可用；需二次清洗 |

## 7. 红线

- 本轮 **无 live** · **无 CNINFO** · **无 YAML** · **无 DB** · **无 verified**

## 8. 参考

- [live report](cninfo_c_class_stable_200_live_report.csv)
- [live summary](cninfo_c_class_stable_200_live_summary.md)
- [source status decision](../plans/cninfo_c_class_source_status_decision.md)
- [stable 200 plan](../plans/cninfo_c_class_stable_200_sample_plan.md)
