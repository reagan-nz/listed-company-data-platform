# CNINFO F10 / 公司资料静态 HTML 字段验证（Issue #84）

## 数据来源
- 输入：outputs/validation/cninfo_f10_profile_page_reachability.csv（仅 validation_status=success 的记录，数量：23）
- 访问：CNINFO stock profile 页面 URL（/new/disclosure/stock?...#companyProfile）

## 样本概况
- 输入 success 页面数：23
- 实际验证数：23
- success：0
- partial：0
- failed：23

## 字段可得性（按行计数）
- stock_short_name：0/23
- industry：0/23
- listing_status：0/23
- company_profile：0/23
- main_business_summary：0/23
- registered_address：0/23
- office_address：0/23
- website：0/23
- contact_phone：0/23
- contact_email：0/23
- board_secretary：0/23

## 字段抽取观察
- js_render_required：0
- 若核心字段缺失或仅有少量字段，则结果标记为 partial 或 failed。
- 字段语义不清或无静态字段时，不做强行填充。

## recommended_status（小样本）
- 建议：candidate（静态 HTML 信息不足，后续需 Playwright/映射补充）。

## 边界确认
- 未使用 BrowserUser；仅 HTTP + 轻量解析。
- 未做数据库/MinIO 接入；未保存完整 HTML；未解析 PDF/OCR。
- 请求需节流；结果受网络/VPN/映射影响，必要时人工重跑。
