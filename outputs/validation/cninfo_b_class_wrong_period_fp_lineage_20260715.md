# CNINFO B 类 Run 12 Wave 2 — wrong_period FP Lineage Gap Closure

_生成时间：2026-07-15 · offline only · **CNINFO = 0** · **无 live** · **无 commit** · **无 push**_

> **性质：** expected-period validation edge + evidence lineage · **NOT verified** · **NOT production_ready**  
> **不重复** Run 11 announcement_preview FP · **不重复** Run 12 Wave 1 wrong_company · **不重开** BD2E624

---

## 1. Gap Found

| 项 | 说明 |
|----|------|
| gap_id | `GAP-B-WRONG-PERIOD-FP-LINEAGE` |
| 现象 | validation_design §7 已列 `wrong_period`（报告期不匹配），且 routing rules §2.1 要求 `parsed_report_period == expected_period`，但 category routing 校验器 **从未** 解析标题报告期、也 **无** `expected_period` / `false_positive_reason=wrong_period` 锁测 |
| 影响 | 合法定期报告全文在「错年 / 错季」查询下仍可能被当作有效命中；disclosure/event lineage 无法与 Phase 1 expected-period 口径对齐 |
| 为何非 busywork | Wave 1 证据明确推荐此项；与 preview/wrong_company **语义不同**（标题仍 route periodic，假阳性在 period 层） |
| 已排除重复 | Run 11 = preview；Wave 1 = wrong_company — **不含** wrong_period |
| 已排除禁区 | 不重开 BD2E624 · 不碰 scale-200/slice1 production roots · 不写 controller 政策 · 不 commit/push |

### 1.1 搜索证据（checked）

| 检查项 | 结果 |
|--------|------|
| validation_design §7 | 已列 `wrong_period` = 报告期不匹配 |
| routing rules §2.1 | 准入条件含 `parsed_report_period == expected_period` |
| 修复前 `FALSE_POSITIVE_REASONS` | 含 preview/wrong_company，**无** wrong_period |
| 修复前 benchmark | **0** 条 `expected_period` / `expected_false_positive_reason: wrong_period` |
| Phase 1 coverage `parse_report_period` | 口径 2024 / 2024H1 / 2024Q1 / 2024Q3 — 本包离线复用同标签 |

---

## 2. Fix（最小）

1. `config/cninfo_announcement_categories.yaml` — `periodic_report.notes` 注明 period mismatch → `wrong_period`
2. `lab/validate_cninfo_b_class_category_routing.py` — `parse_title_report_period()`；`_apply_wrong_period_fp()`；`route_title(..., expected_period=)`；`FALSE_POSITIVE_REASONS["wrong_period"]`；fp_caught 计入 period 层假阳性
3. `fixtures/b_class/known_documents/known_document_benchmark.yaml` — periodic_001–004 补 `expected_period`；+4 false_positive_guard（014–017）
4. `lab/test_cninfo_b_class_category_routing_wrong_period_fp.py` — 10 项单测

---

## 3. Validation Results

| 检查 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_category_routing_wrong_period_fp.py` | **10 OK** |
| `python lab/test_cninfo_b_class_category_routing_wrong_company_fp.py` | **9 OK**（Wave 1 不回退） |
| `python lab/test_cninfo_b_class_category_routing_preview_fp.py` | **9 OK**（Run11 不回退） |
| `python lab/validate_cninfo_b_class_category_routing.py` | **34/34 PASS** · fail=0 |
| `wrong_period` fp 行数（report CSV） | **4**（014–017） |
| `wrong_company` fp 行数 | **4**（010–013，不变） |
| `announcement_preview` fp 行数 | **4**（005–008，不变） |
| CNINFO calls | **0** |
| live | **none** |

路由汇总已刷新：

- [cninfo_b_class_category_routing_summary.md](cninfo_b_class_category_routing_summary.md)
- [cninfo_b_class_category_routing_report.csv](cninfo_b_class_category_routing_report.csv)

---

## 4. Capability Gain

- 报告期错位（错年 / 同年错季）可 **稳定标注** 为 `false_positive_reason=wrong_period`
- 标题仍正确 route 到 `cninfo_periodic_report_pdf`（与 preview/wrong_company 标题排除语义分离）
- 期一致时 fp 为空（不误标）
- benchmark **30 → 34**；false_positive_guard **13 → 17**
- **不**声称 B complete / verified / full-market %

---

## 5. Gate & Labels

```text
b_class_wrong_period_fp_lineage_gate = PASS_OFFLINE
cninfo_calls_this_package = 0
live_calls_this_package = 0
bd2e624_touched = no
wrong_company_wave1_regressed = no
announcement_preview_run11_regressed = no
scale200_slice1_roots_mutated = no
commit = not_requested
push = not_requested
```

**NOT verified** · **NOT production_ready** · **B NOT complete**

---

## 6. Next Recommended B Task

1. **可选（离线）：** 将 `announcement_preview` + `wrong_company`（及本包非 periodic 行）同步进 non_periodic document fixtures / seed 脚本，使 schema fixture 与 routing benchmark 同源（当前 seed 仍停在 13 行）。  
2. **可选（离线）：** `unrelated_announcement` false_positive lineage（validation_design §7 最后一类未锁测）。  
3. **勿做：** 重复 preview / wrong_company / wrong_period；重开 BD2E624 live；扩 scale-200/slice1 production roots。  
4. Mission 级 full-market % 仍 **UNKNOWN**（分母未冻）— 非本包范围。
