# CNINFO D 类 executive_shareholding_summary — Discovery Recommendation

_生成时间：2026-07-15 · post FIA D-FM-20 first-slice closure · D-FM-21_

> **planning gate：** `d_class_executive_shareholding_summary_discovery_planning_gate = READY_FOR_APPROVAL`
>
> **standing_scope：** full-market shareholder / capital · **Level-2 phrase NOT required**
>
> **Explicit：** NOT verified · NOT production_ready · CNINFO = 0 · 无 runner · 无 live · 无 commit · 无 push · endpoint **unconfirmed**

---

## Primary Recommendation

**Component:** `executive_shareholding_summary`（高管持股变动汇总 tab · **未注册** discovery）

**One-line rationale:** FIA first-slice 已 offline closure（D-FM-20 · `PASS_WITH_CAVEAT`）后，Era D 下一自然资本动作是拆分 ES 页面汇总 tab；明细 `executive_shareholding` / `leader/detail` 已 closed 且不得重开；汇总 tab 仅有 UI 表头证据、无 Network endpoint 捕获，故本回合交付 **offline discovery planning**（endpoint hypotheses + UI field sketch + next probe gate），**不** live。

---

## Runner-Up

**Action:** FIA scale / next-slice offline planning

**Rationale:** first-slice 已收口；scale 有价值但低于未注册组件 discovery；另批执行 · **不** mutate D-FM-13/18 live roots。

---

## Rank Table

| Rank | Component / Action | Risk | Notes |
|------|--------------------|------|-------|
| **1** | **executive_shareholding_summary discovery** | medium | endpoint unconfirmed · CNINFO=0 this round |
| 2 | FIA scale / next-slice offline | low | deferred |
| — | AT / SD scale hardening | medium–high | excluded · no re-live |
| — | executive_shareholding / closed tracks / DLC006R | — | frozen · 不重开 |

---

## Standing Scope Auth

本 discovery 处于 D standing scope（full-market shareholder / capital）。**不** IDLE 等待单独 Level-2 短语。未来 **bounded endpoint probe** 仍须独立任务批准（prefer CNINFO ≤ 2）。

---

## Proposed Next Probe Parameters（NOT this task）

| 项 | 值 |
|----|-----|
| probe size | **1–2** URL candidates（H1 then H2） |
| method | POST · empty body · query params 试探 `timeMark`/`varyType` 或无参 |
| CNINFO cap | **≤ 2**（hard **≤ 3**） |
| success | HTTP 200 + `data.records` 结构可解析 + 字段可对照 UI |
| failure | 404/500/非 JSON → 记证伪 · 不伪成功 |
| after pass | registry draft candidate + sample_raw · **另批** |

**本任务不执行 probe。**

---

## Next Task

Standing-scope continue → **bounded endpoint probe**（CNINFO ≤ 2）· **或** FIA scale offline planning（独立任务）· **或** controller commit-boundary for D-FM-21 discovery 包

---

## Red Lines

No CNINFO · No live · No runner · No closed-track expansion · No FIA live-root mutate · No PDF/DB/MinIO/RAG/verified · No commit · No push · No DLC006R reopen · No Level-2 IDLE
