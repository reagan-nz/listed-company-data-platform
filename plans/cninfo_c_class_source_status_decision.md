# CNINFO C-Class Source Status Decision（Era C Phase 4）

_生成时间：2026-07-07_

> **性质：** 基于已完成的规模验证（30 / 195 / 889 / 62 retry live），对各 C-class source 做**阶段性状态判断**。**不是**新 source discovery；**不写 verified**；**不升级 testing_stable_sample**。

## 1. 执行摘要

| 维度 | 结论 |
|------|------|
| non-BSE 主路线 | **CONDITIONAL YES** — 整体可用，需样本清洗与 source 分级 |
| 最佳 direct source | **dividend_history**（`cninfo_dividend_financing_profile`）— **proceed_testing** |
| partial-risk sources | **top_float**（`source_partial`）、**share_capital**（`source_partial`） |
| observe-only | **security_profile** |
| derived（无单独请求） | contact · business_scope · industry |
| BSE 83/87 legacy | **HOLD** — 不混入主 gate |
| 26 家 6/6 全失败 | **hold / sample_quality_review** |
| YAML backfill | dividend_history **GO（决策 only）** — **本轮不执行** |

**证据链：** [30 active live](../outputs/validation/cninfo_c_class_scale_smoke_30_active_summary.md) · [195 active live](../outputs/validation/cninfo_c_class_scale_smoke_200_active_summary.md) · [889 non-BSE live](../outputs/validation/cninfo_c_class_smoke_1000_non_bse_live_summary.md) · [889 diagnosis](../outputs/validation/cninfo_c_class_smoke_1000_non_bse_diagnosis.md) · [62 retry live](../outputs/validation/cninfo_c_class_retry_889_partial_fail_live_summary.md) · [universe split](cninfo_c_class_universe_split_and_sample_cleaning_plan.md)

---

## 2. Source Status Table

| source_id | source_role | source_type | current_stage_decision | evidence_from_30 | evidence_from_195 | evidence_from_889 | evidence_from_62_retry | main_strength | main_risk | next_action | yaml_backfill_decision | caveat |
|-----------|-------------|-------------|------------------------|------------------|---------------------|-------------------|------------------------|---------------|-----------|-------------|------------------------|--------|
| `cninfo_company_basic_profile` | 主 profile 底座；derived 三源字段来源 | direct | **proceed_testing_with_caveat** | reach **100%**（30/30）；key fill **100%** | reach **94.4%**（184/195，含 BSE 稀释） | reach **94.5%**（840/889）；key fill **≥99.6%** | reach **66.1%**（41/62 困难样本） | 成功样本字段 fill_rate 极高；contact/business/industry 依赖此源 | 异常 / *ST / 退市残留公司 HTTP 500 或 empty；26 家 6/6 拖累 | 继续作为主 profile base；扩充 abnormal_review 清洗；不进入 verified | **NO**（已有 endpoint） | 困难样本明显弱于全量；需 sample-quality filter |
| `cninfo_company_security_profile` | 上市状态 / 交易状态观察 | observe_only | **observe_only** | observe **30/30**；error **0%** | observe **195/195** | observe **889/889** | observe **62/62** | 全样本 observe_pass；零 blocked/429 | `secType=szshe` 硬编码；orgId 跨板块逻辑未充分验证 | 继续观察；**不绑定主 gate** | **N/A** | 不用于主判定 pass/fail |
| `cninfo_company_contact_profile` | 联系方式 | derived | **derived_no_separate_fetch** | 随 basic fill **100%** | 随 basic | 889 derived fill **≥98.9%**（endpoint_found 子集） | 62 retry derived fill **≥97.6%** | 无额外 HTTP；字段稳定 | 完全依赖 basic 可达性 | 不单独请求；随 basic fill_rate 统计 | **N/A** | 无独立 endpoint |
| `cninfo_company_business_scope` | 经营范围 | derived | **derived_no_separate_fetch** | 随 basic **100%** | 随 basic | **≥99.6%** | **≥97.6%** | 同上 | 同上 | 同上 | **N/A** | 无独立 endpoint |
| `cninfo_company_industry_profile` | 行业标签（F032V/MARKET 等） | derived | **derived_no_separate_fetch** | 随 basic **100%** | 随 basic | F032V **99.6%** · F044V **95.5%** | F032V **97.6%** · F044V **92.7%** | 轻量行业字段可用 | **非完整行业分类体系**；F044V 弱于 F032V | 不单独请求；标注语义局限 | **N/A** | observed-only / derived_candidate 语义 |
| `cninfo_executive_profile` | 高管列表 | direct | **proceed_testing_with_caveat** | reach **100%** | reach **94.4%** | reach **94.6%** | reach **67.7%**（42/62） | 常规 non-BSE 接近 95% 门槛 | 困难样本敏感；schema_unexpected 分散 | 继续测试；建立 failure taxonomy；不进入 stable | **NO** | 对异常公司较脆弱 |
| `cninfo_share_capital_profile` | 股本结构 | direct | **source_partial** | reach **100%** | reach **94.4%** | reach **95.1%** | reach **59.7%**（37/62） | 889 全量略超 95% | 困难样本 **<60%**；波动大 | 标 partial-risk；reachable 与 non_empty 分离统计 | **NO** | 可用但不可假设全市场非空 |
| `cninfo_top_shareholders_profile` | 十大股东 | direct | **proceed_testing_with_caveat** | reach **96.7%**；1 empty_but_valid | reach **93.8%** | reach **95.3%** | reach **96.8%**（policy 后）；non_empty **56.5%** | empty_but_valid policy 后 retry 表现好 | non_empty 低于 reachability；空表合法 | 继续测试；empty_but_valid **单独统计** | **NO** | reachable ≠ non_empty |
| `cninfo_top_float_shareholders_profile` | 十大流通股东 | direct | **source_partial** | reach **93.3%** | reach **93.3%** | reach **93.5%**（**低于** top_sh） | reach **96.8%**；non_empty **59.7%** | retry 困难集 endpoint 可达性尚可 | 889 全量最低主源之一；empty_but_valid **多** | 标 **source_partial**；不要求全公司非空 | **NO** | 主 gate 区分 reach vs non_empty |
| `cninfo_dividend_financing_profile` / **dividend_history** | 历史分红 | direct | **proceed_testing** | reach **100%**；valid_empty **2** | reach **94.4%**（mixed）；valid_empty **3** | reach **96.7%**；valid_empty **34** | reach **96.8%**；valid_empty **27** | 两档 scale 均 **>96%**；日期字段 fill 好 | 语义过宽（financing）；**仅 historical dividend** | YAML 窄化命名 **dividend_history**；人工批准后 backfill | **GO（决策 only）** — **不执行** | 不覆盖配股/增发/融资事件 |

---

## 3. Decision 枚举说明

本轮仅使用以下 `current_stage_decision` 值（**无 verified · 无 testing_stable_sample**）：

| 值 | 含义 |
|----|------|
| `proceed_testing` | 可继续作为 testing 主源推进 |
| `proceed_testing_with_caveat` | 可继续测试，但有明确样本/板块/异常公司 caveat |
| `source_partial` | endpoint 可达但 non_empty 或困难样本不稳定；不可全市场硬性要求 |
| `derived_no_separate_fetch` | 不单独 HTTP；随 parent（basic）fill_rate |
| `observe_only` | 仅观察，不绑定主 gate |
| `hold` | 暂停推进（universe / 样本级） |

---

## 4. Universe Decision

| universe | 决策 | 依据 |
|----------|------|------|
| **non-BSE main** | **CONDITIONAL YES** | 889 live 主判定 pass **95.0%**；fail 可解释为样本质量 + 政策性 empty；62 retry 验证困难集行为 |
| **BSE 920** | **separate child universe** | 195 live：920 前缀 **11/12** 主源全过；需独立 gate，不混入 non-BSE 主 gate |
| **BSE 83/87 legacy** | **HOLD** | scode-only 路径 HTTP 500 / 9240002；[BSE diagnosis](../outputs/validation/cninfo_c_class_scale_smoke_200_bse_diagnosis.md) |
| **abnormal_review** | **HOLD / sample_quality_review** | 26 家 6/6 全失败 + 已知 3 家 abnormal；不进主 gate |
| **mixed full market** | **not ready** | 195 混合 BSE 稀释指标；需 universe split 后分轨验证 |

---

## 5. 股东源 empty_but_valid 与 source_partial 口径

已在 `lab/validate_cninfo_c_class_scale_smoke.py` 落地：

- 股东源 HTTP 200 + 空 `data.records` → `empty_but_valid_response`
- **case_result=pass**（非接口失败）
- **计入** reachability；**不计** http_error / blocked / schema_unexpected
- **non_empty_rate** 单独下降
- `top_float` / `top_shareholders`：**top_float** 标 `source_partial`；**top_sh** 标 `proceed_testing_with_caveat`

---

## 6. dividend_history YAML Backfill

| 项 | 决策 |
|----|------|
| reachability（889） | **96.7%** |
| reachability（62 retry） | **96.8%** |
| valid_empty | 889：**34** · 62：**27**（合法空分红历史） |
| 字段 fill（非空记录） | F001V/F007V/F018D **≥93%** |
| 语义 | 仅 **historical dividend**；非 financing / allotment / rights issue |
| **yaml_backfill_decision** | **GO（决策 only）** |
| 执行 | **本轮不执行**；需人工批准；建议 YAML 命名窄化为 `dividend_history` |

---

## 7. Next Stage Recommendation

1. **不再继续** C-class source discovery（P2-B 已收口）。
2. **不再重跑** 889 全量 live。
3. **本轮已完成** source-level status decision（本文档）。
4. **下一步设计：** cleaned 1000-like stable sample 或 **~200 testing stable sample**（非 verified）— 需人工批准样本方案。
5. **dividend_history：** 可起草 YAML backfill decision 执行文档，**仍须人工批准**后执行。
6. **basic / executive / share_capital：** 需异常公司容错与 `abnormal_review` 样本扩充。
7. **shareholder sources：** 保持 empty_but_valid + source_partial 双指标。
8. **security：** 继续 observe-only；跨板块 secType 验证另开 small probe（非本轮）。

---

## 8. 红线确认

- 本文档阶段：**无 live** · **无 CNINFO** · **无 YAML backfill 执行** · **无 DB** · **无 verified** · **无 testing_stable_sample 升级**

---

## 9. 参考

- [889 live summary](../outputs/validation/cninfo_c_class_smoke_1000_non_bse_live_summary.md)
- [889 diagnosis](../outputs/validation/cninfo_c_class_smoke_1000_non_bse_diagnosis.md)
- [62 retry live summary](../outputs/validation/cninfo_c_class_retry_889_partial_fail_live_summary.md)
- [62 retry live report](../outputs/validation/cninfo_c_class_retry_889_partial_fail_live_report.csv)
- [universe split plan](cninfo_c_class_universe_split_and_sample_cleaning_plan.md)
- [eraC execution plan](eraC_execution_plan.md) §7al
