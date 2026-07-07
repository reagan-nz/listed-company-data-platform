# CNINFO C-Class 889 Post-Retry Decision（Era C Phase 4）

_生成时间：2026-07-07_

> **目的：** 基于 **41 家 partial-fail targeted retry live** 结果，给出 post-retry 决策与 harvest gate 初步判断。**本轮仅文档**；**不跑 live**；**不请求 CNINFO**；**非 verified**；**非 testing_stable_sample**。

**前置：**

- [889 rerun diagnosis](../outputs/validation/cninfo_c_class_889_non_bse_rerun_diagnosis.md)
- [889 rerun retry plan](cninfo_c_class_889_rerun_retry_plan.md)
- [partial-fail retry live summary](../outputs/validation/cninfo_c_class_889_rerun_partial_fail_retry_live_summary.md)
- [partial-fail retry live report](../outputs/validation/cninfo_c_class_889_rerun_partial_fail_retry_live_report.csv)
- all6 hold：`lab/eval_companies_c_class_889_rerun_all6_hold.yaml`（**26** 家）

---

## 1. 执行摘要

| 指标 | 值 |
|------|-----|
| sample | `eval_companies_c_class_889_rerun_partial_fail_retry.yaml` |
| companies | **41** |
| cases | **287** |
| pass | **237** |
| fail | **9** |
| blocked | **0** |
| HTTP 429 | **0** |
| http_error | **0** |
| **result** | **LIVE_PARTIAL** |
| **状态** | **targeted retry 已完成**（非 pending approval） |

**核心结论：**

1. **41 家 targeted retry 已完成**；v1 889 rerun 中 partial-fail 簇的 **http_error / blocked / pacing** 问题已基本排除。
2. 残留 **9** 条 fail 全部为 **`empty_but_valid_response`**（executive **1** · share_capital **8**），属 **source-level residual issue**，非 runner/pacing 缺陷。
3. **26 家 all6 hold** 继续 **hold_no_retry**；**889 全量不需要立即重跑**。
4. **share_capital** 继续标 **source_partial**；**executive** 继续 **proceed_testing_with_caveat**。
5. **basic / dividend / shareholder / top_float** 可进入 **C-class harvest gate 评估**；harvest planning **允许启动**，但 summary 必须保留 **26 hold** 与 **share_capital residual** caveat。
6. **dividend_history YAML** 维持 **GO（决策 only）** — **不执行** backfill。

---

## 2. Targeted Retry Live 结果

### 2.1 总体

| 维度 | 889 rerun（41 家子集 v1） | post-retry live |
|------|---------------------------|-----------------|
| 主因 | http_error 142 · blocked 20 · empty_but_valid 52 | **empty_but_valid 9 only** |
| blocked | 20 | **0** |
| 429 | 0 | **0** |
| http_error | 142 | **0** |
| fail | 215（全 889 口径）/ 41 家子集多源 fail | **9** |

**解读：** retry 将此前 partial-fail 簇中的 **瞬时 HTTP/DNS/限流** 失败几乎全部消化；残留为 **合法空 records 仍判 fail** 的语义层问题。

### 2.2 Per-source（41 家 retry 子集）

| source_id | pass | fail | reachability |
|-----------|------|------|--------------|
| `cninfo_company_basic_profile` | 41 | 0 | **100%** |
| `cninfo_dividend_financing_profile` | 41 | 0 | **100%** |
| `cninfo_executive_profile` | 40 | **1** | **97.6%** |
| `cninfo_share_capital_profile` | 33 | **8** | **80.5%** |
| `cninfo_top_shareholders_profile` | 41 | 0 | **100%** |
| `cninfo_top_float_shareholders_profile` | 41 | 0 | **100%** |
| `cninfo_company_security_profile` | observe 41 | — | **100%** |

---

## 3. 剩余 9 Fail 明细

全部为 `retrieval_status=empty_but_valid_response` · HTTP 200 · `data.records` 空 list · `case_result=fail`。

| company_code | company_name | board | source_id | retrieval_status |
|--------------|--------------|-------|-----------|------------------|
| 301198 | 喜悦智行 | chinext | `cninfo_executive_profile` | empty_but_valid_response |
| 301011 | 华立科技 | chinext | `cninfo_share_capital_profile` | empty_but_valid_response |
| 301338 | 凯格精机 | chinext | `cninfo_share_capital_profile` | empty_but_valid_response |
| 301345 | 涛涛车业 | chinext | `cninfo_share_capital_profile` | empty_but_valid_response |
| 301538 | 骏鼎达 | chinext | `cninfo_share_capital_profile` | empty_but_valid_response |
| 301583 | 托伦斯 | chinext | `cninfo_share_capital_profile` | empty_but_valid_response |
| 002710 | 慈铭体检 | szse_main | `cninfo_share_capital_profile` | empty_but_valid_response |
| 601206 | 海尔施 | sse_main | `cninfo_share_capital_profile` | empty_but_valid_response |
| 688688 | 蚂蚁集团 | star | `cninfo_share_capital_profile` | empty_but_valid_response |

### 3.1 Source 分布

| source | fail count | 占比 |
|--------|------------|------|
| `cninfo_share_capital_profile` | **8** | 88.9% |
| `cninfo_executive_profile` | **1** | 11.1% |
| **合计** | **9** | 100% |

### 3.2 失败性质判定

| 判定项 | 结论 |
|--------|------|
| runner / pacing | **排除** — blocked=0 · 429=0 · http_error=0 |
| parser / schema | **排除** — 均为 endpoint 可达 · records 空 |
| 性质 | **source-level residual** — empty_but_valid 语义与 case_result 口径不一致 |
| 是否值得再跑 889 / 41 子集 | **否** — 重跑预期重复 empty_but_valid |

---

## 4. 26 家 All6 Hold（不变）

| 项 | 决策 |
|----|------|
| 样本 | `lab/eval_companies_c_class_889_rerun_all6_hold.yaml`（**26**） |
| hold_reason | `sample_quality_or_status_review` |
| retry_decision | **hold_no_retry** |
| 与 partial retry 关系 | **无重叠**；post-retry 不改变 hold 状态 |

**理由：** 六主源全失败 · HTTP 500/`9240002` · *ST/退市残留；与本次 9 条 empty_but_valid residual **不同簇**。

---

## 5. Source Status 决策（延续 + 强化）

与 [source status decision](cninfo_c_class_source_status_decision.md) 对齐，post-retry 不升级 verified：

| source_id | post-retry 决策 | 依据 |
|-----------|-----------------|------|
| `cninfo_company_basic_profile` | **proceed_testing** | retry 子集 **100%** |
| `cninfo_dividend_financing_profile` | **proceed_testing** | retry 子集 **100%**；dividend_history YAML **GO（决策 only）** |
| `cninfo_executive_profile` | **proceed_testing_with_caveat** | retry 子集 **97.6%**；1 条 empty_but_valid residual |
| `cninfo_share_capital_profile` | **source_partial** | retry 子集 **80.5%** reachable；8 条 empty_but_valid · **不可假设全市场非空** |
| `cninfo_top_shareholders_profile` | **proceed_testing_with_caveat** | retry 子集 **100%** reach；empty_but_valid 单独统计 |
| `cninfo_top_float_shareholders_profile` | **source_partial** | retry 子集 **100%** reach；non_empty 与 reach 分离 |
| `cninfo_company_security_profile` | **observe_only** | 不绑定主 gate |

### dividend_history YAML backfill

| 项 | 决策 |
|----|------|
| 决策 | **GO（决策 only）** |
| 执行 | **不执行** YAML backfill |
| 命名 caveat | 窄化为 `dividend_history`（或等价语义），消除 financing 过度承诺 |

---

## 6. 是否继续重跑？

| 选项 | 决策 | 理由 |
|------|------|------|
| 889 全量重跑 | **否** | 97%+ 主源已达；边际收益低 |
| 41 家 partial retry 再跑 | **否** | 9 fail 均为稳定 empty_but_valid；非瞬态 |
| 9 家公司单源 micro-retry | **否** | 需语义/口径修订，非 HTTP 重试 |
| runner pacing 调整 | **否** | 90001/429 已吸收；本次 0 blocked/429/http_error |

---

## 7. Harvest Gate 初步判断

### 7.1 结论

**C-class harvest 可以进入 planning 阶段。**

前提：harvest summary / runbook **必须**显式保留以下 caveat，且 **不写 verified**、**不升级 testing_stable_sample**。

### 7.2 可纳入 harvest gate 评估的主源

| source | harvest 评估 |
|--------|--------------|
| basic | **可纳入** |
| dividend | **可纳入**（YAML 仍 decision-only） |
| top_shareholders | **可纳入**（区分 reach vs non_empty） |
| top_float | **可纳入**（source_partial 口径） |

### 7.3 Harvest summary 必保留 caveat

1. **26 家 all6 hold**（`eval_companies_c_class_889_rerun_all6_hold.yaml`）— 不 harvest · hold_no_retry · sample_quality_or_status_review。
2. **share_capital source_partial** — 全市场不可假设非空；889+retry 合并口径下仍有 empty_but_valid 簇（含本次 8 家）。
3. **executive caveat** — 困难样本 / empty_but_valid 敏感（含本次 1 家）。
4. **security observe_only** — 不绑定主 gate。
5. **derived 三源** — 随 basic fill_rate；无单独 HTTP。

### 7.4 不建议在 harvest 首轮纳入

| 项 | 理由 |
|----|------|
| 26 家 all6 hold 标的 | hold_no_retry |
| share_capital 作为硬性 non_empty gate | source_partial |
| verified / testing_stable_sample 升级 | 红线 |

---

## 8. 红线确认

| 项 | 状态 |
|----|------|
| live CNINFO | **未执行**（本轮） |
| YAML backfill | **不执行** |
| 入库 | **不做** |
| verified | **不写** |
| testing_stable_sample | **不升级** |
| 新 endpoint discovery | **不做** |
| B/D/Phase1 文件 | **未修改** |

---

## 9. 决策表

| 问题 | 决策 |
|------|------|
| 41 家 targeted retry 是否完成？ | **是** · LIVE_PARTIAL · 非 pending |
| 剩余 9 fail 性质？ | **source-level residual**（empty_but_valid） |
| runner/pacing 是否主因？ | **否** |
| 26 家 all6 hold？ | **继续 hold_no_retry** |
| share_capital？ | **继续 source_partial** |
| executive？ | **继续 caveat** |
| dividend_history YAML？ | **GO 决策 · 不执行** |
| 889 立即重跑？ | **否** |
| C-class harvest planning？ | **允许进入**（带 caveat） |

**下一步：** 起草 C-class **harvest planning** 文档（universe=889 non-BSE 母本 − 26 hold；保留 share_capital / executive caveat）；**不**启动全量 live harvest 直至 planning 文档就绪。
