# CNINFO C 类 — Fuller-Market Slice1 Partial7 证据完备性报告

_生成时间：2026-07-14 · offline only · CNINFO=0_

> **offline only** · **no live** · **no snapshot rebuild** · **no harvest mutation** · **no commit/push** · **approved_for_snapshot_rebuild=false（保持不变）**

---

## 任务范围

对 slice1 universe 200 中 **7 家 partial** 公司（CE1E002/003/034/061/067/070/071）做离线证据完备性评估：基于既有 QA closure CSV/MD 与磁盘 raw/normalized 只读核验，不修改 harvest 产物，不触发 live/CNINFO，不翻转 snapshot 审批。

---

## 来源证据（只读）

| 文件 | 用途 |
|------|------|
| `cninfo_c_class_erad_fuller_market_slice1_qa_closure_caveat_ledger.csv` | partial 明细、caveat 分类、disposition |
| `cninfo_c_class_erad_fuller_market_slice1_qa_closure_metrics.csv` | universe/complete/partial 计数、gate |
| `cninfo_c_class_erad_fuller_market_slice1_qa_closure_summary.md` | QA closure 闭合结论 |
| `cninfo_c_class_erad_fuller_market_slice1_status_ledger_reconcile.csv` | 旧→新 ledger 对账（7 家均为 preserved/partial） |
| `cninfo_c_class_erad_fuller_market_slice1_universe_draft.csv` | case_id ↔ company_code 映射 |
| `cninfo_c_class_erad_fuller_market_slice1_overlap_recheck.csv` | overlap/hold/BSE/ST 预检（7 家全 pass） |
| `cninfo_c_class_erad_fuller_market_slice1_qa_closure_audit/reports/c_class_erad_harvest_resume_audit_report.csv` | resume-audit 行级 partial 判定 |
| `outputs/harvest/cninfo_c_class/fuller_market_slice1_200/raw/` | HTTP retrieval_status 磁盘证据 |
| `outputs/harvest/cninfo_c_class/fuller_market_slice1_200/normalized/` | normalized 存在性计数 |

---

## 汇总

| 指标 | 值 |
|------|-----|
| universe | 200 |
| complete | 193 |
| **partial（本报告）** | **7** |
| missing | 0 |
| partial 共性 | 4/10 normalized；raw 7 源中 6×`http_error`/500、1×`endpoint_found`/200 |
| caveat_class | `delisted_or_merged_partial_normalized` |
| disposition | `accept_with_caveat`（全部 7 家） |
| QA gate | `PASS_WITH_CAVEAT` |
| snapshot | **blocked**（`approved_for_snapshot_rebuild=false`） |
| CNINFO 调用 | **0** |

**确认 partial7 case_id：** CE1E002, CE1E003, CE1E034, CE1E061, CE1E067, CE1E070, CE1E071

---

## 分类规则（引用 closure）

- normalized sources ≥ 10 → complete
- 1–9 → partial
- 0 → missing

7 家均为 **4/10 partial**；缺失 6 个 normalized 源与 raw `http_error` 一一对应。

---

## 逐案证据缺口

### CE1E002 · 600001 · 邯郸钢铁

| 维度 | 证据 |
|------|------|
| harvest_status | partial（4/10） |
| normalized 已有 | business_scope, contact_profile, industry_profile, security_observe |
| normalized 缺失 | company_basic_profile, dividend_history, executive_profile, share_capital_profile, top_float_shareholders_profile, top_shareholders_profile |
| raw HTTP | 6 源 `http_error` http_status=500 business_code=9240002；security_observe `endpoint_found` http_status=200 |
| security_observe | delisted=true |
| ledger 对账 | before=partial → after=partial，action=preserved |
| overlap 预检 | 全 pass |
| 证据缺口 | 缺 6 个 HTTP 驱动 normalized 产物；缺 raw 成功 payload 以支撑 basic/executive/shareholder/dividend 规范化；缺「退市/合并」结构化旁证字段（仅 security_observe 单行） |
| 离线可补强 | 打包 raw 500 响应 + security_observe delisted 标记 + case_id 映射 + caveat disposition 引用 |
| 需 snapshot | 否（snapshot 仍 blocked；且缺源非 snapshot 可补） |
| 需 live | 理论上可重试 6 HTTP 源，但 caveat 注明 not re-live recommended；退市标的 CNINFO 500 属预期 |

### CE1E003 · 600005 · 武钢股份

与 CE1E002 模式一致：4/10 partial；6×http_error/500 + security_observe endpoint_found；delisted=true；disposition accept_with_caveat。

证据缺口：同上（6 normalized + raw success payload + 合并退市旁证）。

### CE1E034 · 600068 · 葛洲坝

与 CE1E002 模式一致：4/10 partial；6×http_error/500 + security_observe endpoint_found；delisted=true；board=sse_main。

证据缺口：同上。

### CE1E061 · 000003 · PT金田A

与 CE1E002 模式一致：4/10 partial；6×http_error/500 + security_observe endpoint_found；delisted=true；tradingStatus=0（PT）。

证据缺口：同上；额外缺 PT/终止上市状态的 QA 旁证链（仅 security_observe 字段）。

### CE1E067 · 000015 · PT中浩A

与 CE1E061 模式一致：PT 标的；delisted=true；tradingStatus=0。

证据缺口：同上。

### CE1E070 · 000022 · 深赤湾A

与 CE1E002 模式一致：4/10 partial；delisted=true；board=szse_main。

证据缺口：同上（合并重组类退市标的）。

### CE1E071 · 000024 · 招商地产

与 CE1E002 模式一致：4/10 partial；delisted=true；board=szse_main。

证据缺口：同上。

---

## 共性证据缺口（QA 视角）

### 已有（可闭合）

1. **case_id ↔ company_code ↔ company_name** 在 universe_draft、caveat_ledger、reconcile、audit 中一致。
2. **harvest_status=partial** 在 rebuilt status ledger、caveat_ledger、resume-audit 三处一致。
3. **normalized 4/10 计数** 与磁盘文件存在性一致。
4. **raw retrieval_status** 可离线复算：6 failed + 1 success（security_observe）。
5. **overlap/hold/BSE/ST 预检** 7 家均为 pass（非 universe 准入问题）。
6. **disposition=accept_with_caveat** 已在 caveat_ledger 记录。

### 缺失（证据/QA 视角）

| 缺口类型 | 说明 | 严重度 |
|----------|------|--------|
| normalized 6 源缺失 | 无 company_basic/executive/share_capital/shareholder/dividend normalized 文件 | 高（定义性 partial） |
| raw success payload 缺失 | 6 HTTP 源仅保留 error envelope（500/9240002），无业务记录 | 高 |
| 退市原因结构化旁证 | 仅 security_observe.delisted=true；缺合并对手方、终止上市日期等 | 中 |
| per-source QA 行级 manifest | caveat_ledger 为 case 级；缺独立 per-source evidence CSV（本任务 offline_qa_matrix 部分填补） |
| snapshot eligibility 证据 | 7 家不可进入 complete 集合；snapshot 审批仍为 false | 信息性（非缺口，为 gate） |

---

## 离线可立即补强 vs 需 snapshot/live

### 离线可立即补强（本任务交付范围）

| 动作 | 产出 | 不依赖 |
|------|------|--------|
| 生成 partial7 offline QA matrix | `cninfo_c_class_partial7_offline_qa_matrix_20260714.csv` | live / snapshot |
| 本 evidence completeness 报告 | 逐案缺口 + gate 声明 | live / snapshot |
| 引用既有 audit source_ledger 行 | 70 行（7×10 源）已在 closure_audit 存在 | 无需重跑 |
| 显式标注 delisted/http_error 模式 | 自 raw 磁盘只读提取 | live |
| 保持 accept_with_caveat disposition | 不升级为 complete / PASS | snapshot |

### 需 snapshot（仍 blocked）

| 动作 | 为何需 snapshot 或不可做 |
|------|--------------------------|
| snapshot candidate 纳入 | `approved_for_snapshot_rebuild=false`；7 家 partial 不符合 complete 门槛 |
| 下游 production bundle | snapshot 未批准；partial 数据不得冒充 complete |
| 跨源 lineage 快照固化 | 需 Controller 另批 snapshot rebuild |

**本任务明确：snapshot 保持 blocked，不生成 snapshot 产物。**

### 需 live（不建议）

| 动作 | 说明 |
|------|------|
| 重试 6×HTTP 源 | 需 CNINFO live；caveat_ledger 注明 not re-live recommended |
| 补齐 6 normalized 源 | 依赖 raw 成功检索；退市/合并标的预期持续 500 |
| resume-audit 建议 | audit report 标 `deferred_targeted_live_after_approval`；无 Controller live 批准时不得执行 |

---

## Gate 状态（不变）

```
c_class_erad_fuller_market_slice1_qa_closure_gate = PASS_WITH_CAVEAT
approved_for_snapshot_rebuild = false  （未翻转）
```

- **NOT verified**
- **NOT production_ready**
- **NOT bare PASS**
- harvest success ≠ snapshot readiness

---

## 伴生 caveat（非 partial7，仅交叉引用）

closure 另列 3 家 complete + needs_review（CE1E176/188/193，empty_but_valid dividend）。**不在本 partial7 报告逐案范围**，但计入同一 `PASS_WITH_CAVEAT` gate。

---

## 产出文件

| 文件 | 说明 |
|------|------|
| `cninfo_c_class_partial7_evidence_completeness_20260714.md` | 本报告 |
| `cninfo_c_class_partial7_offline_qa_matrix_20260714.csv` | 7 行 QA 矩阵 |

---

## 保护根（未触碰）

- `outputs/harvest/cninfo_c_class/fuller_market_slice1_200/` 生产文件：**只读，未修改**
- `outputs/snapshot/`：**未创建/未修改**
- 863 primary / phase3 / phase35：**未触碰**
- A/B/D tracks：**未触碰**

---

## Controller 后续

1. Evidence Auditor 核验本包与 closure 包一致性。
2. 若需提升 complete 率，需 Controller 单独裁决是否对退市/合并子集做 **live retry**（当前建议：否）。
3. snapshot rebuild 需另批；本任务不推进。
