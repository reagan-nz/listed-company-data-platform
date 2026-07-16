# B-FM-03 Live Metrics — residual scale50（base）

| 项 | 值 |
|----|-----|
| task_id | B-FM-03（R19） |
| result（本根） | **PARTIAL** |
| pass / fail / ambiguous | **48** / **2** / 0 |
| CNINFO（本根） | **~100**（50×(topSearch+query)；PDF=0） |
| fail cases | `legal_opinion_known_019`, `legal_opinion_known_021` |
| fail 根因 | 律所全称 searchkey 在 CNINFO 返回 0 条；公司锚定缩短后可命中 |
| 后续 | 见 `cninfo_b_class_residual_scale50_retry_v1_live_20260716/` |

选择依据：

- R19 ladder：B-FM-01/02 已 LIVE_PASS → 本包升至 **~50** 单根 allow-list
- deferred known_002 四族仍薄；`audit_report_known_002` 仍拒年报陷阱
- 组成：bond_trustee 10 / tracking_rating 2 / legal_opinion 16 / shareholder_meeting 12 / board_resolution 5 / raised_funds_cash_management 4 / continuous_supervision_annual 1

不重开：

B-FM-01/02 及更早 LIVE_PASS（含 tracking/bond known_001–010/007 等）
