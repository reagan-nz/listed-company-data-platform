# CNINFO F10 / 公司资料页面可达性验证（Issue #84 第二轮）

## 数据来源
- 输入：outputs/validation/cninfo_f10_entry_mapping.csv
- 访问：CNINFO stock profile 页面 URL（/new/disclosure/stock?...#companyProfile）

## 样本概况
- entry mapping 总数：40
- 成功：23
- partial：7
- failed：10

## 按规则类型统计
- manual_rule_600_300_gssh0: total 17, success 10, partial 7, failed 0
- needs_orgid_mapping: total 10, success 0, partial 0, failed 10
- manual_star_orgid_mapping: total 7, success 7, partial 0, failed 0
- manual_bse_430_to_920_orgid_mapping: total 6, success 6, partial 0, failed 0

## 可达性结果
- HTTP 200：30/40
- 404：0
- 500：0
- timeout：0
- 需要 JS 渲染（无关键词且无公司名）：7
- 含公司资料关键词：23
- 含公司名称：0
- 缺 orgId/映射待补充：10

## 北交所 / 代码映射观察
- 430/920 映射仅对 430017→920017 有样例，其余 430 需补 orgId 后再测；本轮未泛化。

## 当前结论
- 若页面 200 且含关键词，可进入后续轻量 HTML 抽取验证；若 200 但无内容，考虑 JS 渲染（Playwright 备用）。
- 若大量 500/超时，需继续修正 orgId / stockCode 映射或检查网络环境。

## recommended_status（小样本）
- 建议：testing / partial（小样本继续验证），不代表长期稳定可用。

## 合规与边界确认
- 未绕过登录/验证码/付费/权限。
- 未使用 BrowserUser；未做数据库/MinIO 接入。
- 未做字段抽取，仅做可达性与轻量关键词检查。
- 请求间加入 sleep，避免高频访问。
