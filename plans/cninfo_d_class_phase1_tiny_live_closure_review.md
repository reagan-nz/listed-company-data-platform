# CNINFO D 类 Phase 1 Tiny Live Validation — Closure Review

_生成时间：2026-07-09_

> **性质：** 离线收口评审；**无 CNINFO** · **无 live** · **无 rerun** · **不是 verified** · **不是 production_ready**

---

## 1. Objective

在已执行的 D-class Phase 1 tiny live metadata validation（DLC001–DLC007）基础上，完成离线收口评审：

- 确认 7 组件 endpoint 可用性与质量口径
- 区分 **acceptable** vs **expectation mismatch**（非 schema failure）
- 冻结 execution / closure gate 为 `PASS_WITH_CAVEAT`
- 为 universe 预期校准留下决策记录

**不修改** execution report 原始行 · **不重跑** probe · **不升级** testing_stable_sample。

---

## 2. Execution Scope

| 项 | 内容 |
|----|------|
| universe | DLC001–DLC007（**7** 家 · 每组件 1 case） |
| schema | `d_class_phase1_freeze_v1` · market_event + 7 组件 |
| 允许 | metadata / event availability · retrieval_status · quality_status · lineage_status |
| 禁止 | harvest · DB/MinIO/RAG · verified · production_ready · PDF |
| 批准 flag | `--approve-d-class-tiny-live-validation`（已使用） |
| 输出隔离 | `outputs/validation/cninfo_d_class_tiny_live_validation/` |

**输入产物：**

- [d_class_tiny_live_report.csv](../outputs/validation/cninfo_d_class_tiny_live_validation/reports/d_class_tiny_live_report.csv)
- [d_class_tiny_live_summary.md](../outputs/validation/cninfo_d_class_tiny_live_validation/reports/d_class_tiny_live_summary.md)
- [d_class_tiny_live_quality_report.csv](../outputs/validation/cninfo_d_class_tiny_live_validation/reports/d_class_tiny_live_quality_report.csv)
- [cninfo_d_class_phase1_tiny_live_universe.csv](../outputs/validation/cninfo_d_class_phase1_tiny_live_universe.csv)
- [cninfo_d_class_event_quality_policy.md](cninfo_d_class_event_quality_policy.md)

---

## 3. Component Coverage

| source_id | case | company | endpoint | probe result |
|-----------|------|---------|----------|--------------|
| margin_trading | DLC001 | 000895 | detailList | found · 1 row |
| block_trade | DLC002 | 601988 | ints/statistics | empty_but_valid |
| restricted_shares_unlock | DLC003 | 300009 | liftBan/detail | empty · 8 date probes |
| disclosure_schedule | DLC004 | 600000 | getPrbookInfo | found · 1 row |
| equity_pledge | DLC005 | 688981 | equityPledge/list | empty_but_valid |
| shareholder_change | DLC006 | 000550 | shareholeder/detail | empty · 5 mode probes |
| executive_shareholding | DLC007 | 002415 | leader/detail | found · 2 rows · needs_review |

**components_covered = 7 / 7**

---

## 4. Request and Case Counts

| 指标 | 值 |
|------|-----|
| CNINFO requests（execution） | **18** |
| CNINFO requests（closure 回合） | **0** |
| input_cases | **7** |
| acceptable_cases | **5** |
| failed_expectation_cases | **2** |
| empty_but_valid（observed） | **4** |
| needs_review（observed） | **1** |
| DB write | **0** |
| MinIO write | **0** |
| RAG run | **0** |

---

## 5. DLC001–DLC007 Results（Final · 自 execution report）

| case | expected | retrieval | quality | lineage | records | acceptable |
|------|----------|-----------|---------|---------|---------|------------|
| DLC001 | captured_normal | found | pass | discovered | 1 | **yes** |
| DLC002 | empty_but_valid | empty_but_valid | pass | discovered | 0 | **yes** |
| DLC003 | captured_normal | empty_but_valid | pass | discovered | 0 | **no** |
| DLC004 | captured_normal | found | pass | discovered | 1 | **yes** |
| DLC005 | empty_but_valid | empty_but_valid | pass | discovered | 0 | **yes** |
| DLC006 | captured_normal | empty_but_valid | pass | discovered | 0 | **no** |
| DLC007 | needs_review_candidate | found | needs_review | needs_review | 2 | **yes** |

---

## 6. empty_but_valid Behavior

| case | 预期 | 观测 | 结论 |
|------|------|------|------|
| DLC002 | empty_but_valid | 0 rows · pass | **符合预期** |
| DLC005 | empty_but_valid | 0 rows · pass | **符合预期** |
| DLC003 | captured_normal | 0 rows · pass · 合法空态 | **API 语义正确 · 预期不符** |
| DLC006 | captured_normal | 0 rows · pass · 合法空态 | **API 语义正确 · 预期不符** |

**质量口径确认：** 公司级零行 + HTTP 200 → `retrieval_status=empty_but_valid` · `quality_status=pass`（见 quality policy §4）。

---

## 7. needs_review Behavior

| case | 预期 | 观测 | 结论 |
|------|------|------|------|
| DLC007 | needs_review_candidate | 2 rows · needs_review · position/amount medium confidence | **符合预期** |

**质量口径确认：** 映射歧义不 forced pass → `quality_status=needs_review` · `lineage_status=needs_review`（见 quality policy §5）。

---

## 8. DLC003 Analysis

**组件：** restricted_shares_unlock · **公司：** 300009 安科生物

| 项 | 内容 |
|----|------|
| 预期 | `captured_normal` |
| 探测 | `liftBan/detail` · **8** 个 tdate 参数 |
| 结果 | 各日期 API 有响应，但公司级过滤后 **0** 行 |
| retrieval | `empty_but_valid` |
| quality | `pass` |

**结论：** 非 endpoint 失败 · 非 schema 映射失败 · **universe 预期与探针窗口不匹配**（所选公司在探测日期内无解禁事件）。

详见 [expectation calibration note](cninfo_d_class_phase1_expectation_calibration_note.md)。

---

## 9. DLC006 Analysis

**组件：** shareholder_change · **公司：** 000550 江铃汽车

| 项 | 内容 |
|----|------|
| 预期 | `captured_normal` |
| 探测 | `type=desc` · `type=inc` + 多 tdate · 共 **5** 组参数 |
| 结果 | API 有全市场行，但公司级过滤后 **0** 行 |
| retrieval | `empty_but_valid` |
| quality | `pass` |

**结论：** 非 endpoint 失败 · 非 schema 映射失败 · **universe 预期与探针窗口/模式不匹配**（所选公司在探测窗口内无增减持事件）。

详见 [expectation calibration note](cninfo_d_class_phase1_expectation_calibration_note.md)。

---

## 10. Quality Policy Impact

| policy 维度 | tiny live 验证 |
|-------------|----------------|
| retrieval_status | found / empty_but_valid 均出现 · 无 http_error 阻断 |
| quality_status | pass（5 cases）· needs_review（1 case）· 无 verified |
| lineage_status | discovered / needs_review · 无 linked |
| empty_but_valid | DLC002/005 预期命中 · DLC003/006 合法空态但预期不符 |
| needs_review | DLC007 命中 |

**schema / field catalog / registry：** **无变更需求**（失败为 universe 预期问题，非 contract 缺陷）。

---

## 11. Universe Expectation Calibration

| case | 问题 | 推荐处理 |
|------|------|----------|
| DLC003 | captured_normal vs 观测 empty | 见 calibration note · 选项 A/B/C · **暂不视为 schema failure** |
| DLC006 | captured_normal vs 观测 empty | 见 calibration note · 选项 A/B/C · **暂不视为 schema failure** |

**收口决定：** 保留 execution report 原样；closure 仅文档化决策选项，**本回合不修改 universe CSV**。

---

## 12. Output Isolation

| 项 | 状态 |
|----|------|
| 输出根 | `outputs/validation/cninfo_d_class_tiny_live_validation/` only |
| harvest 产物 | **未写入** |
| C-class harvest | **未触碰** |
| A/B-class 输出 | **未触碰** |
| execution report | **未修改**（closure 只读） |

---

## 13. Non-production Claim

| 声明 | 值 |
|------|-----|
| verified | **false** |
| production_ready | **false** |
| testing_stable_sample upgrade | **未执行** |
| d_class_tiny_live_execution_gate | **PASS_WITH_CAVEAT**（保持） |
| d_class_phase1_tiny_live_closure_gate | **PASS_WITH_CAVEAT** |

**不是 PASS** · **不是 live_ready** · tiny sample only。

---

## 14. Gates

```text
d_class_tiny_live_execution_gate = PASS_WITH_CAVEAT
d_class_phase1_tiny_live_closure_gate = PASS_WITH_CAVEAT
```

---

## 15. Red Lines（closure 回合）

- No CNINFO · No live · No rerun · No harvest
- No DB · No MinIO · No RAG
- No verified · No production_ready · No testing_stable_sample upgrade
- No modification of execution report rows
- No A/B/C output touch
