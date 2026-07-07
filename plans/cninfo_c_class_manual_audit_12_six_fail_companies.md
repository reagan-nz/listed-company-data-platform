# CNINFO C-Class Manual Audit — Stable 200 十二家 6/6 Fail 公司

_审计日期：2026-07-07_

> **性质：** 人工网页审计结论记录；**非** live 重跑；**非** 样本剔除决策。对应 [stable 200 diagnosis](../outputs/validation/cninfo_c_class_stable_200_diagnosis.md) 中 12 家 `all6_main_fail` 的 **人工复核 overturn**。

## 1. 审计对象

| stock_code | company_name | board |
|------------|--------------|-------|
| 300261 | 雅本化学 | chinext |
| 300288 | 朗玛信息 | chinext |
| 300355 | 蒙草生态 | chinext |
| 300414 | 中光防雷 | chinext |
| 600061 | 国投资本 | sse_main |
| 600063 | 皖维高新 | sse_main |
| 600130 | 波导股份 | sse_main |
| 600203 | 福日电子 | sse_main |
| 600207 | 安彩高科 | sse_main |
| 600233 | 圆通速递 | sse_main |
| 600390 | 五矿资本 | sse_main |
| 600523 | 贵航股份 | sse_main |

**机器可读表：** [cninfo_c_class_stable_200_manual_audit_12_companies.csv](../outputs/validation/cninfo_c_class_stable_200_manual_audit_12_companies.csv)

## 2. 人工审计结论（12/12 一致）

| 字段 | 值 |
|------|-----|
| `manual_cninfo_search_found` | **yes**（全部） |
| `manual_f10_page_exists` | **yes**（全部） |
| `manual_basic_profile_visible` | **yes**（全部） |
| `manual_judgment` | **`endpoint_parameter_issue_or_parser_issue`**（全部） |

**manual_notes（统一）：** CNINFO web page shows structured company profile; do not hold as sample_quality_issue without endpoint/parser diagnosis.

## 3. 为什么不能直接剔除这 12 家

1. **12/12** 在 CNINFO 网页端可找到公司页，「公司介绍」可见结构化字段 — 公司**有效、可展示**。
2. stable 200 live 的失败形态为：basic `empty_but_valid_response` + 其余 5 源 `schema_unexpected`（`data.records missing`），**http_error=0**。
3. 若仅为提高 stable 200 pass 率而剔除这 12 家，属于 **对 live 结果的过拟合（overfitting）**，不能证明 non-BSE 宇宙真实稳定。
4. 当前失败更应解释为 **runner endpoint / parser 与网页真实数据源不一致**，而非 `sample_quality_issue` 或 `six_fail_hold` 类异常上市状态。

## 4. 与自动诊断的差异

| 维度 | stable 200 diagnosis（自动） | 人工审计（本轮） |
|------|------------------------------|------------------|
| 12 家定性 | 样本二次清洗不足 · 建议剔除 | **不剔除** · endpoint/parser 调查 |
| stable 200 v2 | 隐含方向（扩充清洗） | **暂停** |
| 根因假设 | sample cleaning gap | **endpoint_parameter / parser_schema / response_shape** |

## 5. 决策

| 项 | 决策 |
|----|------|
| 12 家进入 hold？ | **否** — 不标记为 `sample_quality_issue` |
| stable 200 v2 清洗 | **暂停** |
| 下一步 | [12 six-fail endpoint debug plan](cninfo_c_class_12_six_fail_endpoint_debug_plan.md)（**待人工批准**后执行，本轮不请求 CNINFO） |
| dividend YAML backfill | **HOLD**（维持） |

## 6. manual_judgment 枚举扩展

本轮新增允许值：

- **`endpoint_parameter_issue_or_parser_issue`** — 网页端有数据，runner/API 路径或解析假设与网页不一致；需 endpoint debug，不可直接当样本质量问题。

## 7. 红线

- 本轮 **无 live** · **无 CNINFO 程序请求** · **无 stable 200 v2** · **无剔除 12 家** · **无 YAML** · **无 verified**

## 8. 参考

- [stable 200 live report](../outputs/validation/cninfo_c_class_stable_200_live_report.csv)
- [stable 200 diagnosis](../outputs/validation/cninfo_c_class_stable_200_diagnosis.md)
- [source status decision](cninfo_c_class_source_status_decision.md)
