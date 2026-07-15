# CNINFO B 类 Run 12 Wave 3 — Non-periodic FP Fixture Sync

_生成时间：2026-07-15 · offline only · **CNINFO = 0** · **无 live** · **无 commit** · **无 push**_

> **性质：** schema fixture ↔ routing benchmark FP lineage 同源 · **NOT verified** · **NOT production_ready**  
> **不重复** Run 11 preview / Wave 1 wrong_company / Wave 2 wrong_period · **不重开** BD2E624

---

## 1. Gap Found

| 项 | 说明 |
|----|------|
| gap_id | `GAP-B-NONPERIODIC-FP-FIXTURE-SYNC` |
| 现象 | routing benchmark 已锁 `announcement_preview`（005–008）+ `wrong_company`（010–013），但 `non_periodic_document_fixtures.jsonl` / seed **仍停在 13 行**；`build_document` **不写出** `expected_false_positive_reason` |
| 影响 | schema fixture 与 category-routing benchmark **不同源** — Phase 3 document seed 无法复用 FP lineage |
| 为何非 busywork | Wave 2 证据明确推荐此项；fixtures 路径真实存在且可执行（非弱路径） |
| 已排除重复 | preview / wrong_company / wrong_period routing 锁测已 PASS — **本包只做 fixture 同源同步** |
| 已排除禁区 | 不重开 BD2E624 · 不碰 scale-200/slice1 · 不 lock unrelated_announcement（fixtures 路径足够强，走 sync 而非 fallback） |

### 1.1 路径判定

| 检查项 | 结果 |
|--------|------|
| `fixtures/b_class/document/non_periodic_document_fixtures.jsonl` | **存在**（修复前 13 行） |
| `lab/seed_cninfo_b_class_non_periodic_document_fixtures.py` | **存在** |
| `lab/validate_cninfo_b_class_non_periodic_document_schema.py` | **存在** |
| `retrieval_validation/known_document_retrieval_cases.yaml` | design_only placeholder — **不作为本包主路径** |
| 判定 | **fixtures path strong → sync FP coverage**（不转 lock unrelated_announcement） |

---

## 2. Fix（最小）

1. `lab/seed_cninfo_b_class_non_periodic_document_fixtures.py` — `build_document` 的 `benchmark_row` 增加 `expected_false_positive_reason`
2. 重跑 seed → `non_periodic_document_fixtures.jsonl`：**13 → 26**（含 preview×4 + wrong_company×4 + 更正/Era D2E 非 periodic 增量）；`wrong_period` 014–017 仍 `skipped_periodic`
3. `lab/validate_cninfo_b_class_non_periodic_document_schema.py` — summary 增加 FP 同源覆盖统计
4. `lab/test_cninfo_b_class_non_periodic_fp_fixture_sync.py` — 7 项锁测

---

## 3. Validation Results

| 检查 | 结果 |
|------|------|
| `python lab/seed_cninfo_b_class_non_periodic_document_fixtures.py` | benchmark=34 · seeded=**26** · skipped_periodic=**8** |
| `python lab/validate_cninfo_b_class_non_periodic_document_schema.py` | **26/26 PASS** · fail=0 |
| `python lab/test_cninfo_b_class_non_periodic_fp_fixture_sync.py` | **7 OK** |
| `python lab/test_cninfo_b_class_category_routing_preview_fp.py` | **9 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_wrong_company_fp.py` | **9 OK**（不回退） |
| `python lab/test_cninfo_b_class_category_routing_wrong_period_fp.py` | **10 OK**（不回退） |
| fixture `announcement_preview` | **4** |
| fixture `wrong_company` | **4** |
| fixture 含 `wrong_period` | **0**（正确跳过） |
| CNINFO calls | **0** |
| live | **none** |
| BD2E624 | **not touched** |

---

## 4. Capability Gain

- non-periodic schema fixture 与 routing benchmark 对 `announcement_preview` / `wrong_company` **同源**（含 `expected_false_positive_reason` 字段）
- seed 可重复生成；重跑不会丢 FP 字段（roundtrip 锁测）
- 不改变 routing 语义；不引入 live

---

## 5. Gate

```
b_class_non_periodic_fp_fixture_sync_gate = PASS_OFFLINE
cninfo_calls = 0
live = none
bd2e624_touched = no
preview_run11_regressed = no
wrong_company_wave1_regressed = no
wrong_period_wave2_regressed = no
```

**NOT verified** · **NOT production_ready** · **B NOT complete**

---

## 6. Next Recommended B Task

1. **仍有价值（离线）：** `unrelated_announcement` false_positive lineage（validation_design §7 最后一类未锁测）。  
2. **可选（离线）：** 重跑 parse_run dry-run seed（仍可能停在旧 33=20+13；本包未触碰）。  
3. **勿做：** 重复 preview / wrong_company / wrong_period / 本包 fixture sync；重开 BD2E624 live；扩 scale-200/slice1 production roots。  

### B 是否还有有价值的离线 gap？

**是。** 最清晰的下一项仍是 `unrelated_announcement` FP lineage；parse_run 与 non_periodic 行数漂移为次要维护项。
