# CNINFO 公告 PDF 元数据小样本验证（Issue #83）

## 数据来源
- 输入：outputs/validation/cninfo_latest_announcement_validation.csv（Issue #82 成功公告记录）
- PDF URL 来源：Issue #82 最新公告验证结果中的 pdf_url

## 样本概况
- 候选 PDF 记录数：100
- 实际验证 PDF 数：100
- success：100
- partial：0
- failed：0

## 字段可得性（按行计数）
- pdf_url：100/100
- http_status_code=200：100/100
- content_hash：100/100
- file_size：100/100
- mime_type：100/100
- download_time：100/100
- has_text_layer：填充为 unknown（本次未解析正文）

## 失败原因汇总
- success: 100

## 文件大小概况
- 统计口径：仅基于 download_status=success 且 file_size>0 的记录
- min=59906, max=1689957, avg=232330

## hash 规则
- content_hash 使用 sha256；计算对象是 PDF 原始二进制内容，不基于 URL/标题/文本。
- 本次仅做元数据验证，不做 MinIO object_key 设计。

## recommended_status（小样本）
- 建议：testing / partial（小样本可继续验证），不代表长期稳定可用。

## 合规与边界确认
- 未绕过登录/验证码/付费/权限。
- 未解析 PDF 正文，未做 OCR，未做字段抽取。
- 未上传 MinIO，未做 PostgreSQL / MongoDB 接入。
- 请求间加入 sleep，避免高频访问。
- 结果受网络/VPN/映射影响，需人工环境确认后视情况重跑。
