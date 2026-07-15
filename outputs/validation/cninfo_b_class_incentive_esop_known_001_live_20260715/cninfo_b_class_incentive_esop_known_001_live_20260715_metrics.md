# B-FM-35 Live Metrics — incentive_trading_self_inspection_known_001 / employee_stock_ownership_plan_known_001

| 项 | 值 |
|----|-----|
| task_id | B-FM-35 |
| result | **LIVE_PASS** |
| pass / fail / ambiguous | **2** / 0 / 0 |
| CNINFO（成功 live） | **4**（2×(topSearch+query)；PDF=0） |
| CNINFO（本任务合计） | **12**（含 2 次 ESOP title_pattern 消歧重试） |
| wall（成功 live） | **~27.4 s** |
| PDF | **0** |

要点：

- harvest 锚点 BD2E087（北新建材 000786 / ann=1224017800）、BD2E062（东方盛虹 000301 / ann=1224016542）。
- 无 orgId fallback；成功轮无 ambiguous。
- ESOP 案首两轮因窗内多条「员工持股计划」ambiguous，收窄 title_pattern 至「第二期员工持股计划（草案）(修订稿）」后 LIVE_PASS。
- 窄 pattern：勿裸「自查报告」；routing 仍用「员工持股计划」闭合 other。
