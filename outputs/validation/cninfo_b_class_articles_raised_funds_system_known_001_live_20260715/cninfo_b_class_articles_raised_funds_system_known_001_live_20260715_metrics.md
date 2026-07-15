# B-FM-36 Live Metrics — company_articles_known_001 / raised_funds_management_system_known_001

| 项 | 值 |
|----|-----|
| task_id | B-FM-36 |
| result | **LIVE_PASS** |
| pass / fail / ambiguous | **2** / 0 / 0 |
| CNINFO（成功 live） | **4**（2×(topSearch+query)；PDF=0） |
| CNINFO（本任务合计） | **4**（首轮即过，无重试） |
| wall | **~17.8 s** |
| PDF downloads | **0** |

备注：

- harvest 锚点 BD2E262（古麒绒材 001390 / ann=1223886833）、BD2E756（绿城水务 601368 / ann=1223973494）。
- 路由窄 pattern：「公司章程」「募集资金管理制度」；勿裸「章程」/「管理制度」/「制度」。
- 同 harden 另覆盖 harvest BD2E189 / BD2E330 公司章程标题（未单列 known）。
- 未 mutate 既有 LIVE_PASS live 根；未 PDF。
