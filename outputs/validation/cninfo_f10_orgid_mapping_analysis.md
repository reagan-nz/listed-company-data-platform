# CNINFO F10 / 公司资料 orgId 映射分析（Issue #84）

## 1. 背景

CNINFO 个股 F10 / 公司资料页面**不能**直接通过 `company_code` 访问，而依赖 **stockCode + orgId** 组合构造 URL。Issue #84 多轮验证表明：

- 旧接口 `/new/information/topSearch/detailOfQuery` 在小样本上全部失败（HTTP 500 / timeout），**不适合**作为 F10 / 公司资料的主入口。
- 人工发现的新入口形式为 `/new/disclosure/stock?stockCode=...&orgId=...#companyProfile`；在部分板块上，配合经验规则可构造有效 URL。
- 旧接口失败**不代表** F10 数据源整体不可用，而是说明：**入口形态与 orgId 映射需要单独处理**，不能假设 `company_code` 与 CNINFO 内部标识一一对应。

当前 P0 小样本（40 家）中，约 30 家已通过经验规则或人工映射得到 `cninfo_profile_url`；其余约 10 家仍标记为 `needs_orgid_mapping`（主要为 000 开头深交所主板），是 #84 后续验证的主要阻塞之一。

688 科创板原经验规则（`gshk0000`+后三位）经 Playwright 验证**全部 failed**，已改为 7 家人工 orgId 映射（`manual_star_orgid_mapping`）。

## 2. 当前已发现的入口格式

```
https://www.cninfo.com.cn/new/disclosure/stock?stockCode=<stockCode>&orgId=<orgId>#companyProfile
```

字段含义：

| 参数 | 说明 |
|---|---|
| `stockCode` | CNINFO 页面使用的股票代码（可能与样本中的 `company_code` 不同，如北交所 430→920） |
| `orgId` | CNINFO 内部公司 ID，**不能随意伪造**；错误 orgId 可能导致页面跳转异常或无法定位公司资料 |
| `#companyProfile` | 公司资料锚点，指向「公司概况 / 公司资料」区块 |

要点：**仅有 stockCode 不足以构造可靠 URL**，必须同时获得正确的 orgId。

## 3. 已验证的经验规则

| 类型 | 示例 | stockCode 规则 | orgId 规则 | 当前判断 |
|---|---|---|---|---|
| 上交所主板 600 | 600000（浦发银行） | stockCode = 原代码（600000） | orgId = `gssh0` + 原代码（gssh0600000） | 小样本经验规则，暂可用于验证 |
| 深交所创业板 300 | 300750（宁德时代，规则类推） | stockCode = 原代码（300750） | orgId = `gssh0` + 原代码（gssh0300750） | 小样本经验规则，暂可用于验证 |
| 科创板 688 | 688001（华兴源创） | stockCode = 原代码（688001） | ~~`gshk0000`+后三位~~ **已推翻**；需人工 orgId（99000... / gfbj...） | **不可简单构造**；7 家 P0 样本已人工映射 |
| 北交所 430（旧代码） | 430017 → 920017 / 9900003482 | 430xxx 需映射为 920xxx（后缀替换） | **无简单公式**，需人工搜索或页面解析 | 不能只靠 430 代码直接构造 companyProfile；须单独获取 orgId |

说明：

- 600 / 300 共用 `gssh0` + 全码前缀，在小样本 reachability / Playwright 验证中表现稳定。
- **688 原 `gshk0000`+后三位规则已被 Playwright 小样本全部 failed 推翻**；orgId 形态多样（`9900038969`、`gfbj0833231` 等），须逐家获取。
- 000 开头深交所主板代码**尚未**总结出 orgId 构造规则（见第 5 节）。

## 4. BSE 手工映射样本

以下 6 家北交所样本已通过人工搜索 CNINFO 页面获得 stockCode / orgId，写入 `BSE_MANUAL_MAPPING`；重新跑 reachability 后 **6/6 success**。

| 原 company_code | 公司名 | cninfo_stock_code | cninfo_org_id | mapping_status | 备注 |
|---|---|---|---|---|---|
| 430017 | 星昊医药 | 920017 | 9900003482 | mapped | 人工搜索页面结果，仅适用于当前小样本 |
| 430047 | 诺思兰德 | 920047 | 9900006121 | mapped | 人工搜索页面结果，仅适用于当前小样本 |
| 430090 | 同辉信息 | 920090 | 9900020567 | mapped | 人工搜索页面结果，仅适用于当前小样本 |
| 430139 | 华岭股份 | 920139 | 9900024205 | mapped | 人工搜索页面结果，仅适用于当前小样本 |
| 430198 | 微创光电 | 920198 | 9900024889 | mapped | 人工搜索页面结果，仅适用于当前小样本 |
| 430300 | 辰光医疗 | 920300 | 9900023934 | mapped | 人工搜索页面结果，仅适用于当前小样本 |

对应 URL 示例（430017）：

```
https://www.cninfo.com.cn/new/disclosure/stock?stockCode=920017&orgId=9900003482#companyProfile
```

`profile_url_rule = manual_bse_430_to_920_orgid_mapping`。

## 4.1 STAR（688）手工映射样本

Playwright 验证显示，按 `gshk0000`+后三位构造的 688 URL 在小样本上**全部 failed**。以下 7 家已通过人工搜索获得 orgId，写入 `STAR_MANUAL_MAPPING`（`profile_url_rule = manual_star_orgid_mapping`）。

| 原 company_code | 公司名 | cninfo_stock_code | cninfo_org_id | mapping_status | 备注 |
|---|---|---|---|---|---|
| 688001 | 华兴源创 | 688001 | 9900038969 | mapped | 人工搜索页面结果，仅适用于当前小样本 |
| 688002 | 睿创微纳 | 688002 | 9900038939 | mapped | 人工搜索页面结果，仅适用于当前小样本 |
| 688003 | 天准科技 | 688003 | gfbj0833231 | mapped | 人工搜索页面结果，仅适用于当前小样本 |
| 688004 | 博汇科技 | 688004 | gfbj0871038 | mapped | 人工搜索页面结果，仅适用于当前小样本 |
| 688005 | 容百科技 | 688005 | 9900038937 | mapped | 人工搜索页面结果，仅适用于当前小样本 |
| 688006 | 杭可科技 | 688006 | 9900037551 | mapped | 人工搜索页面结果，仅适用于当前小样本 |
| 688007 | 光峰科技 | 688007 | 9900038970 | mapped | 人工搜索页面结果，仅适用于当前小样本 |

观察：

- **688 stockCode 仍使用原代码**（与 company_code 相同）。
- **orgId 不可简单构造**；可能是 `99000...` 或 `gfbj...` 等形式，**没有统一公式**。
- `manual_star_orgid_mapping` **只适用于当前 P0 小样本**，不代表所有科创板公司。
- 688 开头但不在字典中：标记 `star_orgid_required`，不伪造 orgId。
- 映射更新后需**重新运行** reachability / static HTML / Playwright 验证。

对应 URL 示例（688001）：

```
https://www.cninfo.com.cn/new/disclosure/stock?stockCode=688001&orgId=9900038969#companyProfile
```

## 5. 当前未解决的问题

### 5.1 needs_orgid_mapping 样本（10 家）

当前 P0 小样本中，以下深交所主板公司仍无 orgId / profile URL（`profile_url_rule = needs_orgid_mapping`）：

| company_code | 公司名 |
|---|---|
| 000001 | 平安银行 |
| 000002 | 万科A |
| 000004 | 国华退 |
| 000006 | 深振业A |
| 000007 | 全新好 |
| 000008 | 神州高铁 |
| 000009 | 中国宝安 |
| 000010 | *ST美丽 |
| 000011 | 深物业A |
| 000012 | 南玻A |

### 5.2 核心阻塞

- **orgId 没有从当前样本中总结出可靠公式**；000 开头深交所代码的 orgId 前缀规律尚不明确。
- **688 原 `gshk0000`+后三位规则已被推翻**；7 家人工映射后仍需重跑验证，且不能泛化到其他 688 公司。
- **北交所 430→920 stockCode 映射**在 6 家样本中成立，但**不能自动泛化**到全部北交所公司；orgId 均为独立数值，无可见算术规律。
- 后续需要从以下来源获取 orgId：
  - CNINFO 站内搜索结果页
  - 公告 / 披露列表页跳转链接中的 `orgId` 参数
  - 其他公开接口或页面解析（需单独验证，不绕过登录 / 验证码）
- **不应**把当前人工样本规则直接写入长期生产逻辑；生产接入前应完成更大样本的映射验证与自动化方案设计。

## 6. 对后续验证的影响

| 状态 | 样本范围 | 可进行的验证 |
|---|---|---|
| mapped（600/300 经验规则） | 约 17 家 | reachability ✓、static HTML ✓、Playwright 字段验证 ✓ |
| mapped（STAR 688 人工映射 7 家） | 7 家 | **需重跑** reachability / static HTML / Playwright（旧 gshk 规则 URL 已失效） |
| mapped（BSE 人工映射 6 家） | 6 家 | reachability ✓（6/6 success）；可纳入 static HTML / Playwright |
| needs_orgid_mapping | 10 家（000xxx） | **应暂时排除**在 Playwright 字段验证之外；不伪造 orgId |

Issue #84 的主要剩余阻塞已从「页面是否可达 / 字段是否由 JS 渲染」**转向**「orgId 映射自动化」：

- 对已 mapped 样本：Playwright 验证表明 JS 渲染后可提取 company_profile、main_business_summary、registered_address 等字段；静态 HTML 不足。
- 对未 mapped 样本：在获得 orgId 之前，无法构造有效 `#companyProfile` URL，不应强行纳入字段验证流水线。

若后续接入数据库，建议单独设计并持久化：

- `cninfo_stock_code`（CNINFO 页面使用的 stockCode，可能与 company_code 不同）
- `cninfo_org_id`（CNINFO 内部 orgId）
- `cninfo_profile_url`（完整 companyProfile 入口 URL）
- `profile_url_rule` / `mapping_status`（映射来源与置信度，便于区分经验规则 vs 人工映射）

## 7. 边界说明

- 本文档**只总结当前 P0 小样本经验**，基于 Issue #84 已有验证产物（entry mapping、reachability、static HTML、Playwright 等）整理。
- **不代表**长期稳定规则；`recommended_status` 仍应维持 `candidate` / `testing`，不写 `verified`。
- 撰写本文档时：**未访问 CNINFO**；**未运行新验证脚本**；**未修改**任何验证结果 CSV / summary。
- **未修改** `docs/data_sources.md`；**未修改** `plans/storage_schema_design_plan.md`。
- **未做**数据库 / MinIO 接入；**未使用** BrowserUser。
