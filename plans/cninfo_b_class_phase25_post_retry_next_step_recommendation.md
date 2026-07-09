# CNINFO B 类 Phase 2.5 — Post-Retry Next Step Recommendation

_生成时间：2026-07-09_

> **性质：** Phase 2.5 failed retry closure 后路线建议；**离线 only** · **无 live** · **不是 verified**

**当前状态：**

```text
b_class_phase25_failed_retry_closure_gate = PASS_WITH_CAVEAT
b_class_phase25_failed_retry_execution_gate = PASS_WITH_CAVEAT
b_class_phase25_expansion_closure_gate = PASS_WITH_CAVEAT
b_class_phase25_expansion_execution_gate = PASS_WITH_CAVEAT
```

**Effective coverage：** **50/50**（45 original + 5 retry recovered）· CNINFO total **103** · PDF **0**

---

## Options

### Option A — Create B-class Phase 2.5 commit boundary

**内容：**

- 将 Phase 1 tiny live → Phase 2 → Phase 2.5 expansion + failed retry + closure 产物纳入 **git commit boundary**
- 冻结 **50/50 effective** 为 B-class metadata expansion 里程碑
- 包含 merged effective result CSV 与 closure 文档

**优点：** 清晰版本节点；审阅完整 B-class track  
**风险：** 低  
**CNINFO：** 0（commit only）

---

### Option B — Prepare B-class Phase 3 100-company planning package

**内容：**

- 离线 universe design + bucket 扩展至 100 家
- **仅规划** — 不 live · 不 runner 执行
- 前置条件：Option A commit boundary 完成

**优点：** 为更大样本积累设计基础  
**风险：** 中（若跳过 commit 则证据链不完整）  
**CNINFO：** 0

---

### Option C — Prepare A/B lineage integration design

**内容：**

- 离线设计 B-class announcement metadata 与 A-class report metadata 的 lineage 对齐
- 字段映射 · 交叉引用 · 质量策略 · **无 live**

**优点：** 为跨类数据产品打基础  
**风险：** 低（设计 only）  
**CNINFO：** 0

---

### Option D — Add title/date matching hardening before Phase 3

**内容：**

- 强化 periodic_report 标题匹配规则
- general_announcement 选取策略优化
- 离线 fixture + benchmark 扩展

**优点：** 降低扩大样本后的 `needs_review` 与误匹配  
**风险：** 低  
**CNINFO：** 0

---

## Recommendation

### 推荐顺序

1. **Option A first** — 创建 **B-class Phase 2.5 commit boundary**（**推荐优先**）
2. **Then Option B or C** — 视并行优先级：
   - 若需更多 B-class 证据 → **Option B**（100 家规划 only，**不立即 live**）
   - 若需跨类整合 → **Option C**（lineage integration design）
3. **Option D** 可与 B/C 并行作为质量加固 track

### 明确不推荐

- **立即 100-company live expansion**
- 在未 commit Phase 2.5 boundary 前启动新一轮 live
- 任何 `verified` / `production_ready` 声明

---

## Red Lines（所有选项）

- No CNINFO until explicit approval per option
- No PDF download · No PDF parse · No OCR · No extraction
- No DB · No MinIO · No RAG
- No verified · No production_ready · No testing_stable_sample upgrade
- No rerun of 45 successful cases

---

## Related

| 文档 | 路径 |
|------|------|
| retry closure review | [cninfo_b_class_phase25_failed_retry_closure_review.md](cninfo_b_class_phase25_failed_retry_closure_review.md) |
| closure summary | [cninfo_b_class_phase25_failed_retry_closure_summary.md](../outputs/validation/cninfo_b_class_phase25_failed_retry_closure_summary.md) |
| merged effective result | [cninfo_b_class_phase25_effective_merged_result.csv](../outputs/validation/cninfo_b_class_phase25_effective_merged_result.csv) |
