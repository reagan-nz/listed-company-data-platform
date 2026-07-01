# CNINFO F10 / 公司资料 Playwright 验证（Issue #84）

## 数据来源
- A：`outputs/validation/cninfo_f10_static_html_field_validation.csv`
- B：`outputs/validation/cninfo_f10_profile_page_reachability.csv`

## 样本选择
- static_html_no_fields 候选：23
- reachability_partial 候选：7
- 去重后实际验证：30
- 未纳入 Playwright（mapping/orgId/空 URL 等）：0
- 明确未纳入：reachability failed、needs_orgid_mapping、bse_orgid_required、缺 orgId、profile_url 为空

## 验证结果
- 实际验证数：30
- success：22
- partial：1
- failed：7

## sample_source 分布
- static_html_no_fields：23 家（success 22 / partial 1 / failed 0）
- reachability_partial：7 家（success 0 / partial 0 / failed 7）

## profile_url_rule 分布
- manual_rule_600_300_gssh0：17 家（success 10 / partial 0 / failed 7）
- manual_bse_430_to_920_orgid_mapping：6 家（success 6 / partial 0 / failed 0）
- manual_star_orgid_mapping：7 家（success 6 / partial 1 / failed 0）

## 字段可得性（按行计数）
- stock_short_name：0/30
- industry：22/30
- listing_status：0/30
- company_profile：23/30
- main_business_summary：22/30
- registered_address：22/30
- office_address：22/30
- website：0/30
- contact_phone：22/30
- contact_email：22/30
- board_secretary：22/30

## 当前结论
- 静态 HTML 已不足以提取字段；本步用于判断 JS 渲染后是否可见。
- 若仍无字段，需继续修正 entry mapping 或页面结构。

## recommended_status（小样本）
- 建议：testing / partial（Playwright 后可提取部分字段），不代表长期稳定可用。

## 边界确认
- 未使用 BrowserUser。
- 未绕过登录 / 验证码 / 权限。
- 未做数据库 / MinIO 接入；未保存完整 HTML 快照。
