# B-FM-42 Live Metrics — bond_trustee_report_known_002 / tracking_rating_report_known_002

| 项 | 值 |
|----|-----|
| task_id | B-FM-42 |
| result | **LIVE_PASS** |
| pass / fail / ambiguous | **2** / 0 / 0 |
| CNINFO（成功 live） | **4**（2×(topSearch+query)；PDF=0） |
| CNINFO（本任务合计） | **4** |
| wall（成功 live） | **~6.8 s** |
| allow-list | `bond_trustee_report_known_002`, `tracking_rating_report_known_002` |
| ready（全量） | **68**（+2；invalid_ready=0） |
| routing 变更 | **无**（复用 B-FM-29） |

## 能力增益

- 公司债券受托管理事务报告（非可转债）进入 known-document ready 并经公司窗 live metadata 确认
- 主体年度跟踪评级报告（非可转债定期跟踪）进入 known-document ready 并经 live 确认
- bond_trustee / tracking_rating 族由 known_001-only → known_001+002

## 边界

- NOT verified · NOT production_ready
- 未重开 known_001 LIVE_PASS
- remaining other harvest 仍为 ~0
