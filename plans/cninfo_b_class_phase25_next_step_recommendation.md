# CNINFO B 类 Phase 2.5 — Next Step Recommendation

_生成时间：2026-07-09_

> **性质：** Phase 2.5 closure 后路线建议；**离线 only** · **无 live** · **不是 verified**

**当前状态：**

```text
b_class_phase25_expansion_closure_gate = PASS_WITH_CAVEAT
b_class_phase25_expansion_execution_gate = PASS_WITH_CAVEAT
b_class_phase2_expansion_closure_gate = PASS_WITH_CAVEAT
b_class_phase1_tiny_live_closure_gate = PASS_WITH_CAVEAT
```

Phase 2.5：**45/50** acceptable · **5** network_error · CNINFO **93** · PDF **0**

---

## Options

### Option A — Commit B-class Phase 2.5 closure boundary after closure

**内容：**

- 将 Phase 2.5 planning + runner + live execution + closure 产物纳入 **git commit boundary**
- 冻结 50 家 Phase 2.5 为 B-class metadata expansion 里程碑
- 不在本阶段继续 live 扩大

**优点：** 清晰版本节点；便于审阅与并行 A/C/D 工作  
**风险：** 低  
**CNINFO：** 0（commit only）

---

### Option B — Prepare isolated retry package for 5 failed cases

**内容：**

- 基于 [failed-case triage](../outputs/validation/cninfo_b_class_phase25_failed_case_triage.csv) 创建 5-case retry universe
- 扩展 runner 支持 `--approve-b-class-phase25-failed-retry`
- 输出隔离至 `outputs/validation/cninfo_b_class_phase25_failed_retry/`
- **不** rerun 45 例成功 case
- dry-run + approval package → 人工批准后方可 live

**优点：** 以最小 CNINFO 成本补齐 5 例缺口；延续 Phase 1 TLC002 isolated retry 纪律  
**风险：** 低–中（5 case only）  
**CNINFO：** 0 until explicit approval

---

### Option C — Prepare 100-company planning only after retry decision

**内容：**

- 离线 universe design + bucket 扩展至 100 家
- **仅规划** — 不 live · 不 runner 执行
- 前置条件：Option B retry 决策完成（接受-with-caveat 或 retry 后 50/50）

**优点：** 为更大样本积累设计基础  
**风险：** 中（若跳过 retry 决策则证据不足）  
**CNINFO：** 0

---

### Option D — Prepare B/A lineage integration design

**内容：**

- 离线设计 B-class announcement metadata 与 A-class report metadata 的 lineage 对齐
- 字段映射 · 交叉引用 · 质量策略 · **无 live**

**优点：** 为跨类数据产品打基础  
**风险：** 低（设计 only）  
**CNINFO：** 0

---

## Recommendation

### 推荐顺序

1. **Option B first** — 准备 5-case isolated retry 批准包（**推荐优先**）
2. **Then Option A** — retry 决策后创建 commit boundary
3. **Then Option C or D** — 视并行优先级：
   - 若需更多 B-class 证据 → **Option C**（100 家规划 only，**不立即 live**）
   - 若需跨类整合 → **Option D**（lineage integration design）

### 明确不推荐

- **立即 100-company live expansion**
- 在未完成 5-case retry 决策前启动新一轮 live 扩大
- 任何 `verified` / `production_ready` 声明

---

## Red Lines（所有选项）

- No CNINFO until explicit approval per option
- No PDF download · No PDF parse
- No DB · No MinIO · No RAG
- No verified · No production_ready · No testing_stable_sample upgrade
- No modification of Phase 1 / TLC002 / Phase 2 / C-class outputs

---

## Related

| 文档 | 路径 |
|------|------|
| closure review | [cninfo_b_class_phase25_expansion_closure_review.md](cninfo_b_class_phase25_expansion_closure_review.md) |
| closure summary | [cninfo_b_class_phase25_expansion_closure_summary.md](../outputs/validation/cninfo_b_class_phase25_expansion_closure_summary.md) |
| failed-case triage | [cninfo_b_class_phase25_failed_case_triage.csv](../outputs/validation/cninfo_b_class_phase25_failed_case_triage.csv) |
| retry planning note | [cninfo_b_class_phase25_failed_retry_planning_note.md](cninfo_b_class_phase25_failed_retry_planning_note.md) |
