# CNINFO B 类 B-FM-03（R19）— Offline Harvest 决策记录（~50 scale）

> **executor:** b-class-executor · **track:** B · **task_id:** B-FM-03  
> **性质：** offline harvest 扫描 + ~50 residual 路径选择 · **CNINFO=0** · **NOT verified**

---

## 1. Scale policy

R19：先验 B-FM-01（3）/ B-FM-02（8）已 LIVE_PASS → 本包升至 **~50** 单根 allow-list。  
不拆多包微残量。

## 2. Deferred / reject

| family | 结论 |
|--------|------|
| deferred known_002 四族 | **薄** — 推迟 |
| `audit_report_known_002` | **拒绝** — 年报陷阱 |
| 已 LIVE_PASS tracking/bond known_001–010/007 等 | **勿重开** |

## 3. 本包组成（50）

| family | n |
|--------|---|
| bond_trustee_report | 10（含 spotlight 精测/润禾/奥飞/金田 + 公司债余量） |
| tracking_rating_report | 2（中天精装/润达医疗「跟踪评级结果的公告」） |
| legal_opinion | 16 |
| shareholder_meeting | 12 |
| board_resolution | 5 |
| raised_funds_cash_management | 4 |
| continuous_supervision_annual | 1 |

路由：既有硬化；**本包不改路由**。

## 4. Gate（本阶段）

```text
b_class_r19_bfm03_offline_harvest_gate = PASS_OFFLINE
cohort_size = 50
cninfo_calls = 0
```
