# CNINFO D 类 equity_pledge First-Slice — Do-Not-Commit List

_生成时间：2026-07-10_

> **性质：** explicit-path 排除清单 · boundary review only · **无 commit**

---

## 1. Live Snapshots（local-only by default）

Bulk JSON audit trail — **不纳入 explicit-path commit** unless separate policy override：

| 路径 | 原因 |
|------|------|
| `outputs/validation/cninfo_d_class_equity_pledge_first_slice/live_snapshots/DEP001_equity_pledge.json` | bulk JSON · local audit |
| `outputs/validation/cninfo_d_class_equity_pledge_first_slice/live_snapshots/DEP002_equity_pledge.json` | 同上 |
| `outputs/validation/cninfo_d_class_equity_pledge_first_slice/live_snapshots/DEP003_equity_pledge.json` | 同上 |
| `outputs/validation/cninfo_d_class_equity_pledge_first_slice/live_snapshots/DEP004_equity_pledge.json` | 同上 |
| `outputs/validation/cninfo_d_class_equity_pledge_first_slice/live_snapshots/DEP005_equity_pledge.json` | 同上 |

**政策：** metadata JSON only · 无 PDF · 保留本地复现；CSV/MD reports 已覆盖 commit 所需摘要。

---

## 2. Mock Test Temp Dirs

| 路径 | 原因 |
|------|------|
| `outputs/validation/cninfo_d_class_equity_pledge_first_slice/_mock_live_tests/` | mock live-path test isolation · 测试后清理 |

---

## 3. Phase1 / Unrelated Fixtures

| 路径 | 原因 |
|------|------|
| `fixtures/d_class/phase1/equity_pledge_fixture.json` | Phase1 fixture · 非 first-slice deliverable（若存在） |
| `outputs/validation/cninfo_d_class_tiny_live_validation/live_snapshots/DLC005_equity_pledge.json` | tiny-live v1 snapshot · 非 first-slice root（若存在） |

---

## 4. Next-Component Planning（非 first-slice explicit path）

| 路径 | 原因 |
|------|------|
| `plans/cninfo_d_class_equity_pledge_next_component_planning.md` | next-component planning · 独立 Era D 任务 |
| `outputs/validation/cninfo_d_class_equity_pledge_next_component_*` | planning artifacts · 非 first-slice commit scope |
| `plans/cninfo_d_class_equity_pledge_first_slice_plan_draft.md` | superseded draft |
| `outputs/validation/cninfo_d_class_equity_pledge_first_slice_universe_draft_sketch.csv` | superseded sketch |

---

## 5. Closed / Unrelated Track Roots（整目录排除）

| 类别 | 路径模式 |
|------|----------|
| known-event replacement | `outputs/validation/cninfo_d_class_known_event_replacement_validation/` |
| known-event targeted probe | `outputs/validation/cninfo_d_class_known_event_targeted_probe/` |
| margin_trading first-slice | `outputs/validation/cninfo_d_class_margin_trading_first_slice/` |
| disclosure_schedule first-slice | `outputs/validation/cninfo_d_class_disclosure_schedule_first_slice/` |
| block_trade first-slice | `outputs/validation/cninfo_d_class_block_trade_first_slice/` |
| restricted_shares_unlock first-slice | `outputs/validation/cninfo_d_class_restricted_shares_unlock_first_slice/` |
| tiny-live v1 | `outputs/validation/cninfo_d_class_tiny_live_validation/` |
| tiny-live v2 | `outputs/validation/cninfo_d_class_tiny_live_validation_v2/` |
| A/B/C validation / harvest | `outputs/validation/cninfo_a_class_*` · `outputs/harvest/cninfo_a_class/` 等 |

---

## 6. Category Blocks（任何路径）

| 类别 | 状态 |
|------|------|
| PDF 文件 | **不包含** |
| DB 文件 / dumps | **不包含** |
| MinIO artifacts | **不包含** |
| RAG artifacts / indexes | **不包含** |
| raw downloaded blobs | **不包含** |
| verified / production_ready / testing_stable_sample flags | **未标记 · 禁止** |
| bare PASS 升级措辞 | **禁止** |

---

## 7. Deferred Work（非 commit 范围）

| 项 | 状态 |
|----|------|
| DEP004 offline retag | **not in commit scope** |
| nonzero-tdate equity_pledge probe | **DEFERRED** |
| `shareholder_change` next-component planning | **after-commit only** · 本 boundary 不启动 |

---

## 8. DEP004 Caveat Visibility

Do-not-commit policy **不得** 用于删除或隐藏：

- `cninfo_d_class_equity_pledge_first_slice_final_caveat_ledger.csv`
- DEP004 rows in live/quality reports
- closure / boundary docs referencing `expectation_mismatch_on_sparse_day`

---

## 9. Gate

```text
d_class_equity_pledge_first_slice_commit_boundary_gate = READY_FOR_COMMIT_REVIEW
```

**本清单不排除 safe-to-commit list 中的 ~33 条 explicit paths。**
