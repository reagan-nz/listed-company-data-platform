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
- 已人工补充 6 个 BSE 430→920/orgId 映射（430017、430047、430090、430139、430198、430300），见 `BSE_MANUAL_MAPPING` / `cninfo_f10_entry_mapping.csv`
- 430→920 stockCode 在这 6 个样本上成立；orgId 无简单公式，当前来自人工公司名称搜索
- 该映射仅适用于当前小样本，不代表所有北交所公司
- 重新跑 reachability 后 BSE 6 家全部 success
- 映射仅为小样本保守策略，不代表长期通用

## 科创板 / orgId 映射观察
- **原规则失败**：688 使用 `gshk0000`+后三位构造 orgId，Playwright 验证 7 家样本全部 failed
- **已新增 7 个 STAR 人工 orgId 映射**（688001–688007），见 `STAR_MANUAL_MAPPING` / `manual_star_orgid_mapping`
- 688 stockCode 仍用原代码；orgId 可能是 99000... 或 gfbj...，无统一公式
- 该映射仅适用于当前 P0 小样本，不代表长期稳定规则
- **下一步**：重新运行 reachability / static HTML / Playwright 验证（使用新 orgId）

## recommended_status（小样本）
- 建议：candidate（需改进可达性/映射后再测）。

## 初次验证结论与后续排查
- 本轮 F10 / 公司资料 HTTP 尝试未成功获取资料字段，整体视为 candidate / failed attempt。
- 旧接口 /new/information/topSearch/detailOfQuery 返回 500/timeout，不应视为有效 F10 入口。
- 人工发现新的入口：/new/disclosure/stock?stockCode=...&orgId=...#companyProfile（600/300 用 gssh0+code）。
- 688：`gshk0000`+后三位规则已推翻；已人工补充 7 家 orgId 映射。
- 北交所：已人工补充 6 个 430/920/orgId 映射（`manual_bse_430_to_920_orgid_mapping`）。
- **下一步**：重新运行 `validate_cninfo_f10_profile_page_reachability.py`、`validate_cninfo_f10_static_html_fields.py`、`validate_cninfo_f10_playwright_profile_fields.py`（688 新映射 + 已有 BSE/600/300）。
- entry mapping 见 cninfo_f10_entry_mapping.csv / cninfo_f10_entry_discovery_notes.md / cninfo_f10_orgid_mapping_analysis.md。

## 合规与边界确认
- 未绕过登录/验证码/付费/权限。
- 未使用 BrowserUser；如需 Playwright 仅作为后续备用。
- 未解析 PDF 正文，未做 OCR，未做字段抽取。
- 未上传 MinIO，未做 PostgreSQL / MongoDB 接入。
- 请求间加入 sleep，避免高频访问。
- 结果可能受网络/VPN/映射影响，需人工环境确认后视情况重跑。
