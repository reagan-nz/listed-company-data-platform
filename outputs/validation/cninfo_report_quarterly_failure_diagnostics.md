# CNINFO 季报（Q1/Q3）not_found 诊断（Era C Phase 1）

- 生成时间：2026-07-02（离线分析，未联网）
- 输入：`cninfo_report_coverage_validation.csv`（coverage 84.17% 跑次）
- 关联：`cninfo_report_coverage_validation_summary.md`、`cninfo_report_coverage_parameter_diagnostics.md`
- 边界：未改 CSV / coverage 口径；未发新请求；未下载 PDF

---

## 1. 总览

| 指标 | Q1 | Q3 | 合计 |
|------|----|----|------|
| expected（mapped） | 30 | 30 | 60 |
| found | 20 | 21 | 41 |
| **not_found** | **10** | **9** | **19** |
| coverage | 66.67% | 70.00% | 68.33% |

对比：年报/半年报均为 **30/30 = 100%**；SSE 季报 **34/34 = 100%**。  
**全部 19 条 not_found 的 `failure_reason` 均为 `empty_response`（HTTP 200，公告列表为空）**，无 `period_mismatch` / `missing_pdf_url` / `not_found`（有返回但未命中）。

---

## 2. 按 exchange / board 分布

| exchange | board | Q1 not_found | Q3 not_found | 季报合计失败 | 备注 |
|----------|-------|--------------|--------------|--------------|------|
| **BSE** | 北交所 | 6 | 6 | **12** | 样本 6 家公司季报 **全失败** |
| **SZSE** | 创业板 | 4 | 3 | **7** | 7/14 季报行失败；SSE 主板未 mapped |
| SSE | 主板/科创板 | 0 | 0 | 0 | 季报 34/34 全成功 |

**结论：季报缺口 100% 集中在 BSE 北交所 + SZSE 创业板；参数修复后 SSE 季报已稳定，不是全局关键词问题。**

---

## 3. 失败 company_code 清单

### 3.1 按公司 × 季报

| company_code | 公司 | exchange | board | Q1 | Q3 | 年报/半年报 |
|--------------|------|----------|-------|----|----|-------------|
| 300001 | 特锐德 | SZSE | 创业板 | ❌ | ❌ | ✅ |
| 300002 | 神州泰岳 | SZSE | 创业板 | ❌ | ❌ | ✅ |
| 300003 | 乐普医疗 | SZSE | 创业板 | ❌ | ✅ | ✅ |
| 300006 | 莱美药业 | SZSE | 创业板 | ❌ | ❌ | ✅ |
| 430017 | 星昊医药 | BSE | 北交所 | ❌ | ❌ | ✅ |
| 430047 | 诺思兰德 | BSE | 北交所 | ❌ | ❌ | ✅ |
| 430090 | 同辉信息 | BSE | 北交所 | ❌ | ❌ | ✅ |
| 430139 | 华岭股份 | BSE | 北交所 | ❌ | ❌ | ✅ |
| 430198 | 微创光电 | BSE | 北交所 | ❌ | ❌ | ✅ |
| 430300 | 辰光医疗 | BSE | 北交所 | ❌ | ❌ | ✅ |

**10 家公司、19 行**（300003 仅 Q1 失败）。

### 3.2 创业板对照：成功 vs 失败

| 公司 | Q1 | Q3 | 命中标题特征（成功时） |
|------|----|----|------------------------|
| 300004 南风股份 | ✅ | ✅ | `…第一季度/第三季度报告…披露提示性公告` |
| 300005 探路者 | ✅ | ✅ | 同上 |
| 300007 汉威科技 | ✅ | ✅ | 同上 |
| 300003 乐普医疗 | ❌ | ✅ | Q3：`2024年第三季度报告披露提示性公告`（`keyword_recent`） |
| 300001/300002/300006 | ❌ | ❌ | — |

成功创业板季报多命中 **「披露提示性公告」** 类标题，而非「报告全文」；失败样本在 **同一 orgId override + column=szse** 下年报/半年报已成功，说明 **不是 orgId/column 整体错误**。

---

## 4. failure_reason 统计

| failure_reason | 条数 | 占比 |
|----------------|------|------|
| `empty_response` | **19** | **100%** |
| 其他 | 0 | 0% |

含义：对失败样本，当前脚本在 **全部内部 param variant × 全部 strategy × 全部 keyword** 组合下，CNINFO 均未返回任何公告行（而非「有公告但标题/报告期不匹配」）。

---

## 5. 失败样本查询参数（来自 CSV `notes` + mapping）

`last_param` 表示 **耗尽 fallback 后最后一组尝试**；成功样本的首组多为 `chinext_announcement_orgid_override` 或 `mapping_csv_orgid + column=bj`。

### 5.1 SZSE 创业板（7 行）

| code | period | query_code | CSV orgId | override orgId | column（primary） | last_param（耗尽后） |
|------|--------|------------|-----------|----------------|-------------------|----------------------|
| 300001 | Q1/Q3 | 300001 | gssh0300001 | 9900008270 | szse | `stock=cninfo_stock_code; orgid=mapping_csv_orgid; column=szse` |
| 300002 | Q1/Q3 | 300002 | gssh0300002 | 9900008268 | szse | 同上 |
| 300003 | Q1 | 300003 | gssh0300003 | 9900008269 | szse | 同上 |
| 300006 | Q1/Q3 | 300006 | gssh0300006 | 9900008273 | szse | 同上 |

推断 payload 形态（首组应已尝试）：`stock=30000x,990000827x`，`column=szse`，`searchkey` 依次为 `2024年第×季度报告` / `第×季度报告` / `季度报告` / 空（report_title_pattern），`seDate` 在前三策略为空、longer_time_window 为近三年。

### 5.2 BSE 北交所（12 行）

| code | period | query_code | orgId | column（primary） | last_param（耗尽后） |
|------|--------|------------|-------|-------------------|----------------------|
| 430017 | Q1/Q3 | 920017 | 9900003482 | bj | `stock=company_code; orgid=mapping_csv_orgid; column=neeq` |
| 430047 | Q1/Q3 | 920047 | 9900006121 | bj | 同上 |
| 430090 | Q1/Q3 | 920090 | 9900020567 | bj | 同上 |
| 430139 | Q1/Q3 | 920139 | 9900024205 | bj | 同上 |
| 430198 | Q1/Q3 | 920198 | 9900024889 | bj | 同上 |
| 430300 | Q1/Q3 | 920300 | 9900023934 | bj | 同上 |

推断已尝试组合：`920xxx`/`430xxx` × `orgId` × `column=bj|neeq`（见 parameter_diagnostics §5 BSE）。  
年报/半年报成功参数：`stock=920xxx,{orgId}`，`column=bj`（与 parameter_diagnostics 一致）。

---

## 6. 根因推测（按可能性排序）

### 6.1 关键词 / 标题写法（**主因，尤其创业板部分失败**）

当前脚本季报配置（`validate_cninfo_report_coverage.py`）：

| report_type | keyword_with_year | keywords_recent | title_patterns |
|-------------|-------------------|-----------------|----------------|
| Q1 | `2024年第一季度报告` | `第一季度报告`, `季度报告` | `第一季度报告` |
| Q3 | `2024年第三季度报告` | `第三季度报告`, `季度报告` | `第三季度报告` |

**缺口：**

1. **未覆盖「一季报 / 三季报 / 一季度报告 / 三季度报告」**——`parse_report_period` 已识别 `一季度报告`/`三季度报告`，但 **searchkey 与 title_patterns 未包含**，导致即使 CNINFO 有公告也可能搜不到或命中后被过滤。
2. **未覆盖「披露提示性公告」变体**——创业板成功案例（300004/300005/300007）标题多为 `…第一季度报告…披露提示性公告`；300003 Q3 亦如此。失败公司可能使用 **更短或不同措辞**（如仅「一季报」「一季度报告全文」），现有 searchkey 无匹配。
3. **`季度报告` 过宽但未单独作为 Q1/Q3 区分策略**——在 keyword_recent 中与季别词混用，对 empty_response 无帮助（接口层即无结果）。

**证据：** 300003 同公司 Q3 成功、Q1 失败 → orgId/column 正确，**Q1 专用关键词/标题更可疑**。300001/300002/300006 季报全失败但年报半年报成功 → **非身份映射问题，是季报检索词/标题覆盖不足或该公司季报标题更偏**。

### 6.2 BSE 季报检索词 + 披露习惯（**主因，北交所 12/12 失败**）

1. **6/6 北交所样本季报全部 empty_response**，年报/半年报在 `920xxx + bj` 下正常 → **query code / orgId / column 对定期报告主体可用**。
2. 北交所公司可能更常用 **「一季度报告」「三季度报告」「一季报」** 而非「第一季度报告」；或季报在 CNINFO 上 **标题/分类与沪深不一致**。
3. 脚本 **未使用 CNINFO category 码**（`probe_cninfo` 中 `category_yjdbg_szsh` / `category_sjdbg_szsh`），季报仅靠 `searchkey` 全文检索；BSE 上可能 **必须或更适合带 category 查询**。
4. **披露规则差异**：部分北交所公司历史上季报披露频率/格式与沪深不同；需在下一轮用更宽关键词或 category 探测区分「真无披露」与「检索未命中」。

### 6.3 seDate 时间窗口（**次要**）

- 当前 Q1/Q3 在 `keyword_with_year` / `keyword_recent` 下 `seDate=""`（全历史）；SSE 季报 100% 成功，说明 **空 seDate 对沪深并非普遍问题**。
- `longer_time_window` 已作为 fallback，失败样本仍 empty → **单靠加 seDate 可能不够**，但可对 **SZSE/BSE 季报优先或额外** 使用 `2024-01-01 ~ 2024-12-31` 等披露窗口（与 longer 并行），作为低成本增强。

### 6.4 query code / orgId（**基本可排除为主因**）

| 场景 | 证据 |
|------|------|
| 创业板 | 失败公司年报/半年报已用 `chinext_announcement_orgid_override` 成功；季报耗尽 fallback 后 last_param 显示 gssh，说明 **override 路径已试仍 empty** |
| 北交所 | 年报/半年报 `920xxx + numeric orgId + bj` 成功；季报同参组合已包含在 variant 内仍 empty |

**结论：季报 not_found 更像「搜不到公告」而非「orgId/column 完全错误」；但 BSE 仍值得在季报策略中 **强制优先 `920xxx+bj`** 并尝试 **category 查询**（不改变 coverage 行口径，仅内部 fallback）。

### 6.5 板块参数 column（**基本可排除**）

- 创业板失败与成功混用 `column=szse`。
- 北交所失败末组为 `neeq`，但前面应已试 `bj`；与年报成功 column 一致。

---

## 7. 与当前策略顺序的关系

内部顺序：`keyword_with_year` → `keyword_recent` → `longer_time_window` → `report_title_pattern`。

- **SSE 季报**：多数 `keyword_with_year` 即命中标准「第×季度报告」标题。
- **创业板成功**：多为 `keyword_with_year` 或 `keyword_recent` + 「披露提示性公告」标题。
- **失败样本**：四套策略 + 全部 param variant 均无公告 → 需在 **季报专用 keywords / title_patterns** 上扩展，而非调整年报/半年报。

---

## 8. 下一步建议（仅季报；不改 annual/semi）

### 8.1 扩展 Q1/Q3 关键词（推荐 P0）

在 `REPORT_TYPES` 的 **quarterly_report_q1 / quarterly_report_q3** 中增加（仅影响季报 strategy）：

**Q1 建议追加：**

- `一季报`
- `一季度报告`
- `第一季度报告全文`
- `第一季度报告披露` / `第一季度报告披露的提示性公告`

**Q3 建议追加：**

- `三季报`
- `三季度报告`
- `第三季度报告全文`
- `第三季度报告披露` / `第三季度报告披露的提示性公告`

同步扩展 `title_patterns`：

- Q1：增加 `一季度报告`、`一季报`
- Q3：增加 `三季度报告`、`三季报`

（`parse_report_period` 已支持一季/三季写法，扩展 title_patterns 可与解析对齐。）

### 8.2 BSE 季报专用放宽（推荐 P0）

- 在季报 fallback 中增加：`一季度报告`、`三季度报告`、`季报`（BSE 可仅在 `exchange==BSE` 时追加，避免污染 SSE）。
- 尝试 **category 参数**（内部 fallback，不拆行）：`category_yjdbg_szsh`（Q1）、`category_sjdbg_szsh`（Q3），`searchkey` 可为空或保留季别词（参考 `probe_cninfo.query_announcements`）。
- 保持 **stock=920xxx,orgId** + **column=bj** 为 BSE 季报首组参数。

### 8.3 时间窗口（推荐 P1）

- 对 **quarterly_report_q1 / q3** 且 `exchange in (SZSE, BSE)`：在 `keyword_recent` 之后增加一季专用 `seDate` fallback，例如 Q1：`2024-01-01 ~ 2024-06-30`，Q3：`2024-07-01 ~ 2024-12-31`。
- **不要**改动 `annual_report` / `semi_annual_report` 的 keyword 或 seDate 逻辑。

### 8.4 不建议在本阶段做的

- 不改 coverage 口径（仍一行 = company × report_type × expected_period）。
- 不为季报单独改 `parse_report_period`（除非新增 title_pattern 后需对齐，属标题匹配而非解析逻辑变更）。
- 不将 `needs_orgid_mapping` 的 SZSE 主板算入季报分母（当前已正确排除）。

### 8.5 验证方式

本地改脚本后重跑：

```bash
python lab/validate_cninfo_report_coverage.py
```

关注指标：

- `quarterly_report_q1` / `quarterly_report_q3` coverage 是否上升；
- BSE 是否仍 12 条 empty_response；
- 创业板 300001/300002/300003/300006 是否仍失败（若仍失败，需人工抽查 CNINFO 是否确有 2024Q1/Q3 公告）。

---

## 9. 预期收益（粗估）

| 改动 | 可能挽回行数 | 依据 |
|------|--------------|------|
| 创业板关键词 + title_patterns | 1–7 | 300003 Q1 最可能；300001/002/006 视实际披露标题而定 |
| BSE category + 一季/三季关键词 | 0–12 | 若 CNINFO 确有季报则全可挽回；若规则上未披露则仍为 not_found |
| SZSE/BSE 季报 seDate | 0–若干 | 辅助手段，优先级低于关键词/category |

**保守目标：** 季报 coverage 从 68% 提升到 **≥80%**（对齐 overall partial 阈值上沿）。  
**乐观目标：** BSE 季报若均有披露，overall 可接近 **~93%**（101+12=113/120，未计创业板新增）。

---

## 10. 边界确认

- 本文档为 **离线诊断**，未发 CNINFO 请求、未改 CSV、未写 `verified`。
- 年报/半年报逻辑与结果 **不在本次修改范围**。
- 参数背景见 `cninfo_report_coverage_parameter_diagnostics.md`。
