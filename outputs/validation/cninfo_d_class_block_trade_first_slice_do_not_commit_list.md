# CNINFO D 类 block_trade First-Slice — Do-Not-Commit List

_生成时间：2026-07-10_

> **性质：** explicit-path 排除清单 · boundary review only · **无 commit**

---

## 1. Live Snapshots（local-only by default）

Bulk JSON audit trail — **不纳入 explicit-path commit** unless separate policy override：

| 路径 | 原因 |
|------|------|
| `outputs/validation/cninfo_d_class_block_trade_first_slice/live_snapshots/DBT001_block_trade.json` | bulk JSON · local audit |
| `outputs/validation/cninfo_d_class_block_trade_first_slice/live_snapshots/DBT002_block_trade.json` | 同上 |
| `outputs/validation/cninfo_d_class_block_trade_first_slice/live_snapshots/DBT003_block_trade.json` | 同上 |
| `outputs/validation/cninfo_d_class_block_trade_first_slice/live_snapshots/DBT004_block_trade.json` | 同上 |
| `outputs/validation/cninfo_d_class_block_trade_first_slice/live_snapshots/DBT005_block_trade.json` | 同上 |

**政策：** metadata JSON only · 无 PDF · 保留本地复现；CSV/MD reports 已覆盖 commit 所需摘要。

---

## 2. Phase1 / Unrelated Fixtures

| 路径 | 原因 |
|------|------|
| `fixtures/d_class/phase1/block_trade_fixture.json` | Phase1 fixture · 非 first-slice deliverable |
| `outputs/validation/cninfo_d_class_tiny_live_validation/live_snapshots/DLC002_block_trade.json` | tiny-live v1 snapshot · 非 first-slice root |

---

## 3. Closed / Unrelated Track Roots（整目录排除）

| 类别 | 路径模式 |
|------|----------|
| known-event replacement | `outputs/validation/cninfo_d_class_known_event_replacement_validation/` |
| known-event targeted probe | `outputs/validation/cninfo_d_class_known_event_targeted_probe/` |
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

---

## 5. Deferred Work（非 commit 范围）

| 项 | 状态 |
|----|------|
| DBT002 offline retag | **not in commit scope** |
| nonzero-tdate block_trade probe | **DEFERRED** |
| `restricted_shares_unlock` planning | **next-after-commit only** · 本 boundary 不启动 |

---

## 6. DBT002 Caveat Visibility

Do-not-commit policy **不得** 用于删除或隐藏：

- `cninfo_d_class_block_trade_first_slice_unresolved_case_ledger.csv`
- DBT002 rows in live/quality reports
- closure / boundary docs referencing `expectation_mismatch_on_sparse_day`

---

## 7. Gate

```text
d_class_block_trade_first_slice_commit_boundary_gate = READY_FOR_COMMIT_REVIEW
```

**本清单不排除 safe-to-commit list 中的 ~27 条 explicit paths。**
