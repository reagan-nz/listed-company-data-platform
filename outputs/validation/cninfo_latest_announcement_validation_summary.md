# CNINFO 最新公告列表小样本验证（Issue #82）

## 数据来源
- 输入样本：outputs/validation/cninfo_p0_sample_companies.csv
- CNINFO 公开接口：/new/hisAnnouncement/query（HTTP POST）

## 样本概况
- 样本公司数：40
- 成功公司数：34
- partial 公司数：0
- 失败公司数：6

## 字段可得性（按行计数）
- announcement_title：102/108
- publish_time：102/108
- source_url：102/108
- pdf_url：102/108
- announcement_type：102/108

## 失败原因汇总
- no_announcements_returned: 6

## 小样本人工复核 / 代码映射发现
- 关闭 VPN 后重新运行结果未改善，仍有 6 条 `no_announcements_returned`。
- 6 条均为北交所 430 开头旧代码：430017/430047/430090/430139/430198/430300。
- 脚本已增加 430xxx -> 920xxx 的保守映射并尝试查询，但本次 920xxx 仍返回空。
- 这些结果不代表公司没有公告，可能仍有代码映射或数据口径问题，需后续人工复核或补充 cninfo_query_code 映射。
- 后续如需继续验证，建议人工在可访问 CNINFO 的环境下再次运行，并进一步排查北交所代码映射。

## recommended_status（小样本）
- 建议：testing / partial（小样本层面可继续验证），不代表长期稳定可用。

## 合规与边界确认
- 未绕过登录/验证码/付费/权限。
- 未下载 PDF 正文，未计算 hash。
- 未做 PostgreSQL / MongoDB / MinIO 接入。
- 请求间插入 sleep，未进行高频访问。
- 使用 mapped BSE code 成功的公司数：0
- 430xxx -> 920xxx 映射仅用于小样本验证，可能未覆盖所有北交所代码；如仍失败需人工复核映射或公司状态。
