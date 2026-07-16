# B-FM-01 Live Metrics — tracking_rating known_004/005 / bond_trustee known_004

| 项 | 值 |
|----|-----|
| task_id | B-FM-01（R19） |
| gate | **LIVE_PASS** |
| pass / fail / ambiguous | **3** / 0 / 0 |
| CNINFO（成功 live） | **6**（3×(topSearch+query)；PDF=0） |
| wall | **~22 s** |
| allow-list | `tracking_rating_report_known_004`, `tracking_rating_report_known_005`, `bond_trustee_report_known_004` |

## 本包目标

- deferred known_002 四族 offline harvest 仍无清晰第二案 → 走 fallback 余量
- 扩展跟踪评级 known_004（相关债券）/ known_005（主体及转债）与债券受托 known_004（可续期）
- equity_change known_002 仍薄；audit_report_known_002 仍拒年报陷阱

## 不重开

B-FM-54 及更早 LIVE_PASS（含 supervisory/supervision known_005、tracking/bond known_001–003）
