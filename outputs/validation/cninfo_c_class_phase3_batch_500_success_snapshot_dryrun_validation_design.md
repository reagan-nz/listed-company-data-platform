# CNINFO C-Class Phase 3 Batch 500 Success-Subset Snapshot Dry-Run Validation Design

_生成时间：2026-07-09_

> Dry-run / 未来 build 阶段的离线 validation 设计。**无 CNINFO** · **无 snapshot build**（本轮）

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**batch_id：** `phase3_batch_500_001`

---

# 1. Validation Scope

| 项 | 值 |
|----|-----|
| universe | **491** identity-clean companies |
| excluded | **9** identity caveat（不得出现） |
| harvest input | `outputs/harvest/cninfo_c_class/phase3_batch_500_001/normalized/` |
| snapshot output（未来） | `outputs/snapshot/cninfo_c_class/phase3_batch_500_001_success/` |

---

# 2. Module Availability Checks

| 模块 | 来源 | dry-run 检查 | build 检查 |
|------|------|--------------|------------|
| company_basic_profile | normalized direct | 路径规划 | 记录存在 + mapper |
| executive_profile | normalized direct | 路径规划 | 记录存在 |
| share_capital_profile | normalized direct | 路径规划 | 记录存在（允许 partial） |
| top_shareholders_profile | normalized direct | 路径规划 | 记录存在 |
| top_float_shareholders_profile | normalized direct | 路径规划 | 记录存在 |
| dividend_history | normalized direct | 路径规划 | 记录存在（允许 empty） |
| contact_profile | derived from basic | 路径规划 | derived mapper |
| business_scope | derived from basic | 路径规划 | derived mapper |
| industry_profile | derived from basic | 路径规划 | derived mapper |
| security_profile | observe-only | 路径规划 | 不绑定主 gate |
| 其余 8 模块 | mapper 链 | 路径规划 | module status 统计 |

**Dry-run：** 仅验证 `planned_modules=18` 与 output path 规划，不读 normalized 内容。

**Build（未来）：** 逐模块 `available` / `partial` / `missing` 统计。

---

# 3. Missing Fields Checks

| 级别 | 规则 |
|------|------|
| company-level | `company_code` · `company_name` 必填 |
| module-level | basic 缺失 → `snapshot_status=failed` |
| field-level | 非关键字段缺失 → `partial` flag |
| derived | basic 不可用 → derived `not_available` |

Dry-run 阶段：**不执行** field-level 检查。

---

# 4. Quality Flags

| flag | 触发条件 | snapshot 影响 |
|------|----------|---------------|
| `harvest_partial` | harvest_status=partial | `complete_with_caveat` |
| `harvest_failed` | harvest_status=failed but identity-clean | `complete_with_caveat` 或 exclude（QA 判定） |
| `share_capital_partial` | source_partial policy | module `partial` |
| `dividend_empty_valid` | valid_empty | module `partial` |
| `identity_caveat` | caveat ledger 命中 | **exclude**（不进 universe） |

**491 纳入集：** 允许 `harvest_partial` / `harvest_failed` caveat 传播到 quality flags，但不自动排除（与 Phase 2 188 模式一致）。

---

# 5. Caveat Propagation

| 来源 | 传播到 snapshot |
|------|-----------------|
| identity caveat ledger（9） | **hard exclude** — 不在 universe |
| subset design `caveat` 列 | QA review 参考 |
| harvest `partial`/`failed` | `snapshot_status=complete_with_caveat` 候选 |
| security observe-only | 不阻塞主 gate |

**规则：** identity caveat **不 merge** · **不解析** · 仅 hard exclude。

---

# 6. Dry-Run Validation Matrix

| 检查项 | 方法 | 通过标准 |
|--------|------|----------|
| universe count | YAML meta | **491** |
| hold overlap | batch runner validate | **0** |
| excluded codes absent | YAML diff vs ledger | **9/9 absent** |
| report row count | dry-run CSV | **491** |
| snapshot JSON count | filesystem glob | **0** |
| output root isolation | path check | under `phase3_batch_500_001_success/` |
| 863 / phase2 isolation | path check | 无写入 |

---

# 7. Future Build Validation（未执行）

| 检查项 | 预期 |
|--------|------|
| JSON count | **491**（或 <491 若 QA 再排除 partial） |
| module coverage report | 491 行 |
| quality flags CSV | per-company flags |
| completeness gate | `PASS` or `PASS_WITH_CAVEAT` |

---

# 8. Red Lines

- **no CNINFO**
- **no identity merge**
- **no registry write**
- **no verified**
