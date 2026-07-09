# CNINFO B 类 Phase 2 — Next Step Recommendation

_生成时间：2026-07-09_

> **性质：** Phase 2 closure 后路线建议；**离线 only** · **无 live** · **不是 verified**

**当前状态：**

```text
b_class_phase2_expansion_closure_gate = PASS_WITH_CAVEAT
b_class_phase2_expansion_execution_gate = PASS_WITH_CAVEAT
b_class_phase1_tiny_live_closure_gate = PASS_WITH_CAVEAT
```

Phase 2 Option A：**20/20** acceptable · CNINFO **40** · PDF **0**

---

## Options

### Option A — Hold at 20-company Phase 2 and commit boundary

**内容：**

- 将 Phase 2 planning + runner + live execution + closure 产物纳入 **git commit boundary**
- 冻结 Option A（20 家）为 B-class Phase 2 metadata expansion 里程碑
- 不在本阶段继续 live 扩大

**优点：** 清晰版本节点；便于审阅与并行 A/C/D 工作  
**风险：** 低  
**CNINFO：** 0（commit only）

---

### Option B — Prepare 50-company Phase 2.5 expansion planning

**内容：**

- 离线准备 Option B universe design + approval package
- 扩展 bucket 规则至 50 家；**不**自动 live
- 评估 EP002 transient error 监控与 isolated retry 纪律

**优点：** 在 Phase 2 成功基础上适度扩大样本  
**风险：** 中（批次更长 · 潜在 network_error）  
**CNINFO：** 0 until explicit approval

---

### Option C — B-class + A-class report/announcement lineage integration design

**内容：**

- 离线设计 B-class announcement metadata 与 A-class report metadata 的 lineage 对齐
- 字段映射 · 交叉引用 · 质量策略 · **无 live**

**优点：** 为跨类数据产品打基础  
**风险：** 低（设计 only）  
**CNINFO：** 0

---

### Option D — Title/date matching hardening before further expansion

**内容：**

- 强化 periodic_report 标题匹配规则
- general_announcement 选取策略（避免券商核查意见等非代表性公告）
- 离线 fixture + benchmark 扩展

**优点：** 降低扩大样本后的 `needs_review` 与误匹配  
**风险：** 低  
**CNINFO：** 0

---

## Recommendation

### 推荐顺序

1. **Option A first** — 创建 **commit boundary** after closure（本回合收口后的首要动作）
2. **Then Option B or C** — 视并行优先级：
   - 若需更多 B-class 证据 → **Option B**（50 家规划）
   - 若需跨类整合 → **Option C**（lineage integration design）
3. **Option D** 可与 B/C 并行作为质量加固 track

### 明确不推荐

- **立即 100-company live expansion**（Option C in expansion plan）
- 在未 commit Option A 边界前启动新一轮 live
- 任何 `verified` / `production_ready` 声明

---

## Red Lines（所有选项）

- No CNINFO until explicit approval per option
- No PDF download · No PDF parse
- No DB · No MinIO · No RAG
- No verified · No production_ready · No testing_stable_sample upgrade
- No modification of Phase 1 / TLC002 / C-class outputs

---

## Related

| 文档 | 路径 |
|------|------|
| closure review | [cninfo_b_class_phase2_expansion_closure_review.md](cninfo_b_class_phase2_expansion_closure_review.md) |
| closure summary | [cninfo_b_class_phase2_expansion_closure_summary.md](../outputs/validation/cninfo_b_class_phase2_expansion_closure_summary.md) |
| expansion plan | [cninfo_b_class_phase2_expansion_plan.md](cninfo_b_class_phase2_expansion_plan.md) |
