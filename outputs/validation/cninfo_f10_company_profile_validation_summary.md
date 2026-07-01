# CNINFO 个股 F10 / 公司资料小样本验证（Issue #84）

## 数据来源
- 输入样本：outputs/validation/cninfo_p0_sample_companies.csv
- CNINFO 公开接口：/new/information/topSearch/detailOfQuery（HTTP POST）

## 样本概况
- 样本公司数：40
- success：0
- partial：0
- failed：40

## 字段可得性（按行计数）
- stock_short_name：0/40
- exchange：40/40（来自样本输入/构造，不代表 F10 接口返回）
- board：40/40（来自样本输入/构造，不代表 F10 接口返回）
- industry：0/40
- listing_status：0/40
- is_st：40/40（来自样本输入/构造，不代表 F10 接口返回）
- company_profile：0/40
- main_business_summary：0/40
- registered_address：0/40
- office_address：0/40
- website：0/40
- contact_phone：0/40
- contact_email：0/40
- board_secretary：0/40
- source_url：40/40（构造的查询 URL）

## 字段分层总结
- company：company_code / company_name / stock_short_name / exchange / board / listing_status
- company_profile 候选：industry / company_profile / main_business_summary
- 联系方式：registered_address / office_address / website / contact_phone / contact_email（需后续语义与时效性复核）
- 治理辅助：board_secretary（可选，需语义与时效性确认）
- 证据：source_url / crawl_time

## 失败原因汇总
- http_error: 39
- network_timeout: 1

## 北交所 / 代码映射观察
- 使用 430xxx -> 920xxx 映射成功的公司数：0
- 映射仅为小样本保守策略，不代表长期通用；如仍失败需人工复核。

## recommended_status（小样本）
- 建议：candidate（需改进可达性/映射后再测）。

## 初次验证结论与后续排查
- 本轮 F10 / 公司资料 HTTP 尝试未成功获取资料字段，整体视为 candidate / failed attempt。
- 需人工检查 source_url 在浏览器能否打开，确认 /new/information/topSearch/detailOfQuery 是否为正确接口。
- 若页面可访问但接口持续 500，下一步可考虑页面解析或 Playwright 备用（不使用 BrowserUser）。
- 后续可尝试 company_name / stock_short_name 查询，或引入 orgId / cninfo_query_code 映射，而非仅用 company_code。

## 合规与边界确认
- 未绕过登录/验证码/付费/权限。
- 未使用 BrowserUser；如需 Playwright 仅作为后续备用。
- 未解析 PDF 正文，未做 OCR，未做字段抽取。
- 未上传 MinIO，未做 PostgreSQL / MongoDB 接入。
- 请求间加入 sleep，避免高频访问。
- 结果可能受网络/VPN/映射影响，需人工环境确认后视情况重跑。
