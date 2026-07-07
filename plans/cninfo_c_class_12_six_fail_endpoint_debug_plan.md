# CNINFO C-Class 12 Six-Fail Endpoint / Parser Debug Plan

_生成时间：2026-07-07_

> **范围：** 仅 stable 200 live 中 **12 家 6/6 主源失败** 公司（见 [manual audit](cninfo_c_class_manual_audit_12_six_fail_companies.md)）。**最小化 debug** — 不扩大至 889 / 200 全量。**本轮仅计划** — **不实际请求 CNINFO**。

## 1. 背景与目标

人工审计确认 12/12 在 CNINFO 网页「公司介绍」可见结构化 profile，故根因调查从 **sample cleaning** 转向 **endpoint / parser debug**。

**目标：** 判定失败属于下列哪一类（可多选）：

| 类别 | 说明 |
|------|------|
| `endpoint_parameter_issue` | 仅 `scode` 不足；网页使用 `stockCode` + `orgId` |
| `parser_schema_assumption_issue` | runner 硬编码 `data.records` 路径 |
| `current_endpoint_not_web_source` | `getCompanyIntroduction?scode=` 非网页 Tab 实际接口 |
| `response_shape_mismatch` | 有 `data` 但非 `records` list |
| `source_coverage_gap` | 网页有字段但 API 覆盖不全 |
| `sample_quality_issue` | 仅当 debug 证明网页亦无可达数据时才启用 |

**非目标：** 新 source discovery · stable 200 v2 · 剔除 12 家以提高 pass 率。

## 2. 十二家公司清单

| code | name | board | orgid | runner basic URL 模式 |
|------|------|-------|-------|------------------------|
| 300261 | 雅本化学 | chinext | 9900021099 | `getCompanyIntroduction?scode=300261` |
| 300288 | 朗玛信息 | chinext | 9900021632 | `getCompanyIntroduction?scode=300288` |
| 300355 | 蒙草生态 | chinext | 9900022668 | `getCompanyIntroduction?scode=300355` |
| 300414 | 中光防雷 | chinext | 9900023935 | `getCompanyIntroduction?scode=300414` |
| 600061 | 国投资本 | sse_main | gssh0600061 | `getCompanyIntroduction?scode=600061` |
| 600063 | 皖维高新 | sse_main | gssh0600063 | `getCompanyIntroduction?scode=600063` |
| 600130 | 波导股份 | sse_main | gssh0600130 | `getCompanyIntroduction?scode=600130` |
| 600203 | 福日电子 | sse_main | gssh0600203 | `getCompanyIntroduction?scode=600203` |
| 600207 | 安彩高科 | sse_main | gssh0600207 | `getCompanyIntroduction?scode=600207` |
| 600233 | 圆通速递 | sse_main | gssh0600233 | `getCompanyIntroduction?scode=600233` |
| 600390 | 五矿资本 | sse_main | gssh0600390 | `getCompanyIntroduction?scode=600390` |
| 600523 | 贵航股份 | sse_main | gssh0600523 | `getCompanyIntroduction?scode=600523` |

**live 失败形态（12/12 一致）：** basic → `empty_but_valid_response`；dividend / executive / share_capital / 股东 → `schema_unexpected` · `data.records missing`；HTTP **200**。

## 3. Debug 步骤（批准後执行）

### A. Runner 侧（已有 live report，无需新请求）

从 [stable 200 failure cases](../outputs/validation/cninfo_c_class_stable_200_failure_cases.csv) 提取：

- 每家公司 × 每 source 的 `request_url`
- `http_status` · `json_code` · `result_code` · `retrieval_status` · `error_message`

### B. 网页 URL 对照（人工 DevTools）

对每家公司记录：

```
https://www.cninfo.com.cn/new/disclosure/stock?stockCode={code}&orgId={orgid}#companyProfile
```

记录 `stockCode` / `orgId` 与 runner `scode-only` 差异。

### C. 接口对比

| 检查项 | 方法 |
|--------|------|
| C1 | `getCompanyIntroduction?scode=xxx` 是否返回 `data.records` |
| C2 | raw JSON 是否存在 `data` 但结构非 `records` |
| C3 | 网页 Network ·「公司介绍」Tab 实际 XHR/fetch URL |
| C4 | 网页接口是否同时带 `orgId` / `secCode` / 其它 query |
| C5 | dividend / executive 等是否同一参数问题 |

### D. 失败分类矩阵

每家公司一行，填入 `failure_category`（上表枚举）。

## 4. 计划产出（下一轮 · 需人工批准）

| 产出 | 路径 |
|------|------|
| debug cases | `outputs/validation/cninfo_c_class_12_six_fail_endpoint_debug_cases.csv` |
| debug summary | `outputs/validation/cninfo_c_class_12_six_fail_endpoint_debug_summary.md` |

**debug_cases.csv 字段（草案）：**

- `stock_code` · `company_name` · `board` · `orgid`
- `runner_request_url` · `web_cninfo_url`
- `web_network_endpoint` · `web_has_records` · `runner_has_records`
- `json_top_level_keys` · `failure_category` · `notes`

## 5. 暂停项

| 项 | 状态 |
|----|------|
| stable 200 v2 样本清洗 | **PAUSED** |
| 剔除 12 家 six-fail | **禁止**（过拟合风险） |
| 889 / 200 全量重 live | **不做** |
| dividend YAML backfill | **HOLD** |
| verified / testing_stable_sample | **不写** |

## 6. 批准门槛

执行最小化 debug（含受控 CNINFO 网页 DevTools / 少量 API 对照）前需：

1. 人工批准本 plan；
2. 明确 **仅 12 家** 范围；
3. 结果只写入 debug cases/summary，**不**自动改 stable 样本、**不**升级 source status 至 verified。

## 7. 红线（本轮）

- **不跑 live**
- **不程序请求 CNINFO**（本轮零网络）
- **不生成 stable 200 v2**
- **不 YAML backfill** · **无 DB** · **无 verified**

## 8. 参考

- [manual audit CSV](../outputs/validation/cninfo_c_class_stable_200_manual_audit_12_companies.csv)
- [manual audit plan](cninfo_c_class_manual_audit_12_six_fail_companies.md)
- [stable 200 diagnosis](../outputs/validation/cninfo_c_class_stable_200_diagnosis.md)
- `lab/validate_cninfo_c_class_scale_smoke.py` — `_scode_url` · `validate_basic_live` · `validate_records_list_live`
