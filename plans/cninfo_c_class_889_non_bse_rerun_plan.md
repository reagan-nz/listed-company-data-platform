# CNINFO C-Class 889 Non-BSE Rerun Plan（Era C Phase 4）

_生成时间：2026-07-07_

> **目的：** 在 stable 200 **LIVE_PASS**（新版 runner）基础上，规划 **889 non-BSE** 全候选集重跑。**本轮仅 plan + dry-run/preflight**；**不跑 live**；**非 verified**；**非 testing_stable_sample**。

**前置决策：** [stable 200 live pass decision](cninfo_c_class_stable_200_live_pass_decision.md)

---

## 一、Why Rerun 889

| 背景 | 说明 |
|------|------|
| stable 200 rerun | 新版 runner（backoff + orgId fallback）下 **LIVE_PASS** · 六主源 200/200 |
| 12 家 six-fail | retry **LIVE_PASS**；证明 v1 失败非 sample_quality |
| 889 v1 live | **LIVE_PARTIAL**（旧 runner · 无退避）· pass=4953 fail=270 |
| 扩展验证需求 | 验证 backoff/orgId 在 **889 规模**是否可扩展 |

**为何现在 rerun：**

1. stable 200 已证明 cleaned 样本 + 新 runner 可达 **LIVE_PASS**。
2. 889 是 non-BSE main universe 的 **官方候选母本**（非 full market）。
3. 需用同一 runner 口径重跑，与 v1 结果对比，评估 non-BSE **CONDITIONAL YES** 是否可加强。
4. **不**直接 full market；**不**混入 BSE 920 / BSE legacy / abnormal_review。

---

## 二、Sample Preflight

### 样本来源

| 项 | 值 |
|----|-----|
| **sample source** | `lab/eval_companies_c_class_smoke_1000_non_bse_candidate.yaml` |
| **universe_id** | `non_bse_active` |
| **actual companies** | **889** |
| **parent** | `lab/eval_companies_1000.yaml`（1020）· 离线剔除 131 |

**不复建副本 YAML。** rerun 直接复用上述 candidate；dry-run/live 输出使用 `cninfo_c_class_889_non_bse_rerun_*` 命名区分 v1。

### 已剔除（母本派生时完成）

| 规则 | 剔除数 |
|------|--------|
| board == bse | 106 |
| name 退市 / delisted | 7 |
| name suffix 退 | 15 |
| abnormal_review explicit | 3 |
| **合计 excluded** | **131** |

### Preflight 检查结果（2026-07-07）

| 检查项 | 结果 |
|--------|------|
| company_count | **889** ✓ |
| BSE board | **0** ✓ |
| abnormal_review（600065/600978/000405） | **0** ✓ |
| 退市名称 / suffix 退 | **0** ✓ |
| six_fail_hold 子集 | **不在**单独 hold 文件约束内；889 含 v1 困难公司（含 26 家 six_fail 模式） |
| suspicious duplicate orgid | **000765 + 001267** 同在（共享 `gssz0000765`）· stable 200 已剔 000765 · **889 保留双码并标注 notes** · post-run 监测 |

### Board distribution

| board | count | % |
|-------|-------|---|
| sse_main | 292 | 32.8% |
| szse_main | 239 | 26.9% |
| chinext | 233 | 26.2% |
| star | 125 | 14.1% |
| **合计** | **889** | 100% |

### Planned cases

| 维度 | 数量 |
|------|------|
| companies | **889** |
| sources per company | **7**（6 主判定 + security observe） |
| **total cases** | **6223** |
| main judgment cases | **5334**（889 × 6） |
| security observe cases | **889** |

### Dry-run / preflight 产出

| 产出 | 路径 |
|------|------|
| dry-run report | [cninfo_c_class_889_non_bse_rerun_dryrun_report.csv](../outputs/validation/cninfo_c_class_889_non_bse_rerun_dryrun_report.csv) |
| dry-run summary | [cninfo_c_class_889_non_bse_rerun_dryrun_summary.md](../outputs/validation/cninfo_c_class_889_non_bse_rerun_dryrun_summary.md) |

**Dry-run 结果：** companies=**889** · cases=**6223** · **DRY_RUN_ONLY** · 无 CNINFO 请求。

---

## 三、Runner Safety

新版 `lab/validate_cninfo_c_class_scale_smoke.py`（post-§7ar）已具备：

| 能力 | 配置 |
|------|------|
| live 基础节流 | **0.5s** / 请求（`LIVE_BASE_SLEEP_SECONDS`） |
| 业务码限流识别 | `cninfo_throttled_business_code`（JSON 429/90001 + 限流文案） |
| 退避重试（仅 live） | **2s → 5s → 10s** · 最多 **3** 次 |
| orgId fallback | data20 endpoint · `scode+orgId` 单次 fallback |
| report 字段 | `retry_count` · `first_result_code` · `final_result_code` · `final_retrieval_status` · `used_orgid_variant` |
| 并发 | **无**（串行 per company × source） |

**889 预估耗时（粗算）：** 6223 请求 × (~0.5s sleep + ~2–4s RTT) ≈ **4–6 小时**；含退避可能更长。建议 `nohup` + `caffeinate`。

---

## 四、Live Execution Recommendation

> **本轮不执行。** 待人工批准后运行。

### 推荐命令

```bash
nohup caffeinate python lab/validate_cninfo_c_class_scale_smoke.py --live \
  --sample-file lab/eval_companies_c_class_smoke_1000_non_bse_candidate.yaml \
  --output-csv outputs/validation/cninfo_c_class_889_non_bse_rerun_live_report.csv \
  --output-md outputs/validation/cninfo_c_class_889_non_bse_rerun_live_summary.md \
  > outputs/validation/cninfo_c_class_889_non_bse_rerun_live.log 2>&1 &
```

### Preflight hard gate（live 前建议）

| 项 | 期望 |
|----|------|
| company_count | **889** |
| planned cases | **6223** |
| board | 仅 sse_main / szse_main / chinext / star |
| runner | backoff + orgId patch 已合并 |

---

## 五、Expected Gate（889 rerun 通过标准）

| 指标 | 门槛 |
|------|------|
| blocked | **0** |
| HTTP 429 | **0** 或极低且 backoff 可恢复 |
| 六主源 reachability | 各源 **≥ 95%**（889 尺度） |
| basic | 单独统计 reach / pass / non_empty |
| dividend | 单独统计 · valid_empty 允许 · reach ≥ 95% |
| executive | 单独统计 |
| share_capital | 单独统计 · 保持 source_partial 口径 |
| top_shareholders | 单独统计 |
| top_float | 单独统计 · 保持 source_partial 口径 |
| security observe | **100%** observe 可达（不绑定主 gate） |
| retry_count | 分布可解释 · 无异常高簇 |
| used_orgid_variant | **不应大规模爆炸**（stable 200 为低比例） |
| 新 6/6 fail 簇 | **必须先 debug** · **不清洗** |

**对比 v1：** v1 LIVE_PARTIAL（fail=270）；期望新版显著降低 `schema_unexpected` / 业务码限流假失败。

---

## 六、Post-Run Decisions

889 rerun **完成后**方可决定：

| 决策项 | 条件 |
|--------|------|
| dividend_history YAML backfill | GO（决策）→ 是否进入**执行候选**（命名窄化 `dividend_history`） |
| non-BSE main universe | CONDITIONAL YES → 是否进入 **stronger testing** 证据（仍 **no verified**） |
| full 1000-like rerun | 889 通过后评估是否扩至母本 1020 剔除后全量 |
| BSE 920 | **单独 child universe** 计划 · 不混入 889 |

**889 前不做：** YAML 执行 · DB 入库 · verified · testing_stable_sample 升级。

---

## 七、Caveats

- 889 rerun **仍不是 full market**（1020 母本剔除 131 后候选）。
- **BSE 920**、**BSE 83/87 legacy**、**abnormal_review** **不在本轮**。
- v1 889 live 使用旧 runner；rerun 结果不可与 v1 直接混算 pass 率而不标注 runner 版本。
- **000765/001267** duplicate orgid 对在 889 内共存；需 post-run 监测，非 pre-live 剔除条件。
- source status 仍为 **testing / proceed_testing** 层级。
- **no verified** · **no testing_stable_sample** · **no database ingestion** · **no YAML backfill executed**。

---

## 八、参考

- [stable 200 live pass decision](cninfo_c_class_stable_200_live_pass_decision.md)
- [source status decision](cninfo_c_class_source_status_decision.md)
- [889 v1 diagnosis](../outputs/validation/cninfo_c_class_smoke_1000_non_bse_diagnosis.md)
- [889 v1 live summary](../outputs/validation/cninfo_c_class_smoke_1000_non_bse_live_summary.md)
- `lab/validate_cninfo_c_class_scale_smoke.py`

---

## 九、红线（本轮）

- **不跑 live** · **无 CNINFO 请求**（dry-run only）· **无 YAML** · **无 DB** · **无 verified**
