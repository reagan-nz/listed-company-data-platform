# CNINFO Era C Phase 1 A 类报告 Retrieval 最终总结

- 生成时间：2026-07-05（离线整理）
- 权威分层口径：[plans/cninfo_data_source_layered_inventory.md](../../plans/cninfo_data_source_layered_inventory.md)（A 类）
- 脚本：`lab/validate_cninfo_report_coverage.py`
- P0 总结：[cninfo_report_coverage_final_summary.md](cninfo_report_coverage_final_summary.md)
- P1 跑次摘要：[cninfo_report_p1_coverage_validation_summary.md](cninfo_report_p1_coverage_validation_summary.md)
- P1 精简收口：[cninfo_report_p1_coverage_final_summary.md](cninfo_report_p1_coverage_final_summary.md)

---

## 1. 阶段目标

**Era C Phase 1** 验证 CNINFO **A 类报告 PDF 文档流**的 **report retrieval** 是否可工程化。

| 要素 | 说明 |
|------|------|
| 报告类型 | `annual_report`、`semi_annual_report`、`quarterly_report_q1`、`quarterly_report_q3` |
| 计行口径 | **company × report_type × expected_period** |
| 数据源 | `hisAnnouncement/query`（公告全文检索） |
| 验证内容 | 能否稳定检索到 **正式报告 PDF 链接**（`pdf_url`）、标题与报告期是否匹配 |
| **非目标** | 不下载 / 解析 PDF 正文；不计算 hash；不接生产库 |

目标不是宣称「全市场已 verified」，而是：在 **分层扩展样本（P0 → P1）** 上，机制是否 **passed**，质量是否经 **audit** 支撑，可否评为 **testing / usable candidate**。

---

## 2. 为什么旧口径作废

旧验证（`cninfo_report_announcement_validation_summary.md`）按 **company × report_type × query_strategy** 计行，得到 **`success 368/780`**。

| 问题 | 说明 |
|------|------|
| 一行 ≠ 一份报告 | 同一公司、同一预期报告，因多种 query strategy 拆成多行 |
| success / failed 可并存 | 无法汇总为「这家公司这份报告到底找没找到」 |
| 分母膨胀 | 780 行混入策略维度，不是干净的「公司 × 预期报告期」分母 |

**结论：`368/780` 不作为 Era C A 类最终 coverage 口径**，仅保留为历史策略探测记录。Phase 1 全面改用 **company × report_type × expected_period**。

---

## 3. P0 小样本结果

| 指标 | 数值 |
|------|------|
| 样本公司数 | 40 |
| **mapped 公司数** | **30** |
| skipped（needs_orgid_mapping） | 10 家 SZSE 主板 |
| **expected rows** | **120** |
| **found** | **113** |
| **coverage** | **113/120 = 94.17%** |

### 按 report_type

| report_type | found / expected | coverage |
|-------------|------------------|----------|
| annual_report | 30/30 | 100% |
| semi_annual_report | 30/30 | 100% |
| quarterly_report_q1 | 26/30 | 86.67% |
| quarterly_report_q3 | 27/30 | 90.00% |

### 按 exchange

| exchange | found / expected | coverage |
|----------|------------------|----------|
| SSE | 68/68 | 100% |
| BSE | 24/24 | 100% |
| SZSE | 21/28 | 75.00% |

**P0 结论：** mechanism **passed** — 在已知 mapped 身份与参数修复后，`hisAnnouncement/query` 可检索 A 类报告 PDF 链接；**不代表全市场**，SZSE 创业板 Q1/Q3 仍有 `empty_response` 残留。

---

## 4. P1 扩展样本设计

| 项 | 设计 |
|----|------|
| 目标样本 | **200 家** |
| 分层 | 五层各 **40** 家：SSE 主板、SZSE 主板、SZSE 创业板、SSE 科创板、BSE 北交所 |
| random seed | 42（可复现） |
| **mapped** | **199** |
| **skipped** | **1** 家（000001 平安银行，`needs_orgid_mapping`），**4 行** |
| **expected rows（分母）** | **796** |

详见 [cninfo_report_p1_expansion_plan.md](cninfo_report_p1_expansion_plan.md)、[cninfo_report_p1_sample_companies_summary.md](cninfo_report_p1_sample_companies_summary.md)、[cninfo_report_p1_identity_mapping_summary.md](cninfo_report_p1_identity_mapping_summary.md)。

---

## 5. 参数修复与 retrieval 规则演进

经 P0 失败诊断与 [cninfo_report_p1_coverage_parameter_diagnostics.md](cninfo_report_p1_coverage_parameter_diagnostics.md) 确认，主要修复如下：

| 板块 / 问题 | 修正 |
|-------------|------|
| **SZSE 创业板** `gssh0{code}` orgId | 对公告查询无效 → 改 **numeric orgId** + `CHINEXT_ANNOUNCEMENT_ORGID_OVERRIDES`；fallback topSearch |
| **BSE** `column=neeq`（旧） | 改为 **`column=bj`**，fallback **`neeq`** |
| **BSE stock** | 尝试 **`920xxx`** 与 **`430xxx`**（old/new code） |
| **Q1/Q3** | 增加 `quarterly_keyword_expanded`、`quarterly_seDate_fallback`、`quarterly_category_fallback`（SZSE + BSE） |
| **策略链** | `keyword_with_year` → `keyword_recent` → `longer_time_window` → `report_title_pattern`；季报另增 expanded / seDate / category fallback；**命中即停，不拆行** |

修正轨迹（P1 overall）：

```
初跑（无 title filter / 无完整季报 fallback）：620/796 = 77.89%
    ↓ 参数修复 + 季报策略 + title filter v1
750/796 = 94.22%（含假阳性）
    ↓ audit-driven official title exclusion（全 report_type）
749/796 = 94.10%（effective found，最终 P1 rerun）
```

---

## 6. Title filter 修正

**一轮 quality audit** 发现：旧 retrieval **94.22%** 中 found 样本标题级 pass rate 仅 **78%**，大量 **假阳性**。

主要假命中类型：

- **披露提示性公告** / 提示性公告
- **说明会** / 业绩说明会 / 投资者说明会
- **预告公告**
- **问询函** / 回复公告 / 监管问询函
- **摘要** / 解读
- **关于披露**（交叉披露其他公司报告）
- **延期披露** / **关于延期披露**（二轮唯一 fail，已补入脚本 exclusion）

因此 **official report title exclusion** 扩展到 **所有 report_type**。**found** 必须是 **effective found**：

1. `pdf_url` 非空；
2. `parsed_report_period == expected_period`；
3. 标题匹配 `report_type`；
4. **未命中** official title exclusion（命中则继续 fallback，不计入分子）。

最终 rerun：`excluded_title_count = 0`（假阳性已在策略链层面被排除或不再命中）。二轮 audit 后脚本另补 **延期披露** exclusion；若重跑，个别行可能从 found 降为 excluded（影响极小）。

---

## 7. 最终 P1 rerun 结果

跑次日志：[cninfo_report_p1_coverage_final_rerun.log](cninfo_report_p1_coverage_final_rerun.log)  
逐行结果：[cninfo_report_p1_coverage_validation.csv](cninfo_report_p1_coverage_validation.csv)

| 指标 | 数值 |
|------|------|
| mapped companies | 199 |
| **expected rows** | **796** |
| **found / effective found** | **749** |
| **not_found** | **47** |
| **skipped rows** | **4** |
| **effective coverage** | **749/796 = 94.10%** |

### 按 report_type

| report_type | found / expected | coverage |
|-------------|------------------|----------|
| annual_report | 193/199 | **96.98%** |
| semi_annual_report | 185/199 | **92.96%** |
| quarterly_report_q1 | 184/199 | **92.46%** |
| quarterly_report_q3 | 187/199 | **93.97%** |

### 按 exchange

| exchange | found / expected | coverage |
|----------|------------------|----------|
| SSE | 304/320 | **95.00%** |
| SZSE | 305/316 | **96.52%** |
| BSE | 140/160 | **87.50%** |

### 按 board

| board | found / expected | coverage |
|-------|------------------|----------|
| 主板 | 301/316 | **95.25%** |
| 创业板 | 157/160 | **98.12%** |
| 科创板 | 151/160 | **94.38%** |
| 北交所 | 140/160 | **87.50%** |

### not_found 构成

| failure_reason | 行数 |
|----------------|------|
| empty_response | **39** |
| period_mismatch | **8** |

与 P0 对比：P0 **113/120 = 94.17%** → P1 **749/796 = 94.10%**，机制在 **199 mapped / 五层样本** 上与 P0 **同量级**，但样本更大、板块更均衡。

---

## 8. Quality audit 结果

### 一轮（seed=42，修正前 CSV，750 found）

| 指标 | 数值 |
|------|------|
| found sample | 100 |
| pass | 78 |
| fail | 22 |
| **pass rate** | **78%** |
| 主因 | **披露提示性公告**（18/22 fail） |
| 粗算有效 coverage | **~73.5%**（750 × 78% / 796） |

**结论：** 旧 **94.22%** retrieval 含大量标题假阳性，**不能当 accuracy**。

详见 [cninfo_report_p1_quality_audit_results.md](cninfo_report_p1_quality_audit_results.md)。

### 二轮（seed=43，title-filter 修正后 CSV，749 found）

| 指标 | 数值 |
|------|------|
| found sample | 40 |
| pass | 39 |
| fail | 1 |
| **found pass rate** | **97.5%** |
| not_found sample | 10 |
| not_found 合理 | **10/10** |
| 唯一 fail | P1-AUD2-006（300241 瑞丰光电 Q1，**延期披露**公告） |
| 粗算有效 coverage | **~91.7%**（749 × 97.5% / 796） |

**结论：** title filter 对披露提示性公告类假阳性 **修正效果显著**；二轮支持 **94.10% effective coverage 可信度明显高于一轮旧口径**；延期披露 exclusion 已写入脚本。

详见 [cninfo_report_p1_quality_audit_round2_results.md](cninfo_report_p1_quality_audit_round2_results.md)。

---

## 9. 当前 recommended_status

| 维度 | 结论 |
|------|------|
| **P1 样本内 recommended_status** | **testing / usable candidate** |
| 自动 effective coverage | **94.10%**（749/796） |
| audit 外推有效 coverage | **~91.7%**（二轮抽样，非全量人工 accuracy） |
| **verified** | **不写** |
| **full-market stable** | **不写** |

**94.10%** 是 **effective retrieval coverage**（脚本在 CNINFO 上检索到符合规则的 PDF 链接的比例），**不是**对 796 行全量人工打开 PDF 后的 accuracy，**也不是** 6000+ 上市公司全市场结论。但经 **二轮 audit（97.5% found pass）**，其可信度 **明显高于** 一轮修正前外推的 **~73.5%**。

---

## 10. 剩余问题

| 项 | 说明 |
|----|------|
| **remaining gaps** | **47** 行 not_found |
| empty_response | **39**（主因，多集中在 BSE 920xxx 样本） |
| period_mismatch | **8**（新上市、历史代码、退市或对应期间报告不存在） |

**BSE 北交所 coverage 最低：140/160 = 87.50%**

已确认参数侧（非 column 配错）：

- `column=bj`，fallback `neeq`
- stock 尝试 `920xxx` / `430xxx`

剩余问题更可能来自：

- **BSE old/new code**（920 ↔ 430）与 mapping 不一致；
- **公司上市状态**（新挂牌、尚未披露对应期报）；
- **披露期间不存在**（如 2024H1 对 2024 年末上市公司）；
- **样本历史代码**（600840 新湖创业、000522 白云山A 等）；
- **查询标题 / 关键词策略**与 CNINFO 索引口径差异；
- CNINFO 对部分 BSE 公告 **返回空列表**（`empty_response`）。

完整 not_found 清单见 [cninfo_report_p1_coverage_validation_summary.md](cninfo_report_p1_coverage_validation_summary.md) §14。

---

## 11. 边界

- **未**下载 PDF 正文；**未**解析 PDF；**未**计算 hash。
- **未**接 PostgreSQL / MinIO / MongoDB。
- **未**使用 BrowserUser。
- **不**绕过登录 / 验证码 / 付费 / 权限。
- 请求间 sleep；仅使用公开 `hisAnnouncement/query` 接口。
- 结果仅代表 **P1 扩展样本（199 mapped / 796 expected rows）**。
- **不是 full-market stable**；**不写 verified**。

---

## 12. 下一步建议

1. **阶段性 close Phase 1 A 类主线** — retrieval 机制与 title filter 在 P1 样本内已达 **testing / usable candidate**。
2. **单独开 BSE residual diagnostics** — `empty_response`、920/430 code、not_found 公司状态（不必再大改主 retrieval 逻辑）。
3. **暂缓全市场扩展** — 不在未解决 BSE residual 前盲目扩面。
4. **进入 Era C Phase 2** — **D 类固定表格入口**探测（`cninfo_table_sources.yaml` + `validate_cninfo_table_sources.py`）。
5. **生产化（若后续需要）** — 再加 PDF download metadata、hash、document 表；当前 Phase 1 刻意未做。

可选：对 **延期披露** exclusion 做一次轻量 P1 rerun，确认 `found` 与 audit fail 行归零（非阻塞 Phase 1 close）。

---

## 13. 产物索引

| 文件 | 用途 |
|------|------|
| [cninfo_report_coverage_final_summary.md](cninfo_report_coverage_final_summary.md) | **P0** 小样本最终总结 |
| [cninfo_report_coverage_validation_summary.md](cninfo_report_coverage_validation_summary.md) | P0 跑次摘要 |
| [cninfo_report_coverage_validation.csv](cninfo_report_coverage_validation.csv) | P0 逐行 coverage |
| [cninfo_report_p1_expansion_plan.md](cninfo_report_p1_expansion_plan.md) | **P1 扩展样本设计** |
| [cninfo_report_p1_sample_companies.csv](cninfo_report_p1_sample_companies.csv) | P1 样本公司清单 |
| [cninfo_report_p1_sample_companies_summary.md](cninfo_report_p1_sample_companies_summary.md) | P1 样本摘要 |
| [cninfo_report_p1_identity_mapping.csv](cninfo_report_p1_identity_mapping.csv) | P1 identity mapping |
| [cninfo_report_p1_identity_mapping_summary.md](cninfo_report_p1_identity_mapping_summary.md) | **P1 identity mapping 摘要** |
| [cninfo_report_p1_coverage_validation.csv](cninfo_report_p1_coverage_validation.csv) | **P1 逐行 coverage（最终 rerun）** |
| [cninfo_report_p1_coverage_validation_summary.md](cninfo_report_p1_coverage_validation_summary.md) | **P1 跑次摘要** |
| [cninfo_report_p1_coverage_final_rerun.log](cninfo_report_p1_coverage_final_rerun.log) | **P1 最终 rerun 日志** |
| [cninfo_report_p1_coverage_parameter_diagnostics.md](cninfo_report_p1_coverage_parameter_diagnostics.md) | **参数诊断**（SZSE orgId / BSE column / stock） |
| [cninfo_report_p1_quality_audit.md](cninfo_report_p1_quality_audit.md) | 一轮 audit 抽样设计 |
| [cninfo_report_p1_quality_audit_sample.csv](cninfo_report_p1_quality_audit_sample.csv) | 一轮 audit 样本 |
| [cninfo_report_p1_quality_audit_results.md](cninfo_report_p1_quality_audit_results.md) | **一轮 audit 结果** |
| [cninfo_report_p1_quality_audit_round2.md](cninfo_report_p1_quality_audit_round2.md) | 二轮 audit 抽样设计 |
| [cninfo_report_p1_quality_audit_round2_sample.csv](cninfo_report_p1_quality_audit_round2_sample.csv) | 二轮 audit 样本 |
| [cninfo_report_p1_quality_audit_round2_results.md](cninfo_report_p1_quality_audit_round2_results.md) | **二轮 audit 结果** |
| [cninfo_report_p1_coverage_final_summary.md](cninfo_report_p1_coverage_final_summary.md) | P1 精简收口（指向本文档） |
| **本文档** | **Era C Phase 1 A 类最终总结** |

### Phase 1 一句话

**A 类 report retrieval 经 P0 机制验证与 P1 五层扩展（749/796 = 94.10% effective coverage），经两轮 quality audit 修正 title filter 后可信度显著提升，评为 P1 样本内 testing / usable candidate；Phase 1 主线可收口，下一步单独处理 BSE residual 并进入 Phase 2 D 类表格探测 — 不写 verified，不写 full-market stable。**
