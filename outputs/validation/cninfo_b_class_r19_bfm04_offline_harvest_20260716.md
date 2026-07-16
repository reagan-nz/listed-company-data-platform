# CNINFO B 类 B-FM-04（R19）— Discovery Harvest 决策记录（~200 scale）

> **executor:** b-class-executor · **track:** B · **task_id:** B-FM-04  
> **性质：** discovery harvest（市场关键词窗）+ ~200 residual 晋升准备 · **NOT verified**

---

## 1. Scale policy

B-FM-03 ~50 LIVE_PASS excellent → 本包 **~200**。非 excellent 则停留/硬化于 200，不通胀 1000。

## 2. Harvest source

既有 erad CSV residual 近耗尽；本包 **bounded CNINFO discovery**（空 stock + family keyword + 日期窗）。  
证据：`_bfm04_candidate_pool.json` / `_bfm04_discovery_meta.json`。

## 3. Reject / closed

- `audit_report_known_002` 拒绝
- deferred known_002 薄族推迟
- 已 LIVE_PASS 集不重开

## 4. 本包组成（200）

| family | n |
|--------|---|
| legal_opinion | 43 |
| bond_trustee_report | 30 |
| shareholder_meeting | 29 |
| board_resolution | 25 |
| tracking_rating_report | 20 |
| supervisory_board | 15 |
| raised_funds_cash_management | 15 |
| continuous_supervision_annual | 8 |
| verification_opinion | 6 |
| company_articles | 5 |
| employee_stock_ownership_plan | 4 |

## 5. Gate

```text
b_class_r19_bfm04_offline_harvest_gate = PASS_OFFLINE
cohort_size = 200
discovery_cninfo_calls_total = 110
```
