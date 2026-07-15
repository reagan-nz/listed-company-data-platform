# B-FM-24 Live Metrics — supervisory_board_known_002

_生成时间：2026-07-15_

| 项 | 值 |
|----|-----|
| task_id | B-FM-24 |
| result | **LIVE_PASS** |
| allow-list | `supervisory_board_known_002` |
| CNINFO | **4**（试跑 ambiguous：topSearch=1+query=1；收紧后 LIVE_PASS：topSearch=1+query=1；PDF=0） |
| wall（成功跑） | **~12.7 s** |
| query_executed（成功跑） | **1** |
| pass / fail / ambiguous（成功跑） | **1 / 0 / 0** |

| case_id | kind | matched title | date | classification | result |
|---------|------|---------------|------|----------------|--------|
| `supervisory_board_known_002` | known | 农心作物科技股份有限公司第二届监事会第二十二次会议决议的公告 | 2025-06-26 | classified_correctly / announcement | **pass** |

## 观察

- 首跑 pattern=`会议决议的公告` → 同窗 **ambiguous×3**（PARTIAL）；收紧为 `第二十二次会议决议的公告` 后 LIVE_PASS。
- 成功跑无网络失败；无 orgId fallback；**未**修改共享 validator。
- 未重开 supervisory_board_known_001 / shareholder_meeting_known_001–007 / board_resolution_known_001。
- harvest 锚点 BD2E244（农心科技 001231 / ann=1223998915）。
