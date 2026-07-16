# B-FM-02 Live Metrics — tracking_rating known_006–010 / bond_trustee known_005–007

| 项 | 值 |
|----|-----|
| task_id | B-FM-02（R19） |
| result | **LIVE_PASS** |
| pass / fail / ambiguous | **8** / 0 / 0 |
| CNINFO（成功 live） | **16**（8×(topSearch+query)；PDF=0） |
| CNINFO（本任务合计） | **16** |
| allow-list | `tracking_rating_report_known_006`–`010`, `bond_trustee_report_known_005`–`007` |

选择依据：

- deferred known_002 四族 offline harvest 仍无清晰第二案 → 走 fallback 余量
- 扩展跟踪评级 known_006–010（华阳国际 / 广联航空 / 立讯精密 / 天合光能 / 航新科技）与债券受托 known_005–007（南方航空 A 股可转债 / 铜陵有色特定对象 / 美锦能源语序变体）
- equity_change known_002 仍薄；audit_report_known_002 仍拒年报陷阱

不重开：

B-FM-01 及更早 LIVE_PASS（含 tracking/bond known_001–005/004、supervisory/supervision known_005）
