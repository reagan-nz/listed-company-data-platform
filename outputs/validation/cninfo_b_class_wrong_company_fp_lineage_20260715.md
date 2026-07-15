# CNINFO B 类 Run 12 — wrong_company FP Lineage Gap Closure

_生成时间：2026-07-15 · offline only · **CNINFO = 0** · **无 live** · **无 commit** · **无 push**_

> **性质：** disclosure/event taxonomy edge + evidence lineage · **NOT verified** · **NOT production_ready**  
> **不重复** Run 11 announcement_preview FP · **不重开** BD2E624

---

## 1. Gap Found

| 项 | 说明 |
|----|------|
| gap_id | `GAP-B-WRONG-COMPANY-FP-LINEAGE` |
| 现象 | Phase 1 quality audit `wrong_company`（交叉披露他司报告，如「关于披露冀东水泥半年报的提示性公告」）路由已能排除 periodic，但 `false_positive_reason` 被 **误标为 `announcement_preview`**（因同含「提示性公告」），或实体名交叉披露 **fp 为空** |
| 影响 | disclosure/event 边缘分类 lineage 将「他司交叉披露」与「本公司报告期提示」混为一谈；无法对齐 validation_design §7 / Phase 1 P1-AUD-022 |
| 为何非 busywork | Run 11 证据明确推荐此项；与 preview **相邻但语义不同**；规则枚举已存在，缺可执行 lineage + 锁测 |
| 已排除重复 | Run 11（`7fd3953`）仅 preview/更正 — **不含** wrong_company |
| 已排除禁区 | 不重开 BD2E624 · 不碰 scale-200/slice1 production roots · 不写 controller 政策 · 不 commit/push |

### 1.1 搜索证据（checked）

| 检查项 | 结果 |
|--------|------|
| Phase 1 audit P1-AUD-022 | `601992` / `关于披露冀东水泥半年报的提示性公告` / `wrong_company` |
| validation_design §7 | 已列 `wrong_company` = 交叉披露其他公司 |
| coverage `classify_exclusion_keyword("关于披露")` | → `cross_company_disclosure`（A 类统计口径） |
| 修复前路由探测 | 冀东水泥/他司标题 → `fp=announcement_preview`；无提示性公告实体名标题 → `fp=''` |
| Run 11 本公司提示基准 | `关于披露第一季度报告的提示性公告` 须 **保持** `announcement_preview`（不回退） |

---

## 2. Fix（最小）

1. `config/cninfo_announcement_categories.yaml` — 新增 `excluded_from_periodic_routing.wrong_company`（他司 / 关于披露他司 / 其他公司）
2. `lab/validate_cninfo_b_class_category_routing.py` — `_is_wrong_company_cross_disclosure()`；`FALSE_POSITIVE_REASONS["wrong_company"]`；Priority-4/5 中 **wrong_company 优先于 announcement_preview**；排除「关于延期披露」子串陷阱
3. `fixtures/b_class/known_documents/known_document_benchmark.yaml` — +4 false_positive_guard（010–013）
4. `lab/test_cninfo_b_class_category_routing_wrong_company_fp.py` — 9 项单测

---

## 3. Validation Results

| 检查 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_category_routing_wrong_company_fp.py` | **9 OK** |
| `python lab/test_cninfo_b_class_category_routing_preview_fp.py` | **9 OK**（Run11 不回退） |
| `python lab/validate_cninfo_b_class_category_routing.py` | **30/30 PASS** · fail=0 |
| `wrong_company` fp 行数（report CSV） | **4**（010–013） |
| `announcement_preview` fp 行数 | **4**（005–008，不变） |
| CNINFO calls | **0** |
| live | **none** |

路由汇总已刷新：

- [cninfo_b_class_category_routing_summary.md](cninfo_b_class_category_routing_summary.md)
- [cninfo_b_class_category_routing_report.csv](cninfo_b_class_category_routing_report.csv)

---

## 4. Capability Gain

- 交叉披露他司报告可 **稳定标注** 为 `false_positive_reason=wrong_company`（不再误标 preview / 空）
- 与本公司「关于披露第一季度报告的提示性公告」语义分离锁测
- benchmark **26 → 30**；false_positive_guard **9 → 13**
- **不**声称 B complete / verified / full-market %

---

## 5. Gate & Labels

```text
b_class_wrong_company_fp_lineage_gate = PASS_OFFLINE
cninfo_calls_this_package = 0
live_calls_this_package = 0
bd2e624_touched = no
announcement_preview_run11_regressed = no
scale200_slice1_roots_mutated = no
commit = not_requested
push = not_requested
```

**NOT verified** · **NOT production_ready** · **B NOT complete**

---

## 6. Next Recommended B Task

1. **可选（离线）：** 将 `announcement_preview` + `wrong_company` 行同步进 non_periodic document fixtures / seed 脚本，使 schema fixture 与 routing benchmark 同源。  
2. **可选（离线）：** `wrong_period` false_positive lineage（validation_design §7 仍缺锁测）。  
3. **勿做：** 重复 Run 11 preview FP；重开 BD2E624 live；扩 scale-200/slice1 production roots。  
4. Mission 级 full-market % 仍 **UNKNOWN**（分母未冻）— 非本包范围。
