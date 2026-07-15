# B-FM-41 Live Metrics — incentive_object_list_known_001 / sales_brief_known_001

| 项 | 值 |
|----|-----|
| result | **LIVE_PASS** |
| pass / fail / ambiguous | **2** / 0 / 0 |
| CNINFO（成功 live） | **4**（2×(topSearch+query)；PDF=0） |
| CNINFO（本任务合计） | **14**（首轮 PARTIAL 4 + 消歧诊断 6 + 成功 live 4） |
| wall（成功 live） | **~6.9 s** |
| allow-list | `incentive_object_list_known_001`, `sales_brief_known_001` |
| PDF | **0** |

## 备注

- 首轮激励对象名单同窗命中名单正文 + 委员会核查意见 → ambiguous；title_pattern 收窄为
  「股份有限公司2025年限制性股票激励计划激励对象名单（授予日）」后 2/2 LIVE_PASS。
- 路由仍用窄串「激励对象名单」/「销售简报」；勿裸「名单」/「简报」。
- remaining other ~2 → **0**（本 harvest 抽样闭合）。
- 未重开 B-FM-40 及更早 LIVE_PASS。
