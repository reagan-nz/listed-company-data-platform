# CNINFO C 类 Era D Snapshot Rebuild — Next-Step Recommendation

_生成时间：2026-07-10_

---

## Primary Recommendation（本包唯一首选）

### **Option A — HOLD rebuild**

**Snapshot already sufficient for Era D MVP; do not rebuild 491 or 863 production snapshot roots.**

| 依据 | 详情 |
|------|------|
| 491 track | **491/491** local JSON · QA **`PASS_WITH_CAVEAT`** · remote closed on `origin/main` |
| 863 track | **863/863** full snapshot · `complete_with_caveat=863` |
| Harvest audit | 863_primary **0 partial · 0 missing** · live resume **HOLD** |
| needs_review 58 | Ledger/status 不一致 · **非** harvest 缺口 · rebuild 无净收益 |
| Holdout 9 | **closed-with-caveat** · **no promotion** |
| Approval | **`approved_for_snapshot_rebuild = false`** |

**人批动作（建议）：** 勾选 [readiness checklist](cninfo_c_class_erad_snapshot_rebuild_readiness_checklist.md) 中 Option A HOLD 项 · 保持 **NOT APPROVED rebuild**。

---

## Deferred Options

### Option B — offline rebuild readiness dry-run script design

**Status:** **DEFERRED** until human approves `c_class_erad_snapshot_rebuild_readiness_planning_gate`.

- 未来实现：mock-root dry-run only（`outputs/snapshot/cninfo_c_class/_mock_erad_rebuild_*` 或 validation 子树）  
- 复用 `build_cninfo_c_class_snapshot_batch.py --dry-run` + cleanup guard  
- **本包不实现 · 不执行**

### Option C — defer until 58 needs_review human triage

**Status:** **DEFERRED**（与 Slice-C-EraD-02b 绑定）

- 仅当 triage 发现明确 live harvest 缺口后，才重新评估 partial cohort rebuild  
- **当前无证据支持**

---

## Explicitly NOT Recommended

| 动作 | 原因 |
|------|------|
| Rebuild 491 production root | 已存在 · closed-with-caveat · 无增量价值 |
| Rebuild 863 production root | 已存在 · 58 needs_review 非 blocking |
| Live harvest / resume | **HOLD** per Slice-C-EraD-02 |
| Holdout promotion | **forbidden** |

---

## Next C-Class Task After This Planning Package

**Human sign-off on Option A HOLD** → then **Era D C-line pause / handoff** or **optional Slice-C-EraD-03b** (mock-root rebuild dry-run **design+impl only** if team wants executable readiness path before any future execute).

**Parallel safe work（不踩红线）：**

- Portrait ontology P4 field_id 回填（只读）  
- 58 needs_review offline triage ledger（**无 live**）  
- Documentation / branch hygiene on `c-class-erad-resume`

**Do NOT start:** production snapshot rebuild · live harvest · holdout promotion.

---

## Gate

```
c_class_erad_snapshot_rebuild_readiness_planning_gate = READY_FOR_APPROVAL
```

---

## Red Lines

No CNINFO · no rebuild · no live · no commit/push · production roots read-only
