# CNINFO D 类 abnormal_trading — Dense-Day Offline Cite

_生成时间：2026-07-15 · D-FM-29_

> **性质：** AT next-slice denser-day **离线 cite** · **CNINFO = 0** · **无 live** · **无 runner** · **无 universe lock** · **无 commit** · **无 push** · **不是 verified** · **不是 production_ready**
>
> **prefer taken：** AT denser-day offline cite（高于 SD next-slice approval · 高于 FIA further-scale）— D-FM-28 `PENDING_DENSE_DAY_CITE` 门禁

**Prior state：**

| 项 | 状态 |
|----|------|
| D-FM-28 AT/SD scale planning | `READY_FOR_APPROVAL` · sketch DAT101–105 · **committed** |
| AT dense-day status（D-FM-28） | `blocked_until_dense_day_cite` |
| AT first-slice | D-FM-15 live **4/5** · lock **frozen** · anchor `2026-07-03` company-level empty |
| SD first-slice / FIA first+next | **frozen** · **不得 mutate** |
| ESS H3/H4 | **禁止盲探** |
| DLC006R / 301259 / 688671 | **未重开** |

**Cite gate：**

```text
d_class_abnormal_trading_dense_day_cite_gate = READY_FOR_APPROVAL
d_class_abnormal_trading_dense_day_cited_anchor_tdate = 2026-07-02
d_class_abnormal_trading_dense_day_cite_strength = offline_multidate_observed_total_rows
at_dense_day_status = OFFLINE_PROVISIONAL_CITE_2026_07_02
at_next_slice_universe_lock_status = draft_not_locked
live_found_path_for_DAT101_105 = NOT_PROVEN
standing_scope_auth = full_market_shareholder_capital
level2_phrase_required = false
```

**Explicit：** READY_FOR_APPROVAL ≠ verified · cite ≠ lock · offline provisional ≠ live found · **不** Level-2 IDLE · **不** mutate closed roots · **不** H3/H4 · **不** reopen DLC006R

---

## 1. Why Cite Now

| 事件 | 含义 |
|------|------|
| D-FM-28 | DAT101–105 sketch 以 `PENDING_DENSE_DAY_CITE` 占位 · **禁** lock |
| D-FM-15 | `2026-07-03` 对 DAT001–005 company-level **全空** · **禁**作 found 唯一锚 |
| Multidate stability（2026-07-05） | 同端点三交易日均有 **dense** `observed_total_rows` · 可离线排序选日 |

本回合 **仅** 解析 denser-day cite · **不** lock · **不** 实现 next-slice runner · **不** live。

---

## 2. Offline Evidence Corpus（CNINFO=0 · 只读既有产物）

| 证据 | 路径 | 用途 |
|------|------|------|
| Multidate stability CSV | `outputs/validation/cninfo_table_sources_multidate_stability.csv` | AT 三日 `observed_total_rows` |
| Multidate summary | `outputs/validation/cninfo_table_sources_multidate_stability_summary.md` | 摘要与 schema 稳定声明 |
| Priority-1 summary | `outputs/validation/cninfo_table_sources_priority1_summary.md` | 端点 discovery 上下文 |
| D-FM-15 live | `outputs/validation/cninfo_d_class_abnormal_trading_dfm15_bounded_live_20260715.md` | 证明 `2026-07-03` 不适合作 found 唯一锚 |
| D-FM-28 planning | `plans/cninfo_d_class_at_sd_next_slice_scale_planning_20260715.md` | cite 门禁定义 |

**本回合未调用 CNINFO** · 未重跑 multidate 脚本 · 未读取/写入 closed live roots。

---

## 3. Candidate Ranking（marketList · single_day_paged）

| rank | candidate_tdate | observed_total_rows | observed_total_pages | page1_sample_rows | vs forbidden | decision |
|------|-----------------|--------------------:|---------------------:|------------------:|--------------|----------|
| **1** | **2026-07-02** | **173** | 6 | 30 | ≠ `2026-07-03` | **SELECTED** |
| 2 | 2026-07-03 | 151 | 6 | 30 | **forbidden** sole found anchor | rejected |
| 3 | 2026-07-01 | 127 | 5 | 30 | ≠ `2026-07-03` | alternate |

选择规则（离线）：

1. **排除** `2026-07-03` 作为 next-slice found 唯一锚（D-FM-15 / D-FM-28）。
2. 在剩余候选中取 **最高** `observed_total_rows`。
3. 要求 multidate `validation_status=sample_ok` · `records_path=marketList`。

**Selected：** `anchor_tdate = 2026-07-02`

---

## 4. Caveats（必须保留）

| ID | 内容 |
|----|------|
| CAV-AT-DD-001 | Multidate 采样于 **2026-07-05** · 相对今日可能有滚动窗口漂移 · **非** 2026-07-15 实时截面 |
| CAV-AT-DD-002 | `observed_total_rows` 为 **市场截面** · **不**保证 DAT101–105 各 code company-level found |
| CAV-AT-DD-003 | D-FM-15 仅证 `2026-07-03` company-level empty · **未**证 `2026-07-02` live found |
| CAV-AT-DD-004 | Tier-1 found fixtures 仍为合成 · **不** claim live found-path |
| CAV-AT-DD-005 | cite 后仍 **draft_not_locked** · approval package / lock 另批 |

期望策略（沿用 D-FM-28）：DAT101–104 `captured_normal_or_empty_but_valid` · DAT105 `empty_but_valid` · **禁** sole `captured_normal_or_needs_review`。

---

## 5. Sketch Update

| 项 | 值 |
|----|-----|
| cases | DAT101–DAT105 |
| anchor_tdate | **2026-07-02**（原 `PENDING_DENSE_DAY_CITE`） |
| shared_probe_prefer | **1** |
| universe_lock_status | **draft_not_locked** |
| first-slice lock | **未 mutate** |

---

## 6. Excludes / Frozen

| 类别 | 项 |
|------|-----|
| AT first-slice | universe lock · live_report · live_snapshots · DAT001–005 |
| SD first-slice | universe lock · live_report · live_snapshots · DSD001–005 |
| FIA | first-slice + next-slice live roots / locks |
| Codes | **688671** · **301259** · DLC006R |
| ESS | **不** H3/H4 |
| Forbidden | PDF/DB/MinIO/RAG · verified · production_ready · bare PASS · commit/push · A/B/C · Level-2 IDLE · next-slice live |

---

## 7. Red Lines

No CNINFO · No live · No runner · No first-slice mutate · No FIA mutate · No ESS H3/H4 · No DLC006R · No A/B/C · No Level-2 IDLE · No commit · No push · No verified · No sole found-anchor reuse of `2026-07-03`
