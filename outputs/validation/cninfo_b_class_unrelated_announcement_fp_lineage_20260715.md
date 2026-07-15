# CNINFO B 类 Run 12 Wave 4 — unrelated_announcement FP Lineage Gap Closure

_生成时间：2026-07-15 · offline only · **CNINFO = 0** · **无 live** · **无 commit** · **无 push**_

> **性质：** disclosure/event taxonomy edge + evidence lineage · **NOT verified** · **NOT production_ready**  
> **不重复** Run 11 announcement_preview · Wave 1 wrong_company · Wave 2 wrong_period · Wave 3 fixture sync · **不重开** BD2E624

---

## 1. Gap Found

| 项 | 说明 |
|----|------|
| gap_id | `GAP-B-UNRELATED-ANNOUNCEMENT-FP-LINEAGE` |
| 现象 | validation_design §7 最后一类 `unrelated_announcement`（其他无关公告）无锁测；补充/更正已排除 periodic 但 **fp 为空**；审计机构/内控评价/非标意见等含「年度报告」字样标题 **误 route periodic** |
| 影响 | §7 假阳性枚举不完整；retrieval 复用 `route_title` 时无法标注「其他无关公告」；部分非全文标题计入 periodic |
| 为何非 busywork | Wave 3 证据明确推荐此项为 §7 **最后一类未锁测**；与 preview/wrong_company/wrong_period **语义不同** |
| 已排除重复 | preview / wrong_company / wrong_period routing + Wave 3 fixture sync — **不含** unrelated_announcement |
| 已排除禁区 | 不重开 BD2E624 · 不碰 scale-200/slice1 production roots · 不写 controller 政策 · 不 commit/push |

### 1.1 搜索证据（checked）

| 检查项 | 结果 |
|--------|------|
| validation_design §7 | 已列 `unrelated_announcement` = 其他无关公告 |
| 修复前 `FALSE_POSITIVE_REASONS` | 含 preview/wrong_company/wrong_period，**无** unrelated_announcement |
| 修复前探测 | 补充/更正 → route general、**fp 空**；审计机构/内控评价/非标意见 → **误 route periodic** |
| Run11/W1/W2 不回退基准 | 本公司提示 → preview；冀东水泥 → wrong_company；错年年报 → wrong_period |

---

## 2. Fix（最小）

1. `config/cninfo_announcement_categories.yaml` — `periodic_report.exclusion_patterns` 增补补充/更正/取消披露/审计机构/内控评价/非标意见；新增 `excluded_from_periodic_routing.unrelated_announcement`
2. `lab/validate_cninfo_b_class_category_routing.py` — `FALSE_POSITIVE_REASONS["unrelated_announcement"]`；`_is_unrelated_announcement()`；Priority-4/5 映射（排在 delayed/wrong_company/preview/summary **之后**）
3. `fixtures/b_class/known_documents/known_document_benchmark.yaml` — 003/009 锁 `expected_false_positive_reason`；+4 行（018–021）
4. `lab/test_cninfo_b_class_category_routing_unrelated_announcement_fp.py` — 10 项单测
5. 重跑 seed → non_periodic fixtures **26 → 30**（含 unrelated×6）；schema summary 记 unrelated 计数

---

## 3. Validation Results

| 检查 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_category_routing_unrelated_announcement_fp.py` | **10 OK** |
| `python lab/test_cninfo_b_class_category_routing_preview_fp.py` | **9 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_wrong_company_fp.py` | **9 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_wrong_period_fp.py` | **10 OK**（不回退） |
| `python lab/validate_cninfo_b_class_category_routing.py` | **38/38 PASS** · fail=0 |
| `python lab/test_cninfo_b_class_non_periodic_fp_fixture_sync.py` | **7 OK** |
| schema validation（`.venv`） | **30/30 PASS** |
| `unrelated_announcement` fp 行数（report CSV） | **6**（003、009、018–021） |
| `announcement_preview` / `wrong_company` / `wrong_period` | **4 / 4 / 4**（不变） |
| CNINFO calls | **0** |
| live | **none** |

路由汇总已刷新：

- [cninfo_b_class_category_routing_summary.md](cninfo_b_class_category_routing_summary.md)
- [cninfo_b_class_category_routing_report.csv](cninfo_b_class_category_routing_report.csv)

---

## 4. Capability Gain

- 含报告字样的其他无关公告可 **稳定标注** 为 `false_positive_reason=unrelated_announcement`
- 审计机构 / 内控评价 / 非标意见 **不再误 route** `cninfo_periodic_report_pdf`
- benchmark **34 → 38**；false_positive_guard **17 → 21**；non_periodic fixtures **26 → 30**
- validation_design §7 标题路由 FP 类（preview / wrong_company / wrong_period / unrelated）**离线锁测齐套**
- **不**声称 B complete / verified / full-market %

---

## 5. Gate & Labels

```text
b_class_unrelated_announcement_fp_lineage_gate = PASS_OFFLINE
cninfo_calls_this_package = 0
live_calls_this_package = 0
bd2e624_touched = no
announcement_preview_run11_regressed = no
wrong_company_wave1_regressed = no
wrong_period_wave2_regressed = no
scale200_slice1_roots_mutated = no
commit = not_requested
push = not_requested
```

**NOT verified** · **NOT production_ready** · **B NOT complete**

---

## 6. Next Recommended B Task

1. **§7 标题路由 FP lineage 已耗尽（离线）。** 再开同类离线 FP 包收益低。  
2. **仍有价值（非再开 §7 FP）：** parse_run dry-run 与 non_periodic 行数对齐；真实 known-document（公司+日期）替换离线标题样例；category_code probe。  
3. **勿做：** 重复 preview / wrong_company / wrong_period / unrelated / Wave3 fixture sync；重开 BD2E624 live；扩 scale-200/slice1 production roots。  
4. Mission 级 full-market % 仍 **UNKNOWN**（分母未冻）— 非本包范围。

### Honest answer

**是：B 类 validation_design §7 标题路由 / FP lineage 离线锁测集已齐，暂时耗尽。**  
剩余价值在 retrieval/live、真实 known-document、parse_run 维护，而非再发明一个离线 FP 类。
