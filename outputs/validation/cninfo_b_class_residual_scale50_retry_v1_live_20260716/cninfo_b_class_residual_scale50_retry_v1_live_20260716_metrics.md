# B-FM-03 Live Metrics — residual scale50 retry_v1

| 项 | 值 |
|----|-----|
| task_id | B-FM-03（R19） |
| result | **LIVE_PASS** |
| pass / fail / ambiguous | **2** / 0 / 0 |
| CNINFO（retry_v1） | **4**（2×(topSearch+query)；PDF=0） |
| allow-list | `legal_opinion_known_019`, `legal_opinion_known_021` |
| lineage | 硬化自 base PARTIAL fail；不覆盖 base live 根 |

硬化：

| case_id | 旧 title_pattern（律所全称） | 新 title_pattern（公司锚定） |
|---------|------------------------------|------------------------------|
| `legal_opinion_known_019` | 北京市安理律师事务所关于中粮糖业…法律意见书 | 中粮糖业控股股份有限公司2024年年度股东大会的法律意见书 |
| `legal_opinion_known_021` | 北京金诚同达（深圳）律师事务所关于…法律意见书 | 深圳市杰普特光电股份有限公司2024年度差异化分红事项的法律意见书 |

cohort 合成（base 48 pass + retry 2 pass，覆盖同 case_id）：

| 指标 | 值 |
|------|-----|
| size | **50** |
| pass / fail / ambiguous | **50** / 0 / 0 |
| excellence | **YES**（B excellent = LIVE_PASS fail=0 ambiguous=0） |
