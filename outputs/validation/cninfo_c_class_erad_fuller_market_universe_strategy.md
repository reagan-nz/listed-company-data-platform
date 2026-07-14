# CNINFO C 类 Era D — Fuller-Market Universe Strategy

_生成时间：2026-07-10 · offline planning only · CNINFO = 0_

---

## 1. Cumulative Target

| 阶段 | 规模 | cohort | 与 863 关系 |
|------|------|--------|-------------|
| Era C 863（已完成） | **863** | `harvest_863_non_bse` | 主线锚点 · **read-only** |
| **Era D slice 1（本规划）** | **+200** | `fuller_market_slice1` | **CE1E001–CE1E200** · 零 overlap |
| Future slice 2（占位） | +500 | `fuller_market_slice2` | 1063→1563 · planning only |
| Fuller non-BSE | ~4200+ | `full_market_a_share_non_bse` | 6124 − 863 − hold − BSE − 清洗 |

**累计 lineage 目标（slice1 后）：1063 家公司代码（863 已覆盖 + 200 新）**

---

## 2. Overlap Rules

### 2.1 Include（slice1）

| 规则 | 说明 |
|------|------|
| 公司代码唯一 | 与 `harvest_863_non_bse` **零 overlap** |
| 非 BSE | 排除 `board_bse`（与 863 主线一致） |
| 非 hold | 排除 `eval_companies_c_class_889_rerun_all6_hold.yaml`（26） |
| 非 ST/退市 | 名称含 ST/*ST/退 排除 |
| 市场分层 | SSE / SZSE / ChiNext / STAR 分层（draft：**58/48/52/42**） |
| 源池 | `eval_companies_full_market_2024.yaml` 离线派生 |

### 2.2 Overlap Matrix

| 对照集 | 政策 | prior_in_863 |
|--------|------|--------------|
| 863 primary harvest | **exclude rerun** · lineage-reference | `yes` if hit → **reject** |
| 26 all6 hold | **exclude** | n/a |
| Phase 2 smoke 200 | **exclude**（新片） | check YAML |
| Phase 3 batch 500 | **exclude**（新片） | check YAML |
| Phase 3.5 resume 491 | **exclude**（新片） | check YAML |
| B-class Era D 200/300 | **无写入冲突** · 只读参照 | B 轨 metadata · C 轨 harvest |
| A/D live 根 | **禁止 mutation** | n/a |

**draft slice1：** 全部 `prior_in_863=no`（200/200）

### 2.3 Phase3 / Phase35 关系

| 子树 | 路径 | 与 slice1 |
|------|------|-----------|
| phase3_batch_500_001 | 隔离 batch · 491 overlap 域 | slice1 公司 **不在** phase3 YAML |
| phase35_batch_500_001_resume | resume 补洞 | 独立 · 不覆盖 slice1 |
| 863 primary | `outputs/harvest/cninfo_c_class/` | **禁止 mutation** |

新 slice 建议隔离根：`outputs/harvest/cninfo_c_class/fuller_market_slice1_200/`

---

## 3. BSE / Holdout / Abnormal

### 3.1 BSE

| 轨 | 政策 |
|----|------|
| 863 主线 | **explicitly non-BSE** |
| BSE 920 active | **future side-track** · 见 `cninfo_c_class_bse_expansion_strategy.md` |
| BSE 83/87 legacy | **hold** · `legacy_code_incompatible` |

Slice1 **不含** BSE。

### 3.2 Holdout

| 项 | 政策 |
|----|------|
| Era C holdout 9 | **closed-with-caveat** · **no promotion** |
| 26 all6 hold | 永久 exclude 于 active expansion |
| slice1 新失败 | 入 slice1 unresolved ledger · 不 rollback 863 |

### 3.3 Abnormal

| 类型 | 政策 |
|------|------|
| ST / 退市 | 规划阶段排除 |
| abnormal_review explicit | 参照 registry conflict triage |
| source_count_mismatch | accept_with_caveat · 不阻塞 slice |

---

## 4. A/B Fuller-Market Sync

| 线 | 当前方向 | C 对齐方式 |
|----|----------|------------|
| **B** | BD2E201–500 · +300 metadata | 共享 `full_market_2024` 源池口径 · **独立 case_id**（CE1E* vs BD2E*） |
| **A** | scale-200 isolated retry | C slice 不写入 A 根 · 公司代码交叉引用只读 |
| **D** | block_trade first-slice | 无 harvest 冲突 · universe 独立 |

**Sync 原则：**

1. 公司代码级 manifest 定期交叉（offline CSV join）· **CNINFO=0**
2. 任一线 live 批准 **不自动** 批准他线
3. Registry Layer 2 实现前 · 各线保留独立 YAML + validation ledger

---

## 5. Draft Universe Reference

- [slice1 universe draft](cninfo_c_class_erad_fuller_market_slice1_universe_draft.csv) · **200 rows** · CE1E001–CE1E200
- 源：`eval_companies_full_market_2024.yaml` − 863 − hold − BSE − ST/退

---

## 6. Red Lines

No CNINFO · no live · no 863 mutation · no snapshot rebuild · Era D not finished
