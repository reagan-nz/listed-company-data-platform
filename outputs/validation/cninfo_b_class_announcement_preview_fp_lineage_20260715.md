# CNINFO B 类 Run 11 — announcement_preview FP Lineage Gap Closure

_生成时间：2026-07-15 · offline only · **CNINFO = 0** · **无 live** · **无 commit** · **无 push**_

> **性质：** disclosure/event taxonomy edge + evidence lineage · **NOT verified** · **NOT production_ready**  
> **不重复** Run 9 routing-benchmark 扩面（q3 / ambiguous / general_004–006）

---

## 1. Gap Found

| 项 | 说明 |
|----|------|
| gap_id | `GAP-B-PREVIEW-FP-LINEAGE` |
| 现象 | Phase 1 quality audit 主假阳性类 `announcement_preview`（披露提示性公告 / 提示性公告 / 预告公告）已能从 periodic 排除并落入 general，但 `false_positive_reason` **恒为空**；benchmark **0** 条覆盖 |
| 影响 | disclosure/event 边缘分类 lineage 断裂 — live/retrieval 复用 `route_title` 时无法对齐 validation_design §7 / Phase 1 审计口径 |
| 为何非 busywork | Phase 1 季报 fail 主因即披露提示性公告；规则与枚举已存在，缺的是 **可执行 lineage + 锁测** |
| 已排除重复 | Run 9（`85489c5`）覆盖 q3/ambiguous/回购/业绩预告/监事会 — **不含** preview FP |
| 已排除禁区 | 不重开 BD2E624 · 不碰 scale-200/slice1 production roots · 不写 controller 政策 |

### 1.1 搜索证据（checked）

| 检查项 | 结果 |
|--------|------|
| `fixtures/b_class/**` 含「提示性公告\|预告公告\|announcement_preview\|更正公告」 | **0** matches（修复前） |
| Run 9 commit `85489c5` | 仅 +5 fixtures（q3/ambiguous/general） |
| `PROJECT_CONTROL` B blocked_actions | 记「no open scope」自 Run 9 — 本包发现 **新** open gap |
| delayed/summary Priority-4 路径 | 已有 fp；preview 仅在 periodic `exclusion_patterns`，落入 Priority-5 时 fp 被写成空或仅「摘要」 |
| BD2E624 / empty_response taxonomy / mission_event_prep_gap | 已完成包 — 不重复 |

---

## 2. Fix（最小）

1. `config/cninfo_announcement_categories.yaml` — 新增 `excluded_from_periodic_routing.announcement_preview`
2. `lab/validate_cninfo_b_class_category_routing.py` — `_excluded_false_positive_reason()`；Priority-4/5 正确写出 `announcement_preview`；可选 `expected_false_positive_reason` 参与 `overall_pass`
3. `fixtures/b_class/known_documents/known_document_benchmark.yaml` — +5 false_positive_guard（preview×4 + 更正公告×1）
4. `lab/test_cninfo_b_class_category_routing_preview_fp.py` — 9 项单测

---

## 3. Validation Results

| 检查 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_category_routing_preview_fp.py` | **9 OK** |
| `python lab/validate_cninfo_b_class_category_routing.py` | **26/26 PASS** · fail=0 |
| `announcement_preview` fp 行数（report CSV） | **4**（005–008） |
| CNINFO calls | **0** |
| live | **none** |

路由汇总已刷新：

- [cninfo_b_class_category_routing_summary.md](cninfo_b_class_category_routing_summary.md)
- [cninfo_b_class_category_routing_report.csv](cninfo_b_class_category_routing_report.csv)

---

## 4. Capability Gain

- disclosure/event corpus 可将 Phase 1 主假阳性类 **稳定标注** 为 `false_positive_reason=announcement_preview`（非空、非误标为 delayed/summary）
- benchmark **21 → 26**；false_positive_guard **4 → 9**
- 更正公告对称锁定：不得路由为 periodic 全文
- **不**声称 B complete / verified / full-market %

---

## 5. Gate & Labels

```text
b_class_announcement_preview_fp_lineage_gate = PASS_OFFLINE
cninfo_calls_this_package = 0
live_calls_this_package = 0
bd2e624_touched = no
scale200_slice1_roots_mutated = no
commit = not_requested
push = not_requested
```

**NOT verified** · **NOT production_ready** · **B NOT complete**

---

## 6. Next Recommended B Task

1. **可选（离线）：** 将 `announcement_preview` 行同步进 non_periodic document fixtures / seed 脚本，使 schema fixture 与 routing benchmark 同源。  
2. **可选（离线）：** 对 `wrong_company`（「关于披露他司报告的提示性公告」交叉披露）加一条 lineage 基准 — 与 preview 相邻但语义不同。  
3. **勿做：** 重复 Run 9 式 general 扩面；重开 BD2E624 live；扩 scale-200/slice1 production roots。  
4. Mission 级 full-market % 仍 **UNKNOWN**（分母未冻）— 非本包范围。
