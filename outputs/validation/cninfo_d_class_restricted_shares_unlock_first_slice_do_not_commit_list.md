# CNINFO D 类 restricted_shares_unlock First-Slice — Do-Not-Commit List

_生成时间：2026-07-10_

> **性质：** explicit-path 排除清单 · boundary review only · **无 commit**

---

## 1. Live Snapshots（local-only by default）

Bulk JSON audit trail — **不纳入 explicit-path commit** unless separate policy override：

| 路径 | 原因 |
|------|------|
| `outputs/validation/cninfo_d_class_restricted_shares_unlock_first_slice/live_snapshots/DRU001_restricted_shares_unlock.json` | bulk JSON · local audit |
| `outputs/validation/cninfo_d_class_restricted_shares_unlock_first_slice/live_snapshots/DRU002_restricted_shares_unlock.json` | 同上 |
| `outputs/validation/cninfo_d_class_restricted_shares_unlock_first_slice/live_snapshots/DRU003_restricted_shares_unlock.json` | 同上 |
| `outputs/validation/cninfo_d_class_restricted_shares_unlock_first_slice/live_snapshots/DRU004_restricted_shares_unlock.json` | 同上 |
| `outputs/validation/cninfo_d_class_restricted_shares_unlock_first_slice/live_snapshots/DRU005_restricted_shares_unlock.json` | 同上 |

**政策：** metadata JSON only · 无 PDF · 保留本地复现；CSV/MD reports 已覆盖 commit 所需摘要。

---

## 2. Phase1 / Unrelated Fixtures

| 路径 | 原因 |
|------|------|
| `fixtures/d_class/phase1/restricted_shares_unlock_fixture.json` | Phase1 fixture · 非 first-slice deliverable（若存在） |
| `outputs/validation/cninfo_d_class_tiny_live_validation/live_snapshots/DLC003_restricted_shares_unlock.json` | tiny-live v1 snapshot · 非 first-slice root（若存在） |

---

## 3. Closed / Unrelated Track Roots（整目录排除）

| 类别 | 路径模式 |
|------|----------|
| known-event replacement | `outputs/validation/cninfo_d_class_known_event_replacement_validation/` |
| known-event targeted probe | `outputs/validation/cninfo_d_class_known_event_targeted_probe/` |
| block_trade first-slice | `outputs/validation/cninfo_d_class_block_trade_first_slice/` |
| margin_trading first-slice | `outputs/validation/cninfo_d_class_margin_trading_first_slice/` |
| disclosure_schedule first-slice | `outputs/validation/cninfo_d_class_disclosure_schedule_first_slice/` |
| tiny-live v1 | `outputs/validation/cninfo_d_class_tiny_live_validation/` |
| tiny-live v2 | `outputs/validation/cninfo_d_class_tiny_live_validation_v2/` |
| A-class validation / harvest | `outputs/validation/cninfo_a_class_*` · `outputs/harvest/cninfo_a_class/` |
| B-class validation / harvest | `outputs/validation/cninfo_b_class_*` · `outputs/harvest/cninfo_b_class/` |
| C-class validation / harvest | `outputs/validation/cninfo_c_class_*` · `outputs/harvest/cninfo_c_class/` |

---

## 4. Category Blocks（任何路径）

| 类别 | 状态 |
|------|------|
| PDF 文件 | **不包含** |
| DB 文件 / dumps | **不包含** |
| MinIO artifacts | **不包含** |
| RAG artifacts / indexes | **不包含** |
| raw downloaded blobs | **不包含** |
| `_mock_live_tests/` temp dirs | **不包含** |
| verified / production_ready / testing_stable_sample flags | **未标记 · 禁止** |
| bare PASS 升级措辞 | **禁止** |
| empty_but_valid→found 升级 | **禁止** |

---

## 5. Deferred Work（非 commit 范围）

| 项 | 状态 |
|----|------|
| denser-day / nonzero-tdate RSU probe | **DEFERRED** |
| `equity_pledge` planning | **next-after-commit only** · 本 boundary 不启动 |
| block_trade verified claim | **禁止** |

---

## 6. Sparse-Day Caveat Visibility

Do-not-commit policy **不得** 用于删除或隐藏：

- `cninfo_d_class_restricted_shares_unlock_first_slice_final_caveat_ledger.csv`
- sparse-day rows in live/quality reports
- closure / boundary docs referencing `empty_but_valid ×5` on `tdate=2026-06-08`

---

## 7. Superseded / Pre-Live Docs（可选排除）

| 路径 | 原因 |
|------|------|
| `plans/cninfo_d_class_restricted_shares_unlock_first_slice_plan_draft.md` | superseded sketch · formal plan 已取代 |
| `outputs/validation/cninfo_d_class_restricted_shares_unlock_first_slice_next_step_recommendation.md` | pre-live next-step · 已由 post-closure doc 取代 |

---

## 8. Gate

```text
d_class_restricted_shares_unlock_first_slice_commit_boundary_gate = READY_FOR_COMMIT_REVIEW
approval_status_for_commit = NOT_APPROVED
```

**本清单不排除 safe-to-commit list 中的 ~32 条 explicit paths。**
