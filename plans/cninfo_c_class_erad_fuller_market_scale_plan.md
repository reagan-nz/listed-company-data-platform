# CNINFO C 类 Era D — Fuller-Market Scale Plan

_生成时间：2026-07-10_

> **offline planning only** · **CNINFO = 0** · **NOT APPROVED live** · **Option A HOLD rebuild**

**关联：** [full market universe design](../outputs/validation/cninfo_c_class_full_market_universe_design.md) · [50 closure summary](../outputs/validation/cninfo_c_class_erad_needs_review_50_closure_summary.md) · [B-class next-scale strategy](../outputs/validation/cninfo_b_class_erad_next_scale_universe_strategy.md)

---

## 1. 当前基线

| 项 | 值 |
|----|-----|
| 863_primary harvest | **813** complete · **50** needs_review（closure 已收口 · **0** live_needed） |
| Snapshot | 863 full JSON · 491 phase35 expanded · **Option A HOLD** |
| Universe 锚点 | `harvest_863_non_bse`（889 − 26 hold） |
| Fuller 目标池 | `eval_companies_full_market_2024.yaml` · **6124**（Era B 基准） |
| 净扩展粗估 | **~4200+** non-BSE 未入 863（离线派生 · 待 registry 去重） |

---

## 2. 路径选项（排序）

### Option A — Staged fuller-market expansion（**推荐 · Primary**）

从 863 non-BSE 锚点向 Era B 6124 active 层 **分批 +200/+500** 扩展。

| 优点 | 说明 |
|------|------|
| 复用成熟 tooling | `harvest_cninfo_c_class.py` · `--resume` · isolated `--output-root` |
| 与 A/B 节奏对齐 | B-class Era D 已走 200→+300；C 可 200→500→fuller |
| 风险可控 | 每 slice 独立 harvest 子树 · 不盲跑 6124 |
| 863 不突变 | 新 slice 零 overlap · 生产 863 根只读 |

| 缺点 | 缓解 |
|------|------|
| registry 6124 与 F10 偏差 | slice1 live 前 dry-run + smoke |
| 磁盘增长 | local retention policy · gitignore |

### Option B — Deepen quality on 863 first, then expand

先清零 50 needs_review（status align · caveat 文档化），再扩展。

| 优点 | ledger 更干净 |
|------|---------------|
| 缺点 | **50/50 已 non-blocking** · 延迟扩展收益低 · C-line 不应 pause |

**判定：** 作为 **并行小修**（000037/000055 status align）可接受 · **不作主路径**。

### Option C — Portrait backfill wave（10→50→200）并行

在现有 863 本地 harvest 上补 portrait / 衍生字段。

| 优点 | 不增 CNINFO harvest 面 |
|------|------------------------|
| 缺点 | 不直接扩大 market coverage · 与 Era D fuller-market 主目标次优 |

**判定：** **并行 follow-up**（10–20 家 smoke）· 不替代 Option A slice1。

---

## 3. 推荐主路径

**Option A — Staged fuller-market expansion**

| 决策 | 内容 |
|------|------|
| Next execution slice | **Slice 1 · +200**（CE1E001–CE1E200） |
| 累计目标（slice1 后） | **1063** 公司代码（863 + 200 new） |
| Overlap | 与 863 / 26 hold / phase3·phase35 batch **零 overlap** |
| Rebuild 政策 | **no-blind-full-rerun** · 863 snapshot **HOLD** · 新 slice 隔离子树 |
| Live 政策 | **NOT APPROVED** · 须 `c_class_erad_fuller_market_planning_gate` 人批后另开 live gate |

---

## 4. 执行切片（规划 · 未启动）

| 阶段 | 规模 | case_id | 状态 |
|------|------|---------|------|
| Era C 863 | 863 | harvest_863 | **完成** |
| **Era D slice 1** | **+200** | **CE1E001–CE1E200** | **draft universe** |
| Era D slice 2（占位） | +500 | CE2E001+ | planning only |
| Era D slice 3+ | 至 non-BSE fuller | — | 依赖 registry refresh |

---

## 5. 红线

| 约束 | 政策 |
|------|------|
| CNINFO | 本规划 **0** |
| Live harvest | **NOT APPROVED** |
| Snapshot rebuild | **Option A HOLD** |
| 863 生产根 | **read-only** |
| A/B/D mutation | **禁止** |
| Holdout promotion | **禁止** |
| Era D finished | **不得宣称** |

---

## 6. Gate（本规划包）

```
c_class_erad_fuller_market_planning_gate = READY_FOR_APPROVAL
```

人批后下一 gate：`c_class_erad_fuller_market_slice1_dryrun_gate`（offline runner prep · 仍 CNINFO=0）
