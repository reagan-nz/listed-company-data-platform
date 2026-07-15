# CNINFO D 类 executive_shareholding_summary — Endpoint Hypothesis Ledger

_生成时间：2026-07-15 · D-FM-21_

> **性质：** 高管持股变动汇总 tab 离线 endpoint 假说台账 · **CNINFO = 0** · **无 HTTP** · **不是 verified**

**Sibling（confirmed · closed track · 高管持股明细）：** `POST https://www.cninfo.com.cn/data20/leader/detail`

---

## Hypotheses

| hyp_id | method | url | params_guess | confidence | status | probe_cninfo | notes |
|--------|--------|-----|--------------|------------|--------|--------------|-------|
| H1 | POST | `https://www.cninfo.com.cn/data20/leader/summary` | `timeMark`/`varyType` 或无参 | low_medium | **unprobed** | 0 | 与 detail 命名对称；首选探针 |
| H2 | POST | `https://www.cninfo.com.cn/data20/leader/statistics` | 同上 | low | **unprobed** | 0 | 汇总语义备选 |
| H3 | POST | `https://www.cninfo.com.cn/data20/leader/total` | 同上 | low | **unprobed** | 0 | 合计语义备选 |
| H4 | POST | `https://www.cninfo.com.cn/data20/leader/detail` | 未知汇总专用参 | low | **unprobed** | 0 | 若无独立 API；须 DevTools 证伪；**不** reopen ES first-slice live |

---

## Probe Rules（未来任务 · 非本任务）

1. 一次只探 **一个** URL；失败再换 H2。
2. 总 CNINFO **≤ 2**（硬顶 **≤ 3**）。
3. 禁止把 404/空壳伪装成 success。
4. 禁止写入 FIA / ES / AT / SD 既有 live 根。
5. 成功后另批：registry draft · sample_raw · field semantics · **仍不** verified。

---

## Explicit

```text
endpoint_status = unconfirmed
cninfo_calls = 0
probe_executed = false
```
