# CNINFO D 类 executive_shareholding Next-Slice — Closure Review

_生成时间：2026-07-16 02:04:12 UTC_

> **性质：** 离线 post-live closure review only · task **D-FM-02** · **无 CNINFO** · **无 live** · **无 rerun** · **不是 verified** · **无 commit 执行**

**关联 gate：** `d_class_executive_shareholding_next_slice_execution_gate = PASS_WITH_CAVEAT`

---

## 1. Objective

对 D-FM-01 executive_shareholding next-slice bounded live（DES101–105 · shared CNINFO=1）结果进行正式离线收口评审，确认 denser-window 语义、登记 density caveat、产出 closure metrics / effective result / freeze attestation，并为 commit boundary 提供 Controller 输入。

**本评审不：** 重跑 DES101–105 · 重开 DLC006R / ESS H3/H4 · 将 empty 升级为 found · 标记 verified / production_ready · 执行 commit / push / git add。

---

## 2. Live Result Recap（只读 · D-FM-01）

| 项 | 值 |
|----|-----|
| mode | `--executive-shareholding-next-slice --live` |
| standing auth | R19 standing D · bounded live |
| universe | DES101–105（**5**）· lock sha256 `4213de37…b6d2fd1` |
| output root | `outputs/validation/cninfo_d_class_executive_shareholding_next_slice/` |
| component | **executive_shareholding** only |
| endpoint | `https://www.cninfo.com.cn/data20/leader/detail` |
| query | **timeMark=threeMonth** + **varyType=b**（shared） |
| total CNINFO（prior live） | **1** |
| PDF/OCR/extraction | **0** |
| DB/MinIO/RAG | **0** |

| case_id | company | retrieval | records | acceptable |
|---------|---------|-----------|---------|------------|
| DES101 | 002415 | found | 2 | yes |
| DES102 | 000895 | empty_but_valid | 0 | yes |
| DES103 | 600000 | empty_but_valid | 0 | yes |
| DES104 | 000550 | empty_but_valid | 0 | yes |
| DES105 | 601988 | empty_but_valid | 0 | yes |

**汇总：** acceptable **5/5** · found **1** · empty_but_valid **4** · failed **0**

---

## 3. Denser-Window Semantics

Query **`timeMark=threeMonth`** + **`varyType=b`** shared probe，公司级 SECCODE 过滤后：

| 项 | 结论 |
|----|------|
| DES101 found | **yes** — 2 structured rows |
| DES102–105 empty | **legal** under expectation / empty control |
| density cite = full-company found | **no** — caveat retained |
| endpoint failure | **no** |

---

## 4. Density Caveat（诚实登记）

| 项 | 内容 |
|----|------|
| caveat_type | `density_cite_not_full_company_found` |
| disposition | **retain** · not blocking |
| forbidden | claim DES101–105 all found；upgrade empty to found |

---

## 5. Scope Confirmation

| 约束 | 状态 |
|------|------|
| component = executive_shareholding only | **yes** |
| metadata / structured-table scoped | **yes** |
| first-slice / peer capital roots frozen | **yes**（attestation MATCH） |
| DLC006R / ESS H3/H4 | **未重开** |
| A/B/C | **未触碰** |

---

## 6. Gate

```text
d_class_executive_shareholding_next_slice_closure_gate = PASS_WITH_CAVEAT
```

**NOT verified** · **NOT production_ready** · **NOT bare PASS**
