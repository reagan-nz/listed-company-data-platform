# C-class 200-Company Scale Smoke Test Plan

_Era C Phase 4 · 2026-07-06_

> **前置条件：** active-only 30-company live smoke 已完成（[active summary](../outputs/validation/cninfo_c_class_scale_smoke_30_active_summary.md)）。**200 active dry-run checkpoint 已通过**；**200 live 等待人工明确批准**（本轮不跑 `--live`）。

---

## 0. 200 live 前 checkpoint（2026-07-06）

| 项 | 状态 |
|----|------|
| active 样本 | [eval_companies_c_class_smoke_200_active.yaml](../lab/eval_companies_c_class_smoke_200_active.yaml) · **195** 家 |
| dry-run | **PASS** — companies=195 · cases=1365 · skipped=1365 · `DRY_RUN_ONLY` |
| dry-run 输出 | [report](../outputs/validation/cninfo_c_class_scale_smoke_200_active_report.csv) · [summary](../outputs/validation/cninfo_c_class_scale_smoke_200_active_summary.md) |
| planned live requests | **1365** = 195 × 7 |
| CNINFO 请求（本轮） | **0**（dry-run only） |
| shareholder empty_but_valid 口径 | **已文档化**（§6） |
| security observe-only 口径 | **已文档化**（§7） |
| verified / testing_stable_sample / DB / YAML backfill | **均未执行** |
| **200 `--live`** | **等待人工明确批准** |

---

## 1. 目标

在 **active-listed** 200 家分层样本上，复用 `lab/validate_cninfo_c_class_scale_smoke.py`，验证 C 类 direct source 的可扩展性（fill_rate + reachability + 板块分组），为是否进入 1000 家提供证据。

**不做：** verified · testing_stable_sample · DB 入库 · YAML backfill 执行 · 新增 endpoint discovery · 单独请求 derived 三源。

---

## 2. 样本来源与 active 过滤策略

| 项 | 说明 |
|----|------|
| **母本** | `lab/eval_companies_200.yaml`（200 家 · 含 `stock_code` / `orgid` / `board` / `exchange`） |
| **派生文件（计划）** | `lab/eval_companies_c_class_smoke_200_active.yaml` |
| **派生文件（已生成）** | `lab/eval_companies_c_class_smoke_200_active.yaml` — **195** active（母本剔除 5 退市 · dry-run 通过） |
| **分层（母本）** | sse_main 60 · szse_main 50 · chinext 45 · star 25 · bse 20 |

### Active-listed 过滤规则（与 30 active 一致）

1. **剔除** `short_name` 含「退市」的条目。
2. **剔除** 已知退市/退代码（30 轮已验证：600647 · 600002 · 002473；200 轮扫描母本后维护 `removed_delisted` 列表）。
3. **不联网** 校验上市状态；`*ST` 等仍可能保留（limitation 写入样本 `notes`）。
4. 剔除后若某板块不足母本配额，**不从母本外补股**；记录实际各板块 count 与 limitation。
5. 预期 active 池略小于 200（母本含若干退市名）；以派生 YAML 实际 `companies` 长度为准。

### 30 轮经验

含退市样本会系统性产生 HTTP 500（`9240002`），污染 reachability；**200 轮必须使用 active 过滤后的母本**，不得直接对 raw `eval_companies_200.yaml` 跑 live。

---

## 3. 参与 source

### 主判定（scode-only）

| source_id | endpoint |
|-----------|----------|
| `cninfo_company_basic_profile` | `getCompanyIntroduction?scode=` |
| `cninfo_dividend_financing_profile` | `getCompanyHisDividend?scode=` |
| `cninfo_executive_profile` | `getCompanyExecutives?scode=` |
| `cninfo_share_capital_profile` | `getStockStructure?scode=` |
| `cninfo_top_shareholders_profile` | `getTopTenStockholders?scode=` |
| `cninfo_top_float_shareholders_profile` | `getTopTenCirculatingStockholders?scode=` |

### 观察维度（不绑定主判定 gate）

| source_id | 说明 |
|-----------|------|
| `cninfo_company_security_profile` | `marketOverview` · `secType=szshe` 硬编码；**保持 observe-only** 直至跨板块 secType 逻辑修复 |

### Derived 三源（不单独请求）

`cninfo_company_contact_profile` · `cninfo_company_business_scope` · `cninfo_company_industry_profile` — 仅随 basic `basicInformation` **fill_rate** 统计。

---

## 4. 脚本与输出（计划）

| 项 | 路径 |
|----|------|
| 脚本 | `lab/validate_cninfo_c_class_scale_smoke.py` |
| 样本参数 | `--sample-file lab/eval_companies_c_class_smoke_200_active.yaml` |
| CSV | `outputs/validation/cninfo_c_class_scale_smoke_200_active_report.csv` |
| Summary | `outputs/validation/cninfo_c_class_scale_smoke_200_active_summary.md` |
| 对比基线 | `cninfo_c_class_scale_smoke_30_active_report.csv` |

**执行顺序：** `--dry-run` 确认装载与 URL → 人工批准后再 `--live`。

**限流：** 保持 `SLEEP_SECONDS=0.8`；195 家 × 7 源 = **1365** 请求，预估 **~25–35 分钟**（不含重试）。

**脚本小改（可选，200 live 跑前）：** 将 §6 股东源 `empty_but_valid` 口径落实为 runner 内 gate 统计（当前 30 轮脚本仍可能将 empty 记为 `case_result=fail`）。

---

## 5. 指标口径

### 5.1 Per-source

- **endpoint_reachable%** — 端点可连通且 JSON 形状合法（含 dividend `valid_empty`、股东源 `empty_but_valid_response`）
- **non_empty_rate%** — 有实质 records 的占比（basic / list 源；与 reachable 分开统计）
- **blocked / 429 / http_error** 计数与 error%
- **pass / fail**（`security_profile` 使用 `observe_pass` / `observe_fail`，不进入主 gate）

### 5.2 Fill_rate

- **basic 关键字段：** F001V · F004V · F005V · F015V · F016V · F032V · MARKET（endpoint_found 子集）
- **dividend 日期类：** F018D · F020D · F023D（非空 records 子集）
- **derived：** contact 8 字段 · business_scope 3 字段 · industry 3 字段（随 basic）

### 5.3 Board-level

按 `board` × `source_id` 输出 pass% · reachability%；用于发现板块系统性失败。

### 5.4 阈值（与 30 轮一致，200 轮沿用）

| 指标 | 门槛 |
|------|------|
| blocked + 429 | **= 0**（硬门槛） |
| http_error（退市除外） | **< 5%** per source |
| basic reachability | **≥ 95%** |
| basic non_empty | **≥ 90%** |
| basic 关键字段 fill_rate | **≥ 85%**（endpoint_found 子集） |
| dividend reachability | **≥ 95%**（valid_empty 计 reachable） |
| dividend 日期类 fill_rate | **≥ 80%**（非空 records 子集） |
| 板块系统性失败 | 任一 board × 主判定 source pass **< 80%** → 降级 |

---

## 6. Shareholder `empty_but_valid` policy（正式口径）

**适用 source：**

- `cninfo_top_shareholders_profile`
- `cninfo_top_float_shareholders_profile`

### 6.1 判定条件（全部满足）

| 条件 | 要求 |
|------|------|
| HTTP | **200** |
| top-level `code` | **200**（或脚本已接受的等价 success code） |
| `data.resultCode` | **200** |
| `data.records` | **存在且为 list** |
| `records` 长度 | **0** |

→ 记录为 **`retrieval_status: empty_but_valid_response`**

### 6.2 在 200 smoke 中的语义

- **不计** blocked
- **不计** http_error
- **不计** schema_unexpected
- **不直接代表** endpoint 不可用
- **单独统计**于 `empty_but_valid` / valid-empty 类指标（与 dividend `valid_empty` 分列）
- summary 按 **board** 汇总；若样本含上市年限字段则按 **company_age** 观察是否集中于新股、北交所、科创板或特殊公司

### 6.3 主 gate 建议

| 维度 | 规则 |
|------|------|
| reachability vs non_empty | **区分** `endpoint_reachable` 与 `non_empty`；股东源 empty_but_valid 计入前者、不计入后者 |
| source 降级 | 仅当 empty_but_valid 比例**异常高**时标记 **`source_partial`** |
| 全样本 review | empty_but_valid **> 15%**（per source）→ 进入 **review** |
| 板块 review | 某 **board** empty_but_valid **> 30%**（per source）→ **board-specific review** |

### 6.4 30 active live 先例（非 failure）

| code | name | board | source |
|------|------|-------|--------|
| 688797 | 臻宝科技 | star | top_shareholders · top_float |
| 920186 | 中科仪 | bse | top_float |

均为 HTTP 200 + 空 list，**非** network / schema failure。

---

## 7. `security_profile` observe-only policy（正式口径）

| 项 | 说明 |
|----|------|
| source | `cninfo_company_security_profile` · `GET .../marketOverview` |
| 200 live | **继续跑** live observation（计入 7 源/公司请求） |
| 主 go/no-go | **不绑定** — 不参与主 source pass/fail gate |
| 原因 | `marketOverview` 依赖 `orgId` + `secType`；当前 runner 硬编码 **`secType=szshe`**，跨板块逻辑**未充分验证** |
| summary | **单独展示** reachability / blocked / 板块分布；与 basic/dividend/P2-A 主判定分开解读 |
| case_result | 使用 `observe_pass` / `observe_fail`（若有），**不计入**主判定 pass/fail 分子 |

**修复 secType 跨板块映射前：** security 仅作观察维度，**不得**因 security 单独失败而否决 200→1000 主 gate。

---

## 8. Gate 决策

### 8.1 dividend YAML backfill（决策层，不执行）

30 active 轮：**GO**（reachability 100% · valid_empty=2 · blocked/429=0）。

**执行仍暂缓**，待 200 轮确认后单独 backfill PR。backfill 时必须：

- 窄化命名为 **`dividend_history`**（或等价），消除 financing 过度承诺
- Caveat：**historical dividend only**；financing / allotment **not confirmed**

### 8.2 enter_200（当前）

30 active 轮结论：**CONDITIONAL YES**。200 准备阶段：

**进入 200 live 前 checklist：**

- [x] 生成 `eval_companies_c_class_smoke_200_active.yaml` 并记录剔除列表（195 家）
- [x] dry-run 通过（1365 cases · URL 正确 · 无 CNINFO 请求）
- [x] 股东源 empty_but_valid 策略已文档化（§6）
- [x] security observe-only 策略已文档化（§7）
- [x] 红线确认：无 verified · 无 testing_stable_sample · 无 DB · 无 YAML backfill
- [ ] **人工明确批准** 后执行 `--live`

### 8.3 200 → 1000 go/no-go（预设，200 live 跑完后填）

| 条件 | 门槛 |
|------|------|
| 200 active reachability（basic + dividend + P2-A 四源） | **≥ 95%** 各源 |
| blocked + 429 | **= 0** |
| http_error（非退市） | **< 3%** 各源 |
| 无板块系统性失败 | 各 board pass **≥ 85%**（主判定） |
| basic 关键 fill_rate | **≥ 85%** |
| security secType 跨板块 | **已修复** 或仍 observe-only 且不影响主判定 |
| 限流可控 | 1400 请求无大规模 429；若出现需 backoff 策略 |
| 反爬 / 空值兜底口径 | 文档化后方可启动 1000 |

**未达标 → 不启动 1000**；优先修样本、限流、secType、empty 语义。

---

## 9. 红线（重申）

- 不写 **verified**
- 不升级 **testing_stable_sample**
- **不执行** dividend YAML backfill（仅决策 GO + caveat）
- **不入库** · 无 migration
- 不新增 C-class endpoint discovery
- 不单独请求 derived contact / business_scope / industry
- 不改 B / D / Phase 1 文件
- **不跑 `--live`**（直至人工明确批准）

---

## 10. 参考

- 200 dry-run checkpoint：[summary](../outputs/validation/cninfo_c_class_scale_smoke_200_active_summary.md)
- 30 active live：[summary](../outputs/validation/cninfo_c_class_scale_smoke_30_active_summary.md) · [report](../outputs/validation/cninfo_c_class_scale_smoke_30_active_report.csv)
- 30 含退市（对比基线）：[summary](../outputs/validation/cninfo_c_class_scale_smoke_30_summary.md)
- P2-B decision：[cninfo_c_class_p2b_source_decision_table.md](cninfo_c_class_p2b_source_decision_table.md)
- Era C 执行计划：[eraC_execution_plan.md](eraC_execution_plan.md) §7ae · §7af
