# CNINFO C 类 — Fuller-Market Slice1 Empty-Dividend 证据完备性报告

_生成时间：2026-07-14 · offline only · CNINFO=0_

> **offline only** · **no live** · **no snapshot rebuild** · **no harvest mutation** · **no commit/push** · **approved_for_snapshot_rebuild=false（保持不变）**

---

## 任务范围

对 slice1 universe 200 中 **3 家 empty-but-valid dividend** caveat 公司（CE1E176/188/193）做离线证据完备性评估：基于既有 QA closure CSV/MD 与磁盘 raw/normalized 只读核验，不修改 harvest 产物，不触发 live/CNINFO，不翻转 snapshot 审批。

**不在本任务范围：** partial7 包（CE1E002/003/034/061/067/070/071）已于 `cninfo_c_class_partial7_evidence_completeness_20260714.md` 完成，本任务不重复。

---

## 来源证据（只读）

| 文件 | 用途 |
|------|------|
| `cninfo_c_class_erad_fuller_market_slice1_qa_closure_caveat_ledger.csv` | empty dividend 明细、caveat 分类、disposition |
| `cninfo_c_class_erad_fuller_market_slice1_qa_closure_metrics.csv` | universe/complete/partial 计数、gate、needs_review 计数 |
| `cninfo_c_class_erad_fuller_market_slice1_qa_closure_summary.md` | QA closure 闭合结论 |
| `cninfo_c_class_erad_fuller_market_slice1_status_ledger_reconcile.csv` | 旧→新 ledger 对账（3 家 appended_from_disk / complete） |
| `cninfo_c_class_erad_fuller_market_slice1_universe_draft.csv` | case_id ↔ company_code 映射 |
| `cninfo_c_class_erad_fuller_market_slice1_qa_closure_audit/reports/c_class_erad_harvest_resume_audit_report.csv` | resume-audit 行级 needs_review 判定 |
| `cninfo_c_class_erad_fuller_market_slice1_qa_closure_audit/reports/c_class_erad_harvest_resume_audit_source_ledger.csv` | per-source present/missing 行级证据 |
| `outputs/harvest/cninfo_c_class/fuller_market_slice1_200/raw/dividend_history/` | raw `valid_empty` 磁盘证据 |
| `outputs/harvest/cninfo_c_class/fuller_market_slice1_200/normalized/dividend_history/` | 0 字节 normalized 磁盘证据 |
| `outputs/harvest/cninfo_c_class/fuller_market_slice1_200/quality/company_harvest_status.csv` | rebuilt ledger complete 行 |

---

## 汇总

| 指标 | 值 |
|------|-----|
| universe | 200 |
| complete（ledger） | 193 |
| partial | 7（另包，非本任务） |
| **empty-dividend caveat（本报告）** | **3** |
| caveat_class | `empty_but_valid_dividend_normalized_zero_byte` |
| disposition | `accept_with_caveat`（全部 3 家） |
| ledger harvest_status | **complete**（10/10 normalized 源目录存在） |
| resume-audit state | **needs_review**（3 家） |
| QA gate | `PASS_WITH_CAVEAT` |
| snapshot | **blocked**（`approved_for_snapshot_rebuild=false`） |
| CNINFO 调用 | **0** |

**确认 empty-dividend case_id：** CE1E176, CE1E188, CE1E193

---

## 分类规则（引用 closure）

### Status-ledger 规则

- normalized sources ≥ 10 → complete
- 1–9 → partial
- 0 → missing

**注：** 文件存在（含 0 字节 `dividend_history.jsonl`）计入 sources_present，与 harvest runner「HTTP 无 fail → complete」一致。

### Resume-audit 补充规则

offline resume-audit 对 0 字节 dividend normalized 另标 `needs_review`（`status_csv_complete_but_source_gap`），与 ledger complete 形成质量层 caveat，不翻转 harvest_status。

---

## 逐案证据缺口

### CE1E176 · 688031 · 星环科技

| 维度 | 证据 |
|------|------|
| harvest_status（ledger） | complete（10/10） |
| resume-audit | needs_review |
| normalized dividend | `dividend_history/688031.jsonl` **size=0** |
| raw dividend | `retrieval_status=valid_empty` · `http_status=200` · `raw_records=[]` |
| 其他 9 源 | 全部 present（basic/executive/shareholder/contact 等） |
| security_observe | `delisted=false` · STAR 板活跃标的 |
| ledger 对账 | appended_from_disk → complete |
| audit source_ledger | `cninfo_dividend_financing_profile` → **no/missing**（audit 按非空内容判定） |
| caveat_ledger notes | ledger complete；resume-audit needs_review；no re-live |
| 证据缺口 | audit 与 ledger 对 dividend 语义不一致（零字节文件 vs missing）；缺「无分红历史」结构化 QA 旁证（仅 raw valid_empty）；缺 per-source 质量 manifest 独立于 case 级 caveat_ledger |
| 离线可补强 | 打包 raw valid_empty JSON + 零字节 normalized 路径 + audit/ledger 交叉引用 |
| 需 snapshot | 否 |
| 需 live | 否（caveat 注明 no re-live；valid_empty 为 CNINFO 合法空响应） |

### CE1E188 · 688062 · 迈威生物

与 CE1E176 模式一致：ledger complete 10/10；raw dividend `valid_empty` http 200；normalized 0 字节；resume-audit needs_review；STAR 板 `delisted=false`。

证据缺口：同上（audit missing vs zero-byte present；缺无分红历史 QA 旁证链）。

### CE1E193 · 688071 · 华依科技

与 CE1E176 模式一致：ledger complete 10/10；raw dividend `valid_empty` http 200；normalized 0 字节；resume-audit needs_review；STAR 板 `delisted=false`。

证据缺口：同上。

---

## 共性证据缺口（QA 视角）

### 已有（可闭合）

1. **case_id ↔ company_code ↔ company_name** 在 universe_draft、caveat_ledger、reconcile、audit 中一致。
2. **ledger harvest_status=complete** 在 rebuilt status ledger、caveat_ledger 一致（10/10）。
3. **raw dividend valid_empty** 可离线复算：3 家均为 http 200 + empty raw_records。
4. **normalized 0 字节文件存在** 与磁盘 `ls` 一致。
5. **resume-audit needs_review** 在 audit report 三处一致。
6. **disposition=accept_with_caveat** 已在 caveat_ledger 记录。
7. **非退市标的**：security_observe delisted=false，与 partial7 退市模式可区分。

### 缺失（证据/QA 视角）

| 缺口类型 | 说明 | 严重度 |
|----------|------|--------|
| audit vs ledger 语义分歧 | audit 标 dividend missing；ledger 计 sources_present（零字节） | 中（已文档化为 caveat） |
| 无分红历史 QA 旁证 | raw valid_empty 已证；缺独立「confirmed_no_dividend_history」质量字段 | 低 |
| per-source QA manifest | caveat_ledger 为 case 级；本任务 offline_matrix 部分填补 | 低 |
| snapshot eligibility | 3 家 ledger complete 但 audit needs_review；snapshot 审批仍为 false | 信息性（gate，非数据缺口） |

---

## 离线可立即补强 vs 需 snapshot/live

### 离线可立即补强（本任务交付范围）

| 动作 | 产出 | 不依赖 |
|------|------|--------|
| 生成 empty-dividend offline matrix | `cninfo_c_class_empty_dividend_offline_matrix_20260714.csv` | live / snapshot |
| 本 evidence completeness 报告 | 逐案缺口 + gate 声明 | live / snapshot |
| 引用既有 audit source_ledger 行 | 30 行（3×10 源）已在 closure_audit 存在 | 无需重跑 |
| 显式标注 valid_empty/zero-byte 模式 | 自 raw/normalized 磁盘只读提取 | live |
| 保持 accept_with_caveat disposition | 不升级为 bare PASS / verified | snapshot |

### 需 snapshot（仍 blocked）

| 动作 | 为何需 snapshot 或不可做 |
|------|--------------------------|
| snapshot candidate 纳入 | `approved_for_snapshot_rebuild=false`；3 家虽 ledger complete 但 audit needs_review |
| 下游 production bundle | snapshot 未批准；needs_review caveat 须保留 |
| 跨源 lineage 快照固化 | 需 Controller 另批 snapshot rebuild |

**本任务明确：snapshot 保持 blocked，不生成 snapshot 产物。**

### 需 live（不建议）

| 动作 | 说明 |
|------|------|
| 重试 dividend HTTP 源 | 需 CNINFO live；caveat_ledger 注明 no re-live |
| 期望获得非空分红记录 | STAR 新股/未分红标的 CNINFO 返回 valid_empty 属预期 |
| resume-audit 建议 | audit report 标 `offline_review_first`；无 Controller live 批准时不得执行 |

---

## Gate 状态（不变）

```
c_class_erad_fuller_market_slice1_qa_closure_gate = PASS_WITH_CAVEAT
approved_for_snapshot_rebuild = false  （未翻转）
```

- **NOT verified**
- **NOT production_ready**
- **NOT bare PASS**
- harvest complete（ledger）≠ audit needs_review 消除 ≠ snapshot readiness

---

## 与 partial7 的交叉引用

closure 另列 7 家 partial（CE1E002/003/034/061/067/070/071，delisted_or_merged）。**已在 partial7 包逐案处理**，本报告仅覆盖 empty-dividend 3 家。合计 10 caveat case 计入同一 `PASS_WITH_CAVEAT` gate。

---

## 产出文件

| 文件 | 说明 |
|------|------|
| `cninfo_c_class_empty_dividend_evidence_20260714.md` | 本报告 |
| `cninfo_c_class_empty_dividend_offline_matrix_20260714.csv` | 3 行 offline 矩阵 |

---

## 保护根（未触碰）

- `outputs/harvest/cninfo_c_class/fuller_market_slice1_200/` 生产文件：**只读，未修改**
- `outputs/snapshot/`：**未创建/未修改**
- 863 primary / phase3 / phase35：**未触碰**
- A/B/D tracks：**未触碰**
- partial7 证据包：**未重做**

---

## Controller 后续

1. Evidence Auditor 核验本包与 closure 包、partial7 包一致性。
2. 3 家 empty dividend 质量 caveat 已文档化；**不建议** live retry。
3. snapshot rebuild 需另批；`approved_for_snapshot_rebuild=false` 保持不变。
4. 可选后续：统一 audit 对 zero-byte normalized 的 present/missing 语义（runner/audit 对齐，需另批实现任务）。
