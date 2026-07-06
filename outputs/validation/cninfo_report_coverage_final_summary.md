# CNINFO A 类报告 coverage — Era C Phase 1 最终总结

- 生成时间：2026-07-02（离线整理）
- 脚本：`lab/validate_cninfo_report_coverage.py`
- 分层口径：[plans/cninfo_data_source_layered_inventory.md](../../plans/cninfo_data_source_layered_inventory.md)（A 类）
- 详细跑次摘要：[cninfo_report_coverage_validation_summary.md](cninfo_report_coverage_validation_summary.md)

---

## 1. 为什么旧 368/780 口径作废

旧验证（`cninfo_report_announcement_validation_summary.md`）按 **company × report_type × query_strategy** 计行，得到 `success 368/780`。

该口径存在根本缺陷：

| 问题 | 说明 |
|------|------|
| 一行 ≠ 一份报告 | 同一家公司、同一份预期报告，会因多种 query strategy 拆成多行 |
| success / failed 可并存 | 同一报告可能一行 success、另一行 failed，无法汇总为「到底找没找到」 |
| 分母膨胀 | 780 行混入策略维度，不是「公司 × 预期报告期」的干净分母 |
| 无法回答核心问题 | **「这家公司这份报告到底找没找到？」** — 旧口径不能直接回答 |

因此 **368/780 不作为 Era C A 类最终 coverage 口径**，仅保留为历史策略探测记录。

---

## 2. 新口径（Phase 1 权威）

与 [cninfo_data_source_layered_inventory.md](../../plans/cninfo_data_source_layered_inventory.md) A 类定义对齐：

| 要素 | 定义 |
|------|------|
| **计行单位** | `company × report_type × expected_period` |
| **一行** | 一家公司、一种报告类型、一个预期报告期（如 2024 年报、2024Q1） |
| **内部 fallback** | 多种 query strategy（关键词、seDate、category、stock/orgId/column 变体）仅在 `try_find_report` 内部尝试，**命中即停，不拆行** |
| **分母 expected** | `mapping_status=mapped` 的公司 × 各 report_type 的 expected_period |
| **分子 found** | `found=yes`，且标题匹配 report_type、`parsed_report_period == expected_period`、`pdf_url` 非空 |
| **skipped** | `needs_orgid_mapping` 计入 CSV 与 skipped 统计，**不计入 coverage 分母** |
| **公式** | **coverage = found / expected** |

---

## 3. 最终结果（40 家 P0 样本，30 mapped）

### 3.1 总体

| 指标 | 数值 |
|------|------|
| 样本公司数 | 40 |
| mapped 公司数 | 30 |
| **expected rows（分母）** | **120** |
| **found** | **113** |
| **not_found** | **7** |
| **skipped rows** | **40**（10 家 SZSE 主板未映射 orgId） |
| **overall coverage** | **113/120 = 94.17%** |

### 3.2 按 report_type

| report_type | found / expected | coverage |
|-------------|------------------|----------|
| annual_report | 30/30 | **100%** |
| semi_annual_report | 30/30 | **100%** |
| quarterly_report_q1 | 26/30 | 86.67% |
| quarterly_report_q3 | 27/30 | 90.00% |

### 3.3 按 exchange

| exchange | found / expected | coverage |
|----------|------------------|----------|
| SSE | 68/68 | **100%** |
| BSE | 24/24 | **100%** |
| SZSE | 21/28 | 75.00% |

（SZSE 28 行 = 7 家 mapped 创业板 × 4 report_type；10 家未映射主板仅产生 skipped，不计入分母。）

### 3.4 failure_reason

- not_found 的 7 行：**全部为 `empty_response`**（HTTP 200，公告列表为空）

---

## 4. 参数修复过程（三阶段）

### 4.1 阶段一：SZSE / BSE 身份与 column（56.67% → 84.17%）

| 板块 | 问题 | 修复 |
|------|------|------|
| SZSE 创业板 | F10 经验规则 `gssh0{code}` 对 `hisAnnouncement/query` 无效 → `empty_response` | 优先 `CHINEXT_ANNOUNCEMENT_ORGID_OVERRIDES`（numeric orgId）；gssh 时 fallback topSearch |
| BSE 北交所 | 旧脚本 `column=neeq` | 改为 `column=bj`（与 `probe_cninfo` 一致），fallback `neeq`；stock 试 `920xxx` 与 `430xxx` |

修复后：**101/120 = 84.17%**（年报/半年报 100%；季报仍集中在创业板与北交所）。

详见：[cninfo_report_coverage_parameter_diagnostics.md](cninfo_report_coverage_parameter_diagnostics.md)

### 4.2 阶段二：Q1/Q3 季报策略（84.17% → 94.17%）

在 **不改年报/半年报逻辑** 前提下，仅增强季报：

- **quarterly_keyword_expanded**：一季报/三季报、一季度报告、披露提示性公告、全文等关键词变体
- **quarterly_seDate_fallback**：SZSE/BSE 季报披露窗口（Q1：3–5 月；Q3：9–11 月）
- **quarterly_category_fallback**：BSE 季报尝试 `category_yjdbg_szsh` / `category_sjdbg_szsh`
- **title_patterns / parse_report_period**：扩展一季/三季及「披露提示性公告」标题识别

| 指标 | 优化前 | 优化后 | Δ |
|------|--------|--------|---|
| overall | 101/120 = 84.17% | **113/120 = 94.17%** | **+12** |
| Q1 | 20/30 | 26/30 | +6 |
| Q3 | 21/30 | 27/30 | +6 |

季报新增 fallback 命中：**12 行**（主要为 `quarterly_category_fallback`，挽回北交所 12 条季报）。

详见：[cninfo_report_quarterly_failure_diagnostics.md](cninfo_report_quarterly_failure_diagnostics.md)、validation summary §14。

### 4.3 阶段轨迹一览

```
旧口径 368/780（作废，非 coverage）
    ↓ 新口径 + 身份/column 修复
84.17%（101/120）
    ↓ 季报关键词 / seDate / category
94.17%（113/120）← Phase 1 最终结果
```

---

## 5. 剩余问题

| 维度 | 结论 |
|------|------|
| **数量** | 7 条 not_found |
| **分布** | **全部为 SZSE 创业板 Q1/Q3 季报** |
| **公司** | 300001 特锐德、300002 神州泰岳、300003 乐普医疗（仅 Q1）、300006 莱美药业 |
| **failure_reason** | 全部为 `empty_response`（已耗尽 param variant + 全部 strategy + 季报 fallback） |
| **年报/半年报** | **已不是问题**（30/30 = 100%） |
| **SSE / BSE** | **已达到 100%**（mapped 样本内） |
| **SZSE 主板** | 10 家未映射 orgId → skipped，需 mapping 扩展后再纳入分母 |

**后续若继续提升**：应单独做 **SZSE 创业板 Q1/Q3 residual fix**（人工抽查 CNINFO 是否确有 2024Q1/Q3 公告、标题是否与现有模式不一致），**不要**再动年报/半年报或 BSE 已稳定逻辑。

### 剩余 7 行明细

| company_code | 公司 | report_type | failure_reason |
|--------------|------|-------------|----------------|
| 300001 | 特锐德 | quarterly_report_q1 | empty_response |
| 300001 | 特锐德 | quarterly_report_q3 | empty_response |
| 300002 | 神州泰岳 | quarterly_report_q1 | empty_response |
| 300002 | 神州泰岳 | quarterly_report_q3 | empty_response |
| 300003 | 乐普医疗 | quarterly_report_q1 | empty_response |
| 300006 | 莱美药业 | quarterly_report_q1 | empty_response |
| 300006 | 莱美药业 | quarterly_report_q3 | empty_response |

---

## 6. 当前结论（recommended_status）

| 项 | 判定 |
|----|------|
| **A 类报告 PDF 文档流** | 达到 **testing / usable candidate**（94.17%，阈值 90–95%） |
| **verified** | **不写** — 仅代表当前 40 家 P0 小样本 |
| **工程化主线** | 可作为后续 **document/report retrieval** 主线继续工程化（检索 → `pdf_url` → 与 Era B 抽取衔接） |
| **stable pipeline** | **暂不写** — 仍有 7 条 SZSE 创业板季报缺口，且 10 家 SZSE 主板尚未 mapped |

与分层表 A 类状态对齐：年报/半年报 **stable candidate**（本样本 100%）；一季报/三季报 **testing**（86–90%）。

---

## 7. 是否还有提升机会

| 点 | 说明 |
|----|------|
| **理论上限** | 当前 94.17%；若修复剩余 **7 条**，可达 **120/120 = 100%**（在 mapped 30 家、2024 预期期内） |
| **问题集中度** | 剩余问题 **高度集中**（4 家公司 × 创业板季报），非全市场分散失败 |
| **建议下一步** | 仅针对 **SZSE 创业板 Q1/Q3** 做 residual diagnostics（人工标题对照 + 可选单公司 probe），参考已成功的 300004/300005/300007 |
| **不建议** | 继续改 **annual_report / semi_annual_report** 逻辑（已 100%）；不宜为 7 条个案大幅放宽标题匹配导致误命中 |

提升 ROI 最高路径：**窄口径 residual fix**，而非扩大 P0 样本或回退旧 368/780 口径。

---

## 8. 边界确认

- 未下载 PDF 正文；未解析 PDF；未计算 hash
- 未做数据库 / MinIO 接入；未使用 BrowserUser
- 请求间 sleep；不绕过登录 / 验证码 / 权限
- 结果仅代表当前 **40 家 P0 样本**（30 mapped + 10 skipped）
- **recommended_status 不写 verified**

---

## 9. 相关产物索引

| 文件 | 用途 |
|------|------|
| [cninfo_report_coverage_validation.csv](cninfo_report_coverage_validation.csv) | 逐行 coverage 结果（160 行含 skipped） |
| [cninfo_report_coverage_validation_summary.md](cninfo_report_coverage_validation_summary.md) | 跑次摘要 + Q1/Q3 优化对比 |
| [cninfo_report_coverage_parameter_diagnostics.md](cninfo_report_coverage_parameter_diagnostics.md) | SSE/SZSE/BSE 参数与 orgId/column 修复 |
| [cninfo_report_quarterly_failure_diagnostics.md](cninfo_report_quarterly_failure_diagnostics.md) | 季报 not_found 离线根因分析 |
| [cninfo_report_announcement_validation_summary.md](cninfo_report_announcement_validation_summary.md) | **旧口径** 368/780（历史参考） |
| [plans/cninfo_data_source_layered_inventory.md](../../plans/cninfo_data_source_layered_inventory.md) | A–F 分层与验证口径权威文档 |

---

## 10. Phase 1 一句话

**Era C Phase 1 以「company × expected_period」干净口径完成 A 类 coverage 验证：废弃 368/780 策略计行；经身份/column 与季报策略三轮修复，mapped 样本达 94.17%；SSE/BSE 与年报半年报已稳，剩余 7 条全部为 SZSE 创业板季报 empty_response，A 类整体评为 testing/usable candidate，可继续工程化但尚未 stable pipeline。**
