# CNINFO A 类 Phase 1 Next-step Recommendation

_生成时间：2026-07-09_

> **上下文：** `a_class_phase1_tiny_live_metadata_v2_closure_gate = PASS_WITH_CAVEAT` · tiny live v2 收口完成 · **不是 verified** · **不是 production_ready**

---

## Current Boundary（已达成）

| 层 | 状态 |
|----|------|
| schema freeze v1 | `PASS_OFFLINE` |
| ready-case benchmark | `READY_FOR_REVIEW` · AC001–AC005 |
| tiny live v1 | `PASS_WITH_CAVEAT`（历史 · 有 caveat） |
| tiny live v2 | `PASS_WITH_CAVEAT` · **5/5 correct report-type** |
| v2 closure | `PASS_WITH_CAVEAT` |

**红线保持：** metadata only · 无 PDF 下载/解析 · 无 DB/MinIO/RAG · 无 verified

---

## Options

### Option A — Commit A-class Phase 1 freeze + benchmark + tiny live v2 closure boundary

**内容：**

- 归档 Phase 1 产物链：freeze v1 · ready-case benchmark · tiny live v1/v2 · fix · closure
- 固化 gate 表与 red-line 声明
- 将 universe v2 draft 标记为 Phase 1 tiny live 参考 universe（仍非 production）

**优点：** 边界清晰，可审计，为 Phase 2 提供稳定起点  
**风险：** 低（文档/边界 only，无 live）

**推荐优先级：** **第一**

---

### Option B — Prepare A-class Phase 2 20-company metadata expansion planning

**内容：**

- 起草 20 家 universe · approval 包 · dry-run runner 扩展
- 继承 v2 matching logic · 仍 metadata-only

**优点：** 扩大 coverage 证据  
**风险：** 须新 approval；仍 tiny-to-small，非生产

**推荐优先级：** Option A 之后

---

### Option C — Prepare A/B report-announcement lineage integration design

**内容：**

- A-class `report_document` 与 B-class announcement metadata 谱系对齐设计
- 离线 only · 无 live · 无 PDF

**优点：** 跨类一致性，支撑未来 lineage QA  
**风险：** 设计复杂度；与 C-class 边界须明确

**推荐优先级：** Option A 之后；可与 Option B 并行规划

---

### Option D — Registry documentation sync only; no status upgrade

**内容：**

- 同步 `phase1_report_title_exclusions`（含英文变体）到 registry draft 文档
- **不**改 `live_validation_status` · **不写 verified** · **不**升 `testing_stable_sample`

**优点：** 低改动、低风险  
**风险：** 不扩大验证覆盖面

**推荐优先级：** 可与 Option A 同轮执行

---

## Recommended Sequence

```
1. Option A  — Phase 1 boundary closure signoff（本轮已完成文档包）
2. Option D  — registry 文档同步（可选 · 同轮）
3. Option B 或 C — Phase 2 扩展 或 A/B lineage 设计（须新 approval）
```

**明确不推荐（当前阶段）：**

- PDF download / parsing
- OCR / section extraction
- DB / MinIO / RAG
- verified / production_ready / testing_stable_sample 升级

---

## Immediate Next Task

**Option A：** 人工审阅并 signoff [v2 closure review](cninfo_a_class_phase1_tiny_live_metadata_v2_closure_review.md) + [closure summary](../outputs/validation/cninfo_a_class_phase1_tiny_live_metadata_v2_closure_summary.md)，确认 Phase 1 A-class metadata layer 边界可冻结归档。
