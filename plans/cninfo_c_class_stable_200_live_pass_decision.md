# CNINFO C-Class Stable 200 Non-BSE Live Pass Decision

_决策日期：2026-07-07_

> **性质：** Era C Phase 4 C 类 **stable 200 non-BSE** 在新版 runner 下 **LIVE_PASS** 的阶段性决策记录。**非** verified · **非** testing_stable_sample · **非** YAML 执行 · **非** 入库。

---

## 一、Executive Decision

| 项 | 决策 |
|----|------|
| stable 200 non-BSE（新版 runner） | **LIVE_PASS** |
| C-class non-BSE 主宇宙 | cleaned stable 200 样本上 **具备继续扩展条件** |
| 前次 LIVE_PARTIAL 主因 | **runner 对 CNINFO 业务码限流处理不足**；**非** source 覆盖失败、**非** 样本公司无效 |
| 12 家 six-fail | **不清洗、不 hold** |
| stable 200 v2 | **取消 / 不需要** |
| 下一步 | **889 non-BSE rerun planning** |

**结论：** 在 backoff + orgId fallback 修复后，stable 200 cleaned non-BSE 样本上六主源 + security observe 全部通过；可将 non-BSE main universe 推进至 **889 全量重跑规划**阶段。

---

## 二、Evidence Chain

| 阶段 | 事件 | 产出 | 结论 |
|------|------|------|------|
| 1 | stable 200 **v1** live | [v1 diagnosis](../outputs/validation/cninfo_c_class_stable_200_diagnosis.md) | **LIVE_PARTIAL** · pass=1069 fail=131 · 12 家 6/6 |
| 2 | 12 家 **人工审计** | [audit CSV](../outputs/validation/cninfo_c_class_stable_200_manual_audit_12_companies.csv) · [audit plan](cninfo_c_class_manual_audit_12_six_fail_companies.md) | 12/12 网页有结构化公司介绍 · **非** sample_quality_issue |
| 3 | **endpoint/parser debug** | [debug summary](../outputs/validation/cninfo_c_class_12_six_fail_endpoint_debug_summary.md) | paced debug 11/12 可达 · 主因候选为批量节流 · 600203 需 orgId |
| 4 | **runner patch** | `validate_cninfo_c_class_scale_smoke.py` · §7ar | `cninfo_throttled_business_code` · backoff 2/5/10s · orgId fallback |
| 5 | **12 家 targeted retry** live | [12 live summary](../outputs/validation/cninfo_c_class_retry_stable_200_six_fail_12_live_summary.md) | **LIVE_PASS** · pass=72 observe_pass=12 fail=0 |
| 6 | **stable 200 rerun** live | [stable 200 live summary](../outputs/validation/cninfo_c_class_stable_200_live_summary.md) | **LIVE_PASS** · pass=1200 fail=0 · 六主源 200/200 |

---

## 三、Stable 200 Rerun Result

**样本：** `lab/eval_companies_c_class_stable_200_non_bse.yaml`  
**Runner：** backoff + orgId fallback（post-§7ar）  
**报告：** [live_report.csv](../outputs/validation/cninfo_c_class_stable_200_live_report.csv) · [live_summary.md](../outputs/validation/cninfo_c_class_stable_200_live_summary.md)

### Overall

| 指标 | 值 |
|------|-----|
| companies | **200** |
| planned cases | **1400**（200 × 7） |
| main judgment cases | **1200**（200 × 6） |
| pass | **1200** |
| fail | **0** |
| skipped | **0** |
| blocked | **0** |
| HTTP 429 | **0** |
| **result** | **LIVE_PASS** |

### Per-source（200/200）

| source_id | reachable | pass | fail | 备注 |
|-----------|-----------|------|------|------|
| `cninfo_company_basic_profile` | 200/200 | 200 | 0 | non_empty 100% |
| `cninfo_dividend_financing_profile` | 200/200 | 200 | 0 | valid_empty=2 · reach 100% |
| `cninfo_executive_profile` | 200/200 | 200 | 0 | |
| `cninfo_share_capital_profile` | 200/200 | 200 | 0 | |
| `cninfo_top_shareholders_profile` | 200/200 | 200 | 0 | |
| `cninfo_top_float_shareholders_profile` | 200/200 | 200 | 0 | |
| `cninfo_company_security_profile` | 200/200 | 0 | 0 | **observe_pass=200** · 不绑定主 gate |

### v1 → rerun 对比

| 指标 | v1 live | rerun（新版 runner） |
|------|---------|----------------------|
| pass | 1069 | **1200** |
| fail | 131 | **0** |
| result | LIVE_PARTIAL | **LIVE_PASS** |
| 12 家 six-fail | 6/6 fail | **全部 pass**（含于 200/200） |

---

## 四、Root Cause Update

| 旧判断（v1 diagnosis） | 更新判断 |
|------------------------|----------|
| 样本二次清洗不足 · 建议剔除 12 家 | **推翻** — 12 家网页审计有 profile |
| `schema_unexpected` / `data.records missing` | 多为 **`cninfo_throttled_business_code`**（JSON 429/90001）在批量连跑时未退避 |
| parser `data.records` 路径错误 | **非主因** — paced debug 与 rerun 证明路径有效 |
| endpoint 选错 | **否** — data20 路径正确 |
| 600203 orgId | **个案** — orgId fallback 有必要 |

**改判主因：** `cninfo_throttled_business_code` / **batch live pacing issue**；runner 修复后 12 家 retry 与 stable 200 rerun 均恢复。

---

## 五、Source Status Update

> 基于 stable 200 rerun + 12 retry 证据；**不写 verified** · **不写 testing_stable_sample**。

| source_id | 前序状态 | stable 200 证据后 | YAML backfill |
|-----------|----------|-------------------|---------------|
| `cninfo_company_basic_profile` | proceed_testing_with_caveat | **stable_200_live_pass evidence** · 继续 proceed_testing_with_caveat | NO |
| `cninfo_dividend_financing_profile` / **dividend_history** | proceed_testing | **stable_200_live_pass** · reach **100%** · valid_empty=2 · error_rate=0 | **GO（决策 only）** · 命名窄化 **dividend_history** · **本轮不执行** |
| `cninfo_executive_profile` | proceed_testing_with_caveat | stable 200 **200/200** · 继续 proceed_testing_with_caveat | NO |
| `cninfo_share_capital_profile` | source_partial | **reachability 200/200** · 保持 **source_partial/caveat** · **不升级 stable** | NO |
| `cninfo_top_shareholders_profile` | proceed_testing_with_caveat | stable 200 **200/200** | NO |
| `cninfo_top_float_shareholders_profile` | source_partial | **reachability 200/200** · 保持 **source_partial** 口径 | NO |
| `cninfo_company_security_profile` | observe_only | observe **200/200** · **不绑定主 gate** | N/A |
| contact / business_scope / industry | derived_no_separate_fetch | 随 basic fill_rate · stable 200 basic 100% | NO |

**dividend_history：** **GO as decision**（语义窄化、非 financing 全包）；889 rerun 后再评估是否执行 YAML backfill。

---

## 六、Universe Decision

| universe | 决策 |
|----------|------|
| **non-BSE main** | **CONDITIONAL YES** · **ready for 889 rerun planning** |
| BSE 920 | **separate child universe** · 不混入本轮 |
| BSE 83/87 legacy | **HOLD** |
| abnormal_review | **HOLD** / sample_quality_review |
| mixed full market | **not ready** |

---

## 七、Next Stage Recommendation

1. **不再做 stable 200 v2** — rerun LIVE_PASS 已覆盖 cleaned 200 样本。
2. **不再剔除 12 家 six-fail** — 已纳入 200/200 pass。
3. **Commit 当前 LIVE_PASS 决策** — 本文档 + 报告归档。
4. **设计 889 non-BSE rerun plan** — 新版 runner · preflight · pacing。
5. **889 rerun preflight** — company_count=889 · cases=6223 · hard gate · 请求节流策略。
6. **889 live 后** — 重新评估 **dividend_history YAML backfill** 是否执行。
7. **仍然** — 不入库 · 不 backfill 执行 · 不写 verified。

---

## 八、Caveats

- stable 200 **不是全市场**；仅为 cleaned non-BSE 分层样本（200/863 eligible）。
- **889 non-BSE 尚未**用新版 runner 重跑；v1 仍为 LIVE_PARTIAL。
- **BSE** 与 **abnormal_review** 公司仍未解决。
- source status 仍为 **testing / proceed_testing** 层级；**no verified**。
- **no testing_stable_sample**（文件名 stable 仅为设计语义）。
- **no database ingestion**。
- **no YAML backfill executed**（dividend_history 仅决策 GO）。

---

## 九、参考

- [source status decision](cninfo_c_class_source_status_decision.md)
- [stable 200 sample plan](cninfo_c_class_stable_200_sample_plan.md)
- [12 retry live summary](../outputs/validation/cninfo_c_class_retry_stable_200_six_fail_12_live_summary.md)
- [stable 200 live summary](../outputs/validation/cninfo_c_class_stable_200_live_summary.md)
- [v1 diagnosis](../outputs/validation/cninfo_c_class_stable_200_diagnosis.md)（已被本决策 supersede 部分结论）

---

## 十、红线（本轮文档）

- 本轮 **无 live** · **无 CNINFO 请求** · **无 YAML 执行** · **无 DB** · **无 verified**
