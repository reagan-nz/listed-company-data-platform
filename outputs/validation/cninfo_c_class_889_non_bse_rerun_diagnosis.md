# CNINFO C-Class 889 Non-BSE Rerun — Post-Live Diagnosis

_生成时间：2026-07-07_

> **基于：** [live_report.csv](cninfo_c_class_889_non_bse_rerun_live_report.csv)（**889** · **6223** cases · **未新增 CNINFO**）

**前置：** [889 rerun plan](../plans/cninfo_c_class_889_non_bse_rerun_plan.md) · [stable 200 live pass decision](../plans/cninfo_c_class_stable_200_live_pass_decision.md)

---

## 1. 执行摘要

| 指标 | 值 |
|------|-----|
| companies | **889** |
| cases | **6223** |
| main judgment pass | **5119** |
| main judgment fail | **215** |
| security observe_pass | **889** |
| blocked | **20** |
| HTTP 429 | **0** |
| **result** | **LIVE_PARTIAL** |

**核心结论：**

1. 新版 runner **显著改善** v1（fail 270→**215**；schema_unexpected 簇基本消失；JSON 429/90001 仅 **1** 条 throttled fail）。
2. 剩余 fail **主因是 HTTP 500 / `9240002`（142）** 与 **executive/share_capital `empty_but_valid_response`（52）**，**不是** parser `data.records` 路径错误。
3. **26 家 6/6 全失败** — 与 stable 200 十二家 **无重叠**；多为 *ST/退市残留 · **sample_quality_or_status_review**；**不应清洗样本**，应 **hold 子集**。
4. **chinext** executive/share_capital 偏弱（87.6%/89.7%）主因是 **合法空 records**（empty_but_valid），非 blocked。
5. **建议：** **41 家** partial-fail targeted retry（非 26 家 all6）；**暂停 harvest** 直至 retry 完成；**不**扩样本清洗。

---

## 2. Failure cases 明细

共 **215** 条 fail → [cninfo_c_class_889_non_bse_rerun_failure_cases.csv](cninfo_c_class_889_non_bse_rerun_failure_cases.csv)

字段：`company_code` · `company_name` · `board` · `source_id` · `retrieval_status` · `final_retrieval_status` · `http_status` · `first_result_code` · `final_result_code` · `retry_count` · `used_orgid_variant` · `error_message` · `request_url`

---

## 3. 失败状态分布

### 3.1 retrieval_status / final_retrieval_status（215 fail）

| status | count | % |
|--------|-------|---|
| `http_error` | **142** | 66.0% |
| `empty_but_valid_response` | **52** | 24.2% |
| `blocked` | **20** | 9.3% |
| `cninfo_throttled_business_code` | **1** | 0.5% |

### 3.2 HTTP 层

| 指标 | count |
|------|-------|
| fail 中 HTTP **500** | 156 |
| fail 中 HTTP **200** | 53 |
| `json_code=9240002`（http_error） | **136** |

### 3.3 per-source fail 分布

| source_id | fail | 主要 retrieval_status |
|-----------|------|------------------------|
| `cninfo_executive_profile` | **55** | empty_but_valid **27** · http_error **24** · blocked **4** |
| `cninfo_share_capital_profile` | **52** | http_error **25** · empty_but_valid **25** · blocked **2** |
| `cninfo_company_basic_profile` | 27 | http_error **23** · blocked **4** |
| `cninfo_dividend_financing_profile` | 27 | http_error **23** · blocked **3** · throttled **1** |
| `cninfo_top_shareholders_profile` | 27 | http_error **24** · blocked **3** |
| `cninfo_top_float_shareholders_profile` | 27 | http_error **23** · blocked **4** |

**六主源 reachability（pass 口径）：** basic/dividend/top_sh/top_float **97.0%** · executive **93.8%** · share_capital **94.2%**

---

## 4. 公司级聚类

- 至少 1 主源 fail：**67** 家
- **6/6 全失败：** **26** 家（**新簇** · 非 stable 200 十二家）
- **5/6：** **0**
- **2–4 源 partial：** **15**
- **单源 fail：** **26**

### 4.1 新 6/6 fail 簇（26 家 · hold 候选）

共性：**http_error（HTTP 500 · `9240002`）+ 部分 blocked**；*ST/退市/重组残留类名称。

| code | name | board |
|------|------|-------|
| 000043 | 中航善达 | szse_main |
| 000416 | *ST民控 | szse_main |
| 000562 | 宏源证券 | szse_main |
| 000569 | 长城股份 | szse_main |
| 000638 | *ST万方 | szse_main |
| 000765 | *ST华信 | szse_main |
| 000787 | *ST创智 | szse_main |
| 000827 | *ST长兴 | szse_main |
| 000982 | 中银绒业 | szse_main |
| 002113 | *ST天润 | szse_main |
| 002325 | *ST洪涛 | szse_main |
| 002503 | *ST搜特 | szse_main |
| 002776 | *ST柏龙 | szse_main |
| 300116 | *ST保力 | chinext |
| 300262 | *ST巴安 | chinext |
| 600112 | *ST天成 | sse_main |
| 600247 | *ST成城 | sse_main |
| 600253 | 天方药业 | sse_main |
| 600260 | *ST凯乐 | sse_main |
| 600286 | S*ST国瓷 | sse_main |
| 600357 | 承德钒钛 | sse_main |
| 600393 | ST粤泰 | sse_main |
| 600700 | *ST数码 | sse_main |
| 600842 | 中西药业 | sse_main |
| 601258 | *ST庞大 | sse_main |
| 603056 | 德邦股份 | sse_main |

**与 stable 200 十二家：** **零重叠**（十二家 rerun 全部 pass 或仅 1–2 源 empty_but_valid）。

### 4.2 executive / share_capital 专项

| 模式 | 数量 | 说明 |
|------|------|------|
| 仅 executive fail | **14** | 多为 chinext · empty_but_valid |
| 仅 share_capital fail | **11** | empty_but_valid |
| executive + share_capital 同时 fail | **13** | chinext 集中 · 合法空表 |
| executive empty_but_valid 公司 | **27** | 主因 chinext 空高管/股本表 |
| share_capital empty_but_valid 公司 | **25** | 同上 |

### 4.3 stable 200 十二家在 889 rerun 中

| code | rerun 结果 |
|------|------------|
| 300261/300288/300355/300414 | 各 **2** 源 fail（executive+share · empty_but_valid） |
| 其余 8 家 | **全 pass** |

### 4.4 blocked / http_error 重叠

| 维度 | 数量 |
|------|------|
| blocked 涉及公司 | **14** |
| http_error 涉及公司 | **29** |
| 26 家 all6 中 http_error | **26/26** |
| 26 家 all6 中 blocked | **14/26** |

---

## 5. 板块诊断

| board | companies | main cases | pass | fail | weakest source | blocked fails | http fails |
|-------|-----------|------------|------|------|----------------|---------------|------------|
| **chinext** | 233 | 1398 | 1335 | 63 | executive **87.6%** | 2 | 11 |
| **szse_main** | 239 | 1434 | 1354 | 80 | executive **94.1%** | 8 | **71** |
| **sse_main** | 292 | 1752 | 1685 | 67 | share_capital **95.9%** | 10 | 56 |
| **star** | 125 | 750 | 745 | 5 | share_capital **98.4%** | 0 | 4 |

### 5.1 chinext executive/share 偏弱原因

- **不是** blocked/429 主因（blocked fail 仅 2）。
- **主因：** executive/share 返回 HTTP 200 · `data.records=[]` → runner 标 `empty_but_valid_response` · **case_result=fail**（非 endpoint 不可达）。
- basic/dividend/股东源 chinext **≥98.7%**，说明 data20 路径与 backoff **有效**。
- **口径：** reachability 与 non_empty 需分离；chinext executive/share 宜维持 **source_partial / caveat**。

### 5.2 szse_main ~94–95%

- **http_error 集中**（71 fail 行）— 多属 26 家 all6 *ST/退市残留（szse 占 **14/26**）。
- 剔除 all6 hold 后，szse 可达率将显著上升。

### 5.3 sse_main / star

- **sse_main：** 96%+ 主源 pass；fail 多与 all6 hold 重叠。
- **star：** **745/750** pass · 仅 5 fail（含 688750 瞬时 DNS · 4 源）。

---

## 6. Runner 诊断

| 检查项 | 结果 |
|--------|------|
| retry_count 分布 | **0:** 5307 · **1–6:** 27（仅 **2** fail 行 retry>0） |
| used_orgid_variant | **150** 行 · **32** 家公司 · fail 行涉及 **27** 家 · **未爆炸** |
| 90001/429 吸收 | throttled 仅 **1** fail（300160 dividend）· **有效** |
| HTTP 500 / 9240002 | **136** 行 · backoff **无效** · 属公司/端点不可用 |
| blocked | **20** 行 · retry 后仍 fail |
| 688750 | **4** 源 DNS 瞬时失败（`NameResolutionError`）· 可 retry |

**pacing 判断：** 当前 0.5s + backoff **足够**吸收业务码限流；**不宜**仅为 9240002 加长 pacing。可考虑对 **DNS/连接类** 错误增加 **transport retry**（非本轮 scope）。

---

## 7. Source status 判断

| source | 判断 | 889 证据 |
|--------|------|----------|
| `cninfo_company_basic_profile` | **proceed_testing_with_caveat** | 97.0% · fail 多为 http_error 异常公司 |
| `dividend_history` | **GO（决策 only）** · 不执行 YAML | 97.0% reach · valid_empty=55 · error_rate 2.9% |
| `cninfo_executive_profile` | **proceed_testing_with_caveat** · chinext 考虑 **source_partial**（empty 合法） | 93.8% · 55 fail |
| `cninfo_share_capital_profile` | **source_partial** 保持 | 94.2% · empty 与 http 各半 |
| `cninfo_top_shareholders_profile` | **proceed_testing_with_caveat** | 97.0% |
| `cninfo_top_float_shareholders_profile` | **source_partial** 保持 | 97.0% |
| `cninfo_company_security_profile` | **observe_only** 不变 | 100% observe |
| contact/business/industry | **derived_no_separate_fetch** | 随 basic |

**non-BSE main universe：** 维持 **CONDITIONAL YES**；剔除 26 家 all6 hold 后 evidence 更强；**不写 verified**。

---

## 8. 下一步建议（最小动作）

### 8.1 是否 targeted retry？

**是** — 但 **仅 partial-fail 子集**，非 215 行全量重跑。

| 动作 | 范围 | 数量 |
|------|------|------|
| **hold**（sample_quality_or_status_review） | 6/6 · http_error/blocked | **26** 家 |
| **targeted retry** | 1–4 源 fail · 非 all6 | **~41** 家 |
| **跳过重跑** | 688750 等 DNS 瞬时（可选纳入 retry） | 1 家 |

### 8.2 retry 样本构成（建议）

- **包含：** 41 家 partial-fail（chinext executive/share empty_but_valid 为主 · stable 200 十二家中的 4 家）
- **排除：** 26 家 all6 hold
- **粒度：** **按公司聚合重跑**（每家公司 6 主源），非 215 case 逐条

### 8.3 runner / harvest

- **不**为 889 全量加长 pacing（business 码已吸收）。
- **暂停 harvest** 直至 partial-fail targeted retry + 更新 diagnosis。
- **不**新增样本清洗规则（避免 stable 200 v2 式过拟合）。

### 8.4 889 后决策门（retry 完成后）

- dividend_history YAML：是否从 GO decision → 执行候选
- non-BSE：是否加强 testing 证据（仍 no verified）
- BSE 920：单独计划

---

## 9. Caveats

- 889 rerun **非 full market**；仍含 26 家异常上市状态公司。
- **不写 verified** · **不写 testing_stable_sample** · **无 DB** · **无 YAML backfill**。
- v1→rerun：fail 公司 88→**67**；**58** 家 v1 fail 已修复；**37** 家为新 fail 形态。

---

## 10. 参考

- [live_summary.md](cninfo_c_class_889_non_bse_rerun_live_summary.md)
- [v1 diagnosis](cninfo_c_class_smoke_1000_non_bse_diagnosis.md)
- [source status decision](../plans/cninfo_c_class_source_status_decision.md)
