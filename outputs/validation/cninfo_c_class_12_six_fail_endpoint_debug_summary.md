# CNINFO C-Class 12 Six-Fail Endpoint Debug Summary

_生成时间：2026-07-07 04:03 UTC_

> **范围：** stable 200 中 12 家 6/6 fail · 仅 debug 现有 C-class endpoints · **无** YAML · **无** verified

## 1. 执行摘要

| 项 | 值 |
|----|-----|
| 公司数 | **12** |
| 每家公司 CNINFO 请求 | **7**（6 runner + 1 orgId basic 变体） |
| 总请求 | **84** |
| debug basic 现可达（非空 profile） | **11/12** |
| live 曾 fail、debug 现 pass | **11/12** |
| cases CSV | [cninfo_c_class_12_six_fail_endpoint_debug_cases.csv](cninfo_c_class_12_six_fail_endpoint_debug_cases.csv) |

## 2. 网页存在 vs API/parser

- 人工审计：**12/12** 网页「公司介绍」有结构化 profile
- 本轮 paced debug（scode-only runner URL）：**11/12** 现返回 `resultCode=200` 且 `basicInformation`/`listingInformation` 非空
- 仍失败：**600203**
- 结论：失败**不是**永久 `sample_quality_issue`；多数公司在单批 debug  pacing 下 endpoint 可达

## 3. 最常见 failure category

| category | count |
|----------|-------|
| `needs_more_check` | 11 |
| `endpoint_parameter_issue` | 1 |

**最主要：** `needs_more_check`

## 4. basic_profile 机制（对照 stable 200 live）

| 维度 | stable 200 live | 本轮 debug |
|------|-----------------|------------|
| runner URL | `getCompanyIntroduction?scode=xxx`（无 orgId query） | 相同 |
| HTTP | 200 | 200 |
| basic resultCode | **90001**（12/12） | **200**（多数） |
| 五源 resultCode | **429** + `data.records missing` | **200** + records 存在 |
| Referer | 含 orgId（runner 已有） | 含 orgId（runner 已有） |

**解读：** live 中 `json.resultCode=429` **不是** HTTP 429，而是 CNINFO 业务码；与 stable 200 **1400 连跑**时的节流/上下文退化高度一致。

## 5. 六源是否同因

- `six_source_same_cause=yes`：**10/12**（本轮 debug 下六源同达）
- stable 200 live：六源**同簇失败**（basic 90001 + 五源 429）
- 本轮 debug：六源**同簇成功**（均为 200 + records）

## 6. orgId query 变体

- `scode+orgId` 修复 scode-only 空 basic：**1/12**（**600203 福日电子** — scode-only `resultCode=90001` 且 `basicInformation` 空；加 `orgId` 后 `resultCode=200` 且 profile 非空）
- 对其余 11 家：**不支持**「仅靠加 orgId query 即可修复」；Referer 已带 orgId 时 scode-only query 通常足够
- **600130 波导股份**：basic 可达，但五源仍 `resultCode=429`（无 `data.records`）— 连跑内节流/部分退化

## 7. 建议

| 问题 | 判断 |
|------|------|
| endpoint 参数（缺 orgId query） | **次要** — orgId 变体未显著优于 scode-only |
| parser `data.records` 假设 | **非主因** — debug 下 records 路径有效 |
| endpoint 选错 | **否** — `getCompanyIntroduction` 等 data20 路径正确 |
| 批量 live 节流/上下文 | **主因候选** — live fail vs debug pass 对比 |
| sample_quality_issue | **否** |

### 是否建议修 runner

**是（有限）。** 优先：
1. 对 `resultCode` 429/90001 增加**可重试 + 退避**（区分 JSON 业务码与 HTTP 429）；
2. 解析前检查 `data.resultMsg`；
3. **不**改 endpoint 路径；orgId query 非必须但可作 retry 变体。

### 是否建议 targeted retry

**是。** runner 加重试后，仅 **12 家** 做 targeted retry（不扩 200/889 live）。

### stable 200 v2

**继续暂停。** 待 runner 退避修复 + 12 家 retry 结果再决定是否调整样本。

## 8. 红线

- 仅 12 家 · 无 Cookie/SID · 无 YAML · 无 DB · 无 verified

## 9. 参考

- [manual audit CSV](cninfo_c_class_stable_200_manual_audit_12_companies.csv)
- [stable 200 failure cases](cninfo_c_class_stable_200_failure_cases.csv)
- [debug plan](../plans/cninfo_c_class_12_six_fail_endpoint_debug_plan.md)
- `lab/debug_cninfo_c_class_12_six_fail_endpoints.py`
