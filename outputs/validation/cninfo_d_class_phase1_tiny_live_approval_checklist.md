# CNINFO D 类 Phase 1 Tiny Live Metadata Validation — 批准检查清单

_生成时间：2026-07-09_

> **性质：** 未来 tiny live metadata 执行前的批准包；**本轮不执行 live** · **NOT APPROVED**。  
> **前置 offline：** [freeze v1 implementation summary](cninfo_d_class_phase1_freeze_v1_implementation_summary.md) · [ready-case benchmark summary](cninfo_d_class_phase1_ready_case_benchmark_summary.md)（**7/7 PASS**）  
> **质量口径：** [cninfo_d_class_event_quality_policy.md](../../plans/cninfo_d_class_event_quality_policy.md)

---

## Preconditions

以下项须 **PASS / 已审阅** 后方可申请 live execution：

| # | 条件 | 要求 | 当前状态 |
|---|------|------|----------|
| 1 | freeze v1 implementation | `d_class_phase1_freeze_v1_implementation_gate = PASS_OFFLINE` | **PASS_OFFLINE** |
| 2 | ready-case benchmark | `d_class_ready_case_benchmark_gate = READY_FOR_REVIEW` · DC001–DC007 **7/7 PASS** | **PASS（离线）** |
| 3 | quality policy reviewed | retrieval / quality / lineage / empty_but_valid / needs_review 口径已冻结 | **已审阅（离线）** |
| 4 | output isolation | 产物仅写入 `outputs/validation/cninfo_d_class_tiny_live_validation/` | **已定义** |
| 5 | explicit user approval | 用户显式批准 tiny live metadata（见 [approval summary](cninfo_d_class_phase1_tiny_live_approval_summary.md)） | **待批准** |

### 额外并行安全（执行前再确认）

- [ ] C-class Phase 3 live harvest **未在并发运行**
- [ ] `outputs/harvest/cninfo_c_class/` **未被读写**（含 phase3 输出根）
- [ ] C-class status 保持 **`SNAPSHOT_GENERATED_QA_REVIEW`**
- [ ] A-class / B-class 输出 **未触碰**
- [ ] 用户已显式批准 `--approve-d-class-tiny-live-validation`

---

## Live Scope

### Only（允许）

**Metadata / event availability validation only** — 验证 CNINFO 固定表 API 对 tiny universe 的可用性与映射口径：

| 维度 | 验证内容 |
|------|----------|
| `retrieval_status` | `found` · `empty_but_valid` · `http_error` 等检索层结果 |
| `quality_status` | `pass` · `caveat` · `needs_review` · `blocked`（**不写 verified**） |
| `lineage_status` | `discovered` · `needs_review`（Phase 1 默认 discovered） |
| `empty_but_valid` | 合法空态（无大宗交易 · 无质押等）不得标为 `failed` |
| `needs_review` | 映射歧义 / 单位不确定时降级，不 forced pass |
| `component mapping` | 7 组件 payload ↔ registry source_id ↔ endpoint 对齐 |

### In-scope components / sources（Phase 1 · 7 源）

| source_id | 组件 | registry endpoint |
|-----------|------|-------------------|
| margin_trading | 融资融券 | `data20/marginTrading/detailList` |
| block_trade | 大宗交易 | `data20/ints/statistics` |
| restricted_shares_unlock | 限售解禁 | `data20/liftBan/detail` |
| disclosure_schedule | 预约披露 | `new/information/getPrbookInfo` |
| equity_pledge | 股权质押 | `data20/equityPledge/list` |
| shareholder_change | 股东增减持 | `data20/shareholeder/detail` |
| executive_shareholding | 高管持股 | `data20/leader/detail` |

### Exclude（禁止）

- DB write
- MinIO write
- RAG / embeddings / vector index
- PDF download / parse / OCR
- harvest 写入 `outputs/harvest/`
- production claim
- verified claim
- `testing_stable_sample` 升级
- production registry 状态更新
- C-class / A-class / B-class 输出修改
- BSE legacy universe
- 扩大样本超出 tiny universe（**7** cases max）

---

## Tiny Universe 检查

- [ ] [tiny universe CSV](cninfo_d_class_phase1_tiny_live_universe.csv) 已审阅（**7** 家 · 每组件 1 case · 全 `low` risk）
- [ ] 无退市 / ST / *ST / manual review identity
- [ ] 无 BSE legacy 代码（非 920xxx）
- [ ] 含至少 **1** 个 `empty_but_valid` 预期 case（DLC002 · DLC005）
- [ ] 含至少 **1** 个 `captured_normal` 预期 case（DLC001 · DLC003 · DLC004 · DLC006）
- [ ] 含 **1** 个 `needs_review_candidate`（DLC007 · 安全候选）
- [ ] 尚未创建 universe YAML（未来回合）

---

## 执行前技术检查

- [ ] [command draft](../../plans/cninfo_d_class_phase1_tiny_live_command_draft.md) 已审阅
- [ ] `--approve-d-class-tiny-live-validation` 批准 flag 已实现（**未来回合**）
- [ ] `--output-root outputs/validation/cninfo_d_class_tiny_live_validation/` 隔离已确认
- [ ] rate limit：`sleep_seconds >= 0.6` · 并发 = 1
- [ ] resume：读/写 isolation root 内 `run_status.csv`
- [ ] failure handling：HTTP 429 / network_error → 停止并记录，无 retry storm

---

## Post-run 检查（未来 live 回合）

- [ ] `live_report.csv` + `live_summary.md` 写入 isolation root only
- [ ] 无 harvest 产物 · 无 PDF 文件
- [ ] endpoint / registry `live_validation_status` 仅在报告中记录（**不**改 production registry）
- [ ] gate **仍不是** PASS / verified / live_ready
- [ ] C-class / A-class / B-class 输出未被触碰

---

## Gate Reference

```text
d_class_phase1_tiny_live_validation_gate = READY_FOR_APPROVAL
```

**不设为 PASS** · **不是 verified** · **不是 live_ready** — tiny live metadata validation **未执行**。

---

## Red Lines

- No CNINFO in this approval-preparation round
- No live execution in this round
- No harvest · No market data ingestion beyond tiny metadata probe
- No DB · No MinIO · No RAG
- No verified · No testing_stable_sample upgrade
- No C-class / A-class / B-class output touch
- No commit in this round
