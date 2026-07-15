# CNINFO D 类 executive_shareholding_summary — Endpoint Hypothesis Ledger (D-FM-22 update)

_生成时间：2026-07-15 · D-FM-22_

> **性质：** 高管持股变动汇总 tab endpoint 假说台账 · **含 D-FM-22 有界探针结果** · **不是 verified**

**Sibling（confirmed · closed track · 高管持股明细）：** `POST https://www.cninfo.com.cn/data20/leader/detail` · **不 reopen**

---

## Hypotheses

| hyp_id | method | url | params_guess | confidence | status | probe_cninfo | notes |
|--------|--------|-----|--------------|------------|--------|--------------|-------|
| H1 | POST | `https://www.cninfo.com.cn/data20/leader/summary` | `timeMark=oneMonth`/`varyType=b` | low_medium → **falsified** | **rejected_404** | 1 | D-FM-22：`{"msg":"页面不存在","path":"/leader/summary","code":"404"}` |
| H2 | POST | `https://www.cninfo.com.cn/data20/leader/statistics` | 同上 | low → **falsified** | **rejected_404** | 1 | D-FM-22：`{"msg":"页面不存在","path":"/leader/statistics","code":"404"}` |
| H3 | POST | `https://www.cninfo.com.cn/data20/leader/total` | 同上 | low | **unprobed** | 0 | 预算已用尽（CNINFO=2）；**不**猜测性再探 |
| H4 | POST | `https://www.cninfo.com.cn/data20/leader/detail` | 未知汇总专用参 | low | **forbidden_reopen** | 0 | ES detail closed · **不**本任务 reopen |

---

## Probe Rules（执行记录）

1. 一次只探一个 URL；H1 失败再 H2 — **已执行**。
2. 总 CNINFO **≤ 2** — **实际 = 2**。
3. 禁止把 404/空壳伪装成 success — **遵守**（gate=`FAIL_REVIEW_REQUIRED`）。
4. 禁止写入 FIA / ES / AT / SD 既有 live 根 — **遵守**。
5. 成功后另批 registry draft — **未触发**（未成功）。

---

## Explicit

```text
endpoint_status = unconfirmed_probe_failed
h1_status = rejected_404
h2_status = rejected_404
h3_status = unprobed_budget_exhausted
h4_status = forbidden_reopen
cninfo_calls = 2
probe_executed = true
probe_gate = FAIL_REVIEW_REQUIRED
```
